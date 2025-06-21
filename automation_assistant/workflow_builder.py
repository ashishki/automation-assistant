"""
WorkflowBuilder: creates workflows in n8n using REST API.
"""
import uuid

class WorkflowBuilder:
    def __init__(self, n8n_url: str, session):
        # n8n_url: base URL to n8n instance
        # session: authenticated requests.Session (or a mock for tests)
        self.n8n_url = n8n_url
        self.session = session

    def create_workflow(self, plan: dict) -> dict:
        """
        Create a new workflow in n8n based on the plan.
        Returns the created workflow object.
        Raises Exception on HTTP errors.
        """
        # Compose minimal workflow structure for n8n
        workflow = {
            "name": f"Workflow {str(uuid.uuid4())[:8]}",
            "nodes": self._build_nodes(plan),
            "connections": self._build_connections(plan),
            "active": False
        }
        # POST to n8n /rest/workflows
        response = self.session.post(f"{self.n8n_url}/rest/workflows", json=workflow)
        response.raise_for_status()
        return response.json()

    def _build_nodes(self, plan: dict) -> list:
        """
        Convert plan dict to a list of nodes for n8n workflow.
        This is a minimal example (needs extension for real use).
        """
        nodes = []
        # Example: trigger node
        nodes.append({
            "parameters": {"cronExpression": plan["schedule"]},
            "name": "Schedule Trigger",
            "type": "n8n-nodes-base.cron",
            "typeVersion": 1,
            "position": [300, 300]
        })
        # Example: Gmail summary node (placeholder)
        for idx, action in enumerate(plan["actions"], start=1):
            nodes.append({
                "parameters": {},
                "name": f"Action {action}",
                "type": f"custom.{action}",
                "typeVersion": 1,
                "position": [300 + idx*150, 300]
            })
        return nodes

    def _build_connections(self, plan: dict) -> dict:
        """
        Compose the connections for the workflow nodes.
        """
        # Minimal: trigger to first action
        if not plan["actions"]:
            return {}
        return {
            "Schedule Trigger": {
                "main": [
                    [{"node": f"Action {plan['actions'][0]}", "type": "main", "index": 0}]
                ]
            }
        }
