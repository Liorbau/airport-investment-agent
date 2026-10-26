"""The agent loop (D-010): ask the LLM, run the tools it calls, then check its answer (D-012)."""

from collections.abc import Iterator

from app.modules.chat import llm
from app.modules.chat.citations import check_numbers
from app.modules.chat.prompt import SYSTEM_PROMPT
from app.modules.chat.schemas import Answer, ChatMessage, Progress, ToolCall
from app.modules.chat.tools.registry import PROGRESS, TOOLS, run_tool

MAX_STEPS = 8
HISTORY_LIMIT = 10
OUT_OF_STEPS = "I couldn't finish the analysis within my step limit. Try a narrower question."


def _answer(text: str, calls: list[ToolCall], steps: int) -> Answer:
    return Answer(text=text, tool_calls=calls, steps=steps, number_check=check_numbers(text, calls))


def run(history: list[ChatMessage], question: str) -> Iterator[Progress | Answer]:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *(message.model_dump() for message in history[-HISTORY_LIMIT:]),
        {"role": "user", "content": question},
    ]
    calls: list[ToolCall] = []
    for step in range(1, MAX_STEPS + 1):
        reply = llm.complete(messages, TOOLS)
        if not reply.tool_calls:
            yield _answer(reply.content or "", calls, step)
            return
        messages.append(reply.model_dump(exclude_none=True))
        for call in reply.tool_calls:
            yield Progress(message=PROGRESS.get(call.function.name, "Working"))
            output = run_tool(call.function.name, call.function.arguments)
            calls.append(
                ToolCall(
                    name=call.function.name,
                    arguments=call.function.arguments,
                    output=output,
                )
            )
            messages.append({"role": "tool", "tool_call_id": call.id, "content": output})
    yield _answer(OUT_OF_STEPS, calls, MAX_STEPS)
