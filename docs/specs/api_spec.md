# VisionFlow API 规格

Base URL: `http://localhost:8000`

交互式文档：http://localhost:8000/docs

---

## GET /health

健康检查。

**响应 200：**

```json
{
  "status": "ok"
}
```

---

## POST /generate

提交视觉生成任务，同步执行完整多智能体工作流。

**请求体 `GenerationRequest`：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_input | string | 是 | 用户任务描述 |
| task_type | string | 否 | `auto` / `ecommerce_banner` / `academic_figure` / `ppt_visual`，默认 `auto` |
| style_preference | string | 否 | 风格偏好 |
| target_audience | string | 否 | 目标受众 |
| aspect_ratio | string | 否 | 宽高比，如 `16:9` |
| enable_revision | bool | 否 | 是否启用自动修订，默认 `true` |

**请求示例：**

```json
{
  "user_input": "为一款夏季低糖冰咖啡生成一张小红书风格促销图，突出清爽、低糖、限时优惠。",
  "task_type": "auto",
  "style_preference": "小红书风格、清新明亮",
  "target_audience": "年轻消费者",
  "aspect_ratio": "1:1",
  "enable_revision": true
}
```

**响应 200 `GenerationResult`：**

```json
{
  "task_id": "a1b2c3d4",
  "task_type": "ecommerce_banner",
  "route_reason": "关键词匹配: ecommerce=2, academic=0, ppt=0 → ecommerce_banner",
  "visual_spec": { "task_type": "ecommerce_banner", "title": "...", "..." : "..." },
  "prompt": "Subject: ... Scene: ... Style: ...",
  "output_path": "storage/generated/a1b2c3d4_ecommerce_banner.png",
  "report_path": "storage/traces/a1b2c3d4.json",
  "evaluation": {
    "requirement_match_score": 80,
    "domain_compliance_score": 95,
    "visual_quality_score": 85,
    "prompt_completeness_score": 100,
    "traceability_score": 88,
    "risk_count": 0,
    "overall_score": 89,
    "comments": ["..."],
    "suggestions": []
  },
  "traces": [
    {
      "step": "route_task",
      "agent_name": "TaskRouterAgent",
      "input_summary": "...",
      "output_summary": "...",
      "metadata": {},
      "timestamp": "2026-06-16T12:00:00+00:00"
    }
  ],
  "created_at": "2026-06-16T12:00:00+00:00"
}
```

**错误响应：**

- `500`：工作流执行失败

---

## GET /tasks

列出已生成任务摘要。

**Query 参数：**

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| limit | int | 50 | 返回数量上限 |
| offset | int | 0 | 偏移量 |

**响应 200：**

```json
{
  "tasks": [
    {
      "task_id": "a1b2c3d4",
      "task_type": "ecommerce_banner",
      "title": "促销商品",
      "overall_score": 89,
      "output_path": "storage/generated/a1b2c3d4_ecommerce_banner.png",
      "created_at": "2026-06-16T12:00:00+00:00"
    }
  ],
  "total": 1
}
```

---

## GET /tasks/{task_id}

获取单个任务完整详情。

**响应 200：** 完整 `GenerationResult`

**响应 404：**

```json
{
  "detail": "Task a1b2c3d4 not found"
}
```

---

## curl 示例

```bash
# 健康检查
curl http://localhost:8000/health

# 生成电商图
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d "{\"user_input\": \"设计618电商促销主图\", \"task_type\": \"auto\"}"

# 查询任务
curl http://localhost:8000/tasks/a1b2c3d4
```
