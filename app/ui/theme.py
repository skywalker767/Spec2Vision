"""Global CSS theme for VisionFlow Streamlit UI."""

from __future__ import annotations

import streamlit as st

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', system-ui, sans-serif;
}

/* Hide default Streamlit chrome noise */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}

/* Hero */
.vf-hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 45%, #312e81 100%);
    border-radius: 20px;
    padding: 2rem 2.2rem;
    margin-bottom: 1.5rem;
    color: #f8fafc;
    box-shadow: 0 20px 50px rgba(15, 23, 42, 0.25);
}
.vf-hero h1 {
    font-size: 1.85rem;
    font-weight: 700;
    margin: 0 0 0.35rem 0;
    letter-spacing: -0.02em;
}
.vf-hero p {
    margin: 0;
    opacity: 0.85;
    font-size: 0.95rem;
}

/* Step wizard */
.vf-steps {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.25rem;
    flex-wrap: wrap;
}
.vf-step {
    flex: 1;
    min-width: 120px;
    text-align: center;
    padding: 0.65rem 0.5rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
    background: #f1f5f9;
    color: #64748b;
    border: 2px solid transparent;
    transition: all 0.2s;
}
.vf-step.active {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
}
.vf-step.done {
    background: #ecfdf5;
    color: #059669;
    border-color: #a7f3d0;
}

/* Cards */
.vf-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.25rem 1.4rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.vf-card-accent {
    border-left: 4px solid #6366f1;
}

/* Clarification question cards – always light background for readability */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.vf-q-title) {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 12px !important;
    padding: 0.25rem 0.5rem !important;
}
[data-theme="dark"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.vf-q-title) {
    background: #ffffff !important;
    border-color: #94a3b8 !important;
}

/* Clarification question typography */
.vf-q-badge {
    display: inline-block;
    padding: 0.25rem 0.65rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}
.vf-q-badge.core { background: #dcfce7; color: #166534; }
.vf-q-badge.optional { background: #dbeafe; color: #1e40af; }
.vf-q-badge.llm { background: #f3e8ff; color: #6b21a8; }
.vf-q-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #0f172a !important;
    margin: 0 0 0.35rem 0;
    line-height: 1.45;
}
.vf-q-reason {
    font-size: 0.88rem;
    color: #334155 !important;
    margin: 0 0 0.5rem 0;
    line-height: 1.5;
}

/* Horizontal radio options – high contrast on light cards */
[data-testid="stRadio"] div[role="radiogroup"] {
    gap: 0.5rem !important;
    flex-wrap: wrap !important;
}
[data-testid="stRadio"] label {
    background: #f8fafc !important;
    border: 1.5px solid #64748b !important;
    border-radius: 10px !important;
    padding: 0.5rem 0.9rem !important;
    margin: 0 !important;
    cursor: pointer;
}
[data-testid="stRadio"] label:hover {
    border-color: #4f46e5 !important;
    background: #eef2ff !important;
}
[data-testid="stRadio"] label[data-checked="true"],
[data-testid="stRadio"] label:has(input:checked) {
    background: #4f46e5 !important;
    border-color: #4f46e5 !important;
}
[data-testid="stRadio"] label p,
[data-testid="stRadio"] label span,
[data-testid="stRadio"] label div {
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    color: #0f172a !important;
    margin: 0 !important;
}
[data-testid="stRadio"] label:has(input:checked) p,
[data-testid="stRadio"] label:has(input:checked) span,
[data-testid="stRadio"] label:has(input:checked) div {
    color: #ffffff !important;
}

/* Checkbox options (multi-choice) – same high-contrast treatment */
[data-testid="stCheckbox"] label {
    background: #f8fafc !important;
    border: 1.5px solid #64748b !important;
    border-radius: 10px !important;
    padding: 0.45rem 0.75rem !important;
    margin: 0.15rem 0 !important;
}
[data-testid="stCheckbox"] label p,
[data-testid="stCheckbox"] label span,
[data-testid="stCheckbox"] label div {
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    color: #0f172a !important;
}
[data-testid="stCheckbox"] label:has(input:checked) {
    background: #4f46e5 !important;
    border-color: #4f46e5 !important;
}
[data-testid="stCheckbox"] label:has(input:checked) p,
[data-testid="stCheckbox"] label:has(input:checked) span,
[data-testid="stCheckbox"] label:has(input:checked) div {
    color: #ffffff !important;
}
[data-testid="stCheckbox"] label:has(input:disabled) {
    background: #f1f5f9 !important;
    border-color: #cbd5e1 !important;
    opacity: 0.75;
}
[data-testid="stCheckbox"] label:has(input:disabled) p,
[data-testid="stCheckbox"] label:has(input:disabled) span {
    color: #64748b !important;
}

/* Dark theme: keep clarification cards light; only adjust outer page chrome */
[data-theme="dark"] .vf-q-title { color: #0f172a !important; }
[data-theme="dark"] .vf-q-reason { color: #334155 !important; }
[data-theme="dark"] [data-testid="stRadio"] label {
    background: #f8fafc !important;
    border-color: #64748b !important;
}
[data-theme="dark"] [data-testid="stRadio"] label p,
[data-theme="dark"] [data-testid="stRadio"] label span {
    color: #0f172a !important;
}
[data-theme="dark"] [data-testid="stCheckbox"] label p,
[data-theme="dark"] [data-testid="stCheckbox"] label span {
    color: #0f172a !important;
}

.vf-carousel-dots {
    display: flex;
    justify-content: center;
    gap: 6px;
    margin-top: 1rem;
}
.vf-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #cbd5e1;
}
.vf-dot.active { background: #6366f1; width: 24px; border-radius: 4px; }
.vf-dot.done { background: #34d399; }

/* Result hero image frame */
.vf-result-frame {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    border-radius: 20px;
    padding: 1rem;
    box-shadow: 0 25px 50px rgba(0,0,0,0.15);
}
.vf-score-ring {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 72px;
    height: 72px;
    border-radius: 50%;
    background: conic-gradient(#6366f1 var(--pct), #e2e8f0 0);
    font-weight: 700;
    font-size: 1.1rem;
    color: #0f172a;
}
.vf-metric-pill {
    display: inline-block;
    background: #f1f5f9;
    padding: 0.35rem 0.75rem;
    border-radius: 8px;
    font-size: 0.8rem;
    margin: 0.2rem;
    color: #475569;
}

/* Example chips row */
.vf-chip-hint {
    font-size: 0.8rem;
    color: #94a3b8;
    margin-bottom: 0.5rem;
}
</style>
"""


def inject_theme() -> None:
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def render_hero(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="vf-hero"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def render_steps(current: int, labels: list[str]) -> None:
    """current: 0-based active step index."""
    parts = []
    for i, label in enumerate(labels):
        cls = "vf-step"
        if i < current:
            cls += " done"
        elif i == current:
            cls += " active"
        parts.append(f'<div class="{cls}">{i + 1}. {label}</div>')
    st.markdown(f'<div class="vf-steps">{"".join(parts)}</div>', unsafe_allow_html=True)
