"""Tests for API-only provider requirements."""

from __future__ import annotations

import pytest

from app.config import get_settings
from app.llm.llm_factory import LLMProviderError, get_llm
from app.tools.image_factory import get_image_generator
from app.tools.image_generator import ImageProviderError


def test_llm_requires_api_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    get_settings.cache_clear()

    with pytest.raises(LLMProviderError, match="OPENAI_API_KEY"):
        get_llm()


def test_mock_llm_disabled(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    get_settings.cache_clear()

    with pytest.raises(LLMProviderError, match="Mock LLM is disabled"):
        get_llm()


def test_image_mock_disabled(monkeypatch):
    monkeypatch.setenv("IMAGE_PROVIDER", "mock")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    get_settings.cache_clear()

    with pytest.raises(ImageProviderError, match="Mock image provider is disabled"):
        get_image_generator()


def test_image_requires_api_key(monkeypatch):
    monkeypatch.setenv("IMAGE_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("IMAGE_API_KEY", "")
    get_settings.cache_clear()

    with pytest.raises(ImageProviderError, match="Image API key required"):
        get_image_generator().generate("t1", "ecommerce_banner", "title", "prompt")
