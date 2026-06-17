# MCP Tool Server Specification

## 目标
将 Spec2Vision 能力暴露为 MCP Tools，供 Claude Desktop / Cursor / Trae 等 Agent 客户端调用。

## 传输
- **stdio JSON-RPC 2.0**（轻量实现，无额外 SDK 依赖）
- 启动：`python scripts/run_mcp_server.py`

## Tools

| Tool | 输入 | 输出 | 复用模块 |
|------|------|------|----------|
| `create_visual_spec` | user_input, task_type, style… | Visual Spec JSON | Router + Requirement + VisualSpec Agent |
| `generate_visual_asset` | user_input, task_type | output_path, prompt, trace_id | `GenerationService.run_generation` |
| `evaluate_visual_asset` | visual_spec, asset_path/task_id | score, suggestions | `Evaluator` |
| `query_generation_trace` | trace_id | traces JSON | `storage/traces/` |

## 错误格式
```json
{"success": false, "error": {"code": "...", "message": "...", "recoverable": true}, "trace_id": "..."}
```

## Mock 模式
脚本默认 `LLM_PROVIDER=mock`, `IMAGE_PROVIDER=mock`，无 Key 可演示。

## 实现路径
- `app/mcp/server.py` – JSON-RPC loop
- `app/mcp/tools.py` – handlers
- `app/mcp/schemas.py` – Pydantic I/O
- `tests/test_mcp_tools.py`
