import os
import time
from dotenv import load_dotenv
import requests
from automation_assistant.llm_parser import LLMParser
from automation_assistant.guardrails import SafetyValidator
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

def main():
    # Load .env variables
    load_dotenv()
    n8n_url = os.getenv("N8N_API_URL")           # http://localhost:5678
    email   = os.getenv("N8N_USER_EMAIL")
    pwd     = os.getenv("N8N_USER_PASSWORD")

    if not (n8n_url and email and pwd):
        print("ERROR: Missing N8N_API_URL or login credentials")
        return

    # Step 1: Login (cookie-based session)
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

    # Give n8n a bit of time to initialize completely
    time.sleep(2)

    # Step 2: Get user prompt
    prompt = input("Enter your workflow request (in English): ")

    # Step 3: Validate prompt for safety
    validator = SafetyValidator()
    if not validator.validate_input(prompt):
        print("Prompt failed safety validation. Please try again with a safer request.")
        return

    # Step 4: Parse prompt into workflow plan using LLM
    parser = LLMParser()
    try:
        plan = parser.parse(prompt)
        print("Generated plan:", plan)
    except Exception as e:
        print(f"LLM failed to generate a plan: {e}")
        return

    # Step 5: Validate plan schema and logic
    if not validator.validate_plan(plan):
        print("Workflow plan failed schema validation. Please check your input.")
        return

    # Step 6: Build and create workflow in n8n (using cookie-authenticated session)
    builder = WorkflowBuilder(n8n_url, session)
    try:
        workflow = builder.create_workflow(plan)
    except Exception as e:
        print(f"Workflow creation failed: {e}")
        return

    # Step 7: Show result
    print(f"\nWorkflow created successfully in n8n!")
    print(f"Workflow ID: {workflow.get('id')}")
    print(f"Workflow name: {workflow.get('name')}")
    print(f"Check it in the n8n UI: {n8n_url}/workflow/{workflow.get('id')}")

if __name__ == "__main__":
    main()
