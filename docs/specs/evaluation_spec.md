# 质量评估规格

## 评估指标定义

| 指标 | 字段 | 范围 | 说明 |
|------|------|------|------|
| 需求匹配 | requirement_match_score | 0–100 | prompt 与 main_subject / purpose 一致性 |
| 领域合规 | domain_compliance_score | 0–100 | 是否符合领域关键词与约束 |
| 视觉质量 | visual_quality_score | 0–100 | 输出资产是否存在且有效 |
| Prompt 完整度 | prompt_completeness_score | 0–100 | 是否包含 subject/scene/style 等必要字段 |
| 可追溯性 | traceability_score | 0–100 | Agent Trace 步骤数量 |
| 风险词数 | risk_count | ≥0 | 绝对化宣传用语命中数 |
| 综合评分 | overall_score | 0–100 | 加权平均 − risk_count × 2 |

## 分数计算方式

```python
scores = [
    requirement_match_score,
    domain_compliance_score,
    visual_quality_score,
    prompt_completeness_score,
    traceability_score,
]
overall_score = clamp(int(mean(scores)) - risk_count * 2, 0, 100)
```

### 各维度规则摘要

**需求匹配（基础 60）：**
- main_subject 出现在 prompt 中：+20
- purpose 长度 > 5：+10

**领域合规（基础 70）：**
- 电商：含 product/sale/banner 等词 +15；有 constraints +10
- 学术：含 flowchart/mermaid/diagram +20；有 key_elements +10
- PPT：含 presentation/slide/cover/professional +20

**视觉质量：**
- 资产存在且 > 200 bytes：85
- 否则：40

**Prompt 完整度：**
- 每命中一个必要字段（subject/scene/style/composition/aspect ratio）：+10（基础 50）

**可追溯性：**
- `min(100, 40 + trace_count × 8)`

## 风险词列表

```
最好, 第一, 绝对, 100%, best ever, guaranteed, 永远,
国家级, 顶级, 唯一, #1
```

每命中一个风险词，`risk_count += 1`，`overall_score -= 2`。

## 修订触发条件

```
overall_score < 85 AND enable_revision == true AND revision_done == false
```

RevisionAgent 修正策略：
1. 补充主体描述
2. 增强领域约束
3. 移除风险词
4. 增加构图说明

## 测试样例

| 场景 | 预期 overall_score | 说明 |
|------|-------------------|------|
| 完整 prompt + 有效资产 + 8 步 trace | 80–95 | 正常通过 |
| 无资产文件 | 40–60 | visual_quality 低 |
| 含风险词 prompt | 降低 2×risk_count | 合规扣分 |
| trace < 5 步 | traceability 偏低 | 发出建议 |

## 局限性说明

1. **非真实视觉理解**：评估基于规则和启发式，未使用 CLIP 或人工评审
2. **Mock 图像**：占位图不代表真实生成质量，visual_quality 仅检查文件存在性
3. **关键词路由**：Router 依赖关键词匹配，对模糊输入可能误判
4. **单次修订**：仅执行一轮修订，不支持多轮迭代优化
5. **英文 Prompt 评估**：学术类 Diagram Spec 的评分规则对中英文混合支持有限
6. **风险词表有限**：仅覆盖常见绝对化用语，不完整

后续可通过接入 LLM Critic 或人工反馈（RLHF）提升评估准确性。
