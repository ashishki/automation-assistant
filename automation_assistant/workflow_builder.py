"""
WorkflowBuilder: creates workflows in n8n using REST API.
"""
import uuid

class WorkflowBuilder:
    def __init__(self, n8n_url: str, session):
        self.n8n_url = n8n_url
        self.session = session

    def create_workflow(self, plan: dict) -> dict:
        """
        Create a new workflow in n8n based on the plan (nodes + connections).
        Returns the created workflow object.
        Raises Exception on HTTP errors.
        """
        workflow = {
            "name": f"Workflow {str(uuid.uuid4())[:8]}",
            "nodes": self._build_nodes(plan),
            "connections": self._build_connections(plan),
            "active": False
        }
        response = self.session.post(f"{self.n8n_url}/rest/workflows", json=workflow)
        response.raise_for_status()
        print("DEBUG: raw workflow response", response.json(), flush=True)
        return response.json().get("data", response.json())

    def _build_nodes(self, plan: dict) -> list:
        """
        Converts the plan['nodes'] into the n8n node format.
        Maps node 'type' to actual n8n types when possible.
        """
        if "nodes" in plan:
            return [self._node_to_n8n(node) for node in plan["nodes"]]

        # Fallback for old format
        nodes = []
        if "schedule" in plan:
            nodes.append({
                "parameters": {"cronExpression": plan["schedule"]},
                "name": "Schedule Trigger",
                "type": "n8n-nodes-base.cron",
                "typeVersion": 1,
                "position": [300, 300],
                "id": "schedule1"
            })
        for idx, action in enumerate(plan.get("actions", []), start=1):
            nodes.append({
                "parameters": {},
                "name": f"Action {action}",
                "type": f"custom.{action}",
                "typeVersion": 1,
                "position": [300 + idx*150, 300],
                "id": f"action{idx}"
            })
        return nodes

    def _build_connections(self, plan: dict) -> dict:
        """
        Build the connections object for n8n.
        If 'connections' is in plan, use it as-is (converted to n8n format).
        Otherwise, fallback to linear connection.
        """
        if "connections" in plan and "nodes" in plan:
            return self._convert_connections(plan["connections"], plan["nodes"])
        # fallback: linear
        nodes = self._build_nodes(plan)
        if len(nodes) < 2:
            return {}
        conn = {}
        for i in range(len(nodes)-1):
            conn.setdefault(nodes[i]["name"], {"main": [[{"node": nodes[i+1]["name"], "type": "main", "index": 0}]]})
        return conn

    def _node_to_n8n(self, node: dict) -> dict:
        """
        Convert LLM node to n8n node format.
        Maps 'type' to n8n node types when possible. Keeps parameters if present.
        """
        # Map LLM type to n8n node type if possible
        NODE_TYPE_MAP = {
            "schedule": "n8n-nodes-base.cron",
            "gmail": "n8n-nodes-base.googleGmail",
            "summarize": "n8n-nodes-base.openai",
            "sendEmail": "n8n-nodes-base.emailSend",
            "if": "n8n-nodes-base.if",
            # add more mappings as needed
        }
        out = node.copy()
        # Convert id → name (n8n expects unique "name")
        if "id" in out and "name" not in out:
            out["name"] = out["id"]
        out["type"] = NODE_TYPE_MAP.get(node.get("type", ""), node.get("type"))
        if "position" not in out:
            out["position"] = [300, 300]
        if "typeVersion" not in out:
            out["typeVersion"] = 1
        return out

    def _convert_connections(self, conn: dict, nodes: list) -> dict:
        """
        Convert a simple graph {"a": ["b", "c"]} to n8n's format.
        """
        n8n_conn = {}
        node_map = {n.get("id", n.get("name")): n.get("name", n.get("id")) for n in nodes}
        for from_id, to_ids in conn.items():
            from_name = node_map.get(from_id, from_id)
            n8n_conn[from_name] = {"main": [[{"node": node_map.get(to_id, to_id), "type": "main", "index": 0} for to_id in to_ids]]}
        return n8n_conn
