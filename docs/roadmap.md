# Spec2Vision Roadmap

## V1 · 当前 CS599 课程项目
- LangGraph 多 Agent 流水线
- Mock 默认可运行 + OpenAI 可选
- 启发式 Evaluator + Trace
- Docker Compose + CI

## V2 · MCP + RAG + 云部署（本仓库已包含）
- MCP stdio Server（4 tools）
- 本地 Agentic RAG（TF-IDF 知识库）
- `/traces/{id}` + 结构化错误
- 部署文档 + Nginx/systemd 模板

## V3 · VLM Judge + 人类反馈
- 可选 GPT-4V / 专用 VLM 审美评分
- 人类 thumbs-up/down 回流 Prompt 修订
- A/B Prompt 版本管理

## V4 · 企业级多租户
- 鉴权 / RBAC / 审计日志
- 品牌资产库 + 工作流编排
- 多租户隔离与配额
