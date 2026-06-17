"""Image generator factory – API only."""

from __future__ import annotations

from app.config import get_settings
from app.tools.image_generator import ImageProviderError, OpenAIImageGenerator


def get_image_generator() -> OpenAIImageGenerator:
    """Return configured image generator. Requires valid API credentials."""
    settings = get_settings()
    provider = (settings.image_provider or "openai").lower().strip()

    if provider == "mock":
        raise ImageProviderError(
            "Mock image provider is disabled. Set IMAGE_PROVIDER=openai in .env"
        )
    if provider == "openai":
        gen = OpenAIImageGenerator()
        return gen

    raise ImageProviderError(
        f"Unknown IMAGE_PROVIDER='{provider}'. Supported: openai"
    )
