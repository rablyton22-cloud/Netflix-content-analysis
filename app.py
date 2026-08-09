"""Netflix Content Analysis Dashboard — premium Streamlit application.

Run:  streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Netflix Content Analysis",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

from components import nav, ui
from components.style import inject
from core import filters
from core.config import BRAND, BRAND_TAGLINE, PAGES
from core.data_loader import clean_data

inject()
nav.sync()  # apply any pending navigation target before the sidebar renders

# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown(f"""
    <div class="side-brand">
      <span class="n-logo">N</span>
      <div class="side-title">Netflix Content <small>ANALYSIS · {BRAND_TAGLINE}</small></div>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    options = [name for name, _icon, _d in PAGES]
    icons = {name: icon for name, icon, _d in PAGES}

    selected = st.radio(
        "Navigate",
        options,
        key=nav.NAV_KEY,
        label_visibility="collapsed",
        format_func=lambda name: f"{icons[name]}  {name}",
    )

    if selected in {"Dashboard", "Insights", "Power BI", "World Map"}:
        filters.render(clean_data())

    st.markdown(f"""
    <hr>
    <div style="color:var(--n-muted);font-size:.72rem;line-height:1.6;padding:.2rem .2rem">
      <span class="pill green">● LIVE</span>&nbsp; {BRAND}<br>
      v1.0 · Streamlit {st.__version__}
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------ routing
from pages import about, dashboard, data_cleaning, home, insights, powerbi, sql_viewer, storytelling, world_map

PAGES_MAP = {
    "Home": home.render,
    "Dashboard": dashboard.render,
    "Insights": insights.render,
    "SQL Console": sql_viewer.render,
    "Data Cleaning": data_cleaning.render,
    "Power BI": powerbi.render,
    "World Map": world_map.render,
    "Story": storytelling.render,
    "About": about.render,
}

try:
    PAGES_MAP[selected]()
except Exception as e:  # keep the shell premium even when a page errors
    ui.info_banner("⚠️", f"Something went wrong rendering this page: {type(e).__name__} — {e}", tone="gold")
