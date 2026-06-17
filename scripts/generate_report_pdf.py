#!/usr/bin/env python3
"""Convert CS599 Markdown report to PDF with Chinese font and embedded PNG figures."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "docs" / "CS599_大作业报告.md"
PDF_PATH = ROOT / "docs" / "CS599_大作业报告.pdf"
INFO_JSON = ROOT / "docs" / "student_info.json"

BEGIN_MARKER = "<!-- STUDENT_INFO_BEGIN -->"
END_MARKER = "<!-- STUDENT_INFO_END -->"

FONT_CANDIDATES = [
    Path(r"C:\Windows\Fonts\simhei.ttf"),
    Path(r"C:\Windows\Fonts\msyh.ttc"),
    Path(r"C:\Windows\Fonts\simsun.ttc"),
]


def _load_cover_info() -> dict[str, str]:
    defaults = {
        "course_name": "企业级应用软件设计与开发",
        "course_code": "50120224001 / CS599",
        "project_name": "Spec2Vision：Visual Spec 驱动的多 Agent 视觉资产生成系统",
        "project_direction": "方向一：Agentic AI 原生开发",
        "student_id": "请填写学号",
        "student_name": "请填写姓名",
        "major": "请填写专业",
        "advisor": "戚欣",
        "submit_date": "2026 年 6 月 22 日",
        "github_repo": "https://github.com/skywalker767/Spec2Vision",
        "demo_url": "待部署：请在部署后替换为真实公网 URL",
    }
    if INFO_JSON.exists():
        import json

        try:
            data = json.loads(INFO_JSON.read_text(encoding="utf-8"))
            defaults.update({k: str(v) for k, v in data.items() if k in defaults})
        except json.JSONDecodeError:
            pass
    return defaults


def _strip_student_info_block(text: str) -> str:
    if BEGIN_MARKER in text and END_MARKER in text:
        start = text.index(BEGIN_MARKER)
        end = text.index(END_MARKER) + len(END_MARKER)
        return text[:start] + text[end:]
    return text


def _find_font() -> Path | None:
    for p in FONT_CANDIDATES:
        if p.exists():
            return p
    return None


def _try_pandoc() -> bool:
    if not shutil.which("pandoc") or not shutil.which("xelatex"):
        return False
    cmd = [
        "pandoc",
        str(MD_PATH),
        "-o",
        str(PDF_PATH),
        "--toc",
        "--toc-depth=3",
        "--number-sections",
        "--pdf-engine=xelatex",
        "-V",
        "CJKmainfont=Microsoft YaHei",
        "-V",
        "geometry:margin=2.5cm",
    ]
    try:
        subprocess.run(cmd, check=True, cwd=ROOT)
        return PDF_PATH.exists() and PDF_PATH.stat().st_size > 5000
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _render_fpdf() -> bool:
    from fpdf import FPDF

    font = _find_font()
    if not font:
        print("No CJK font found", file=sys.stderr)
        return False

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(18, 18, 18)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_font("cjk", "", str(font))
    pdf.set_font("cjk", size=11)

    w = pdf.epw
    info = _load_cover_info()

    # ---- Cover ----
    pdf.add_page()
    pdf.set_font("cjk", size=18)
    pdf.ln(30)
    pdf.multi_cell(w, 10, info["project_name"], align="C")
    pdf.ln(4)
    pdf.set_font("cjk", size=14)
    pdf.multi_cell(w, 9, "CS599 期末大作业报告", align="C")
    pdf.ln(8)
    pdf.set_font("cjk", size=11)
    cover_lines = [
        f"课程名称：{info['course_name']}",
        f"课程代码：{info['course_code']}",
        f"方向：{info['project_direction']}",
        f"学号：{info['student_id']}",
        f"姓名：{info['student_name']}",
        f"专业：{info['major']}",
        f"指导教师：{info['advisor']}",
        f"提交日期：{info['submit_date']}",
        f"GitHub：{info['github_repo']}",
        f"在线 Demo：{info['demo_url']}",
    ]
    for line in cover_lines:
        pdf.cell(0, 9, line, ln=True, align="C")

    # ---- TOC ----
    pdf.add_page()
    pdf.set_font("cjk", size=16)
    pdf.cell(0, 10, "目录", ln=True)
    pdf.set_font("cjk", size=11)
    toc = [
        "摘要",
        "第一章 选题背景与设计思想",
        "第二章 Specs 规格文档",
        "第三章 系统架构与设计",
        "第四章 关键实现与代码展示",
        "第五章 测试与评估",
        "第六章 系统升级与扩展",
        "第七章 课程总结",
        "参考文献与开源引用",
        "附录 A / B / C",
    ]
    for i, item in enumerate(toc, 1):
        pdf.cell(0, 7, f"{i}. {item}", ln=True)

    text = MD_PATH.read_text(encoding="utf-8")
    text = _strip_student_info_block(text)
    body = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
    in_code = False
    code_buf: list[str] = []

    def flush_code():
        nonlocal code_buf
        if not code_buf:
            return
        pdf.set_font("cjk", size=9)
        pdf.set_fill_color(245, 245, 245)
        for cl in code_buf:
            pdf.multi_cell(w, 5, cl, fill=True)
        code_buf = []
        pdf.set_font("cjk", size=11)

    for raw in body.splitlines():
        line = raw.rstrip()
        if line.startswith("```"):
            if in_code:
                in_code = False
                flush_code()
            else:
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue
        if line.startswith("\\newpage"):
            pdf.add_page()
            continue
        if not line or line == "---":
            pdf.ln(3)
            continue
        if line.startswith("# "):
            pdf.add_page()
            pdf.set_font("cjk", size=16)
            title = line[2:].strip()
            if hasattr(pdf, "start_section"):
                pdf.start_section(title, level=0)
            pdf.multi_cell(w, 9, title)
            pdf.set_font("cjk", size=11)
            continue
        if line.startswith("## "):
            pdf.ln(2)
            pdf.set_font("cjk", size=13)
            sub = line[3:].strip()
            if hasattr(pdf, "start_section"):
                pdf.start_section(sub, level=1)
            pdf.multi_cell(w, 8, sub)
            pdf.set_font("cjk", size=11)
            continue
        if line.startswith("### "):
            pdf.ln(1)
            pdf.set_font("cjk", size=12)
            pdf.multi_cell(w, 7, line[4:].strip())
            pdf.set_font("cjk", size=11)
            continue
        m = re.match(r"!\[(.*?)\]\((images/[^)]+)\)", line)
        if m:
            cap, rel = m.group(1), m.group(2)
            img = (MD_PATH.parent / rel).resolve()
            if img.exists():
                pdf.ln(3)
                try:
                    pdf.image(str(img), w=170)
                except Exception as exc:
                    pdf.multi_cell(w, 6, f"[图片加载失败: {img.name} {exc}]")
                pdf.set_x(pdf.l_margin)
                pdf.ln(2)
                pdf.set_font("cjk", size=9)
                pdf.multi_cell(w, 5, cap, align="C")
                pdf.set_font("cjk", size=11)
            continue
        if line.startswith("*图 ") and line.endswith("*"):
            pdf.set_font("cjk", size=9)
            pdf.multi_cell(w, 5, line.strip("*"), align="C")
            pdf.set_font("cjk", size=11)
            continue
        if line.startswith("|") and "---" not in line:
            pdf.set_font("cjk", size=9)
            pdf.multi_cell(w, 5, line.replace("|", "  "))
            pdf.set_font("cjk", size=11)
            continue
        if line.startswith(">"):
            pdf.set_font("cjk", size=10)
            pdf.multi_cell(w, 6, line.lstrip("> ").strip())
            pdf.set_font("cjk", size=11)
            continue
        clean = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
        clean = re.sub(r"`([^`]+)`", r"\1", clean)
        if not clean.strip():
            continue
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(w, 6, clean)

    pdf.output(str(PDF_PATH))
    return PDF_PATH.exists() and PDF_PATH.stat().st_size > 20000


def main() -> int:
    if not MD_PATH.exists():
        print(f"Missing {MD_PATH}", file=sys.stderr)
        return 1
    print("Generating PDF from", MD_PATH)
    if _try_pandoc():
        print("PDF created via pandoc+xelatex:", PDF_PATH)
        return 0
    print("Using fpdf2 (pandoc/xelatex not available)...")
    if _render_fpdf():
        print("PDF created via fpdf2:", PDF_PATH)
        print(f"Size: {PDF_PATH.stat().st_size // 1024} KB")
        return 0
    print("PDF generation failed.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
