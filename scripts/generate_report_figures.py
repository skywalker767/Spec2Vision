#!/usr/bin/env python3
"""Generate PNG figures for CS599 final report (no Mermaid, no network)."""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "images" / "generated"
DPI = 220


def _setup_font() -> None:
    candidates = [
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Arial Unicode MS",
        "DejaVu Sans",
    ]
    for name in candidates:
        try:
            plt.rcParams["font.sans-serif"] = [name]
            plt.rcParams["axes.unicode_minus"] = False
            fig, ax = plt.subplots(figsize=(1, 1))
            ax.text(0.5, 0.5, "测试", fontsize=8)
            plt.close(fig)
            return
        except Exception:
            continue


def _box(ax, x, y, w, h, text, fc="#EEF2FF", ec="#1E3A8A", fontsize=9):
    rect = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.04",
        linewidth=1.5,
        edgecolor=ec,
        facecolor=fc,
    )
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize, wrap=True)


def _arrow(ax, x1, y1, x2, y2):
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=1.4,
            color="#334155",
        )
    )


def _save(fig, name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {path}")
    return path


def figure_1_design_overview() -> None:
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 2)
    ax.axis("off")
    ax.set_title("Figure 1-1 Design Overview / 设计思想总览", fontsize=13, fontweight="bold", pad=12)
    nodes = [
        (0.2, 0.6, 1.4, 0.8, "用户模糊需求"),
        (1.9, 0.6, 1.4, 0.8, "Clarification\nAgent"),
        (3.6, 0.6, 1.4, 0.8, "Visual Spec"),
        (5.3, 0.6, 1.2, 0.8, "Router\nAgent"),
        (6.8, 0.6, 1.4, 0.8, "Generator\nAgent"),
        (8.5, 0.6, 1.3, 0.8, "Evaluator\nAgent"),
        (10.1, 0.6, 1.6, 0.8, "Trace / Report\n/ Asset"),
    ]
    for x, y, w, h, t in nodes:
        _box(ax, x, y, w, h, t)
    for i in range(len(nodes) - 1):
        x1 = nodes[i][0] + nodes[i][2]
        x2 = nodes[i + 1][0]
        _arrow(ax, x1 + 0.05, 1.0, x2 - 0.05, 1.0)
    _save(fig, "figure_1_design_overview.png")


def figure_2_sdd_loop() -> None:
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("Figure 2-1 SDD Loop / 规格驱动开发闭环", fontsize=13, fontweight="bold")
    steps = [
        (3.5, 8.5, "Product Spec"),
        (3.5, 7.2, "Architecture Spec"),
        (3.5, 5.9, "API / MCP / RAG Spec"),
        (3.5, 4.6, "Visual Spec Schema"),
        (3.5, 3.3, "Agent Workflow"),
        (3.5, 2.0, "Tests / Evaluation"),
        (3.5, 0.7, "Trace Feedback"),
    ]
    for x, y, t in steps:
        _box(ax, x, y, 3.0, 0.9, t, fc="#F0FDF4", ec="#166534")
    for i in range(len(steps) - 1):
        _arrow(ax, 5.0, steps[i][1], 5.0, steps[i + 1][1] + 0.9)
    _arrow(ax, 6.6, 1.15, 9.0, 1.15)
    _arrow(ax, 9.0, 1.15, 9.0, 8.95)
    _arrow(ax, 9.0, 8.95, 6.6, 8.95)
    ax.text(9.25, 5.0, "Spec\nUpdate", ha="center", fontsize=9, color="#166534")
    _save(fig, "figure_2_sdd_loop.png")


def figure_3_system_architecture() -> None:
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("Figure 3-1 System Architecture / 系统总体架构", fontsize=13, fontweight="bold")
    layers = [
        (0.5, 8.8, 11, 0.9, "Streamlit Web UI  (app/ui/streamlit_app.py)", "#FEF3C7"),
        (0.5, 7.6, 11, 0.9, "FastAPI Backend  (app/main.py)  |  /health  /generate  /traces", "#DBEAFE"),
        (0.5, 6.4, 5.2, 0.9, "GenerationService", "#E0E7FF"),
        (6.0, 6.4, 5.5, 0.9, "MCP Server  (app/mcp/)", "#FCE7F3"),
        (0.5, 5.2, 11, 0.9, "LangGraph Workflow  (app/graph/visionflow_graph.py)", "#EDE9FE"),
        (0.5, 4.0, 7.5, 0.9, "Agents  (Router / Clarification / Spec / Prompt / Critic ...)", "#F3F4F6"),
        (8.3, 4.0, 3.2, 0.9, "RAG  (app/rag/)", "#DCFCE7"),
        (0.5, 2.8, 7.5, 0.9, "Tools  (Image / Diagram / Evaluator / Trace)", "#F3F4F6"),
        (8.3, 2.8, 3.2, 0.9, "Knowledge Base\n(data/knowledge_base/)", "#DCFCE7"),
        (0.5, 1.6, 5.2, 0.9, "Trace Store + SQLite\n(storage/traces, visionflow.db)", "#FEE2E2"),
        (6.0, 1.6, 5.5, 0.9, "Docker / Cloud Deploy\n(docker-compose.yml)", "#FFEDD5"),
        (0.5, 0.3, 11, 0.9, "Local Storage  (storage/generated, diagrams, prompts, reports)", "#F1F5F9"),
    ]
    for x, y, w, h, t, c in layers:
        _box(ax, x, y, w, h, t, fc=c, ec="#475569")
    _save(fig, "figure_3_system_architecture.png")


def figure_4_agent_workflow() -> None:
    fig, ax = plt.subplots(figsize=(11, 9))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 11)
    ax.axis("off")
    ax.set_title("Figure 3-2 Agent Workflow / Agent 交互流程", fontsize=13, fontweight="bold")
    flow = [
        "Requirement Intake",
        "Clarification Agent",
        "Requirement Agent + RAG",
        "VisualSpec Agent",
        "Domain Agent",
        "Prompt Agent",
        "AssetManager\n(Image/SVG)",
        "Critic / Evaluator",
        "Revision Agent (optional)",
        "Trace Recorder / Save",
    ]
    y = 9.8
    for i, label in enumerate(flow):
        _box(ax, 3.5, y, 4.0, 0.75, label, fc="#EFF6FF" if i % 2 == 0 else "#F8FAFC")
        if i < len(flow) - 1:
            _arrow(ax, 5.5, y, 5.5, y - 0.35)
        y -= 1.05
    _save(fig, "figure_4_agent_workflow.png")


def figure_5_data_flow() -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_title("Figure 3-3 Data Flow / 数据流设计", fontsize=13, fontweight="bold")
    _box(ax, 0.5, 5.5, 2.2, 1.0, "User Input\n+ Clarification", "#DBEAFE")
    _box(ax, 3.2, 5.5, 2.2, 1.0, "Requirement\n+ RAG Hits", "#DCFCE7")
    _box(ax, 5.9, 5.5, 2.2, 1.0, "Visual Spec\n(JSON Schema)", "#EDE9FE")
    _box(ax, 8.6, 5.5, 2.2, 1.0, "Prompt\n+ Provider", "#FEF3C7")
    _arrow(ax, 2.7, 6.0, 3.2, 6.0)
    _arrow(ax, 5.4, 6.0, 5.9, 6.0)
    _arrow(ax, 8.1, 6.0, 8.6, 6.0)
    _box(ax, 2.0, 3.2, 3.0, 1.0, "Generated Asset\n(PNG/SVG)", "#FEE2E2")
    _box(ax, 5.5, 3.2, 3.0, 1.0, "Evaluation Report\n(Rubric 6D)", "#FCE7F3")
    _box(ax, 9.0, 3.2, 2.5, 1.0, "Trace JSON\n(pipeline_step)", "#F3F4F6")
    _arrow(ax, 9.7, 5.5, 3.5, 4.2)
    _arrow(ax, 9.7, 5.5, 7.0, 4.2)
    _arrow(ax, 9.7, 5.5, 10.2, 4.2)
    ax.text(6.0, 1.5, "Feedback: revision loop if score < threshold", ha="center", fontsize=10, color="#64748B")
    _save(fig, "figure_5_data_flow.png")


def figure_6_mcp_rag_integration() -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_title("Figure 3-4 MCP & RAG Integration", fontsize=13, fontweight="bold")
    _box(ax, 0.3, 5.2, 2.5, 1.0, "AI IDE /\nExternal Agent", "#FEF3C7")
    _box(ax, 3.2, 5.2, 2.5, 1.0, "MCP Server\n(stdio JSON-RPC)", "#DBEAFE")
    _box(ax, 6.1, 5.2, 2.8, 1.0, "MCP Tools\n(4 tools)", "#E0E7FF")
    _box(ax, 9.2, 5.2, 2.5, 1.0, "Spec2Vision\nCore Service", "#EDE9FE")
    _arrow(ax, 2.8, 5.7, 3.2, 5.7)
    _arrow(ax, 5.7, 5.7, 6.1, 5.7)
    _arrow(ax, 8.9, 5.7, 9.2, 5.7)
    _box(ax, 1.0, 2.8, 3.0, 1.0, "RAG Retriever\n(TF-IDF local)", "#DCFCE7")
    _box(ax, 4.5, 2.8, 3.0, 1.0, "Knowledge Base\n(3 guideline docs)", "#BBF7D0")
    _box(ax, 8.0, 2.8, 3.5, 1.0, "Agent Workflow\n+ Trace Store", "#F3F4F6")
    _arrow(ax, 4.0, 3.3, 4.5, 3.3)
    _arrow(ax, 7.5, 3.3, 8.0, 3.3)
    _arrow(ax, 2.5, 3.8, 10.0, 5.2)
    _arrow(ax, 10.0, 5.2, 2.5, 3.8)
    _save(fig, "figure_6_mcp_rag_integration.png")


def figure_7_trace_evaluation_flow() -> None:
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title("Figure 5-1 Trace & Evaluation Flow", fontsize=13, fontweight="bold")
    _box(ax, 0.5, 4.5, 2.0, 0.9, "trace_id", "#DBEAFE")
    _box(ax, 2.8, 4.5, 2.3, 0.9, "Agent Events\n(duration_ms)", "#EDE9FE")
    _box(ax, 5.4, 4.5, 2.0, 0.9, "Tool Calls", "#FEF3C7")
    _box(ax, 7.8, 4.5, 2.0, 0.9, "Eval Score\n(Rubric)", "#FCE7F3")
    _box(ax, 10.1, 4.5, 1.5, 0.9, "Errors /\nRecovery", "#FEE2E2")
    for i in range(4):
        _arrow(ax, 0.5 + (i + 1) * 2.35, 4.95, 0.5 + (i + 1) * 2.35 + 0.45, 4.95)
    _box(ax, 2.5, 2.5, 3.5, 1.0, "storage/traces/{id}.json", "#F1F5F9")
    _box(ax, 6.5, 2.5, 3.5, 1.0, "GET /traces/{id}\nexport_trace.py", "#F1F5F9")
    _arrow(ax, 4.25, 4.5, 4.25, 3.5)
    _arrow(ax, 8.25, 4.5, 8.25, 3.5)
    _save(fig, "figure_7_trace_evaluation_flow.png")


def figure_8_roadmap() -> None:
    fig, ax = plt.subplots(figsize=(12, 3.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 3.5)
    ax.axis("off")
    ax.set_title("Figure 6-1 System Roadmap / 系统演进路线", fontsize=13, fontweight="bold")
    stages = [
        (0.3, "V1\nCourse Project"),
        (2.5, "V2\nMCP + RAG"),
        (4.7, "V3\nVLM + Human FB"),
        (6.9, "V4\nEnterprise"),
        (9.1, "V5\nAsset Platform"),
    ]
    for x, t in stages:
        _box(ax, x, 1.2, 1.8, 1.4, t, fc="#EFF6FF", ec="#2563EB", fontsize=8)
    for i in range(len(stages) - 1):
        _arrow(ax, stages[i][0] + 1.85, 1.9, stages[i + 1][0] - 0.05, 1.9)
    _save(fig, "figure_8_roadmap.png")


def main() -> int:
    _setup_font()
    figure_1_design_overview()
    figure_2_sdd_loop()
    figure_3_system_architecture()
    figure_4_agent_workflow()
    figure_5_data_flow()
    figure_6_mcp_rag_integration()
    figure_7_trace_evaluation_flow()
    figure_8_roadmap()
    print(f"\nAll figures written to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
