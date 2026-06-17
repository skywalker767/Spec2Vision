"""DeepSeek LLM provider (optional, OpenAI-compatible API)."""

from __future__ import annotations

import logging

from app.config import get_settings
from app.llm.base import BaseLLM

logger = logging.getLogger(__name__)


class DeepSeekLLM(BaseLLM):
    """Call DeepSeek Chat API via httpx (OpenAI-compatible endpoint)."""

    @property
    def provider_name(self) -> str:
        return "deepseek"

    def is_available(self) -> bool:
        settings = get_settings()
        return bool(settings.deepseek_api_key and settings.deepseek_api_key.strip())

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        if not self.is_available():
            raise RuntimeError("DeepSeek API key not configured")

        try:
            import httpx
        except ImportError as exc:
            raise RuntimeError("httpx not installed") from exc

        settings = get_settings()
        base = settings.deepseek_base_url.rstrip("/")
        url = f"{base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.deepseek_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.deepseek_model or "deepseek-chat",
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
            logger.warning("DeepSeek API call failed: %s", exc)
            raise
