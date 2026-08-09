"""About — the analyst behind the build."""
from __future__ import annotations

import html

import streamlit as st

from components import ui
from components.lottie_loader import render as lottie

SKILLS = [
    ("Data Engineering", 92),
    ("Python / Pandas", 95),
    ("SQL / DuckDB", 88),
    ("Data Visualisation", 90),
    ("Streamlit Apps", 86),
    ("BI & Reporting", 82),
]

_TIMELINE = [
    ("2019", "First dataset", "Cleaned my first messy CSV and never looked back."),
    ("2021", "Analytics engineer", "Building pipelines, dashboards and data products."),
    ("2023", "BI lead", "Shipping Power BI reports and DAX models end to end."),
    ("2026", "This dashboard", "A premium Streamlit product over the Netflix catalogue."),
]

_STACK = [
    ("Python", "red"), ("Pandas", "blue"), ("Plotly", "green"), ("DuckDB", "gold"),
    ("Streamlit", "red"), ("Power BI", "gold"), ("NumPy", "blue"), ("HTML/CSS", "purple"),
    ("Git", "cyan"), ("Kaleido", "green"),
]

_CONTACTS = [
    ("✉️", "Email", "data@netflix-analytics.dev", "mailto:data@netflix-analytics.dev"),
    ("💼", "LinkedIn", "in/analytics-builder", "https://linkedin.com/in/analytics-builder"),
    ("🐙", "GitHub", "@analytics-builder", "https://github.com/analytics-builder"),
    ("📄", "Portfolio", "netflix-analytics.dev", "https://netflix-analytics.dev"),
]


def _skill_bars() -> str:
    bars = ""
    for name, pct in SKILLS:
        bars += f"""
        <div class="skill">
          <div class="sk-head"><span>{html.escape(name)}</span><span>{pct}%</span></div>
          <div class="sk-track"><span class="sk-fill" style="--w:{pct}%"></span></div>
        </div>"""
    return bars


def render() -> None:
    ui.section_header("👤", "About Me", "The analyst who built this product")

    c1, c2 = st.columns([1, 1.7], gap="large")
    with c1:
        ui.glass(f"""
        <div style="display:flex;flex-direction:column;align-items:center;padding:1.6rem 1rem;text-align:center">
          <div style="width:120px;height:120px;border-radius:50%;display:grid;place-items:center;
            font-family:var(--n-font-display);font-size:3.4rem;color:#fff;
            background:linear-gradient(135deg,#E50914,#7a0409);
            box-shadow:0 0 0 5px rgba(229,9,20,.25),0 18px 50px rgba(229,9,20,.4)">N</div>
          <div style="font-size:1.3rem;font-weight:800;margin-top:1rem">Netflix Data Analyst</div>
          <div style="color:var(--n-muted);font-size:.86rem;margin-top:.2rem">Analytics · Engineering · Storytelling</div>
          <div style="margin-top:.8rem">
            <span class="pill red">Streamlit</span> <span class="pill gold">Plotly</span> <span class="pill blue">DuckDB</span>
          </div>
          <div style="margin-top:1rem;color:var(--n-muted);font-size:.84rem;line-height:1.7">
            I turn raw catalogues into decisions. This dashboard is a live demonstration of the full
            analytics stack — cleaning, querying, visualising and narrating a dataset end to end.
          </div>
        </div>
        """)
        lottie("heart", height=130, width=130, key="about-heart")
        st.caption("Animated with hand-built offline Lottie JSON")

    with c2:
        ui.glass(f"""
        <div style="padding:1.3rem">
          <div style="font-weight:800;font-size:1.1rem;margin-bottom:1rem">⚡ Core Skills</div>
          {_skill_bars()}
        </div>
        """)
        st.markdown('<div style="height:.6rem"></div>', unsafe_allow_html=True)
        ui.glass(f"""
        <div style="padding:1.3rem">
          <div style="font-weight:800;font-size:1.1rem;margin-bottom:.8rem">🛠️ Tech Stack</div>
          <div style="display:flex;flex-wrap:wrap;gap:.5rem">
            {''.join(ui.pill(name, tone) for name, tone in _STACK)}
          </div>
        </div>
        """)

    ui.section_header("🕰️", "Career Timeline", "From first CSV to production data products")
    tl = "".join(
        f'<div class="tl-item"><div class="tl-date">{y}</div><div class="tl-title">{t}</div>'
        f'<div class="tl-text">{d}</div></div>'
        for y, t, d in _TIMELINE
    )
    st.markdown(f'<div class="timeline glass pad">{tl}</div>', unsafe_allow_html=True)

    ui.section_header("📬", "Get in Touch", "Let's build something with data")
    cols = st.columns(4, gap="medium")
    for i, (icon, label, value, href) in enumerate(_CONTACTS):
        with cols[i]:
            ui.glass(f"""
            <div style="text-align:center;padding:.8rem .4rem">
              <div style="font-size:1.8rem">{icon}</div>
              <div style="font-weight:800;margin-top:.4rem">{html.escape(label)}</div>
              <div style="color:var(--n-muted);font-size:.76rem;margin-top:.2rem;word-break:break-all">{html.escape(value)}</div>
              <a href="{href}" target="_blank" class="btn btn-ghost" style="margin-top:.7rem;padding:.4rem .9rem;font-size:.78rem">Open ↗</a>
            </div>
            """, grow=True)

    ui.footer()
