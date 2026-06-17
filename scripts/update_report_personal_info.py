#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Update the personal information block in docs/CS599_大作业报告.md.

This script only replaces the content between:

<!-- STUDENT_INFO_BEGIN -->
...
<!-- STUDENT_INFO_END -->

It does not regenerate or rewrite the full report body.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_MD = ROOT / "docs" / "CS599_大作业报告.md"
INFO_JSON = ROOT / "docs" / "student_info.json"

BEGIN_MARKER = "<!-- STUDENT_INFO_BEGIN -->"
END_MARKER = "<!-- STUDENT_INFO_END -->"


DEFAULT_INFO: dict[str, str] = {
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


def ensure_info_template() -> None:
    """Create docs/student_info.json if it does not exist."""
    INFO_JSON.parent.mkdir(parents=True, exist_ok=True)

    if INFO_JSON.exists():
        return

    INFO_JSON.write_text(
        json.dumps(DEFAULT_INFO, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"[INFO] Created template: {INFO_JSON}")
    print("[NEXT] Please edit docs/student_info.json, then run this script again.")


def load_info() -> dict[str, Any]:
    """Load student info from JSON."""
    ensure_info_template()

    try:
        data = json.loads(INFO_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"[ERROR] Invalid JSON in {INFO_JSON}: {exc}") from exc

    missing = [key for key in DEFAULT_INFO if key not in data]
    if missing:
        raise SystemExit(
            "[ERROR] Missing required fields in docs/student_info.json: "
            + ", ".join(missing)
        )

    return data


def render_student_info_block(info: dict[str, Any]) -> str:
    """Render the replaceable cover/personal information block."""
    return f"""{BEGIN_MARKER}

# {info["project_name"]}

## CS599 期末大作业报告

| 字段 | 内容 |
|---|---|
| 课程名称 | {info["course_name"]} |
| 课程代码 | {info["course_code"]} |
| 项目名称 | {info["project_name"]} |
| 方向 | {info["project_direction"]} |
| 学号 | {info["student_id"]} |
| 姓名 | {info["student_name"]} |
| 专业 | {info["major"]} |
| 指导教师 | {info["advisor"]} |
| 提交日期 | {info["submit_date"]} |
| GitHub 仓库 | {info["github_repo"]} |
| 在线 Demo | {info["demo_url"]} |

\\newpage

{END_MARKER}"""


def update_report(info: dict[str, Any]) -> None:
    """Replace only the marked personal info block in the Markdown report."""
    if not REPORT_MD.exists():
        raise SystemExit(
            f"[ERROR] Report source not found: {REPORT_MD}\n"
            "Please generate docs/CS599_大作业报告.md first."
        )

    text = REPORT_MD.read_text(encoding="utf-8")

    if BEGIN_MARKER not in text or END_MARKER not in text:
        raise SystemExit(
            "[ERROR] Could not find personal info markers in report.\n"
            f"Please add both markers to {REPORT_MD}:\n"
            f"{BEGIN_MARKER}\n...\n{END_MARKER}"
        )

    start = text.index(BEGIN_MARKER)
    end = text.index(END_MARKER) + len(END_MARKER)

    new_block = render_student_info_block(info)
    updated = text[:start] + new_block + text[end:]

    REPORT_MD.write_text(updated, encoding="utf-8")
    print(f"[OK] Updated personal information block in {REPORT_MD}")


def build_pdf() -> None:
    """Build PDF using Pandoc and XeLaTeX."""
    pandoc = shutil.which("pandoc")
    if pandoc is None:
        raise SystemExit(
            "[ERROR] pandoc not found. Please install Pandoc first.\n"
            "macOS: brew install pandoc\n"
            "Ubuntu: sudo apt install pandoc\n"
            "Windows: install from https://pandoc.org/installing.html"
        )

    xelatex = shutil.which("xelatex")
    if xelatex is None:
        raise SystemExit(
            "[ERROR] xelatex not found. Please install TeX Live or MiKTeX.\n"
            "Ubuntu: sudo apt install texlive-xetex texlive-lang-chinese\n"
            "macOS: brew install --cask mactex\n"
            "Windows: install MiKTeX or TeX Live"
        )

    output_pdf = ROOT / "docs" / "CS599_大作业报告.pdf"

    cmd = [
        pandoc,
        str(REPORT_MD),
        "-o",
        str(output_pdf),
        "--toc",
        "--toc-depth=3",
        "--number-sections",
        "--pdf-engine=xelatex",
        "-V",
        "CJKmainfont=Noto Serif CJK SC",
        "-V",
        "geometry:margin=2.5cm",
    ]

    print("[INFO] Building PDF...")
    print("[CMD] " + " ".join(cmd))

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"[ERROR] PDF build failed with exit code {exc.returncode}") from exc

    print(f"[OK] PDF generated: {output_pdf}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update the personal information block in the CS599 final report."
    )
    parser.add_argument(
        "--build-pdf",
        action="store_true",
        help="Rebuild docs/CS599_大作业报告.pdf after updating personal info.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    info = load_info()

    update_report(info)

    if args.build_pdf:
        build_pdf()
    else:
        print("[NEXT] To rebuild the PDF, run:")
        print("       python scripts/update_report_personal_info.py --build-pdf")
        print("   or: python scripts/generate_report_pdf.py  (fpdf2 fallback if no pandoc)")


if __name__ == "__main__":
    main()
