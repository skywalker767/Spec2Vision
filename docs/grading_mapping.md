# CS599 评分点对照表

| 评分项 | 分值 | 本项目实现 | 关键路径 | Demo 方式 |
|--------|------|------------|----------|-----------|
| 选题与设计思想 | 20 | Visual Spec 驱动多 Agent 视觉资产流水线 | `README.md`, `docs/specs/product_spec.md` | 30s 痛点 + 架构图 |
| Specs 规格设计 | 20 | VisualSpec / API / Agent / Eval 六份规格 | `docs/specs/*.md` | 展示 `visual_spec.json` |
| 系统架构与设计 | 15 | LangGraph 编排 + Service 层 + Tool 层 | `docs/specs/architecture_spec.md`, `app/graph/` | Mermaid 架构图 |
| 关键实现与代码 | 15 | 10 Agent + MCP + RAG + Evaluator | `app/agents/`, `app/mcp/`, `app/rag/` | `python benchmark.py --demo` |
| 测试与评估 | 10 | 147 pytest + benchmark smoke | `tests/`, `docs/test_report.md` | `pytest -v` |
| 升级扩展设想 | 10 | MCP / RAG / 云部署 / VLM Roadmap | `docs/roadmap.md` | Roadmap 讲解 |
| 课程总结 | 10 | Agent 编排思维 + SDD 收获 | `docs/course_summary.md` | 答辩 Q&A |

## 加分项

| 加分 | 实现 | 路径 | 演示 |
|------|------|------|------|
| MCP + Agentic RAG (+3) | 4 MCP tools + 本地 RAG 检索 | `app/mcp/`, `app/rag/`, `scripts/run_mcp_server.py` | `docs/examples/mcp_usage.md` |
| 云部署 (+3) | Docker Compose + 部署文档 | `docker-compose.yml`, `docs/deployment.md` | `docker compose up --build` |
| 课堂展示 (+2) | Demo 脚本 + Checklist | `docs/demo/demo_script.md`, `docs/final_demo_checklist.md` | 5 分钟现场流程 |
| 生产级 (+3) | 错误/安全/Trace | `app/core/`, `docs/security.md`, `docs/observability.md` | `/traces/{id}` + 结构化错误 |
