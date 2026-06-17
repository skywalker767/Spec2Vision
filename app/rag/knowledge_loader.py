"""Load markdown knowledge documents into chunks."""

from __future__ import annotations

import re
from pathlib import Path

from app.config import PROJECT_ROOT
from app.rag.schemas import KnowledgeChunk

KNOWLEDGE_DIR = PROJECT_ROOT / "data" / "knowledge_base"

_DOC_TASK_MAP = {
    "ecommerce_visual_guidelines.md": ["ecommerce_banner"],
    "academic_figure_guidelines.md": ["academic_figure"],
    "ppt_cover_guidelines.md": ["ppt_visual"],
}


def _split_sections(text: str) -> list[tuple[str, str]]:
    parts = re.split(r"(?m)^##\s+", text)
    sections: list[tuple[str, str]] = []
    if parts and not parts[0].strip().startswith("#"):
        intro = parts[0].strip()
        if intro:
            sections.append(("Overview", intro))
        parts = parts[1:]
    for part in parts:
        lines = part.strip().splitlines()
        if not lines:
            continue
        title = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        if body:
            sections.append((title, body))
    return sections


def load_knowledge_chunks(base_dir: Path | None = None) -> list[KnowledgeChunk]:
    root = base_dir or KNOWLEDGE_DIR
    chunks: list[KnowledgeChunk] = []
    if not root.exists():
        return chunks
    for path in sorted(root.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        doc_id = path.stem
        task_types = _DOC_TASK_MAP.get(path.name, [])
        for section, body in _split_sections(text):
            chunks.append(
                KnowledgeChunk(
                    doc_id=doc_id,
                    title=path.stem.replace("_", " "),
                    section=section,
                    text=body,
                    task_types=task_types,
                )
            )
    return chunks
