# VisionFlow Demo Day 展示脚本（约 5 分钟）

> 课程：企业级应用软件设计与开发 CS599  
> 方向：Agentic AI 原生开发  
> 演示环境：FastAPI + Streamlit，默认 Mock 模式（无需 API Key）

---

## 0. 演示前准备（提前 5 分钟）

```bash
cd cs599-project
.venv\Scripts\activate        # Windows
uvicorn app.main:app --reload # 终端 1
streamlit run app/ui/streamlit_app.py  # 终端 2
```

确认：http://localhost:8501 可访问，侧边栏 API 地址为 `http://localhost:8000`。

---

## 1. 选题痛点（45 秒）

**话术：**

> 大家好，我们的项目是 **VisionFlow**。
>
> 现有 AI 生图工具依赖**一次性 Prompt**，存在三个问题：
> 1. 电商、论文、PPT 三类视觉任务规范差异大，统一 Prompt 难以适配；
> 2. 缺少结构化规格，无法表达约束和评估维度；
> 3. 生成过程不可追溯，质量不可控。
>
> 我们的思路是：用 **Visual Spec + 多智能体工作流** 替代单次 Prompt。

**可展示：** README 中的痛点描述或 `docs/specs/product_spec.md` 问题定义。

---

## 2. 系统定位（30 秒）

**话术：**

> VisionFlow 是一个**多领域视觉内容生成平台**，MVP 支持三类任务：
> - 电商营销图 `ecommerce_banner`
> - 学术论文图示 `academic_figure`（SVG 流程图）
> - PPT 配图 `ppt_visual`
>
> 用户输入自然语言，系统自动路由到对应 Agent 工作流。

**可展示：** Streamlit 页面标题 + 项目简介区域。

---

## 3. 架构介绍（60 秒）

**话术：**

> 系统采用分层架构：Streamlit / FastAPI → GenerationService → LangGraph 编排 10 个 Agent → Tool 层 → SQLite + storage。
>
> 核心 Agent 链路：Router → Requirement → VisualSpec → Domain → Prompt → Asset → Critic → Revision。
>
> 默认使用**规则 + 模板**，可选接入 OpenAI / DeepSeek LLM 增强。

**可展示：**

- `docs/images/architecture.mmd` 渲染图（或 README Mermaid）
- `docs/images/agent_flow.mmd` 时序图

---

## 4. 三个案例演示（2 分钟）

### 案例 A：电商图（40 秒）

1. 点击侧边栏或右侧 **「🛒 电商图示例」** 一键填充
2. 点击 **「🚀 开始生成」**
3. 指着结果说明：
   - `route_reason` → 路由到 ecommerce_banner
   - Visual Spec 含促销元素、avoid 规则
   - 生成 PNG 占位图

### 案例 B：论文流程图（40 秒）

1. 点击 **「📊 论文图示例」**
2. 生成后强调：
   - 输出为 **SVG 流程图**（非文生图）
   - Prompt 含 Mermaid diagram spec
   - key_elements 对应方法模块

### 案例 C：PPT 封面（40 秒）

1. 点击 **「📽️ PPT 图示例」**
2. 强调专业科技感、16:9 宽屏适配

**可展示：** 每次生成后展开 **Agent Trace Timeline**，说明每步 Agent 的 input/output 和耗时。

---

## 5. 评估结果（45 秒）

**话术：**

> CriticAgent 对生成结果进行五维规则评分：需求匹配、领域合规、视觉质量、Prompt 完整度、可追溯性。
>
> 综合分低于 85 时，RevisionAgent 自动修订 Prompt 并重新生成。

**操作：**

1. 展示 EvaluationReport 五维指标卡
2. 侧边栏点击 **「Run Benchmark」**
3. 展示三案例 benchmark 表格：routing_correct、overall_score、trace_steps

**可展示：** `storage/reports/benchmark_report.json`

---

## 6. 总结亮点（30 秒）

**话术：**

> 总结 VisionFlow 的四个亮点：
> 1. **多智能体协作** — LangGraph 编排，每步可追溯
> 2. **Visual Spec 驱动** — 结构化规格替代一次性 Prompt
> 3. **跨领域适配** — 三领域差异化 Agent 与工具链
> 4. **可观测 + 可评估** — Trace Timeline、Benchmark、规则/LLM 双模式
>
> 从「一次性 Prompt 生成」升级为「Visual Spec + Multi-Agent Workflow」的视觉生产流程。谢谢！

---

## Q&A 备用回答

| 问题 | 回答要点 |
|------|----------|
| 为什么不用真实文生图 API？ | MVP 用 Mock 保证 Demo 稳定；架构预留 IMAGE_PROVIDER 扩展 |
| LLM 是否必须？ | 否，默认 mock 规则模式，无 Key 可完整运行 |
| 学术图为何用 SVG？ | 流程图需要稳定可控，文生图随机性不适合论文图示 |
| 如何扩展新领域？ | 新增 Domain Agent + VisualSpec 模板 + 路由关键词 |
