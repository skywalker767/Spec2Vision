# MCP Usage Example

## 启动 Server

```bash
python scripts/run_mcp_server.py
```

## 通用 Client 配置思路

在支持 MCP 的 Agent 客户端中添加 **stdio** server：

```json
{
  "mcpServers": {
    "spec2vision": {
      "command": "python",
      "args": ["scripts/run_mcp_server.py"],
      "cwd": "/path/to/Spec2Vision",
      "env": {
        "LLM_PROVIDER": "mock",
        "IMAGE_PROVIDER": "mock",
        "RAG_ENABLED": "true"
      }
    }
  }
}
```

## 手动 JSON-RPC 探测

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"demo","version":"1.0"}}}' | python scripts/run_mcp_server.py
```

## Tool 调用示例（Python）

```python
from app.mcp.tools import create_visual_spec, generate_visual_asset

spec = create_visual_spec({"user_input": "小红书冰咖啡促销主图", "task_type": "ecommerce_banner"})
print(spec.data["visual_spec"])

gen = generate_visual_asset({"user_input": "小红书冰咖啡促销主图", "task_type": "ecommerce_banner"})
print(gen.data["output_path"])
```

## Real Provider

```bash
export LLM_PROVIDER=deepseek
export IMAGE_PROVIDER=openai
export OPENAI_API_KEY=your_key_here
python scripts/run_mcp_server.py
```
