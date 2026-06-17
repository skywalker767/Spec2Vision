# CS599 课程总结

## 从「代码编写者」到「智能体编排者」

Spec2Vision 让我从「写单个函数」转向「设计一条可验证的生产线」：Router 负责决策，Clarification 负责消歧，Visual Spec 负责把模糊语言变成可执行契约，AssetManager 负责调用工具，Evaluator 负责给出可审计反馈。我的核心工作变成：**定义状态、工具边界、失败策略与 Trace**。

## SDD 如何减少模糊需求

没有 Visual Spec 时，Prompt 直接进图像模型，结果不可复现、不可评估。Spec2Vision 强制先产出结构化规格（title / key_elements / constraints / output_format），再生成 Prompt 与资产，使「需求 → 规格 → 实现 → 评估」闭环可追踪。

## Agent 工程中的状态、工具、评估、Trace

- **状态**：`WorkflowState` + LangGraph（`app/graph/visionflow_graph.py`）
- **工具**：图像 / 图表 / 评估 / RAG / MCP（`app/tools/`, `app/mcp/`）
- **评估**：启发式 Rubric + 可选 VLM（`app/tools/evaluator.py`）
- **Trace**：每步 `pipeline_step` + 耗时（`app/tools/trace_logger.py`, `GET /traces/{id}`）

## 个人收获

1. Mock-first 使课程项目可离线验收  
2. 文档必须与实现一致，否则答辩失分  
3. MCP / RAG 不是堆砌，而是让 Agent 可被外部 IDE 调用、被知识库约束  

## 对课程的建议

增加「Agent 可观测性」与「Tool 协议（MCP）」实验环节；提供统一的 Mock LLM/Image 沙箱，降低 API 成本差异。
