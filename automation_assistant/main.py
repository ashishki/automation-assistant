import os
import time
from dotenv import load_dotenv
import requests
from automation_assistant.llm_parser import LLMParser
from automation_assistant.guardrails import SafetyValidator, LatencyMetrics
from automation_assistant.workflow_builder import WorkflowBuilder

def login_and_fetch_session(n8n_url: str, email: str, password: str) -> requests.Session:
    """
    Log in via /rest/login (form data), return a session with the auth cookie.
    """
    
    sess = requests.Session()
    resp = sess.post(
        f"{n8n_url}/rest/login",
        data={
            "emailOrLdapLoginId": email,
            "password": password,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    resp.raise_for_status()
    return sess

def fetch_workflows(session: requests.Session, n8n_url: str) -> list:
    """
    Fetch workflows using the authenticated session.
    """
    resp = session.get(f"{n8n_url}/rest/workflows")
    resp.raise_for_status()
    return resp.json().get("data", [])


def main():
    load_dotenv()
    n8n_url = os.getenv("N8N_API_URL")
    email   = os.getenv("N8N_USER_EMAIL")
    pwd     = os.getenv("N8N_USER_PASSWORD")
    prompt = os.getenv("PROMPT")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not prompt:
        prompt = input("Enter your workflow request (in English): ")
    print("DEBUG: prompt =", prompt)
    
    if not (n8n_url and email and pwd and openai_api_key):
        print("ERROR: Missing N8N_API_URL, login credentials, or OpenAI API key")
        return

    # Metrics object for latency
    metrics = LatencyMetrics()
    validator = SafetyValidator()

    # 1. Login
    metrics.start("login")
    for i in range(1, 7):
        try:
            session = login_and_fetch_session(n8n_url, email, pwd)
            break
        except Exception as e:
            print(f"[Attempt {i}] Login failed ({e}), retrying in 5s…")
            time.sleep(5)
    else:
        print("ERROR: Could not log into n8n in time.")
        return
    metrics.stop("login")
    time.sleep(2)

    # 2. Pre-moderation (blacklist/length)
    metrics.start("pre_validation")
    if not validator.validate_input(prompt):
        print("Prompt failed safety validation. Please try again with a safer request.")
        return
    metrics.stop("pre_validation")

    # 3. Moderation API
    metrics.start("moderation")
    if not validator.moderate_prompt(prompt, openai_api_key):
        print("Prompt failed OpenAI moderation. Please try again.")
        return
    metrics.stop("moderation")

    # 4. LLM
    metrics.start("llm_generation")
    parser = LLMParser()
    try:
        plan = parser.parse(prompt)
        print("Generated plan:", plan)
    except Exception as e:
        print(f"LLM failed to generate a plan: {e}")
        return
    metrics.stop("llm_generation")

    # 5. Post-moderation
    metrics.start("post_validation")
    if not validator.validate_plan(plan):
        print("Workflow plan failed schema validation. Please check your input.")
        return
    metrics.stop("post_validation")

    # 6. Build and create workflow in n8n
    metrics.start("workflow_creation")
    builder = WorkflowBuilder(n8n_url, session)
    try:
        workflow = builder.create_workflow(plan)
    except Exception as e:
        print(f"Workflow creation failed: {e}")
        return
    metrics.stop("workflow_creation")

    # 7. Show result + metrics
    if "data" in workflow:
        workflow_data = workflow["data"]
    else:
        workflow_data = workflow
    print(f"\nWorkflow created successfully in n8n!")
    print(f"Workflow ID: {workflow_data.get('id')}")
    print(f"Workflow name: {workflow_data.get('name')}")
    print(f"Check it in the n8n UI: {n8n_url}/workflow/{workflow_data.get('id')}")
    print("\n=== Latency Metrics ===")
    for step, latency in metrics.summary().items():
        print(f"{step}: {latency:.3f} sec")
    # (Optional) write metrics to file for Prometheus server
    with open("metrics.prom", "w") as f:
        f.write(metrics.export_prometheus())

if __name__ == "__main__":
    main()