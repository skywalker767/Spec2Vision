# Visual Spec 规格

## 字段定义

`VisualSpec` 是 VisionFlow 的核心中间表示，由 `VisualSpecAgent` 生成，驱动 Prompt 生成与质量评估。

| 字段 | 类型 | 说明 |
|------|------|------|
| task_type | string | 任务类型 |
| title | string | 视觉标题 |
| scenario | string | 使用场景描述 |
| target_audience | string | 目标受众 |
| purpose | string | 生成目的 |
| style | string | 视觉风格 |
| aspect_ratio | string | 宽高比 |
| main_subject | string | 画面主体 |
| key_elements | list[str] | 关键视觉元素 |
| text_requirements | list[str] | 文字内容要求 |
| constraints | list[str] | 设计约束 |
| avoid | list[str] | 需避免的内容 |
| output_format | string | 输出格式（png / svg） |
| evaluation_dimensions | list[str] | 评估维度 |

---

## 澄清答案 → Visual Spec 映射

`RequirementAgent` 将选择题答案合并进 `requirement`；`VisualSpecAgent` 据此调整 `key_elements`、`constraints`、`avoid`、`output_format`、`evaluation_dimensions`。

| clarification 字段 | 影响 Visual Spec 字段 | 说明 |
|--------------------|----------------------|------|
| style | style | 映射为中文风格描述 |
| aspect_ratio | aspect_ratio | 直接写入 |
| platform | scenario | 电商平台场景描述 |
| compliance_level=conservative | avoid, constraints | 增加保守合规约束 |
| output_format=svg | output_format, constraints | 矢量图 + 清晰标签箭头 |
| layout_blank=left | constraints | 左侧留白供标题 |
| promotion_intensity=strong | key_elements, evaluation_dimensions | 强促销标签 |
| emphasis | evaluation_dimensions | 追加 emphasis:xxx |

---

## 示例：ecommerce_banner（含澄清）

用户选择：`platform=xiaohongshu`, `compliance_level=conservative`, `aspect_ratio=4:5`

```yaml
scenario: 小红书内容电商推广场景
aspect_ratio: "4:5"
constraints:
  - 符合电商平台尺寸规范
  - use conservative commercial wording
avoid:
  - 绝对化用语
  - absolute advertising claims
  - exaggerated medical or efficacy claims
```

---

## 示例：academic_figure（含澄清）

用户选择：`output_format=svg`, `figure_type=method_pipeline`, `label_language=en`

```yaml
output_format: svg
constraints:
  - 箭头方向明确
  - ensure readable labels and clear arrows
evaluation_dimensions:
  - 模块关系
  - emphasis:algorithm_process
```

---

## 示例：ppt_visual（含澄清）

用户选择：`slide_position=cover`, `layout_blank=left`, `visual_focus=technical_system`

```yaml
purpose: 专业汇报封面，突出主题与品牌感
constraints:
  - 16:9宽屏适配
  - reserve blank space on the left side for slide title
```

---

## 示例：ecommerce_banner

```yaml
task_type: ecommerce_banner
title: 夏季低糖冰咖啡
scenario: 电商平台商品推广场景
target_audience: 年轻消费者
purpose: 突出商品卖点，促进点击与购买
style: 小红书风格、清新明亮、促销感强
aspect_ratio: "1:1"
main_subject: 夏季低糖冰咖啡
key_elements:
  - 商品主图
  - 促销标语
  - 价格/折扣
  - CTA按钮
text_requirements:
  - 商品名称
  - 促销信息
  - 限时优惠
constraints:
  - 符合电商平台尺寸规范
  - 禁用夸大宣传
  - 信息层次清晰
avoid:
  - 绝对化用语
  - 虚假承诺
  - 杂乱排版
output_format: png
evaluation_dimensions:
  - 卖点突出
  - 促销感
  - 平台合规
  - 视觉吸引力
```

---

## 示例：academic_figure

```yaml
task_type: academic_figure
title: 机器学习方法流程
scenario: 学术论文方法或实验说明
target_audience: 研究人员与论文审稿人
purpose: 清晰展示模块关系与处理流程
style: 学术简洁、白底、标签可读
aspect_ratio: "4:3"
main_subject: 研究方法流程
key_elements:
  - 数据预处理
  - 特征提取
  - 双分支网络
  - 特征融合
  - 分类输出
text_requirements:
  - 模块标签
  - 数据流向
  - 图注说明
constraints:
  - 箭头方向明确
  - 字号适合印刷
  - 模块对齐
avoid:
  - 过度装饰
  - 低对比度文字
  - 模糊标签
output_format: svg
evaluation_dimensions:
  - 模块关系
  - 标签可读性
  - 流程逻辑
  - 学术风格
```

---

## 示例：ppt_visual

```yaml
task_type: ppt_visual
title: 人工智能驱动的软件开发
scenario: 商务或学术汇报演示
target_audience: 课程师生
purpose: 专业封面或配图，支撑汇报主题
style: 专业科技感、简洁、留白充足
aspect_ratio: "16:9"
main_subject: 课程汇报封面
key_elements:
  - 主标题
  - 副标题
  - 抽象图形
  - 品牌区域
text_requirements:
  - 标题醒目
  - 副标题补充
constraints:
  - 16:9宽屏适配
  - 标题可读性
  - 背景不干扰文字
avoid:
  - 信息过载
  - 低对比标题
  - 杂乱背景
output_format: png
evaluation_dimensions:
  - 专业感
  - 简洁度
  - 标题可读性
  - 汇报适配
```
