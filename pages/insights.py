"""Insights — business insight generator with confidence scoring."""
from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from components import charts, ui
from core import filters
from core.config import Colors
from core.data_loader import clean_data
from core.insights import DIRECTIONS, FOCUS_AREAS, executive_summary, generate_insights


def _insight_card(i) -> str:
    tone = {"up": "green", "down": "red", "flat": "gold"}[i.direction]
    tags = "".join(ui.pill(t, tone) for t in i.tags)
    return f"""
    <div class="insight-card glass pad grow">
      <div class="ic-top">
        <div>
          <div style="display:flex;gap:.6rem;align-items:center">
            <span style="font-size:1.5rem">{i.icon}</span>
            <h3 class="ic-title">{html.escape(i.title)}</h3>
          </div>
          <div style="display:flex;gap:.5rem;margin-top:.45rem;flex-wrap:wrap">{tags}</div>
        </div>
        <span class="pill {tone}">{DIRECTIONS[i.direction]} {i.direction.title()}</span>
      </div>
      <div class="ic-body">{html.escape(i.body)}</div>
      <div class="conf-meter"><span style="width:{i.confidence * 100:.0f}%"></span></div>
      <div class="conf-tag"><span>confidence</span><span><b>{i.confidence * 100:.0f}%</b> · {i.metric}: {html.escape(i.value)}</span></div>
    </div>
    """


def render() -> None:
    df = clean_data()
    ui.section_header("💡", "Business Insight Generator",
                      "Rule-based analytics that translate the catalogue into executive findings")

    c1, c2, c3 = st.columns([1.4, 1, 1], gap="large")
    with c1:
        focus = st.selectbox("Analysis focus", FOCUS_AREAS)
    with c2:
        k = st.slider("Number of insights", 2, 6, 4)
    with c3:
        st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)
        run = st.button("⚡ Generate insights", width="stretch", type="primary")

    d = filters.apply(df)
    if len(d) < 10:
        ui.info_banner("⚠️", "Your filters leave fewer than 10 titles — widen them for meaningful insights.")
        ui.footer()
        return

    st.markdown("---")
    ui.section_header("🧠", "Findings", f"Generated for “{focus}” · {len(d):,} titles in scope")

    if run or f"insights-{focus}" not in st.session_state or st.session_state.get("insights-focus") != focus:
        with st.spinner("Running detectors…"):
            st.session_state["insights-focus"] = focus
            st.session_state[f"insights-{focus}"] = generate_insights(d, focus, top_k=k)
            st.session_state["last-run"] = True
    else:
        st.caption("Stale results — press ⚡ Generate to refresh with the current filters.")

    insights = st.session_state.get(f"insights-{focus}", [])
    if not insights:
        ui.info_banner("📭", "No insights could be produced for this scope.", tone="gold")
        ui.footer()
        return

    for i in insights:
        st.markdown(_insight_card(i), unsafe_allow_html=True)

    ui.section_header("📝", "Executive Briefing", "One-paragraph summary ready for a slide deck")
    summary = executive_summary(insights)
    st.markdown(ui.glass(f'<div class="quote" style="margin:0">{html.escape(summary)}</div>'), unsafe_allow_html=True)

    ui.section_header("📈", "Supporting Signals", "Raw evidence behind the findings")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        growth = d[d["year_added"].notna()].groupby("year_added")["show_id"].count().reset_index()
        growth.columns = ["label", "value"]
        charts.show(charts.line_area(growth, "Additions over time", "label", "value",
                                     color=Colors.RED, height=300))
    with c2:
        topc = d["primary_country"].replace("Not Available", pd.NA).dropna().value_counts().head(10).reset_index()
        topc.columns = ["label", "value"]
        charts.show(charts.horizontal_bar(topc, "Top markets", color=Colors.GOLD, height=300))

    txt = "\n\n".join(f"{i.icon} {i.title} [{i.confidence * 100:.0f}%]\n{i.body}\nMetric: {i.metric} = {i.value}"
                      for i in insights)
    st.download_button("⬇ Export briefing (.txt)", f"{summary}\n\n---\n\n{txt}".encode(),
                       file_name="netflix_briefing.txt", mime="text/plain")

    ui.footer()
