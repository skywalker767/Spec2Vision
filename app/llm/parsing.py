"""JSON parsing helpers for LLM outputs."""

from __future__ import annotations

import json
import re
from typing import Any


def parse_json_from_text(text: str) -> dict[str, Any] | None:
    """Extract and parse a JSON object from raw LLM text."""
    if not text or not text.strip():
        return None

    cleaned = text.strip()

    # Markdown code block
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", cleaned)
    if fence:
        cleaned = fence.group(1).strip()

    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    # First {...} block
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if match:
        try:
            data = json.loads(match.group())
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            return None

    return None


def llm_trace_meta(
    requested_provider: str,
    actual_provider: str,
    fallback: bool,
    parse_ok: bool,
    extra: dict | None = None,
) -> dict:
    """Build standard LLM metadata for agent traces."""
    meta = {
        "llm_requested_provider": requested_provider,
        "llm_actual_provider": actual_provider,
        "llm_fallback": fallback,
        "llm_parse_ok": parse_ok,
    }
    if extra:
        meta.update(extra)
    return meta
