import os
import time
from dotenv import load_dotenv
import requests

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
    n8n_url = os.getenv("N8N_API_URL")           # http://n8n:5678
    email   = os.getenv("N8N_USER_EMAIL")        # тот e-mail, которым регистрировался
    pwd     = os.getenv("N8N_USER_PASSWORD")     # и его пароль

    if not (n8n_url and email and pwd):
        print("ERROR: Missing N8N_API_URL or login credentials")
        return

    # 1) логинимся
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

    # 2) даём пару секунд на окончательную инициализацию
    time.sleep(2)

    # 3) забираем workflow’ы
    try:
        workflows = fetch_workflows(session, n8n_url)
    except Exception as e:
        print(f"Failed to fetch workflows: {e}")
        return

    # 4) выводим
    print("Workflows in n8n:")
    for wf in workflows:
        print(f"- {wf.get('id')}: {wf.get('name')}")

if __name__ == "__main__":
    main()
