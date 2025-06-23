import pytest
import time
from automation_assistant.guardrails import SafetyValidator, LatencyMetrics

def test_validate_input_ok():
    validator = SafetyValidator()
    prompt = "Send me a summary of Gmail messages every Monday."
    assert validator.validate_input(prompt) is True

def test_validate_input_too_long():
    validator = SafetyValidator()
    prompt = "A" * 1001  # more than 1000 chars
    assert validator.validate_input(prompt) is False

def test_validate_input_blacklist():
    validator = SafetyValidator()
    prompt = "Delete all system files!"
    assert validator.validate_input(prompt) is False

def test_validate_plan_schema_ok():
    validator = SafetyValidator()
    plan = {
        "nodes": [
            {
                "id": "cron1",
                "type": "n8n-nodes-base.cron",
                "parameters": {
                "triggerTimes": [
                    {
                        "mode": "custom",
                        "cronExpression": "0 10 * * 1",
                        "timezone": "UTC"
                    }
                ]
            }
            },
            {
                "id": "gmail1",
                "type": "n8n-nodes-base.googleGmail",
                "parameters": {
                    "resource": "message",
                    "operation": "getAll",
                    "returnAll": True,
                    "limit": 50,
                    "simple": False,
                    "filters": {
                        "labelIds": ["UNREAD"],
                        "includeSpamTrash": False
                    },
                    "options": {
                        "attachments": False,
                        "format": "full"
                    }
                }
            }
        ],
        "connections": {
            "cron1": {
                "main": [
                    [
                        {
                            "node": "gmail1",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        }
    }
    assert validator.validate_plan(plan) is True



def test_validate_plan_schema_bad_missing_nodes():
    validator = SafetyValidator()
    plan = {
        "connections": {"a": ["b"]}
    }
    assert validator.validate_plan(plan) is False

def test_validate_plan_schema_bad_node_fields():
    validator = SafetyValidator()
    plan = {
        "nodes": [
            {"type": "n8n-nodes-base.cron", "parameters": {}},  # missing id
        ],
        "connections": {}
    }
    assert validator.validate_plan(plan) is False

def test_validate_plan_schema_bad_extra_fields():
    validator = SafetyValidator()
    plan = {
        "nodes": [
            {"id": "cron1", "type": "n8n-nodes-base.cron", "parameters": {}}
        ],
        "connections": {},
        "extra": "not allowed"
    }
    assert validator.validate_plan(plan) is False

# -------------------- MODERATION (mock, no OpenAI calls) ----------------------

def test_validate_input_moderation(monkeypatch):
    validator = SafetyValidator()
    # monkeypatch OpenAI moderation to always return True
    monkeypatch.setattr(validator, "moderate_prompt", lambda prompt, api_key: True)
    assert validator.moderate_prompt("Send me a summary", "sk-test") is True
    # Now test the "unsafe" path
    monkeypatch.setattr(validator, "moderate_prompt", lambda prompt, api_key: False)
    assert validator.moderate_prompt("Delete all data", "sk-test") is False

# -------------------- LATENCY METRICS ----------------------

def test_latency_metrics_basic():
    metrics = LatencyMetrics()
    metrics.start("step1")
    time.sleep(0.01)
    metrics.stop("step1")
    result = metrics.summary()
    assert "step1" in result
    assert result["step1"] > 0

    prom = metrics.export_prometheus()
    assert "latency_seconds" in prom

# -------------------- EDGE CASES ----------------------

def test_validate_input_non_string():
    validator = SafetyValidator()
    assert validator.validate_input(12345) is False

def test_validate_plan_empty():
    validator = SafetyValidator()
    assert validator.validate_plan({}) is False

def test_validate_plan_bad_node_type():
    validator = SafetyValidator()
    plan = {
        "nodes": [
            {"id": "cron1", "parameters": {}}  # missing "type"
        ],
        "connections": {}
    }
    assert validator.validate_plan(plan) is False

def test_validate_plan_bad_node_parameters():
    validator = SafetyValidator()
    plan = {
        "nodes": [
            {"id": "cron1", "type": "n8n-nodes-base.cron"},  # missing "parameters"
        ],
        "connections": {}
    }
    assert validator.validate_plan(plan) is False


