"""World Map — choropleth of production footprint with country drill-down."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from components import charts, ui
from core import filters
from core.config import Colors
from core.data_loader import clean_data
from core.geocode import iso3


def render() -> None:
    df = clean_data()
    ui.section_header("🌍", "World Map", "Where the catalogue is produced — and where it's heading")

    d = filters.apply(df)
    if len(d) == 0:
        ui.info_banner("⚠️", "No titles match the current filters.", tone="gold")
        ui.footer()
        return

    c1, c2, c3 = st.columns([1.2, 1, 1], gap="large")
    with c1:
        min_titles = st.slider("Minimum titles to shade", 0, 50, 5)
    with c2:
        top_n = st.slider("Top N for ranking", 5, 30, 15)
    with c3:
        st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)
        if st.button("↺ Reset filters", width="stretch"):
            for k in ["f_types", "f_ratings", "f_years", "f_countries", "f_genres"]:
                st.session_state.pop(k, None)
            st.rerun()

    country_counts = d["primary_country"].replace("Not Available", pd.NA).dropna().value_counts()
    country_counts = country_counts[country_counts >= min_titles]
    map_df = pd.DataFrame({"country": country_counts.index, "titles": country_counts.values})
    map_df["iso"] = map_df["country"].map(iso3)
    map_df = map_df[map_df["iso"].notna()]

    charts.show(charts.choropleth(map_df, "Global Production Footprint"), height=500)

    c1, c2 = st.columns(2, gap="large")
    with c1:
        top = country_counts.head(top_n).reset_index()
        top.columns = ["label", "value"]
        charts.show(charts.horizontal_bar(top, f"Top {top_n} Producing Countries",
                                          color=Colors.GOLD), height=420)
    with c2:
        agg = (d[d["year_added"].notna()]
               .groupby("primary_country")
               .agg(titles=("show_id", "count"), newest=("release_year", "max"))
               .reset_index()
               .query("titles >= 5"))
        charts.show(charts.bubble(
            agg,
            x="titles", y="newest", size="titles", color="titles",
            text="primary_country", title="Production Scale vs Recency",
        ), height=420)

    ui.section_header("🧭", "Country Drill-Down", "Pick a market and inspect its slate")
    c1, c2 = st.columns([1.2, 1], gap="large")
    with c1:
        choices = list(country_counts.index)
        country = st.selectbox("Country", choices)
    with c2:
        st.markdown('<div style="height:30px"></div>', unsafe_allow_html=True)
        how = st.selectbox("Show", ["Genre mix", "Rating mix", "Top titles"])

    sub = d[d["primary_country"] == country]
    st.markdown(f"""
    <div style="display:flex;gap:.7rem;flex-wrap:wrap;margin-bottom:.8rem">
      <span class="pill red">🌍 {country}</span>
      <span class="pill blue">🎞️ {len(sub):,} titles</span>
      <span class="pill green">📆 {int(sub['release_year'].min())}–{int(sub['release_year'].max())}</span>
      <span class="pill gold">🏷️ {sub['listed_in'].replace('Not Available', pd.NA).dropna().str.split(', ').explode().nunique()} genres</span>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="large")
    with c1:
        if how == "Genre mix":
            g = sub["listed_in"].replace("Not Available", pd.NA).dropna().str.split(", ").explode().value_counts().head(12)
            g = g.reset_index(); g.columns = ["label", "value"]
            charts.show(charts.horizontal_bar(g, "Genres", color=Colors.RED), height=380)
        elif how == "Rating mix":
            r = sub["rating"].replace("Not Available", pd.NA).dropna().value_counts().head(10)
            r = r.reset_index(); r.columns = ["label", "value"]
            charts.show(charts.vertical_bar(r, "Ratings", color=Colors.GOLD), height=380)
        else:
            st.caption("Flagship titles from this market")
            view = sub.nlargest(8, "release_year")[["title", "type", "release_year", "rating", "duration"]]
            for _, r in view.iterrows():
                st.markdown(f"""
                <div class="result-card">
                  <div class="rc-poster">{'🎬' if r['type'] == 'Movie' else '📺'}</div>
                  <div style="flex:1">
                    <div class="rc-title">{r['title']}</div>
                    <div class="rc-meta">{r['release_year']} · {r['rating']} · {r['duration']}</div>
                  </div>
                </div>""", unsafe_allow_html=True)
    with c2:
        growth = sub[sub["year_added"].notna()].groupby("year_added")["show_id"].count().reset_index()
        growth.columns = ["label", "value"]
        charts.show(charts.line_area(growth, "Additions over time", "label", "value",
                                     color=Colors.BLUE, height=380))

    ui.footer()
