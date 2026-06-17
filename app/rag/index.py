"""Build and persist a lightweight local retrieval index."""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

from app.config import PROJECT_ROOT
from app.rag.knowledge_loader import load_knowledge_chunks
from app.rag.schemas import KnowledgeChunk

INDEX_PATH = PROJECT_ROOT / "data" / "knowledge_base" / ".index.json"

_TOKEN = re.compile(r"[\w\u4e00-\u9fff]+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN.findall(text) if len(t) > 1]


def build_index(chunks: list[KnowledgeChunk] | None = None) -> dict:
    chunks = chunks or load_knowledge_chunks()
    docs = []
    df: Counter[str] = Counter()
    for chunk in chunks:
        tokens = tokenize(f"{chunk.section} {chunk.text}")
        tf = Counter(tokens)
        for term in tf:
            df[term] += 1
        docs.append(
            {
                "doc_id": chunk.doc_id,
                "section": chunk.section,
                "text": chunk.text,
                "task_types": chunk.task_types,
                "tf": dict(tf),
                "len": max(len(tokens), 1),
            }
        )
    return {"version": 1, "doc_count": len(docs), "df": dict(df), "docs": docs}


def save_index(index: dict, path: Path | None = None) -> Path:
    out = path or INDEX_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def load_index(path: Path | None = None) -> dict:
    target = path or INDEX_PATH
    if target.exists():
        return json.loads(target.read_text(encoding="utf-8"))
    index = build_index()
    save_index(index, target)
    return index
