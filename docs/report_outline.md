# CS599 大作业报告大纲 — VisionFlow

> 课程：企业级应用软件设计与开发  
> 项目：VisionFlow — 基于多智能体协作的多领域视觉内容生成系统  
> 方向：Agentic AI 原生开发

---

## 一、选题背景与设计思想

### 应写内容

- 问题背景：单次 Prompt 生图的局限性
- 设计动机：为何选择多智能体 + Visual Spec
- 目标用户与核心场景（电商 / 学术 / PPT）
- 设计原则：可观测、可评估、可扩展、无 Key 可运行

### 建议配图

| 图/表 | 来源 |
|-------|------|
| 图 1-1 传统 Prompt vs VisionFlow 对比示意图 | 自绘或 README 改造 |
| 表 1-1 三类任务场景对比 | `docs/specs/product_spec.md` |
| 图 1-2 系统定位图 | `docs/images/architecture.mmd` 渲染 |

### 建议代码/截图

- 无需代码，以论述为主

---

## 二、Specs 规格文档

### 应写内容

- 产品规格摘要（问题定义、MVP 范围）
- Visual Spec 数据结构说明
- API 规格摘要
- Agent 工作流规格
- 评估规格

### 建议配图

| 图/表 | 来源 |
|-------|------|
| 表 2-1 Visual Spec 字段定义 | `docs/specs/visual_spec.md` |
| 表 2-2 API 端点一览 | `docs/specs/api_spec.md` |
| 表 2-3 评估指标定义 | `docs/specs/evaluation_spec.md` |
| 图 2-1 三领域 Visual Spec YAML 示例 | `docs/specs/visual_spec.md` 三个 YAML 块 |

### 建议代码截图

- `app/models/schemas.py` 中 `VisualSpec`、`GenerationResult` 类定义

---

## 三、系统架构与设计

### 应写内容

- 分层架构：UI/API → Service → Graph → Agent → Tool → Storage
- LangGraph 工作流设计
- 数据流与状态管理（WorkflowState）
- LLM Provider 可选架构

### 建议配图

| 图/表 | 来源 |
|-------|------|
| 图 3-1 系统分层架构图 | `docs/images/architecture.mmd` |
| 图 3-2 Agent 交互时序图 | `docs/images/agent_flow.mmd` |
| 图 3-3 数据流图 | `docs/images/data_flow.mmd` |
| 表 3-1 Agent 职责表 | README Agent 设计表 |

### 建议代码截图

- `app/graph/visionflow_graph.py` — StateGraph 节点与边
- `app/llm/llm_factory.py` — Provider 工厂与 fallback

---

## 四、关键实现与代码展示

### 应写内容

- TaskRouterAgent 路由逻辑
- VisualSpecAgent 三领域模板
- PromptAgent 图像 Prompt / Mermaid Spec
- CriticAgent + RevisionAgent 评估修订闭环
- Mock 图像生成与 SVG 流程图

### 建议配图

| 图/表 | 来源 |
|-------|------|
| 图 4-1 评估流程图 | `docs/images/evaluation_flow.mmd` |
| 表 4-1 路由关键词规则 | `app/agents/router_agent.py` |

### 建议代码截图

| 截图 | 文件 |
|------|------|
| 路由关键词匹配 | `app/agents/router_agent.py` |
| Visual Spec 领域模板 | `app/agents/visual_spec_agent.py` DOMAIN_DEFAULTS |
| Mock 占位图生成 | `app/tools/image_generator.py` |
| SVG 流程图生成 | `app/tools/diagram_generator.py` |
| Trace 计时 | `app/graph/visionflow_graph.py` `_timed_call` |

### 建议运行截图

- Streamlit 生成结果页
- Agent Trace Timeline 表格
- 电商 PNG / 学术 SVG 输出

---

## 五、测试与评估

### 应写内容

- 测试策略：单元测试 + 集成测试 + LLM fallback 测试
- Benchmark 设计与指标
- 三案例 Benchmark 结果分析
- 局限性说明

### 建议配图

| 图/表 | 来源 |
|-------|------|
| 表 5-1 测试用例覆盖 | `tests/` 目录结构 |
| 表 5-2 Benchmark 结果 | `storage/reports/benchmark_report.json` |
| 图 5-1 pytest 通过截图 | 终端 `pytest tests/ -v` |
| 图 5-2 Benchmark 通过率 | Streamlit Run Benchmark 结果 |

### 建议代码截图

- `tests/test_generation_flow.py` — 三案例参数化测试
- `app/tools/benchmark.py` — `run_benchmark()` 核心逻辑

---

## 六、系统升级与扩展

### 应写内容

- LLM 增强路径（OpenAI / DeepSeek）
- 真实文生图 API 接入方案
- 新领域扩展（如 UI 设计、海报）
- 向量记忆 / 用户反馈闭环

### 建议配图

| 图/表 | 来源 |
|-------|------|
| 表 6-1 LLM Provider 对比 | README LLM 配置表 |
| 表 6-2 扩展路线图 | 自绘 |

### 建议代码截图

- `app/llm/openai_llm.py` — 可选 API 实现
- `.env.example` — 环境变量配置

---

## 七、课程总结

### 应写内容

- 技术收获：FastAPI、LangGraph、Pydantic、Agent 设计
- 项目管理：Specs 驱动开发、测试先行
- 不足与改进方向
- 学术诚信声明：无硬编码 Key、开源依赖注明

### 建议配图

- 无强制配图，可附 Demo 合影或 Streamlit 全页截图

### 附录建议

| 附录 | 内容 |
|------|------|
| 附录 A | 完整 API 文档 `docs/specs/api_spec.md` |
| 附录 B | Demo 脚本 `docs/demo/demo_script.md` |
| 附录 C | Benchmark 原始数据 `benchmark_report.json` |
| 附录 D | 项目目录结构 README |

---

## 报告篇幅建议

| 章节 | 建议页数 |
|------|----------|
| 一、选题背景 | 2–3 页 |
| 二、Specs | 3–4 页 |
| 三、架构设计 | 4–5 页 |
| 四、关键实现 | 5–6 页 |
| 五、测试评估 | 3–4 页 |
| 六、升级扩展 | 2–3 页 |
| 七、课程总结 | 1–2 页 |
| **合计** | **20–27 页** |
