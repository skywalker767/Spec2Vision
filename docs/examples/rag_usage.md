# RAG Usage

## 1. 构建知识库

```bash
python scripts/ingest_knowledge_base.py
# Ingested N chunks -> data/knowledge_base/.index.json
```

## 2. 检索示例

```python
from app.rag import get_retriever

retriever = get_retriever()
hits = retriever.search("电商主图 促销 卖点", task_type="ecommerce_banner", top_k=3)
for h in hits:
    print(h.score, h.source, h.snippet[:80])

ctx = retriever.build_context("我要做电商主图", task_type="ecommerce_banner")
print(ctx.applied_constraints)
```

## 3. 在生成流水线中观察 RAG

```bash
python benchmark.py --demo examples/ecommerce_case.json
# 查看 trace.json 中的 rag_retrieval 步骤
```

## 4. 关闭 RAG

```bash
RAG_ENABLED=false python benchmark.py --demo examples/ecommerce_case.json
```
