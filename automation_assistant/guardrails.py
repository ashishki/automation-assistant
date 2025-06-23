import requests
import time
from jsonschema import validate, ValidationError
from .prompts import COMPLETE_PARAMS

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
                "type": "object",
                "properties": {
                    "main": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "node": {"type": "string"},
                                    "type": {"type": "string"},
                                    "index": {"type": "number"}
                                },
                                "required": ["node", "type", "index"]
                            }
                        }
                    }
                },
                "required": ["main"]
            }
        }
    },
    "required": ["nodes", "connections"],
    "additionalProperties": False
}


class SafetyValidator:
    def __init__(self):
        self.blacklist = {"delete", "shutdown", "format", "rm -rf", "destroy"}
        self.max_prompt_length = 1000

    def validate_input(self, prompt: str) -> bool:
        if not isinstance(prompt, str):
            return False
        if len(prompt) > self.max_prompt_length:
            print("Validation error: Prompt too long")
            return False
        prompt_lower = prompt.lower()
        for bad_word in self.blacklist:
            if bad_word in prompt_lower:
                print(f"Validation error: Forbidden keyword '{bad_word}'")
                return False
        return True

    def validate_plan(self, plan: dict) -> bool:
        # JSON Schema check
        try:
            validate(instance=plan, schema=PLAN_SCHEMA)
        except ValidationError as ve:
            print("Schema validation error:", ve)
            return False
        # Required parameters
        for node in plan.get("nodes", []):
            params_required = COMPLETE_PARAMS.get(node["type"], {})
            for key in params_required:
                if key not in node.get("parameters", {}):
                    print(f"Validation error: node '{node['id']}' missing parameter '{key}'")
                    return False
        return True

    def moderate_prompt(self, prompt: str, openai_api_key: str) -> bool:
        """
        Use OpenAI Moderation API to check for unsafe or restricted content in the prompt.
        Returns True if safe, False if flagged.
        """
        try:
            resp = requests.post(
                "https://api.openai.com/v1/moderations",
                headers={"Authorization": f"Bearer {openai_api_key}"},
                json={"input": prompt}
            )
            resp.raise_for_status()
            flagged = resp.json()['results'][0]['flagged']
            if flagged:
                print("Moderation: Prompt flagged as unsafe by OpenAI API")
            return not flagged
        except Exception as e:
            print(f"Moderation API call failed: {e}")
            # If API fails, block by default for safety
            return False

# Latency logger
class LatencyMetrics:
    def __init__(self):
        self.timings = {}

    def start(self, step):
        self.timings[step] = {"start": time.perf_counter(), "latency": None}

    def stop(self, step):
        end = time.perf_counter()
        if step in self.timings and self.timings[step]["start"]:
            self.timings[step]["latency"] = end - self.timings[step]["start"]

    def get(self, step):
        return self.timings.get(step, {}).get("latency")

    def summary(self):
        return {step: data["latency"] for step, data in self.timings.items()}

    def export_prometheus(self):
        # Export as Prometheus-style text (gauge per step)
        output = []
        for step, data in self.timings.items():
            if data["latency"] is not None:
                output.append(f"latency_seconds{{step=\"{step}\"}} {data['latency']:.4f}")
        return "\n".join(output)
