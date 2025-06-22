import openai
import os
import json

class LLMParser:
    """
    Generates workflow plans from user prompts using OpenAI GPT-4o with explicit graph structure.
    """
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key=api_key)
        # System prompt uses valid n8n node types and connections!
        self.system_prompt = (
            "You are an assistant that generates n8n workflow JSON plans.\n"
            "Always reply only with a valid JSON object.\n"
            "Describe all nodes in a 'nodes' array, each with an 'id', 'type', and (optional) 'parameters'.\n"
            "Use n8n node types like 'n8n-nodes-base.cron', 'n8n-nodes-base.googleGmail', 'n8n-nodes-base.openai', 'n8n-nodes-base.emailSend', 'n8n-nodes-base.if'.\n"
            "Describe all node connections in a 'connections' object, mapping node IDs to an array of next node IDs.\n"
            "If there is a branch, include both connections.\n"
            "Example (with branching):\n"
            "{\n"
            '  "nodes": [\n'
            '    {"id": "trigger1", "type": "n8n-nodes-base.cron", "parameters": {"cronExpression": "0 10 * * MON"}},\n'
            '    {"id": "check", "type": "n8n-nodes-base.if", "parameters": {"condition": "hasAttachment"}},\n'
            '    {"id": "A", "type": "n8n-nodes-base.googleGmail"},\n'
            '    {"id": "B", "type": "n8n-nodes-base.openai"}\n'
            "  ],\n"
            '  "connections": {\n'
            '    "trigger1": ["check"],\n'
            '    "check": ["A", "B"],\n'
            '    "A": ["B"]\n'
            "  }\n"
            "}"
        )

    def parse(self, prompt: str) -> dict:
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        try:
            plan = json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            print("WARNING: LLM output is not JSON. Fallback to empty plan.")
            return {"raw_response": response.choices[0].message.content}
        return plan
