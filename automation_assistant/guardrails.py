"""
SafetyValidator: provides guardrails for validating prompts and workflow plans.
"""
from jsonschema import validate, ValidationError

PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "nodes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "type": {"type": "string"},
                    "parameters": {"type": "object"},
                },
                "required": ["id", "type"]
            },
            "minItems": 1
        },
        "connections": {
            "type": "object",
            "additionalProperties": {
                "type": "array",
                "items": {"type": "string"}
            }
        }
    },
    "required": ["nodes", "connections"],
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
        try:
            # Simple: branch on structure
            if "nodes" in plan and "connections" in plan:
                validate(plan, PLAN_SCHEMA)
            else:
                validate(plan, PLAN_SCHEMA)
            return True
        except ValidationError as e:
            print("Plan validation error:", e)
            return False
