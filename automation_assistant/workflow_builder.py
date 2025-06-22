import uuid

N8N_NODE_TYPES = {
    "schedule": "n8n-nodes-base.cron",
    "gmail": "n8n-nodes-base.googleGmail",
    "openai": "n8n-nodes-base.openai",
    "sendEmail": "n8n-nodes-base.emailSend",
    "if": "n8n-nodes-base.if",
}


FAKE_CREDENTIALS = {
    "n8n-nodes-base.googleGmail": {"googleApi": {"id": "1", "name": "Fake Google Account"}},
    "n8n-nodes-base.openai": {"openAiApi": {"id": "1", "name": "Fake OpenAI Account"}},
    "n8n-nodes-base.emailSend": {"smtp": {"id": "1", "name": "Fake SMTP Account"}},
    "n8n-nodes-base.httpRequest": {"httpBasicAuth": {"id": "1", "name": "Fake HTTP Basic"}}
}


DEFAULT_NODE_PARAMETERS = {
    "n8n-nodes-base.cron": {
        "cronExpression": "0 10 * * MON"
    },
    "n8n-nodes-base.googleGmail": {
        "resource": "message",       
        "operation": "getAll",
        "returnAll": True,
        "filters": {"labelIds": ["UNREAD"]}
    },
    "n8n-nodes-base.openai": {
        "resource": "chat",          
        "operation": "chat",         
        "model": "gpt-4o",
        "messagesUi": {
            "messageValues": [
                {"role": "system", "content": "Summarize the emails in Markdown."},
                {"role": "user", "content": "={{$json[\"messages\"]}}"}
            ]
        }
    },
    "n8n-nodes-base.emailSend": {
        "fromEmail": "bot@example.com",
        "toEmail": "me@example.com",
        "subject": "Weekly Unread Email Summary",
        "text": "={{$json[\"summary\"]}}"
    }
}


def fill_missing_parameters_and_creds(node):
    ntype = node["type"]
    # Fill default params
    params = node.get("parameters", {})
    defaults = DEFAULT_NODE_PARAMETERS.get(ntype, {})
    for k, v in defaults.items():
        if k not in params:
            params[k] = v
    node["parameters"] = params
    # Fill credentials in правильном формате
    creds = FAKE_CREDENTIALS.get(ntype)
    if creds:
        node["credentials"] = creds
    return node

class WorkflowBuilder:
    def __init__(self, n8n_url: str, session):
        self.n8n_url = n8n_url
        self.session = session

    def create_workflow(self, plan: dict) -> dict:
        nodes = self._build_nodes(plan)
        self._validate_nodes(nodes)  # <- добавлено
        workflow = {
            "name": f"Workflow {str(uuid.uuid4())[:8]}",
            "nodes": nodes,
            "connections": self._build_connections(plan, nodes),
            "active": False
        }
        response = self.session.post(f"{self.n8n_url}/rest/workflows", json=workflow)
        response.raise_for_status()
        print("DEBUG: raw workflow response", response.json(), flush=True)
        return response.json().get("data", response.json())

    def _build_nodes(self, plan: dict) -> list:
        nodes = []
        x0, y0 = 300, 300
        dx, dy = 200, 170
        if "nodes" in plan:
            for idx, node in enumerate(plan["nodes"]):
                n8n_type = N8N_NODE_TYPES.get(node["type"], node["type"])
                name = node.get("name", node["id"])
                n = {
                    "id": node["id"],
                    "name": name,
                    "type": n8n_type,
                    "typeVersion": 1,
                    "parameters": node.get("parameters", {}),
                    "position": [x0 + (idx * dx), y0 + ((idx % 2) * dy)]
                }
                n = fill_missing_parameters_and_creds(n)
                nodes.append(n)
            return nodes
        # fallback (legacy)
        return []

    def _build_connections(self, plan: dict, nodes: list) -> dict:
        """
        Converts plan['connections'] {from_id: [to_id, ...]} to n8n format.
        """
        if "connections" not in plan or "nodes" not in plan:
            return {}
        node_id_to_name = {n["id"]: n["name"] for n in nodes}
        n8n_conns = {}
        for from_id, to_ids in plan["connections"].items():
            if from_id not in node_id_to_name:
                continue  # некорректная связь
            from_name = node_id_to_name[from_id]
            n8n_conns[from_name] = {"main": [
                [
                    {
                        "node": node_id_to_name[to_id],
                        "type": "main",
                        "index": 0
                    } for to_id in to_ids if to_id in node_id_to_name
                ]
            ]}
        return n8n_conns

    def _validate_nodes(self, nodes: list):
        """
        Checks for all required parameters in nodes.
        Throws ValueError if any required param is missing.
        """
        for node in nodes:
            required = DEFAULT_NODE_PARAMETERS.get(node["type"], [])
            missing = [k for k in required if k not in node["parameters"] or not node["parameters"].get(k)]
            if missing:
                raise ValueError(
                    f"Node '{node['name']}' of type '{node['type']}' missing required params: {missing}. "
                    f"Parameters: {node['parameters']}"
                )

    