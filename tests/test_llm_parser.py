import pytest
import json
from automation_assistant.llm_parser import LLMParser

@pytest.fixture(autouse=True)
def set_openai_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-1234567")

class DummyResponse:
    def __init__(self, content):
        self.choices = [type("choice", (), {"message": type("msg", (), {"content": content})})()]

class DummyClient:
    def __init__(self, reply):
        self.reply = reply
        self.chat = type("Chat", (), {"completions": self})()
    def create(self, **kwargs):
        return DummyResponse(self.reply)

def test_llmparser_parses_json(monkeypatch):
    """Test LLMParser parses valid JSON responses."""
    reply = json.dumps({
        "name": "Weekly Gmail Summary",
        "nodes": [{"type": "scheduleTrigger", "parameters": {"cron": "0 10 * * MON"}}]
    })
    parser = LLMParser()
    parser.client = DummyClient(reply)  # Monkeypatch OpenAI client
    plan = parser.parse("Every Monday at 10:00 AM, send me a summary of unread Gmail emails.")
    assert plan["name"] == "Weekly Gmail Summary"
    assert isinstance(plan["nodes"], list)

def test_llmparser_handles_invalid_json(monkeypatch):
    """Test LLMParser fallback for non-JSON output."""
    parser = LLMParser()
    parser.client = DummyClient("I don't know what to do!")
    plan = parser.parse("unknown task")
    assert "raw_response" in plan


def test_llmparser_branching(monkeypatch):
    import json
    from automation_assistant.llm_parser import LLMParser

    class DummyCreate:
        def create(self, **kwargs):
            class Dummy:
                choices = [type("M", (), {"message": type("MM", (), {
                    "content": json.dumps({
                        "nodes": [
                            {"id": "trigger1", "type": "schedule"},
                            {"id": "check", "type": "if"},
                            {"id": "A", "type": "doA"},
                            {"id": "B", "type": "doB"}
                        ],
                        "connections": {
                            "trigger1": ["check"],
                            "check": ["A", "B"],
                            "A": ["B"]
                        }
                    })
                })})]
            return Dummy()

    class DummyCompletions:
        def __init__(self):
            self.create = DummyCreate().create

    class DummyChat:
        def __init__(self):
            self.completions = DummyCompletions()

    class DummyClient:
        def __init__(self, api_key=None):
            self.chat = DummyChat()

    monkeypatch.setattr("automation_assistant.llm_parser.openai.OpenAI", DummyClient)
    parser = LLMParser()
    plan = parser.parse("If today is Monday, do A and B in parallel after trigger.")

    assert "nodes" in plan and "connections" in plan
    assert any(n["id"] == "check" for n in plan["nodes"])
    assert set(plan["connections"]["check"]) == {"A", "B"}