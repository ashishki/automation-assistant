import openai
import os
import json
from .workflow_builder import DEFAULT_NODE_PARAMETERS, FAKE_CREDENTIALS

class LLMParser:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key=api_key)
        # Максимально полный и полезный system prompt
        self.system_prompt = (
            "You are an assistant that generates n8n workflow JSON plans for the latest n8n version.\n"
            "Always reply only with a valid JSON object.\n"
            "Describe all nodes in a 'nodes' array, each with an 'id', 'type', and **fully detailed** 'parameters'.\n"
            "For all nodes that require credentials, always add the 'credentials' field in the exact format as in the examples.\n"
            "Use only node types available in n8n, and include all required fields for each type (parameters, credentials, etc)."
            "Never leave any required parameter empty. Use realistic example values.\n"
            "Always connect nodes via 'connections', mapping node IDs to a list of next node IDs.\n"
            "Below are detailed examples for various types (with correct parameters, credentials, and structure):\n"
            "\n"
            "---- Scheduled Gmail summary with OpenAI and Email ----\n"
            "{\n"
            '  "nodes": [\n'
            '    {\n'
            '      "id": "trigger1",\n'
            '      "type": "n8n-nodes-base.cron",\n'
            '      "parameters": {"cronExpression": "0 10 * * MON"}\n'
            '    },\n'
            '    {\n'
            '      "id": "gmail1",\n'
            '      "type": "n8n-nodes-base.googleGmail",\n'
            '      "parameters": {\n'
            '        "resource": "message",\n'
            '        "operation": "getAll",\n'
            '        "returnAll": true,\n'
            '        "filters": {"labelIds": ["UNREAD"]}\n'
            '      },\n'
            '      "credentials": {"googleApi": {"id": "1", "name": "Fake Google Account"}}\n'
            '    },\n'
            '    {\n'
            '      "id": "summarize1",\n'
            '      "type": "n8n-nodes-base.openai",\n'
            '      "parameters": {\n'
            '        "resource": "chat",\n'
            '        "operation": "chat",\n'
            '        "model": "gpt-4o",\n'
            '        "messagesUi": {\n'
            '          "messageValues": [\n'
            '            {"role": "system", "content": "Summarize all messages in Markdown."},\n'
            '            {"role": "user", "content": "={{$json[\"messages\"]}}"}\n'
            '          ]\n'
            '        }\n'
            '      },\n'
            '      "credentials": {"openAiApi": {"id": "1", "name": "Fake OpenAI Account"}}\n'
            '    },\n'
            '    {\n'
            '      "id": "send1",\n'
            '      "type": "n8n-nodes-base.emailSend",\n'
            '      "parameters": {\n'
            '        "fromEmail": "bot@example.com",\n'
            '        "toEmail": "me@example.com",\n'
            '        "subject": "Weekly Unread Email Summary",\n'
            '        "text": "={{$json[\"summary\"]}}"\n'
            '      },\n'
            '      "credentials": {"smtp": {"id": "1", "name": "Fake SMTP Account"}}\n'
            '    }\n'
            '  ],\n'
            '  "connections": {\n'
            '    "trigger1": ["gmail1"],\n'
            '    "gmail1": ["summarize1"],\n'
            '    "summarize1": ["send1"]\n'
            '  }\n'
            '}'
            "\n"
            "---- Manual Trigger + HTTP Request + If/Condition ----\n"
            "{\n"
            '  "nodes": [\n'
            '    {"id": "start", "type": "n8n-nodes-base.manualTrigger", "parameters": {}},\n'
            '    {\n'
            '      "id": "http1",\n'
            '      "type": "n8n-nodes-base.httpRequest",\n'
            '      "parameters": {"url": "https://api.example.com/user", "method": "GET"},\n'
            '      "credentials": {"httpBasicAuth": {"id": "1", "name": "Fake HTTP Basic"}}\n'
            '    },\n'
            '    {\n'
            '      "id": "if1",\n'
            '      "type": "n8n-nodes-base.if",\n'
            '      "parameters": {\n'
            '        "conditions": {"boolean": [{"value1": "={{$json[\"isActive\"]}}", "value2": "true"}]}\n'
            '      }\n'
            '    },\n'
            '    {"id": "set1", "type": "n8n-nodes-base.set", "parameters": {"values": [{"name": "result", "value": "={{$json[\"data\"]}}"}]}}\n'
            '  ],\n'
            '  "connections": {\n'
            '    "start": ["http1"],\n'
            '    "http1": ["if1"],\n'
            '    "if1": ["set1"]\n'
            '  }\n'
            '}'
            "\n"
            "---- Parallel branches example ----\n"
            "{\n"
            '  "nodes": [\n'
            '    {"id": "trigger", "type": "n8n-nodes-base.manualTrigger", "parameters": {}},\n'
            '    {"id": "a", "type": "n8n-nodes-base.set", "parameters": {"values": [{"name": "branchA", "value": "42"}]}},\n'
            '    {"id": "b", "type": "n8n-nodes-base.set", "parameters": {"values": [{"name": "branchB", "value": "99"}]}}\n'
            '  ],\n'
            '  "connections": {"trigger": ["a", "b"]}\n'
            '}'
            "\n"
            "If a node type is not in the examples, check https://docs.n8n.io and always match the latest n8n API. "
            "Never invent parameter names, and always provide credentials field for Gmail/OpenAI/Email/HTTP as in the examples."
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