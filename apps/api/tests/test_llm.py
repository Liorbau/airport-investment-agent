"""LLM settings: provider presets and explicit overrides."""

import pytest

from app.modules.chat.llm import PRESETS, LlmConfigError, settings


def _env(monkeypatch: pytest.MonkeyPatch, **variables: str) -> None:
    for name in ("LLM_PROVIDER", "LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL"):
        monkeypatch.delenv(name, raising=False)
    for name, value in variables.items():
        monkeypatch.setenv(name, value)


def test_provider_preset_fills_url_and_model(monkeypatch: pytest.MonkeyPatch) -> None:
    _env(monkeypatch, LLM_PROVIDER="gemini", LLM_API_KEY="key")
    url, model = PRESETS["gemini"]
    assert settings() == (url, "key", model)


def test_model_variable_overrides_the_preset(monkeypatch: pytest.MonkeyPatch) -> None:
    _env(monkeypatch, LLM_API_KEY="key", LLM_MODEL="gpt-other")
    assert settings()[2] == "gpt-other"


def test_unknown_provider_or_missing_key_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    _env(monkeypatch, LLM_PROVIDER="nope", LLM_API_KEY="key")
    with pytest.raises(LlmConfigError):
        settings()
    _env(monkeypatch)
    with pytest.raises(LlmConfigError):
        settings()
