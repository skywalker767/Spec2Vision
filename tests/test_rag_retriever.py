"""Agentic RAG ingestion and retrieval tests."""

from __future__ import annotations

from app.rag.index import build_index, load_index, save_index
from app.rag.knowledge_loader import load_knowledge_chunks
from app.rag.retriever import KnowledgeRetriever, get_retriever


def test_knowledge_base_has_three_docs():
    chunks = load_knowledge_chunks()
    doc_ids = {c.doc_id for c in chunks}
    assert "ecommerce_visual_guidelines" in doc_ids
    assert "academic_figure_guidelines" in doc_ids
    assert "ppt_cover_guidelines" in doc_ids


def test_build_and_save_index(tmp_path):
    chunks = load_knowledge_chunks()
    index = build_index(chunks)
    path = save_index(index, tmp_path / "index.json")
    loaded = load_index(path)
    assert loaded["doc_count"] >= 3


def test_retriever_finds_ecommerce_guideline():
    retriever = KnowledgeRetriever(load_index())
    hits = retriever.search("电商主图 促销 卖点", task_type="ecommerce_banner", top_k=2)
    assert hits
    assert hits[0].score > 0
    assert hits[0].snippet


def test_retriever_build_context_adds_constraints():
    ctx = get_retriever().build_context(
        "我要做电商主图 banner",
        task_type="ecommerce_banner",
        top_k=2,
    )
    assert ctx.hits
    assert ctx.applied_constraints
