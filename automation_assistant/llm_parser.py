import openai
import os
import json
from .workflow_builder import DEFAULT_NODE_PARAMETERS, FAKE_CREDENTIALS

class LLMParser:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key=api_key)
        
        self.system_prompt = (
            "You are an expert automation engineer generating robust, production-ready n8n workflow plans as JSON.\n"
            "You must always reply ONLY with a valid JSON object representing the entire workflow.\n"
            "\n"
            "# Output requirements\n"
            "1. Reply with a single JSON object ONLY, no comments or explanation.\n"
            "2. All workflow nodes must be described in a 'nodes' array, each with an 'id', 'type', and fully filled 'parameters'.\n"
            "3. Node types must strictly use canonical n8n types (see examples below).\n"
            "4. Always specify all **required** parameters and credentials for each node type. Use realistic, non-empty example values (for emails, prompt texts, subjects, API keys, etc.).\n"
            "5. Describe node connections explicitly in the 'connections' object, mapping node IDs to their direct successors.\n"
            "6. Your output must conform to real n8n workflow JSON structure and pass schema validation for import into the n8n UI. Do not invent your own node types or fields.\n"
            "7. If a required parameter is missing from the user request, fill it with a plausible and safe example value.\n"
            "\n"
            "# Supported nodes (for MVP)\n"
            "- n8n-nodes-base.cron\n"
            "- n8n-nodes-base.googleGmail\n"
            "- n8n-nodes-base.openai\n"
            "- n8n-nodes-base.emailSend\n"
            "- n8n-nodes-base.if\n"
            "- n8n-nodes-base.httpRequest\n"
            "- n8n-nodes-base.set\n"
            "\n"
            "# Example 1: Gmail summary every Monday at 10:00\n"
            '{\n'
            '  "nodes": [\n'
            '    {\n'
            '      "id": "trigger1",\n'
            '      "name": "Schedule Trigger",\n'
            '      "type": "n8n-nodes-base.cron",\n'
            '      "typeVersion": 1,\n'
            '      "position": [240, 300],\n'
            '      "parameters": { "cronExpression": "0 10 * * MON" }\n'
            '    },\n'
            '    {\n'
            '      "id": "gmail1",\n'
            '      "name": "Gmail",\n'
            '      "type": "n8n-nodes-base.googleGmail",\n'
            '      "typeVersion": 1,\n'
            '      "position": [500, 300],\n'
            '      "parameters": {\n'
            '        "resource": "message",\n'
            '        "operation": "getAll",\n'
            '        "returnAll": true,\n'
            '        "filters": { "labelIds": ["UNREAD"] }\n'
            '      },\n'
            '      "credentials": { "googleApi": { "id": "1", "name": "Fake Google Account" } }\n'
            '    },\n'
            '    {\n'
            '      "id": "summarize1",\n'
            '      "name": "Summarize",\n'
            '      "type": "n8n-nodes-base.openai",\n'
            '      "typeVersion": 1,\n'
            '      "position": [740, 300],\n'
            '      "parameters": {\n'
            '        "resource": "chat",\n'
            '        "operation": "chat",\n'
            '        "model": "gpt-4o",\n'
            '        "messagesUi": {\n'
            '          "messageValues": [\n'
            '            { "role": "system", "content": "Summarize all emails in Markdown." },\n'
            '            { "role": "user", "content": "={{$json[\\"messages\\"]}}" }\n'
            '          ]\n'
            '        }\n'
            '      },\n'
            '      "credentials": { "openAiApi": { "id": "1", "name": "Fake OpenAI Account" } }\n'
            '    },\n'
            '    {\n'
            '      "id": "send1",\n'
            '      "name": "Send Email",\n'
            '      "type": "n8n-nodes-base.emailSend",\n'
            '      "typeVersion": 1,\n'
            '      "position": [980, 300],\n'
            '      "parameters": {\n'
            '        "fromEmail": "bot@example.com",\n'
            '        "toEmail": "me@example.com",\n'
            '        "subject": "Weekly Unread Email Summary",\n'
            '        "text": "={{$json[\\"summary\\"]}}"\n'
            '      },\n'
            '      "credentials": { "smtp": { "id": "1", "name": "Fake SMTP Account" } }\n'
            '    }\n'
            '  ],\n'
            '  "connections": {\n'
            '    "trigger1": {\n'
            '      "main": [ [ { "node": "gmail1", "type": "main", "index": 0 } ] ]\n'
            '    },\n'
            '    "gmail1": {\n'
            '      "main": [ [ { "node": "summarize1", "type": "main", "index": 0 } ] ]\n'
            '    },\n'
            '    "summarize1": {\n'
            '      "main": [ [ { "node": "send1", "type": "main", "index": 0 } ] ]\n'
            '    }\n'
            '  }\n'
            '}\n'
            "\n"
            "# Example 2: If branching after trigger\n"
            '{\n'
            '  "nodes": [\n'
            '    {"id": "trigger1", "type": "n8n-nodes-base.cron", "parameters": {"cronExpression": "0 12 * * *"}},\n'
            '    {"id": "if1", "type": "n8n-nodes-base.if", "parameters": {"conditions": {"string": [{"value1": "={{$json[\\"subject\\"]}}", "operation": "contains", "value2": "Urgent"}]}}},\n'
            '    {"id": "gmail1", "type": "n8n-nodes-base.googleGmail", "parameters": {"resource": "message", "operation": "getAll"}},\n'
            '    {"id": "send1", "type": "n8n-nodes-base.emailSend", "parameters": {"fromEmail": "bot@example.com", "toEmail": "admin@example.com", "subject": "Urgent!", "text": "={{$json[\\"body\\"]}}"}}\n'
            '  ],\n'
            '  "connections": {\n'
            '    "trigger1": { "main": [ [ { "node": "if1", "type": "main", "index": 0 } ] ] },\n'
            '    "if1": { "main": [\n'
            '      [ { "node": "gmail1", "type": "main", "index": 0 } ],\n'
            '      [ { "node": "send1", "type": "main", "index": 0 } ]\n'
            '    ] }\n'
            '  }\n'
            '}\n'
            "\n"
            "# Example 3: HTTP request, Set node, Send Email\n"
            '{\n'
            '  "nodes": [\n'
            '    {"id": "trigger1", "type": "n8n-nodes-base.cron", "parameters": {"cronExpression": "0 6 * * 1"}},\n'
            '    {"id": "http1", "type": "n8n-nodes-base.httpRequest", "parameters": {"url": "https://api.example.com", "method": "GET"}},\n'
            '    {"id": "set1", "type": "n8n-nodes-base.set", "parameters": {"values": [{"name": "summary", "value": "={{$json[\\"result\\"]}}" }]}},\n'
            '    {"id": "send1", "type": "n8n-nodes-base.emailSend", "parameters": {"fromEmail": "bot@example.com", "toEmail": "alerts@example.com", "subject": "API Result", "text": "={{$json[\\"summary\\"]}}"}}\n'
            '  ],\n'
            '  "connections": {\n'
            '    "trigger1": { "main": [ [ { "node": "http1", "type": "main", "index": 0 } ] ] },\n'
            '    "http1": { "main": [ [ { "node": "set1", "type": "main", "index": 0 } ] ] },\n'
            '    "set1": { "main": [ [ { "node": "send1", "type": "main", "index": 0 } ] ] }\n'
            '  }\n'
            '}\n'
            "\n"
            "# Rules\n"
            "- Do not invent node types or omit required parameters for any node.\n"
            "- Never output anything except valid JSON with the keys: nodes, connections.\n"
            "- Always provide realistic, non-empty example data for every field."
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
            return self._auto_fill(plan)
        except json.JSONDecodeError:
            print("WARNING: LLM output is not JSON. Fallback to empty plan.")
            return {"raw_response": response.choices[0].message.content}
        
    def _auto_fill(self, plan: dict) -> dict:
        """Add missing required fields and valid parameter values."""
        if "nodes" in plan:
            for idx, node in enumerate(plan["nodes"]):
                if "id" not in node or not node["id"]:
                    node["id"] = f"node{idx+1}"
                if "type" in node:
                    req_params = DEFAULT_NODE_PARAMETERS.get(node["type"], {})
                    node.setdefault("parameters", {})
                    for k, v in req_params.items():
                        node["parameters"].setdefault(k, v)
                    # Always add credentials if needed
                    creds = FAKE_CREDENTIALS.get(node["type"])
                    if creds:
                        node["credentials"] = creds
        return plan