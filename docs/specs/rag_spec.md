# Agentic RAG Specification

## 数据源
- `data/knowledge_base/*.md` – 电商 / 学术 / PPT 视觉规范
- 可扩展：specs、rubric、历史案例 JSON

## 索引
- 本地 TF-IDF（stdlib，无 embedding Key）
- 构建：`python scripts/ingest_knowledge_base.py`
- 索引文件：`data/knowledge_base/.index.json`（首次检索自动生成）

## 检索策略
- 按 `task_type` 过滤文档
- TF-IDF 打分 + domain 默认约束
- Top-K（`RAG_TOP_K`，默认 3）

## Agent 使用
1. `RequirementAgent._apply_rag()` 检索规范  
2. 约束写入 `requirement.constraints`  
3. Trace 记录 `rag_retrieval`（source / snippet / score）

## 输出结构
```python
RetrievalHit(source, score, snippet, section, doc_id)
RagContext(query, hits, applied_constraints)
```

## 扩展
- 接口预留真实 embedding provider（OpenAI / local model）
- 当前默认 Mock / 本地 fallback

## 实现路径
- `app/rag/retriever.py`
- `app/rag/index.py`
- `tests/test_rag_*.py`
