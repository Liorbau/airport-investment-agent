"""All tools the agent can call (D-011), and running one by name."""

import json

from app.modules.chat.tools import airport_details, rank_airports

_REGISTRY = {module.TOOL.name: module.TOOL for module in (rank_airports, airport_details)}
TOOLS = [tool.schema() for tool in _REGISTRY.values()]
PROGRESS = {name: tool.progress for name, tool in _REGISTRY.items()}


def run_tool(name: str, raw_arguments: str) -> str:
    """The tool's result as JSON, or a JSON error the agent must report to the user."""
    if name not in _REGISTRY:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        return _REGISTRY[name].handler(**json.loads(raw_arguments or "{}")).model_dump_json()
    except (json.JSONDecodeError, TypeError) as error:
        return json.dumps({"error": f"Invalid arguments for {name}: {error}"})
