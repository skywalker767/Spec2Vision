# Deployment

## 本地 Mock（验收推荐）

```bash
cp .env.example .env
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/ingest_knowledge_base.py
python -m uvicorn app.main:app --reload --port 8000
streamlit run app/ui/streamlit_app.py --server.port 8501
```

## Docker Compose

```bash
cp .env.example .env
docker compose up --build
# API: http://127.0.0.1:8000/docs
# UI: http://127.0.0.1:8501
# Health: http://127.0.0.1:8000/health
```

## 环境变量（必填 / 可选）

| 变量 | 默认 | 说明 |
|------|------|------|
| `LLM_PROVIDER` | mock | mock 无需 Key |
| `IMAGE_PROVIDER` | mock | mock 无需 Key |
| `RAG_ENABLED` | true | 本地知识库检索 |
| `OPENAI_API_KEY` | 空 | 仅 openai 模式 |

## 云服务器（ECS / VPS）

1. 安装 Docker + Compose  
2. 克隆仓库，`cp .env.example .env`  
3. `docker compose up -d --build`  
4. 安全组放行 8000 / 8501  
5. （推荐）Nginx 反代 + HTTPS：见 `deploy/nginx/spec2vision.conf`  
6. systemd 自启：见 `deploy/systemd/spec2vision.service`

## 在线 Demo URL

> **TODO: replace with deployed URL**  
> 部署完成后写入 README「在线 Demo」：`http://YOUR_PUBLIC_IP:8000/docs`

## 日志与故障

| 问题 | 排查 |
|------|------|
| `/health` degraded | 检查 `storage/` 可写、SQLite 路径 |
| 生成 500 | 查看终端日志；Mock 模式应用 `.env.example` |
| OpenAI 503 | 换 `OPENAI_IMAGE_MODEL` 或回退 `IMAGE_PROVIDER=mock` |
| RAG 无命中 | 运行 `python scripts/ingest_knowledge_base.py` |
