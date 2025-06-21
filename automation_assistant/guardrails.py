"""
SafetyValidator: provides guardrails for validating prompts and workflow plans.
"""
from jsonschema import validate, ValidationError

PLAN_SCHEMA = {
    "type": "object",
    "required": ["trigger", "schedule", "actions"],
    "properties": {
        "trigger": {"type": "string"},
        "schedule": {"type": "string"},
        "actions": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "additionalProperties": False
}

class SafetyValidator:
    def __init__(self):
        # List of forbidden keywords for prompts
        self.blacklist = {"delete", "shutdown", "format", "rm -rf", "destroy"}
        # Max allowed prompt length
        self.max_prompt_length = 1000

    def validate_input(self, prompt: str) -> bool:
        """
        Check that the prompt is not too long and does not contain forbidden keywords.
        """
        if not isinstance(prompt, str):
            return False
        if len(prompt) > self.max_prompt_length:
            return False
        prompt_lower = prompt.lower()
        for bad_word in self.blacklist:
            if bad_word in prompt_lower:
                return False
        return True

    def validate_plan(self, plan: dict) -> bool:
        """
        Validate the workflow plan against a JSON Schema.
        """
        try:
            validate(instance=plan, schema=PLAN_SCHEMA)
        except ValidationError as e:
            print(f"Plan validation error: {e}")
            return False
        return True
