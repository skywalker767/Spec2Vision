#!/usr/bin/env python3
"""Build local knowledge base index for Agentic RAG."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.rag.index import build_index, save_index
from app.rag.knowledge_loader import load_knowledge_chunks


def main() -> int:
    chunks = load_knowledge_chunks()
    index = build_index(chunks)
    path = save_index(index)
    print(f"Ingested {len(chunks)} chunks -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
