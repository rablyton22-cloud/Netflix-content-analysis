"""Data Cleaning — auditable pipeline explorer with before/after metrics."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components import charts, ui
from core.config import Colors
from core.data_loader import _CLEANING_STEPS, clean_data, cleaning_report, load_raw, quality_score


def _missing_heatmap(df: pd.DataFrame, title: str) -> None:
    cols = df.columns.tolist()
    miss = df.isna().to_numpy()
    fig = go.Figure(go.Heatmap(
        z=miss.astype(int), x=cols, y=list(range(len(df))),
        colorscale=[[0, "#141420"], [1, Colors.RED]],
        showscale=False, ygap=0.4,
        hovertemplate="<b>%{y}</b> · %{x}<br>%{z} → missing<extra></extra>",
    ))
    fig.update_layout(title=dict(text=title, font=dict(size=15, color=Colors.TEXT)),
                      height=300, margin=dict(l=0, r=0, t=44, b=0),
                      xaxis=dict(tickangle=-45, nticks=20))
    st.plotly_chart(fig, width="stretch")


def render() -> None:
    raw = load_raw()
    clean = clean_data()
    report = cleaning_report()

    ui.section_header("🧹", "Data Cleaning Pipeline",
                      "Eight auditable steps that turn the raw CSV into an analytics-grade table")

    score = quality_score(clean)
    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1], gap="medium")
    ui.show_kpis([
        {"label": "Rows", "value": float(len(clean)), "icon": "🧾", "color": Colors.RED},
        {"label": "Columns", "value": float(clean.shape[1]), "icon": "🗂️", "color": Colors.BLUE},
        {"label": "Missing values", "value": float(int(clean.isna().sum().sum())), "icon": "🕳️",
         "color": Colors.GOLD, "foot": "down from " + str(int(raw.isna().sum().sum()))},
        {"label": "Duplicates", "value": float(int(clean.duplicated().sum())), "icon": "♻️",
         "color": Colors.GREEN},
    ])
    charts.show(charts.gauge(score, "Data Quality Score", max_val=100), height=250)

    tab_steps, tab_missing, tab_diff = st.tabs(["🔬 Step-by-step", "🕳️ Missing data", "📏 Before → After"])

    with tab_steps:
        st.markdown("### The pipeline")
        for i, step in enumerate(_CLEANING_STEPS):
            row = report.iloc[i]
            st.markdown(f"""
            <div class="glass pad grow">
              <div style="display:flex;gap:1rem;align-items:flex-start">
                <div class="chapter-num" style="font-size:2.6rem">{i + 1:02d}</div>
                <div style="flex:1">
                  <div style="display:flex;align-items:center;gap:.7rem;flex-wrap:wrap">
                    <b style="font-size:1.05rem">{step['title']}</b>
                    <span class="pill green">rows {int(row['rows_before'])} → {int(row['rows_after'])}</span>
                    <span class="pill red">missing {int(row['missing_before'])} → {int(row['missing_after'])}</span>
                  </div>
                  <p style="color:var(--n-muted);font-size:.88rem;margin:.45rem 0">{step['desc']}</p>
                  <div style="margin:.3rem 0"><span class="pill cyan">impact: {step['impact']}</span></div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)
            st.code(step["code"], language="python")
            st.markdown('<div style="height:.6rem"></div>', unsafe_allow_html=True)

    with tab_missing:
        st.markdown("### Missing values — raw vs cleaned")
        c1, c2 = st.columns(2, gap="large")
        with c1:
            _missing_heatmap(raw, "Raw CSV")
        with c2:
            _missing_heatmap(clean, "After cleaning")
        st.caption("Red cells = missing. Post-pipeline gaps remain only in numeric fields that genuinely "
                   "don't exist (runtime for some shows, add-date for legacy titles).")

    with tab_diff:
        st.markdown("### Metrics per step")
        st.dataframe(report, width="stretch", height=340)
        st.markdown("### Side-by-side preview")
        cc1, cc2 = st.columns(2, gap="large")
        with cc1:
            st.caption("Raw (first 5 rows)")
            st.dataframe(raw.head(5), width="stretch", height=220)
        with cc2:
            st.caption("Cleaned (first 5 rows)")
            st.dataframe(clean.head(5), width="stretch", height=220)

    st.markdown("---")
    ui.section_header("📦", "Exports", "Take the pipeline elsewhere")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.download_button("⬇ Cleaned catalogue (.csv)",
                           clean.to_csv(index=False).encode(), file_name="netflix_clean.csv",
                           mime="text/csv", width="stretch")
    with c2:
        st.download_button("⬇ Pipeline report (.csv)",
                           report.to_csv(index=False).encode(), file_name="cleaning_report.csv",
                           mime="text/csv", width="stretch")

    ui.footer()
