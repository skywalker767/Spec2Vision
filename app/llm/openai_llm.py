"""OpenAI-compatible LLM provider (optional, httpx-based)."""

from __future__ import annotations

import logging

from app.config import get_settings
from app.llm.base import BaseLLM

logger = logging.getLogger(__name__)


class OpenAILLM(BaseLLM):
    """Call OpenAI Chat Completions API via httpx (no openai SDK required)."""

    @property
    def provider_name(self) -> str:
        return "openai"

    def is_available(self) -> bool:
        settings = get_settings()
        return bool(settings.openai_api_key and settings.openai_api_key.strip())

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        if not self.is_available():
            raise RuntimeError("OpenAI API key not configured")

        try:
            import httpx
        except ImportError as exc:
            raise RuntimeError("httpx not installed") from exc

        settings = get_settings()
        base = settings.openai_base_url.rstrip("/")
        url = f"{base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.openai_model or "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
        }

        try:
            with httpx.Client(timeout=httpx.Timeout(30.0, read=120.0)) as client:
                resp = client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as exc:
            logger.warning("OpenAI API call failed: %s", exc)
            raise
