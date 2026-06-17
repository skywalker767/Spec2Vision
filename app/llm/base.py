"""Base LLM interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Structured result from an LLM call."""

    text: str
    provider: str
    model: str = ""
    success: bool = True
    error: str = ""


class BaseLLM(ABC):
    """Abstract base class for all LLM providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider identifier (mock / openai / deepseek)."""

    @abstractmethod
    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        """Generate text from system and user prompts."""

    def is_available(self) -> bool:
        """Whether this provider can make real API calls."""
        return True
