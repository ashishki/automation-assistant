import uuid
import json
from .prompts import N8N_NODE_TYPES, COMPLETE_PARAMS, FAKE_CREDENTIALS


def fill_missing_parameters_and_creds(node):
    """
    Fill missing parameters and credentials for n8n node
    """
    ntype = node["type"]
    
    # Fill default params
    params = node.get("parameters", {})
    defaults = COMPLETE_PARAMS.get(ntype, {})
    
    # Deep merge parameters
    for k, v in defaults.items():
        if k not in params:
            params[k] = v
        elif isinstance(v, dict) and isinstance(params[k], dict):
            # Merge nested dictionaries
            merged = v.copy()
            merged.update(params[k])
            params[k] = merged
    
    node["parameters"] = params
    
    # Fill credentials
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
        self._validate_nodes(nodes)
        connections = self._build_connections(plan, nodes)

        
        for node in nodes:
            
            if node.get("type") in ["n8n-nodes-base.cron", "n8n-nodes-base.manualTrigger"]:
                node.pop("credentials", None)
            elif "credentials" in node and not node["credentials"]:
                node.pop("credentials", None)

            
            if node.get("type") == "n8n-nodes-base.emailSend":
                if "message" in node["parameters"]:
                    node["parameters"]["text"] = node["parameters"].pop("message")
                
                for opt in ["cc", "bcc", "replyTo", "html", "attachments", "options"]:
                    if opt in node["parameters"] and not node["parameters"][opt]:
                        del node["parameters"][opt]
       

        workflow = {
            "name": f"AI Generated Workflow {str(uuid.uuid4())[:8]}",
            "nodes": nodes,
            "connections": connections,
            "active": False
        }
        self._validate_workflow(workflow)
        print(json.dumps(workflow, indent=2))  
        response = self.session.post(f"{self.n8n_url}/rest/workflows", json=workflow)
        response.raise_for_status()
        result = response.json()
        print("DEBUG: Workflow created successfully", result.get("data", {}).get("id"), flush=True)
        return result.get("data", result)


    def _build_nodes(self, plan: dict) -> list:
        """
        Build n8n nodes from plan
        """
        nodes = []
        
        if "nodes" in plan and plan["nodes"]:
            for idx, node in enumerate(plan["nodes"]):
                ntype = N8N_NODE_TYPES.get(node.get("type"), node.get("type"))
                name = node.get("name", node.get("id", f"Node {idx+1}"))
                
                node_obj = {
                    "id": node.get("id", f"node_{idx+1}"),
                    "name": name,
                    "type": ntype,
                    "typeVersion": node.get("typeVersion", 1),
                    "parameters": node.get("parameters", {}),
                    "position": node.get("position", [240 + idx*220, 300]),
                    "disabled": False,
                    "notes": f"Auto-generated {ntype.split('.')[-1]} node",
                    "notesInFlow": False
                }
                
                # Fill missing parameters and credentials
                node_obj = fill_missing_parameters_and_creds(node_obj)
                nodes.append(node_obj)
        
        return nodes

    def _build_connections(self, plan: dict, nodes: list) -> dict:
        if not nodes:
            return {}

        id2name = {n["id"]: n["name"] for n in nodes}
        node_names = [n["name"] for n in nodes]

        # Step 1: если есть connections — нормализуем по name
        n8n_conns = {}
        if "connections" in plan and plan["connections"]:
            for from_any, to_list in plan["connections"].items():
                # Маппим и id, и name → name
                from_name = id2name.get(from_any, from_any)
                if from_name not in node_names:
                    continue

                connections_list = []
                for to_any in to_list:
                    to_name = id2name.get(to_any, to_any)
                    if to_name in node_names:
                        connections_list.append({
                            "node": to_name,
                            "type": "main",
                            "index": 0
                        })
                if connections_list:
                    n8n_conns[from_name] = {"main": [connections_list]}

            
            if not n8n_conns and len(nodes) > 1:
                for i in range(len(node_names) - 1):
                    n8n_conns[node_names[i]] = {
                        "main": [[{"node": node_names[i + 1], "type": "main", "index": 0}]]
                    }
            return n8n_conns

        # Step 2: 
        if len(nodes) < 2:
            return {}
        for i in range(len(node_names) - 1):
            n8n_conns[node_names[i]] = {
                "main": [[{"node": node_names[i + 1], "type": "main", "index": 0}]]
            }
        return n8n_conns


    def _validate_workflow(self, workflow: dict):
        """
        Validate workflow structure before creation
        """
        if not workflow.get("nodes"):
            raise ValueError("Workflow must have at least one node")
        
        # Check for required node fields
        for node in workflow["nodes"]:
            required_fields = ["id", "name", "type", "parameters"]
            missing = [f for f in required_fields if f not in node]
            if missing:
                raise ValueError(f"Node missing required fields: {missing}")
        
        # Validate connections reference existing nodes
        node_names = {n["name"] for n in workflow["nodes"]}
        connections = workflow.get("connections", {})
        
        for from_node, conn_data in connections.items():
            if from_node not in node_names:
                raise ValueError(f"Connection references non-existent node: {from_node}")
            
            if "main" in conn_data:
                for conn_list in conn_data["main"]:
                    for conn in conn_list:
                        if conn["node"] not in node_names:
                            raise ValueError(f"Connection references non-existent target node: {conn['node']}")

    def _validate_nodes(self, nodes: list):
        """
        Validate individual nodes for completeness
        """
        for node in nodes:
            node_type = node["type"]
            required_params = COMPLETE_PARAMS.get(node_type, {})
            
            # Check if critical parameters exist
            if node_type == "n8n-nodes-base.cron":
                if "mode" not in node["parameters"]:
                    raise ValueError(f"Cron node '{node['name']}' missing 'mode' parameter")
            
            elif node_type == "n8n-nodes-base.googleGmail":
                required = ["resource", "operation"]
                missing = [k for k in required if k not in node["parameters"]]
                if missing:
                    raise ValueError(f"Gmail node '{node['name']}' missing required params: {missing}")
            
            elif node_type == "n8n-nodes-base.openai":
                if "messagesUi" not in node["parameters"]:
                    raise ValueError(f"OpenAI node '{node['name']}' missing 'messagesUi' parameter")
            
            elif node_type == "n8n-nodes-base.emailSend":
                required = ["fromEmail", "toEmail", "subject"]
                missing = [k for k in required if k not in node["parameters"]]
                if missing:
                    raise ValueError(f"Email node '{node['name']}' missing required params: {missing}")

    def get_workflow(self, workflow_id: str) -> dict:
        """
        Get existing workflow by ID
        """
        response = self.session.get(f"{self.n8n_url}/rest/workflows/{workflow_id}")
        response.raise_for_status()
        return response.json().get("data", response.json())

    def update_workflow(self, workflow_id: str, workflow_data: dict) -> dict:
        """
        Update existing workflow
        """
        response = self.session.put(f"{self.n8n_url}/rest/workflows/{workflow_id}", json=workflow_data)
        response.raise_for_status()
        return response.json().get("data", response.json())

    def execute_workflow(self, workflow_id: str) -> dict:
        """
        Execute workflow manually
        """
        response = self.session.post(f"{self.n8n_url}/rest/workflows/{workflow_id}/execute")
        response.raise_for_status()
        return response.json()