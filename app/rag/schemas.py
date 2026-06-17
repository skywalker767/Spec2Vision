"""RAG schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class KnowledgeChunk(BaseModel):
    doc_id: str
    title: str
    section: str
    text: str
    task_types: list[str] = Field(default_factory=list)


class RetrievalHit(BaseModel):
    source: str
    score: float
    snippet: str
    section: str = ""
    doc_id: str = ""
    task_type: str = ""


class RagContext(BaseModel):
    query: str
    hits: list[RetrievalHit] = Field(default_factory=list)
    applied_constraints: list[str] = Field(default_factory=list)
