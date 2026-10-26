"""The agent loop with a scripted fake LLM: no API key, no network."""

import json
from collections.abc import Iterator
from typing import Any

import pytest
from openai.types.chat import ChatCompletionMessage

from app.modules.chat import agent, llm
from app.modules.chat.schemas import Answer
from app.modules.chat.tools.registry import run_tool


def _tool_reply(*calls: tuple[str, dict[str, Any]]) -> ChatCompletionMessage:
    return ChatCompletionMessage.model_validate(
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": f"call_{index}",
                    "type": "function",
                    "function": {"name": name, "arguments": json.dumps(arguments)},
                }
                for index, (name, arguments) in enumerate(calls)
            ],
        }
    )


def _text_reply(text: str) -> ChatCompletionMessage:
    return ChatCompletionMessage.model_validate({"role": "assistant", "content": text})


def _script(monkeypatch: pytest.MonkeyPatch, *replies: ChatCompletionMessage) -> None:
    queue: Iterator[ChatCompletionMessage] = iter(replies)
    monkeypatch.setattr(llm, "complete", lambda messages, tools: next(queue))


def _answer(question: str) -> Answer:
    events = list(agent.run([], question))
    assert isinstance(events[-1], Answer)
    return events[-1]


def test_reply_without_tool_calls_is_the_final_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    _script(monkeypatch, _text_reply("Hello"))
    answer = _answer("hi")
    assert answer.text == "Hello"
    assert answer.tool_calls == []
    assert answer.steps == 1


def test_tool_calls_are_recorded_in_order(monkeypatch: pytest.MonkeyPatch) -> None:
    _script(
        monkeypatch,
        _tool_reply(("rank_airports", {"states": ["CA"]})),
        _tool_reply(("airport_details", {"codes": ["SNA"]}), ("rank_airports", {"codes": ["SNA"]})),
        _text_reply("Done"),
    )
    answer = _answer("Tell me about Santa Ana")
    assert [call.name for call in answer.tool_calls] == [
        "rank_airports",
        "airport_details",
        "rank_airports",
    ]
    assert answer.steps == 3


def test_step_limit_ends_with_an_explicit_message(monkeypatch: pytest.MonkeyPatch) -> None:
    _script(monkeypatch, *[_tool_reply(("rank_airports", {"codes": ["SFO"]}))] * agent.MAX_STEPS)
    assert _answer("loop forever").text == agent.OUT_OF_STEPS


def test_unknown_tool_is_reported_to_the_agent() -> None:
    assert json.loads(run_tool("delete_everything", "{}")) == {
        "error": "Unknown tool: delete_everything"
    }


def test_invalid_arguments_are_reported_to_the_agent() -> None:
    assert "Invalid arguments" in json.loads(run_tool("rank_airports", "{not json"))["error"]
