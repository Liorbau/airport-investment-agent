"""POST /chat: the event stream, the citation check, and input validation."""

import json

import httpx
import pytest
from fastapi.testclient import TestClient
from openai import APIConnectionError
from openai.types.chat import ChatCompletionMessage

from app.main import app
from app.modules.chat import llm

client = TestClient(app)


def _events(response_text: str) -> list[dict]:
    return [json.loads(line.removeprefix("data: ")) for line in response_text.split("\n\n") if line]


def test_stream_ends_with_a_checked_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    reply = ChatCompletionMessage.model_validate({"role": "assistant", "content": "Growth 7%"})
    monkeypatch.setattr(llm, "complete", lambda messages, tools: reply)
    response = client.post("/chat", json={"question": "hi"})
    assert response.headers["content-type"].startswith("text/event-stream")
    answer = _events(response.text)[-1]
    assert answer["type"] == "answer"
    assert answer["number_check"]["unverified_numbers"] == ["7"]


def test_llm_failure_becomes_an_error_event(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(messages: list, tools: list) -> ChatCompletionMessage:
        raise APIConnectionError(request=httpx.Request("POST", "https://llm.test"))

    monkeypatch.setattr(llm, "complete", fail)
    events = _events(client.post("/chat", json={"question": "hi"}).text)
    assert events[-1]["type"] == "error"


def test_empty_question_is_rejected() -> None:
    assert client.post("/chat", json={"question": ""}).status_code == 422


def test_unexpected_failure_still_ends_with_an_error_event(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def crash(messages: list, tools: list) -> ChatCompletionMessage:
        raise RuntimeError("boom")

    monkeypatch.setattr(llm, "complete", crash)
    events = _events(client.post("/chat", json={"question": "hi"}).text)
    assert events[-1] == {
        "type": "error",
        "message": "Something went wrong on our side. Please try again.",
    }


def test_speech_without_an_openai_provider_asks_the_browser_to_fall_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("LLM_API_KEY", "key")
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    assert client.post("/speech", json={"text": "hello"}).status_code == 501


def test_empty_speech_text_is_rejected() -> None:
    assert client.post("/speech", json={"text": ""}).status_code == 422
