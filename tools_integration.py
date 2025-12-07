# Example tool definitions for Claude
TOOLS = [
    {
        "name": "pubmed_search",
        "description": "Search PubMed for antimicrobial stewardship literature",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        }
    },
    {
        "name": "calculate_dot",
        "description": "Calculate Days of Therapy (DOT) per 1000 patient-days",
        "input_schema": {
            "type": "object",
            "properties": {
                "total_dot": {"type": "number"},
                "patient_days": {"type": "number"}
            },
            "required": ["total_dot", "patient_days"]
        }
    }
]

def execute_tool(name: str, inputs: dict) -> str:
    if name == "pubmed_search":
        # Use your existing citation_search logic
        resp = requests.post(f"{CITATION_API}/api/search", 
                           json=inputs, timeout=15)
        return resp.json()
    elif name == "calculate_dot":
        result = (inputs["total_dot"] / inputs["patient_days"]) * 1000
        return f"DOT per 1000 patient-days: {result:.1f}"