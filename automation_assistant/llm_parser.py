import openai
import os
import json
from typing import Dict, List, Any

# Complete parameters for all supported n8n nodes
COMPLETE_PARAMS = {
    "n8n-nodes-base.cron": {
        "mode": "everyWeek",
        "dayOfWeek": [1],  # Monday
        "hour": 10,
        "minute": 0,
        "timezone": "UTC"
    },
    "n8n-nodes-base.googleGmail": {
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
    },
    "n8n-nodes-base.itemLists": {
        "operation": "aggregateItems",
        "fieldsToAggregate": [
            {
                "fieldToAggregate": "",
                "destinationField": "emails"
            }
        ],
        "outputType": "oneItem"
    },
    "n8n-nodes-base.openai": {
        "resource": "chat",
        "operation": "chat",
        "model": "gpt-4o-mini",
        "options": {
            "temperature": 0.3,
            "maxTokens": 1000,
            "topP": 1,
            "frequencyPenalty": 0,
            "presencePenalty": 0
        },
        "messagesUi": {
            "messageValues": [
                {
                    "role": "system", 
                    "content": "You are a helpful assistant that summarizes emails. Create a concise summary in markdown format."
                },
                {
                    "role": "user", 
                    "content": "={{$json.emails.map(email => `Subject: ${email.subject}\\nFrom: ${email.from}\\nSnippet: ${email.snippet}`).join('\\n\\n')}}"
                }
            ]
        },
        "simplifyOutput": False
    },
    "n8n-nodes-base.emailSend": {
        "fromEmail": "noreply@yourdomain.com",
        "toEmail": "user@example.com",
        "subject": "📧 Weekly Email Summary - {{$now.format('YYYY-MM-DD')}}",
        "message": "={{$json.message.content || $json}}",
        "options": {
            "allowUnauthorizedCerts": False,
            "replyTo": "",
            "cc": "",
            "bcc": "",
            "priority": "normal"
        },
        "transport": "smtp"
    },
    "n8n-nodes-base.if": {
        "conditions": {
            "boolean": [],
            "number": [
                {
                    "value1": "={{$json.count}}",
                    "operation": "larger",
                    "value2": 0
                }
            ],
            "string": []
        },
        "combineOperation": "all"
    },
    "n8n-nodes-base.httpRequest": {
        "method": "GET",
        "url": "",
        "authentication": "none",
        "options": {
            "response": {
                "response": {
                    "responseFormat": "json"
                }
            }
        }
    }
}

FAKE_CREDENTIALS = {
    "n8n-nodes-base.googleGmail": {"googleApi": {"id": "1", "name": "Google Account"}},
    "n8n-nodes-base.openai": {"openAiApi": {"id": "1", "name": "OpenAI Account"}},
    "n8n-nodes-base.emailSend": {"smtp": {"id": "1", "name": "SMTP Account"}},
    "n8n-nodes-base.httpRequest": {"httpBasicAuth": {"id": "1", "name": "HTTP Basic Auth"}}
}

class LLMParser:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = openai.OpenAI(api_key=api_key)
        
        self.system_prompt = """You are an expert n8n workflow architect. Generate complete, production-ready n8n workflow JSON.

CRITICAL REQUIREMENTS:
1. Always include ALL required parameters for each node type
2. Always insert an Item Lists node to aggregate all emails into a single array field named 'emails' between Gmail and OpenAI nodes.
3. Use proper n8n expression syntax: ={{$json.field}} or ={{$node("NodeName").json.field}}
4. Include realistic credential references
5. Create sequential connections between nodes automatically
6. Use modern n8n parameter structure (v1.0+)
7. Generate only valid JSON - no explanations or comments

SUPPORTED NODE TYPES:
- n8n-nodes-base.cron (Schedule Trigger)
- n8n-nodes-base.googleGmail (Gmail)
- n8n-nodes-base.itemLists (Item Lists, for aggregating into emails)
- n8n-nodes-base.openai (OpenAI/ChatGPT)
- n8n-nodes-base.emailSend (Send Email)
- n8n-nodes-base.if (Conditional Logic)
- n8n-nodes-base.httpRequest (HTTP Request)

WORKFLOW STRUCTURE TEMPLATE:
{
  "nodes": [
    {
      "id": "trigger1",
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.cron",
      "typeVersion": 1,
      "parameters": { ... },
      "position": [240, 300],
      "credentials": {},
      "disabled": false
    },
    {
      "id": "gmail1",
      "name": "Get Unread Emails",
      "type": "n8n-nodes-base.googleGmail",
      "typeVersion": 1,
      "parameters": { ... },
      "credentials": { ... },
      "position": [460, 300],
      "disabled": false
    },
    {
      "id": "aggregate1",
      "name": "Aggregate Emails",
      "type": "n8n-nodes-base.itemLists",
      "typeVersion": 1,
      "parameters": {
        "operation": "aggregateItems",
        "fieldsToAggregate": [
          {
            "fieldToAggregate": "",
            "destinationField": "emails"
          }
        ],
        "outputType": "oneItem"
      },
      "position": [570, 300],
      "disabled": false
    },
    {
      "id": "openai1",
      "name": "Summarize Emails",
      "type": "n8n-nodes-base.openai",
      "typeVersion": 1,
      "parameters": {
        "resource": "chat",
        "operation": "chat",
        "model": "gpt-4o-mini",
        "options": { ... },
        "messagesUi": {
          "messageValues": [
            {
              "role": "system",
              "content": "Summarize emails in markdown format"
            },
            {
              "role": "user",
              "content": "={{$json.emails.map(email => `Subject: ${email.subject}\\nFrom: ${email.from}\\nSnippet: ${email.snippet}`).join('\\n\\n')}}"
            }
          ]
        },
        "simplifyOutput": false
      },
      "credentials": { ... },
      "position": [680, 300],
      "disabled": false
    },
    {
      "id": "email1",
      "name": "Send Summary",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 1,
      "parameters": { ... },
      "credentials": { ... },
      "position": [900, 300],
      "disabled": false
    }
  ],
  "connections": {
    "Schedule Trigger": { "main": [[{"node": "Get Unread Emails", "type": "main", "index": 0}]] },
    "Get Unread Emails": { "main": [[{"node": "Aggregate Emails", "type": "main", "index": 0}]] },
    "Aggregate Emails": { "main": [[{"node": "Summarize Emails", "type": "main", "index": 0}]] },
    "Summarize Emails": { "main": [[{"node": "Send Summary", "type": "main", "index": 0}]] }
  }
}

IMPORTANT NOTES:
- Always use node NAMES in connections, not IDs
- Always include the Item Lists node between Gmail and OpenAI.
- OpenAI prompt must reference $json.emails as shown above.
- Include position coordinates for visual layout
- Add proper credentials for each node type
- Use realistic parameter values
- Ensure all required fields are present
- Generate only valid JSON without any markdown formatting"""


    def parse(self, prompt: str) -> Dict[str, Any]:
        """
        Parse user prompt into complete n8n workflow JSON
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Create an n8n workflow for: {prompt}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=3000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            raw_content = response.choices[0].message.content
            print(f"DEBUG: Raw LLM response length: {len(raw_content)}", flush=True)
            
            plan = json.loads(raw_content)
            enhanced_plan = self._enhance_workflow(plan)
            
            print(f"DEBUG: Enhanced workflow has {len(enhanced_plan.get('nodes', []))} nodes", flush=True)
            return enhanced_plan
            
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON from LLM: {e}")
            return self._create_fallback_workflow(prompt)
        except Exception as e:
            print(f"ERROR: LLM parsing failed: {e}")
            return self._create_fallback_workflow(prompt)

    def _enhance_workflow(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance workflow with complete parameters and auto-connections
        """
        if "nodes" not in plan or not plan["nodes"]:
            return self._create_fallback_workflow("Default workflow")
            
        enhanced_nodes = []
        
        for idx, node in enumerate(plan["nodes"]):
            # Ensure required fields
            node.setdefault("id", f"node{idx+1}")
            node.setdefault("name", self._generate_node_name(node.get("type", ""), idx))
            node.setdefault("typeVersion", 1)
            node.setdefault("position", [240 + idx*220, 300])
            node.setdefault("disabled", False)
            
            # Merge complete parameters
            node_type = node.get("type", "")
            if node_type in COMPLETE_PARAMS:
                complete_params = self._deep_merge(
                    COMPLETE_PARAMS[node_type].copy(),
                    node.get("parameters", {})
                )
                node["parameters"] = complete_params
            
            # Add credentials if needed
            if node_type in FAKE_CREDENTIALS:
                node["credentials"] = FAKE_CREDENTIALS[node_type]
            
            enhanced_nodes.append(node)
        
        plan["nodes"] = enhanced_nodes
        
        # Auto-create connections if missing or incomplete
        existing_connections = plan.get("connections", {})
        if not existing_connections or len(existing_connections) < len(enhanced_nodes) - 1:
            plan["connections"] = self._create_auto_connections(enhanced_nodes)
        
        return plan

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """
        Deep merge two dictionaries
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result

    def _generate_node_name(self, node_type: str, index: int) -> str:
        """
        Generate human-readable node names
        """
        name_mapping = {
            "n8n-nodes-base.cron": "Schedule Trigger",
            "n8n-nodes-base.googleGmail": "Gmail",
            "n8n-nodes-base.openai": "OpenAI",
            "n8n-nodes-base.emailSend": "Send Email",
            "n8n-nodes-base.if": "Conditional",
            "n8n-nodes-base.httpRequest": "HTTP Request"
        }
        
        base_name = name_mapping.get(node_type, f"Node {index + 1}")
        return base_name

    def _create_auto_connections(self, nodes: List[Dict]) -> Dict[str, Any]:
        """
        Create sequential connections between nodes
        """
        if len(nodes) < 2:
            return {}
            
        connections = {}
        
        for i in range(len(nodes) - 1):
            current_name = nodes[i]["name"]
            next_name = nodes[i + 1]["name"]
            
            connections[current_name] = {
                "main": [[{"node": next_name, "type": "main", "index": 0}]]
            }
        
        print(f"DEBUG: Auto-created {len(connections)} connections", flush=True)
        return connections

    def _create_fallback_workflow(self, prompt: str) -> Dict[str, Any]:
        """
        Create basic workflow when LLM fails or returns invalid data
        """
        print(f"WARNING: Creating fallback workflow for prompt: {prompt[:50]}...", flush=True)
        
        return {
            "nodes": [
                {
                    "id": "schedule1",
                    "name": "Schedule Trigger", 
                    "type": "n8n-nodes-base.cron",
                    "typeVersion": 1,
                    "parameters": COMPLETE_PARAMS["n8n-nodes-base.cron"],
                    "position": [240, 300],
                    "disabled": False
                },
                {
                    "id": "email1",
                    "name": "Send Email",
                    "type": "n8n-nodes-base.emailSend", 
                    "typeVersion": 1,
                    "parameters": {
                        **COMPLETE_PARAMS["n8n-nodes-base.emailSend"],
                        "subject": f"Workflow: {prompt[:30]}...",
                        "message": f"This is a fallback workflow created for: {prompt}"
                    },
                    "credentials": FAKE_CREDENTIALS["n8n-nodes-base.emailSend"],
                    "position": [460, 300],
                    "disabled": False
                }
            ],
            "connections": {
                "Schedule Trigger": {
                    "main": [[{"node": "Send Email", "type": "main", "index": 0}]]
                }
            },
            "fallback": True,
            "original_prompt": prompt
        }

    def validate_workflow(self, workflow: Dict[str, Any]) -> bool:
        """
        Validate workflow structure
        """
        try:
            # Check basic structure
            if "nodes" not in workflow or not workflow["nodes"]:
                return False
            
            # Check each node
            for node in workflow["nodes"]:
                required_fields = ["id", "name", "type", "parameters"]
                if not all(field in node for field in required_fields):
                    return False
            
            # Check connections reference existing nodes
            if "connections" in workflow:
                node_names = {n["name"] for n in workflow["nodes"]}
                for from_node, conn_data in workflow["connections"].items():
                    if from_node not in node_names:
                        return False
                    
                    if "main" in conn_data:
                        for conn_list in conn_data["main"]:
                            for conn in conn_list:
                                if conn["node"] not in node_names:
                                    return False
            
            return True
            
        except Exception as e:
            print(f"ERROR: Workflow validation failed: {e}")
            return False

    def get_supported_nodes(self) -> List[str]:
        """
        Get list of supported node types
        """
        return list(COMPLETE_PARAMS.keys())

    def get_node_parameters(self, node_type: str) -> Dict[str, Any]:
        """
        Get default parameters for a specific node type
        """
        return COMPLETE_PARAMS.get(node_type, {})