# Observability

## Trace ID
- 每个 HTTP 请求注入 `X-Request-ID`（`app/main.py` middleware）
- 生成任务 ID 即 trace_id（8 位 UUID 前缀）

## Agent Trace
- 每步记录：`agent_name`, `step`, `duration_ms`, `metadata.pipeline_step`
- 持久化：`storage/traces/{task_id}.json`
- RAG 检索写入 `rag_retrieval` 步骤

## 查询 API
```bash
curl http://127.0.0.1:8000/traces/{task_id}
```

响应格式：
```json
{
  "success": true,
  "data": { "trace_id": "...", "traces": [...], "task": {...} },
  "trace_id": "..."
}
```

## 导出
```bash
python scripts/export_trace.py {task_id}
```

## 健康检查
`GET /health` 返回 provider、RAG 开关、DB/存储探测（`app/main.py`）

## 日志
- `LOG_LEVEL`, `LOG_JSON`（`.env.example`）
- `app/core/logging.py` 支持 JSON 行日志
