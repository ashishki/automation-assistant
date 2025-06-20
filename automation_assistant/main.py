import os
from dotenv import load_dotenv
import requests

def fetch_workflows(n8n_url: str, n8n_api_key: str) -> list:
    """Fetch all workflows from n8n. Returns list of dicts."""
    headers = {"Authorization": f"Bearer {n8n_api_key}"}
    resp = requests.get(f"{n8n_url}/workflows", headers=headers)
    resp.raise_for_status()
    return resp.json()

def main():
    load_dotenv()
    url = os.getenv("N8N_API_URL")
    key = os.getenv("N8N_API_KEY")
    if not url or not key:
        print("ERROR: Missing N8N_API_URL or N8N_API_KEY")
        return

    try:
        workflows = fetch_workflows(url, key)
    except Exception as e:
        print(f"Failed to fetch workflows: {e}")
        return

    print("Workflows in n8n:")
    for wf in workflows:
        print(f"- {wf.get('id')}: {wf.get('name')}")

if __name__ == "__main__":
    main()
