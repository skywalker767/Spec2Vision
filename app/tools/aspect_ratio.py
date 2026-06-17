"""Aspect-ratio to image size mapping with normalization metadata."""

from __future__ import annotations

from dataclasses import dataclass

# OpenAI-compatible sizes supported by gpt-image-1 style APIs
_SUPPORTED_SIZES: dict[str, tuple[int, int]] = {
    "1024x1024": (1024, 1024),
    "1792x1024": (1792, 1024),
    "1024x1792": (1024, 1792),
    "1536x1024": (1536, 1024),
    "1024x1536": (1024, 1536),
}

# Ideal mapping from requested ratio to provider size string
_ASPECT_TO_IDEAL_SIZE: dict[str, str] = {
    "1:1": "1024x1024",
    "16:9": "1792x1024",
    "9:16": "1024x1792",
    "4:5": "1024x1536",
    "3:4": "1024x1536",
    "4:3": "1536x1024",
    "a4": "1024x1536",
    "a4 portrait": "1024x1536",
    "a4 landscape": "1536x1024",
    "a4_portrait": "1024x1536",
    "a4_landscape": "1536x1024",
}


@dataclass(frozen=True)
class AspectRatioResolution:
    requested_ratio: str
    normalized_ratio: str
    size: str
    width: int
    height: int
    orientation: str
    normalized: bool
    normalization_reason: str | None = None


def _normalize_ratio_key(aspect_ratio: str) -> str:
    key = (aspect_ratio or "1:1").strip().lower().replace(" ", "_")
    aliases = {
        "a4": "a4_portrait",
        "a4-portrait": "a4_portrait",
        "a4-landscape": "a4_landscape",
    }
    return aliases.get(key, key)


def _orientation_from_size(size: str) -> str:
    w, h = _SUPPORTED_SIZES.get(size, (1024, 1024))
    if w == h:
        return "square"
    return "landscape" if w > h else "portrait"


def resolve_aspect_ratio(aspect_ratio: str = "1:1") -> AspectRatioResolution:
    """Map a requested aspect ratio to the closest supported provider size."""
    key = _normalize_ratio_key(aspect_ratio)
    ideal = _ASPECT_TO_IDEAL_SIZE.get(key, "1024x1024")

    if ideal in _SUPPORTED_SIZES:
        w, h = _SUPPORTED_SIZES[ideal]
        return AspectRatioResolution(
            requested_ratio=aspect_ratio or "1:1",
            normalized_ratio=key if key in _ASPECT_TO_IDEAL_SIZE else aspect_ratio or "1:1",
            size=ideal,
            width=w,
            height=h,
            orientation=_orientation_from_size(ideal),
            normalized=False,
        )

    # Fallback: pick closest by aspect ratio numeric value
    def _ratio_value(r: str) -> float:
        if ":" in r:
            a, b = r.split(":", 1)
            try:
                return float(a) / float(b)
            except ValueError:
                return 1.0
        return 1.0

    target = _ratio_value(aspect_ratio.replace("x", ":") if "x" in aspect_ratio else aspect_ratio)
    best_size = "1024x1024"
    best_delta = float("inf")
    for size, (w, h) in _SUPPORTED_SIZES.items():
        delta = abs((w / h) - target)
        if delta < best_delta:
            best_delta = delta
            best_size = size

    w, h = _SUPPORTED_SIZES[best_size]
    return AspectRatioResolution(
        requested_ratio=aspect_ratio or "1:1",
        normalized_ratio=aspect_ratio or "1:1",
        size=best_size,
        width=w,
        height=h,
        orientation=_orientation_from_size(best_size),
        normalized=True,
        normalization_reason=f"unsupported ratio '{aspect_ratio}' mapped to closest size {best_size}",
    )
