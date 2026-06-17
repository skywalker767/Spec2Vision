# 期末 Demo / 答辩 Checklist

## 5 分钟现场演示

- [ ] 打开 README「CS599 评分点速览」
- [ ] Mock 单案例：`python benchmark.py --demo examples/ecommerce_case.json`
- [ ] 展示 `examples/demo/ecommerce/` 工件（spec / prompt / trace / eval）
- [ ] 展示 RAG：`python scripts/ingest_knowledge_base.py` + 说明约束如何进入 Trace
- [ ] 展示 MCP：`python scripts/run_mcp_server.py`（stdio）+ `docs/examples/mcp_usage.md`
- [ ] 展示 Trace API：`GET /traces/{task_id}`
- [ ] 说明 Docker：`docker compose up --build`

## API 失效 Fallback

- [ ] 默认 `.env.example` → Mock LLM + Mock Image
- [ ] `make demo` / `pytest` 无需 Key
- [ ] 预置 `examples/demo/` 与 `docs/images/examples/` 静态图

## 云端 Demo URL

> **TODO: replace with deployed URL**  
> 部署后替换 README「在线 Demo」一节：`http://YOUR_PUBLIC_IP:8000/docs`

## 截图 / 录屏检查

- [ ] README 9 张 PNG 展示正常
- [ ] Streamlit UI 生成一页
- [ ] CI badge 绿色
- [ ] Trace JSON 含 `rag_retrieval` / `pipeline_step`
