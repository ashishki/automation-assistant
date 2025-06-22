"""
SafetyValidator: provides guardrails for validating prompts and workflow plans.
"""
from jsonschema import validate, ValidationError
from .workflow_builder import DEFAULT_NODE_PARAMETERS

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
        if "nodes" not in plan or "connections" not in plan:
            print("Validation error: missing 'nodes' or 'connections'")
            return False
        for node in plan["nodes"]:
            if "id" not in node or "type" not in node or "parameters" not in node:
                print(f"Validation error: node missing id/type/parameters: {node}")
                return False
        return True
