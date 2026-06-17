# VisionFlow 产品规格

## 问题定义

现有 AI 图像生成工具依赖单次自然语言 Prompt，存在以下问题：

1. **领域适配差**：电商、学术、PPT 三类视觉任务规范差异大，统一 Prompt 难以满足
2. **缺乏结构化规格**：无法表达约束、避免项、评估维度等领域知识
3. **质量不可控**：缺少自动评估与修订机制
4. **过程不透明**：生成过程无法追溯和调试

## 目标用户

| 用户群体 | 使用场景 |
|----------|----------|
| 电商运营人员 | 商品主图、促销 Banner、详情页配图 |
| 研究人员 / 学生 | 论文方法流程图、实验 Pipeline 图示 |
| 职场汇报者 | PPT 封面、报告配图、演示素材 |
| 开发者 / 学习者 | Agentic AI 工作流学习与二次开发 |

## 核心场景

### 场景一：电商营销图
用户输入商品描述和促销需求 → 系统路由到电商工作流 → 生成含卖点、CTA、合规约束的 Visual Spec → 输出促销风格占位图。

### 场景二：学术论文图示
用户输入方法描述 → 系统路由到学术工作流 → 生成模块流程 Visual Spec → 输出 SVG 流程图（非文生图）。

### 场景三：PPT 汇报配图
用户输入汇报主题 → 系统路由到 PPT 工作流 → 生成封面构图 Visual Spec → 输出专业风格占位图。

## 功能需求

| 编号 | 功能 | 优先级 |
|------|------|--------|
| F1 | 自动任务路由（Task Router Agent） | P0 |
| F2 | 结构化 Visual Spec 生成 | P0 |
| F3 | 三领域差异化 Prompt / Diagram 生成 | P0 |
| F4 | Mock 图像 + SVG 图示生成 | P0 |
| F5 | 五维质量评估 + 风险词检测 | P0 |
| F6 | 自动 Prompt 修订 | P1 |
| F7 | Agent Trace 完整记录 | P0 |
| F8 | REST API + Streamlit Demo | P0 |
| F9 | 任务历史查询 | P1 |
| F10 | LLM 接口预留 | P2 |

## 非功能需求

- Python 3.11+，本地可运行，无需外部 API Key
- 响应时间：单次生成 < 30 秒（Mock 模式）
- 数据持久化：SQLite + 本地 storage/
- 可测试性：pytest 覆盖率覆盖核心 Agent 与 API
- 可扩展性：Agent 可替换为 LLM 实现
- 部署：支持 Docker / docker-compose

## MVP 范围

**包含：**
- 三任务类型：`ecommerce_banner`、`academic_figure`、`ppt_visual`
- 10 个规则型 Agent + LangGraph 编排
- Mock 图像生成 + SVG 流程图
- FastAPI 四端点 + Streamlit Demo
- 完整 Trace / Report / Prompt 持久化

**不包含（后续迭代）：**
- 真实文生图 API 接入
- 用户认证与多租户
- 向量数据库长期记忆
- 前端生产级 UI
