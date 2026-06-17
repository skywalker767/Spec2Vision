# Security

## 密钥管理
- 所有 Key 经环境变量注入（`app/config.py`, `.env.example`）
- Trace metadata 脱敏（`app/tools/trace_logger.py`）
- **禁止**在代码 / README / 文档中硬编码真实 Key

## 输入校验
- 用户输入长度上限（`app/core/security.py` → `MAX_USER_INPUT_LENGTH`）
- 上传类型白名单：`.pdf`, `.txt`, `.md`
- 上传大小上限 15MB（`app/main.py`）

## 路径安全
- 资产下载经 `resolve_storage_path()` 限制在 `storage/` 子目录
- `trace_id` / `task_id` 仅允许 `[a-zA-Z0-9_-]`

## Prompt 注入防护
- 用户输入经 `[USER_INPUT_START]…[USER_INPUT_END]` 边界包装（`sanitize_prompt_injection_block`）
- RAG 片段带来源标记写入 Trace，不覆盖 System Prompt
- LLM System Prompt 固定于 Agent 模块，用户无法通过 API 字段覆盖

## 错误暴露
- `AppError` 返回结构化 JSON，不含 Python 堆栈（`app/main.py`）
- 内部异常记录于服务端日志
