"""What a tool is: the Python function that runs, plus the description the LLM reads."""

from collections.abc import Callable
from typing import Any, NamedTuple

from pydantic import BaseModel

CODES = {
    "type": "array",
    "items": {"type": "string"},
    "description": "IATA airport codes, e.g. ['SFO', 'SNA']",
}


class Tool(NamedTuple):
    name: str
    handler: Callable[..., BaseModel]
    progress: str
    description: str
    properties: dict[str, Any]
    required: tuple[str, ...] | None = None

    def schema(self) -> dict[str, Any]:
        """The tool as the LLM sees it (OpenAI function-calling format)."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.properties,
                    "required": [*(self.properties if self.required is None else self.required)],
                },
            },
        }
