"""Home — Netflix-style hero landing page."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from components import nav, ui
from components.kpi import kpi_grid
from components.lottie_loader import render as lottie
from core.config import Colors
from core.data_loader import clean_data, melt_genres

_FEATURES = [
    {
        "icon": "📊", "title": "Interactive Analytics", "page": "Dashboard",
        "desc": "KPI counters, drill-down charts and a full catalogue explorer with global filters.",
    },
    {
        "icon": "💡", "title": "Insight Generator", "page": "Insights",
        "desc": "Rule-based business findings with confidence scores — strategy memos in seconds.",
    },
    {
        "icon": "🗄️", "title": "SQL Console", "page": "SQL Console",
        "desc": "Query the catalogue with live DuckDB — ship 10 example queries to copy.",
    },
    {
        "icon": "🧹", "title": "Data Cleaning", "page": "Data Cleaning",
        "desc": "An auditable 8-step pipeline with before/after metrics and export.",
    },
    {
        "icon": "📈", "title": "Power BI Gallery", "page": "Power BI",
        "desc": "Report-style dashboards with exportable PNG previews and DAX snippets.",
    },
    {
        "icon": "🌍", "title": "World Map", "page": "World Map",
        "desc": "Choropleth geography of production, momentum and market concentration.",
    },
    {
        "icon": "🎬", "title": "Data Story", "page": "Story",
        "desc": "A guided narrative on the decade of streaming, decade by decade.",
    },
    {
        "icon": "👤", "title": "About Me", "page": "About",
        "desc": "The analyst behind the build — skills, timeline and links.",
    },
]


def _feature_cards() -> None:
    for i in range(0, len(_FEATURES), 4):
        cols = st.columns(4, gap="medium")
        for j, feat in enumerate(_FEATURES[i:i + 4]):
            with cols[j]:
                ui.glass(f"""
                <div style="display:flex;flex-direction:column;height:100%">
                  <div style="font-size:2rem">{feat['icon']}</div>
                  <div style="font-weight:800;margin:.6rem 0 .3rem;font-size:1.02rem">{feat['title']}</div>
                  <div style="color:var(--n-muted);font-size:.84rem;line-height:1.55;flex:1">{feat['desc']}</div>
                </div>
                """, grow=True)
                if st.button(f"Open → {feat['title']}", key=f"home-{i + j}", width="stretch"):
                    nav.go(feat["page"])
        st.markdown('<div style="height:1.1rem"></div>', unsafe_allow_html=True)


def render() -> None:
    df = clean_data()
    long = melt_genres(df)

    col_l, col_r = st.columns([3.4, 1], gap="large")
    with col_l:
        ui.hero(
            title="Netflix Content",
            accent="Intelligence",
            subtitle=(
                "A premium analytics suite over 8,800+ titles — global filters, business insight "
                "generation, a live SQL console, an audited cleaning pipeline and cinematic storytelling. "
                "Streaming data, engineered for decision makers."
            ),
            eyebrow="Premium Data Product · 2026 Edition",
        )
        c1, c2, c3, c4 = st.columns(4, gap="medium")
        with c1:
            if st.button("🚀 Explore Dashboard", key="cta-dash", width="stretch"):
                nav.go("Dashboard")
        with c2:
            if st.button("💡 Generate Insights", key="cta-ins", width="stretch"):
                nav.go("Insights")
        with c3:
            if st.button("🗄️ Open SQL Console", key="cta-sql", width="stretch"):
                nav.go("SQL Console")
        with c4:
            if st.button("🎬 Read the Story", key="cta-story", width="stretch"):
                nav.go("Story")

    with col_r:
        ui.glass(f"""
        <div style="text-align:center;padding:.4rem">
          <div style="font-weight:700;letter-spacing:.08em;font-size:.72rem;color:var(--n-muted);margin-bottom:.2rem">WATCH THE DATA</div>
        </div>
        """)
        lottie("pulse_play", height=190, width=190, key="hero-lottie")
        ui.glass(f"""
        <div style="text-align:center;color:var(--n-muted);font-size:.8rem;line-height:1.6">
          Streamlit · Plotly · DuckDB<br>
          <span class="pill gold">Production ready</span> <span class="pill green">Offline Lottie</span>
        </div>
        """, pad=False)

    st.markdown('<div style="height:.6rem"></div>', unsafe_allow_html=True)
    ui.section_header("📌", "The Catalogue at a Glance", "Live numbers from the cleaned 8,807-row dataset")
    kpi_grid([
        {"label": "Total Titles", "value": float(len(df)), "icon": "🎞️", "color": Colors.RED, "foot": "after dedupe"},
        {"label": "Movies", "value": float((df["type"] == "Movie").sum()), "icon": "🎬", "color": Colors.GOLD},
        {"label": "TV Shows", "value": float((df["type"] == "TV Show").sum()), "icon": "📺", "color": Colors.BLUE},
        {"label": "Producing Countries", "value": float(df["primary_country"].replace("Not Available", pd.NA).dropna().nunique()), "icon": "🌍", "color": Colors.GREEN},
        {"label": "Genres", "value": float(long["genre"].nunique()), "icon": "🏷️", "color": Colors.PURPLE},
        {"label": "Earliest Title", "value": 1925, "icon": "🕰️", "color": Colors.CYAN, "foot": "release year"},
    ])

    ui.section_header("🧭", "Explore the Platform", "Eight specialised workbenches, one premium shell")
    _feature_cards()

    ui.glass(f"""
    <div style="display:flex;flex-wrap:wrap;gap:1.2rem;align-items:center;justify-content:space-between">
      <div>
        <div style="font-weight:800;font-size:1.15rem">Ready to go deeper?</div>
        <div style="color:var(--n-muted);font-size:.88rem;margin-top:.2rem">
          Jump into the analytics or read the story behind the numbers.
        </div>
      </div>
    </div>
    """, pad=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("📊 Open Dashboard", key="cta-dash2", width="stretch"):
            nav.go("Dashboard")
    with c2:
        if st.button("🌍 Open World Map", key="cta-map2", width="stretch"):
            nav.go("World Map")

    ui.footer()
