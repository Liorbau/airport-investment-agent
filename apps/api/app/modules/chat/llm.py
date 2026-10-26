"""The LLM client: any OpenAI-compatible API, chosen by environment variables (D-002)."""

import os
from typing import Any

from openai import OpenAI
from openai.types.chat import ChatCompletionMessage

MAX_RETRIES = 3
TIMEOUT_SECONDS = 60
TTS_MODEL = "tts-1"
TTS_VOICE = "coral"
OPENAI_HOST = "api.openai.com"
PRESETS = {
    "openai": ("https://api.openai.com/v1/", "gpt-5.4-mini"),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai/", "gemini-3.5-flash"),
}


class LlmConfigError(Exception):
    """LLM_PROVIDER is unknown or LLM_API_KEY is missing."""


def settings() -> tuple[str, str, str]:
    """(base URL, API key, model): LLM_PROVIDER picks a preset, LLM_BASE_URL/LLM_MODEL override."""
    provider = os.environ.get("LLM_PROVIDER", "openai")
    api_key = os.environ.get("LLM_API_KEY")
    if provider not in PRESETS or not api_key:
        raise LlmConfigError(f"set LLM_API_KEY, and LLM_PROVIDER to one of {', '.join(PRESETS)}")
    base_url, model = PRESETS[provider]
    base_url = os.environ.get("LLM_BASE_URL") or base_url
    return base_url, api_key, os.environ.get("LLM_MODEL") or model


def _client(base_url: str, api_key: str) -> OpenAI:
    return OpenAI(
        base_url=base_url, api_key=api_key, max_retries=MAX_RETRIES, timeout=TIMEOUT_SECONDS
    )


def complete(messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> ChatCompletionMessage:
    base_url, api_key, model = settings()
    response = _client(base_url, api_key).chat.completions.create(
        model=model, messages=messages, tools=tools
    )
    return response.choices[0].message


def synthesize(text: str) -> bytes | None:
    """Speech audio (mp3) for `text`, or None when the provider has no OpenAI voice."""
    base_url, api_key, _ = settings()
    if OPENAI_HOST not in base_url:
        return None
    speech = _client(base_url, api_key).audio.speech.create(
        model=TTS_MODEL, voice=TTS_VOICE, input=text
    )
    return speech.read()
