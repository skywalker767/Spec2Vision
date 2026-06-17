"""Keyword + TF-IDF retriever with deterministic mock fallback."""

from __future__ import annotations

import math
from functools import lru_cache

from app.config import get_settings
from app.rag.index import load_index
from app.rag.schemas import RagContext, RetrievalHit


class KnowledgeRetriever:
    """Local retriever – no external embedding API required."""

    def __init__(self, index: dict | None = None):
        self.index = index or load_index()

    def search(
        self,
        query: str,
        *,
        task_type: str | None = None,
        top_k: int = 3,
    ) -> list[RetrievalHit]:
        from app.rag.index import tokenize

        settings = get_settings()
        if not settings.rag_enabled:
            return []

        q_tokens = tokenize(query)
        if not q_tokens:
            return []

        q_tf = {t: q_tokens.count(t) for t in set(q_tokens)}
        df = self.index.get("df", {})
        n_docs = max(self.index.get("doc_count", 1), 1)
        hits: list[RetrievalHit] = []

        for doc in self.index.get("docs", []):
            if task_type and doc.get("task_types") and task_type not in doc["task_types"]:
                continue
            score = 0.0
            doc_tf = doc.get("tf", {})
            doc_len = doc.get("len", 1)
            for term, q_count in q_tf.items():
                if term not in doc_tf:
                    continue
                idf = math.log((1 + n_docs) / (1 + df.get(term, 0))) + 1.0
                score += (1 + math.log(1 + doc_tf[term])) * idf * q_count
            score /= math.sqrt(doc_len)
            if score <= 0:
                continue
            snippet = doc["text"][:240].replace("\n", " ")
            hits.append(
                RetrievalHit(
                    source=f"{doc['doc_id']}#{doc['section']}",
                    score=round(score, 4),
                    snippet=snippet,
                    section=doc["section"],
                    doc_id=doc["doc_id"],
                    task_type=(doc.get("task_types") or [""])[0],
                )
            )

        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:top_k]

    def build_context(
        self,
        query: str,
        *,
        task_type: str | None = None,
        top_k: int = 3,
    ) -> RagContext:
        hits = self.search(query, task_type=task_type, top_k=top_k)
        constraints: list[str] = []
        domain_defaults = {
            "ecommerce_banner": ["主体居中，保留安全边距", "核心卖点短句，移动端可读"],
            "academic_figure": ["模块箭头方向清晰一致", "白底学术简洁风格"],
            "ppt_visual": ["标题区留白充足，远距可读", "16:9 宽屏适配"],
        }
        if task_type and task_type in domain_defaults:
            constraints.extend(domain_defaults[task_type][:2])
        for hit in hits:
            if "主体" in hit.snippet or "居中" in hit.snippet:
                constraints.append("主体居中，保留安全边距")
            if "箭头" in hit.snippet or "流向" in hit.snippet:
                constraints.append("模块箭头方向清晰一致")
            if "留白" in hit.snippet or "标题" in hit.snippet:
                constraints.append("标题区留白充足，远距可读")
            if "卖点" in hit.snippet:
                constraints.append("核心卖点短句，移动端可读")
        seen: set[str] = set()
        uniq: list[str] = []
        for c in constraints:
            if c not in seen:
                seen.add(c)
                uniq.append(c)
        return RagContext(query=query, hits=hits, applied_constraints=uniq)


@lru_cache
def get_retriever() -> KnowledgeRetriever:
    return KnowledgeRetriever()


def reset_retriever_cache() -> None:
    get_retriever.cache_clear()
