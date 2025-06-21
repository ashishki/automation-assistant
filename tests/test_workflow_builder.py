import pytest
from automation_assistant.workflow_builder import WorkflowBuilder

class DummyResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code
    def json(self):
        return self._json
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

class DummySession:
    def __init__(self):
        self.last_payload = None
    def post(self, url, json):
        self.last_payload = json
        # Always return a fake workflow with id
        return DummyResponse({"id": "abc123", "name": json.get("name", "Unnamed")})

def test_create_workflow_success(monkeypatch):
    """
    Test that a valid plan leads to a successful workflow creation.
    """
    # Patch requests.Session with our dummy session
    builder = WorkflowBuilder(n8n_url="http://fake:5678", session=DummySession())
    plan = {
        "trigger": "cron",
        "schedule": "0 9 * * MON",
        "actions": ["gmail_summary"]
    }
    result = builder.create_workflow(plan)
    assert isinstance(result, dict)
    assert "id" in result
    assert result["name"].startswith("Workflow")

def test_create_workflow_api_error(monkeypatch):
    """
    Test that an API error during workflow creation is raised.
    """
    class BadSession:
        def post(self, url, json):
            return DummyResponse({}, status_code=500)
    builder = WorkflowBuilder(n8n_url="http://fake:5678", session=BadSession())
    plan = {
        "trigger": "cron",
        "schedule": "0 9 * * MON",
        "actions": ["gmail_summary"]
    }
    with pytest.raises(Exception):
        builder.create_workflow(plan)
