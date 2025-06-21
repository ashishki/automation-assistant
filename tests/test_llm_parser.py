import pytest
import json
import openai
from automation_assistant.llm_parser import LLMParser

class DummyChoice:
    def __init__(self, text: str):
        # Simulate the ChatCompletionChoice
        self.text = text

class DummyResponse:
    def __init__(self, choices):
        # Simulate the ChatCompletion response
        self.choices = choices

def test_parse_success(monkeypatch):
    """
    Test that a well-formed JSON string from the LLM is parsed correctly.
    """
    expected_plan = {"trigger": "cron", "schedule": "0 9 * * MON", "actions": ["gmail_summary"]}
    json_text = json.dumps(expected_plan)

    # Monkey-patch the OpenAI call to return our dummy response
    def fake_create(model, messages, temperature):
        return DummyResponse([DummyChoice(text=json_text)])
    monkeypatch.setattr(openai.ChatCompletion, "create", fake_create)

    parser = LLMParser()
    result = parser.parse("Generate a weekly summary workflow")
    assert isinstance(result, dict)
    assert result == expected_plan

def test_parse_api_error(monkeypatch):
    """
    Test that an OpenAIError is propagated when the API call fails.
    """
    # Monkey-patch to raise an API error
    def fake_create(*args, **kwargs):
        raise openai.OpenAIError("API is down")
    monkeypatch.setattr(openai.ChatCompletion, "create", fake_create)

    parser = LLMParser()
    with pytest.raises(openai.OpenAIError):
        parser.parse("Any prompt")

def test_parse_invalid_json(monkeypatch):
    """
    Test that a non-JSON response text raises a ValueError.
    """
    # Monkey-patch to return text that is not valid JSON
    def fake_create(*args, **kwargs):
        return DummyResponse([DummyChoice(text="not-a-json")])
    monkeypatch.setattr(openai.ChatCompletion, "create", fake_create)

    parser = LLMParser()
    with pytest.raises(ValueError):
        parser.parse("Broken JSON prompt")
