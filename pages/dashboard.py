"""Dashboard — search, KPI counters, filters and interactive charts."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from components import charts, ui
from core import filters
from core.config import Colors
from core.data_loader import clean_data, search_titles


def _render_search(df: pd.DataFrame) -> None:
    st.markdown("### 🔎 Search the Catalogue")
    c1, c2 = st.columns([4, 1], gap="medium")
    with c1:
        query = st.text_input("Search", placeholder="Try: 'Love', 'India', 'Nolan', 'Crime'…",
                              label_visibility="collapsed")
    with c2:
        n_results = st.slider("Max results", 6, 30, 12, 1)

    if query.strip():
        hits = search_titles(df, query, limit=n_results)
        if len(hits) == 0:
            ui.info_banner("😕", f"No titles matched “{query}”. Try a broader term.", tone="gold")
        else:
            st.caption(f"{len(hits)} match(es) for “{query}”")
            for _, r in hits.iterrows():
                is_movie = r["type"] == "Movie"
                meta = (f"{r['release_year']} · {r['rating']} · "
                        f"{r['duration_min']:.0f} min" if is_movie and pd.notna(r['duration_min'])
                        else f"{r['release_year']} · {r['rating']} · {r['duration']}")
                pills = "".join(ui.pill(g.strip(), "red" if i == 0 else "") for i, g in
                                enumerate(r["listed_in"].split(",")[:3]))
                st.markdown(f"""
                <div class="result-card">
                  <div class="rc-poster">{'🎬' if is_movie else '📺'}</div>
                  <div style="flex:1">
                    <div class="rc-title">{r['title']}</div>
                    <div class="rc-meta">{meta} · {r['primary_country']}</div>
                    <div class="rc-desc">{r['description']}</div>
                    <div style="margin-top:.5rem">{pills}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)


def _render_kpis(d: pd.DataFrame) -> None:
    movies = int((d["type"] == "Movie").sum())
    shows = int((d["type"] == "TV Show").sum())
    countries = d["primary_country"].replace("Not Available", pd.NA).dropna().nunique()
    avg_min = d["duration_min"].dropna().mean()
    genre_series = d["listed_in"].replace("Not Available", pd.NA).dropna().str.split(", ").explode()
    top_genre = genre_series.value_counts().idxmax() if len(genre_series) else "—"
    top_genre_n = int(genre_series.value_counts().max()) if len(genre_series) else 0
    ui.show_kpis([
        {"label": "Titles in view", "value": float(len(d)), "icon": "🎞️", "color": Colors.RED,
         "foot": f"{movies} movies · {shows} shows"},
        {"label": "Movies", "value": float(movies), "icon": "🎬", "color": Colors.GOLD, "bar": 78},
        {"label": "TV Shows", "value": float(shows), "icon": "📺", "color": Colors.BLUE, "bar": 45},
        {"label": "Countries", "value": float(countries), "icon": "🌍", "color": Colors.GREEN},
        {"label": "Avg Runtime", "value": float(avg_min) if avg_min == avg_min else 0, "decimals": 0,
         "icon": "⏱️", "color": Colors.PURPLE, "suffix": " min"},
        {"label": "Top Genre", "value": float(top_genre_n), "icon": "🏷️", "color": Colors.CYAN,
         "foot": top_genre},
    ])
    st.caption(f"Filter scope: {len(d):,} titles · refresh with the sidebar filters")


def _render_charts(d: pd.DataFrame) -> None:
    c1, c2 = st.columns(2, gap="large")
    with c1:
        dist = d["type"].value_counts().reset_index()
        dist.columns = ["label", "value"]
        charts.show(charts.donut(dist["label"].tolist(), dist["value"].tolist(),
                                 "Content Mix", hole=0.74), height=340)
    with c2:
        growth = d[d["year_added"].notna()].groupby("year_added")["show_id"].count().reset_index()
        growth.columns = ["label", "value"]
        charts.show(charts.line_area(growth, "Catalogue Growth (year added)",
                                     "label", "value", height=340, filled=True))

    c1, c2 = st.columns(2, gap="large")
    with c1:
        genres = d["listed_in"].replace("Not Available", pd.NA).dropna().str.split(", ").explode()
        g = genres.value_counts().reset_index()
        g.columns = ["label", "value"]
        charts.show(charts.horizontal_bar(g, "Top Genres", color=Colors.RED), height=400)
    with c2:
        ratings = d["rating"].replace("Not Available", pd.NA).dropna().value_counts().reset_index()
        ratings.columns = ["label", "value"]
        charts.show(charts.vertical_bar(ratings.head(10), "Rating Distribution",
                                        color=Colors.GOLD), height=400)

    c1, c2 = st.columns(2, gap="large")
    with c1:
        countries = d["primary_country"].replace("Not Available", pd.NA).dropna().value_counts().reset_index()
        countries.columns = ["label", "value"]
        charts.show(charts.horizontal_bar(countries, "Top Producing Countries",
                                          color=Colors.BLUE), height=400)
    with c2:
        hm = d[d["year_added"].notna()]
        piv = hm.pivot_table(index="year_added", columns="month_added",
                             values="show_id", aggfunc="count", fill_value=0)
        if len(piv):
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            piv = piv.reindex(columns=list(range(1, 13)), fill_value=0)
            charts.show(charts.heatmap(piv.to_numpy(), months, [str(y) for y in piv.index],
                                       "Seasonality of Additions (year × month)", height=420))

    genres = d["listed_in"].replace("Not Available", pd.NA).dropna()
    if len(genres):
        tree = (genres.str.split(", ", expand=True).stack()
                .reset_index(level=1, drop=True).rename("genre")
                .to_frame().join(d[["show_id", "type"]]))
        tree["parent"] = "All Content"
        tree["count"] = 1
        agg = tree.groupby(["parent", "genre"])["count"].sum().reset_index()
        charts.show(charts.treemap(agg, ["parent", "genre"], "count",
                                   "Genre Hierarchy (treemap)"), height=440)


def _render_table(d: pd.DataFrame) -> None:
    cols = ["title", "type", "release_year", "rating", "duration", "primary_country", "listed_in"]
    view = d[cols].sort_values("release_year", ascending=False)
    st.dataframe(view.reset_index(drop=True), width="stretch", height=420)
    csv = view.to_csv(index=False).encode()
    st.download_button("⬇ Download filtered CSV", csv,
                       file_name="netflix_filtered.csv", mime="text/csv")


def render() -> None:
    df = clean_data()
    ui.section_header("📊", "Analytics Dashboard", "Search, filter and explore the full Netflix catalogue")

    _render_search(df)
    st.markdown("---")

    d = filters.apply(df)
    _render_kpis(d)

    tab_over, tab_tbl, tab_raw = st.tabs(["📈 Visualisations", "🗂️ Titles Explorer", "📄 Raw Preview"])
    with tab_over:
        _render_charts(d)
    with tab_tbl:
        _render_table(d)
    with tab_raw:
        st.caption("First 200 rows of the cleaned catalogue (all 30 columns)")
        st.dataframe(d.head(200), width="stretch", height=420)
        st.download_button("⬇ Download cleaned CSV",
                           clean_data().to_csv(index=False).encode(),
                           file_name="netflix_clean.csv", mime="text/csv")

    ui.footer()
