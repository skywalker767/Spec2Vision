"""LLM provider factory – API only, no mock fallback."""

from __future__ import annotations

import logging

from app.config import get_settings
from app.llm.base import BaseLLM
from app.llm.deepseek_llm import DeepSeekLLM
from app.llm.openai_llm import OpenAILLM

logger = logging.getLogger(__name__)

_PROVIDERS: dict[str, type[BaseLLM]] = {
    "openai": OpenAILLM,
    "deepseek": DeepSeekLLM,
}


class LLMProviderError(RuntimeError):
    """Raised when LLM provider is missing or misconfigured."""


def get_llm(provider: str | None = None) -> tuple[BaseLLM, str]:
    """Return (llm_instance, requested_provider). Requires a valid API key."""
    settings = get_settings()
    requested = (provider or settings.llm_provider or "openai").lower().strip()

    if requested == "mock":
        raise LLMProviderError(
            "Mock LLM is disabled. Set LLM_PROVIDER=openai or deepseek in .env"
        )

    cls = _PROVIDERS.get(requested)
    if cls is None:
        raise LLMProviderError(
            f"Unknown LLM_PROVIDER='{requested}'. Supported: openai, deepseek"
        )

    instance = cls()
    if not instance.is_available():
        key_name = "OPENAI_API_KEY" if requested == "openai" else "DEEPSEEK_API_KEY"
        raise LLMProviderError(
            f"LLM provider '{requested}' requires {key_name} in .env"
        )

    return instance, requested
