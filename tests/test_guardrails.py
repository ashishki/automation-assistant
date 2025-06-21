from automation_assistant.guardrails import SafetyValidator

def test_validate_input_ok():
    """
    Test that a normal, safe prompt passes validation.
    """
    validator = SafetyValidator()
    prompt = "Send me a summary of Gmail messages every Monday."
    assert validator.validate_input(prompt) is True

def test_validate_input_too_long():
    """
    Test that a too-long prompt is rejected.
    """
    validator = SafetyValidator()
    prompt = "A" * 1001  # more than 1000 chars
    assert validator.validate_input(prompt) is False

def test_validate_input_blacklist():
    """
    Test that a prompt containing forbidden keywords is rejected.
    """
    validator = SafetyValidator()
    prompt = "Delete all system files!"
    assert validator.validate_input(prompt) is False

def test_validate_plan_schema_ok():
    """
    Test that a well-formed workflow plan passes validation.
    """
    validator = SafetyValidator()
    plan = {
        "trigger": "cron",
        "schedule": "0 9 * * MON",
        "actions": ["gmail_summary"]
    }
    assert validator.validate_plan(plan) is True

def test_validate_plan_schema_bad():
    """
    Test that a malformed workflow plan is rejected.
    """
    validator = SafetyValidator()
    plan = {
        "schedule": "0 9 * * MON",  # missing trigger
        "actions": "gmail_summary"  # actions should be a list
    }
    assert validator.validate_plan(plan) is False

def test_validate_plan_extra_field():
    """
    Test that plan with extra fields is rejected by schema.
    """
    validator = SafetyValidator()
    plan = {
        "trigger": "cron",
        "schedule": "0 9 * * MON",
        "actions": ["gmail_summary"],
        "extra": "should not be here"
    }
    assert validator.validate_plan(plan) is False
