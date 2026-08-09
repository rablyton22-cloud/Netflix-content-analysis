"""Power BI — report-style dashboard gallery with exportable previews."""
from __future__ import annotations

import html

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

from components import charts, ui
from core import filters
from core.config import Colors
from core.data_loader import clean_data

REPORTS = [
    {
        "id": "exec", "icon": "🏛️", "name": "Executive Overview",
        "desc": "C-suite snapshot: mix, momentum and the top markets in one glance.",
        "kpis": [("Total Titles", "🎞️", "titles"), ("Movies", "🎬", "movies"),
                 ("TV Shows", "📺", "shows"), ("Countries", "🌍", "countries")],
        "charts": ["mix", "growth", "countries", "ratings"],
        "dax": (
            "Total Titles = COUNTROWS('netflix')\n"
            "Movie Share = DIVIDE(\n"
            "    CALCULATE(COUNTROWS('netflix'), 'netflix'[type] = \"Movie\"),\n"
            "    COUNTROWS('netflix'))\n"
            "YoY Growth = CALCULATE(\n"
            "    COUNTROWS('netflix'), YEAR('netflix'[date_added]) = YEAR(TODAY()) - 1)\n"
            "    - CALCULATE(COUNTROWS('netflix'), YEAR('netflix'[date_added]) = YEAR(TODAY()) - 2)"
        ),
    },
    {
        "id": "growth", "icon": "🚀", "name": "Catalogue Growth",
        "desc": "How Netflix scaled its library: additions by year, seasonality and velocity.",
        "kpis": [("Peak Year", "📈", "peak_year"), ("Peak Additions", "🎉", "peak_n"),
                 ("Avg / Year", "📅", "avg_year"), ("Seasons Skew", "🍂", "season_skew")],
        "charts": ["growth", "seasonality", "velocity", "decades"],
        "dax": (
            "Additions per Year = SUMMARIZE('netflix',\n"
            "    'netflix'[year_added], \"Titles\", COUNTROWS('netflix'))\n"
            "Peak Year = MAXX(Additions per Year, [Titles])"
        ),
    },
    {
        "id": "genre", "icon": "🎭", "name": "Genre Performance",
        "desc": "Category portfolio: which genres carry the library and which are rising.",
        "kpis": [("Genres", "🏷️", "genres_n"), ("Top Genre", "🥇", "top_genre"),
                 ("Genre Titles", "🎯", "top_genre_n"), ("Rising", "🔥", "rising_genre")],
        "charts": ["treemap", "genres", "momentum", "ratings"],
        "dax": (
            "Genre Table = SELECTCOLUMNS(\n"
            "    GENERATE('netflix', VAR g = 'netflix'[genres]\n"
            "        RETURN SELECTCOLUMNS(g, \"Genre\", [Value])),\n"
            "    \"Genre\", [Genre])\n"
            "Genre Count = COUNTROWS(Genre Table)"
        ),
    },
    {
        "id": "global", "icon": "🌍", "name": "Global Expansion",
        "desc": "Production footprint: who makes the content, and where momentum lives.",
        "kpis": [("Markets", "🌐", "countries"), ("Top Market", "🥇", "top_country"),
                 ("Market Titles", "🎯", "top_country_n"), ("Top-3 Share", "🏢", "top3_share")],
        "charts": ["choropleth", "countries", "multicountry", "expansion"],
        "dax": (
            "Top Market = TOPN(1,\n"
            "    SUMMARIZE('netflix', 'netflix'[primary_country], \"T\", COUNTROWS('netflix')),\n"
            "    [T])\n"
            "Market Share = DIVIDE(COUNTROWS('netflix'),\n"
            "    CALCULATE(COUNTROWS('netflix'), ALL('netflix')))"
        ),
    },
    {
        "id": "audience", "icon": "👥", "name": "Audience & Ratings",
        "desc": "Who is the library built for? Ratings mix, family capacity and maturity.",
        "kpis": [("Adult Share", "🔞", "adult_share"), ("Family Share", "👨‍👩‍👧‍👦", "family_share"),
                 ("Top Rating", "🥇", "top_rating"), ("Runtime Avg", "⏱️", "runtime_avg")],
        "charts": ["ratings", "runtime", "seasons", "ratings_trend"],
        "dax": (
            "Adult Share = DIVIDE(\n"
            "    CALCULATE(COUNTROWS('netflix'), 'netflix'[rating] IN {\"TV-MA\", \"R\", \"NC-17\"}),\n"
            "    COUNTROWS('netflix'))\n"
            "Avg Runtime = AVERAGE('netflix'[duration_min])"
        ),
    },
    {
        "id": "library", "icon": "🏆", "name": "Library Quality",
        "desc": "Vintage depth, decade concentration and the golden era of the slate.",
        "kpis": [("Golden Decade", "🥇", "golden_decade"), ("Decade Titles", "🏆", "golden_n"),
                 ("Classic Share", "🕰️", "classic_share"), ("Newest Year", "🆕", "newest_year")],
        "charts": ["decades", "vintage", "genre_concentration", "countries"],
        "dax": (
            "Golden Decade = MAXX(\n"
            "    SUMMARIZE('netflix', 'netflix'[decade], \"N\", COUNTROWS('netflix')),\n"
            "    [N])\n"
            "Classic Titles = CALCULATE(COUNTROWS('netflix'),\n"
            "    'netflix'[release_year] < 2000)"
        ),
    },
]

_DESCRIPTIONS = {
    "mix": "Content mix by type",
    "growth": "Titles added per year",
    "countries": "Top producing countries",
    "ratings": "Rating distribution",
    "genres": "Top genres",
    "treemap": "Genre hierarchy",
    "momentum": "Genre momentum",
    "seasonality": "Seasonality heatmap",
    "velocity": "Additions with trend",
    "decades": "Titles by decade",
    "runtime": "Runtime histogram",
    "seasons": "Series by season count",
    "ratings_trend": "Rating mix over time",
    "multicountry": "Multi-country productions",
    "expansion": "Market momentum",
    "vintage": "Catalogue by release year",
    "genre_concentration": "Top-5 genre share",
}


def _tile(value: str, label: str, icon: str) -> str:
    return f"""<div class="tile tile-kpi"><div style="color:var(--n-muted);font-size:.68rem;letter-spacing:.08em">{icon} {label}</div><b>{html.escape(value)}</b></div>"""


def _report_kpis(d: pd.DataFrame, kpis: list[tuple[str, str, str]]) -> dict:
    out = {}
    for label, icon, key in kpis:
        if key == "titles":
            out[label] = f"{len(d):,}"
        elif key == "movies":
            out[label] = f"{int((d['type'] == 'Movie').sum()):,}"
        elif key == "shows":
            out[label] = f"{int((d['type'] == 'TV Show').sum()):,}"
        elif key == "countries":
            out[label] = f"{int(d['primary_country'].replace('Not Available', pd.NA).dropna().nunique()):,}"
        elif key == "peak_year":
            s = d[d["year_added"].notna()]["year_added"].value_counts()
            out[label] = f"{int(s.idxmax()) if len(s) else '—'}"
        elif key == "peak_n":
            s = d[d["year_added"].notna()]["year_added"].value_counts()
            out[label] = f"{int(s.max()) if len(s) else '—'}"
        elif key == "avg_year":
            s = d[d["year_added"].notna()]["year_added"].value_counts()
            out[label] = f"{s.mean():.0f}" if len(s) else "—"
        elif key == "season_skew":
            s = d[d["month_added"].notna()]["month_added"].value_counts()
            out[label] = f"Q{int(s.idxmax())}" if len(s) else "—"
        elif key == "genres_n":
            out[label] = f"{d['listed_in'].replace('Not Available', pd.NA).dropna().str.split(', ').explode().nunique():,}"
        elif key == "top_genre":
            out[label] = (d["listed_in"].replace("Not Available", pd.NA).dropna().str.split(", ").explode()
                          .value_counts().idxmax() if len(d) else "—")
        elif key == "top_genre_n":
            out[label] = f"{int(d['listed_in'].replace('Not Available', pd.NA).dropna().str.split(', ').explode().value_counts().max()) if len(d) else '—'}"
        elif key == "rising_genre":
            out[label] = "🔥 Detector"
        elif key == "top_country":
            out[label] = d["primary_country"].replace("Not Available", pd.NA).dropna().value_counts().idxmax() if len(d) else "—"
        elif key == "top_country_n":
            out[label] = f"{int(d['primary_country'].replace('Not Available', pd.NA).dropna().value_counts().max()) if len(d) else '—'}"
        elif key == "top3_share":
            c = d["primary_country"].replace("Not Available", pd.NA).dropna().value_counts()
            out[label] = f"{c.iloc[:3].sum() / len(c) * 100:.0f}%" if len(c) else "—"
        elif key == "adult_share":
            r = d["rating"].replace("Not Available", pd.NA).dropna()
            out[label] = f"{r.isin(['TV-MA', 'R', 'NC-17']).mean() * 100:.0f}%"
        elif key == "family_share":
            r = d["rating"].replace("Not Available", pd.NA).dropna()
            out[label] = f"{r.isin(['TV-Y', 'TV-Y7', 'TV-Y7-FV', 'G', 'PG']).mean() * 100:.0f}%"
        elif key == "top_rating":
            out[label] = d["rating"].replace("Not Available", pd.NA).dropna().value_counts().idxmax() if len(d) else "—"
        elif key == "runtime_avg":
            m = d["duration_min"].dropna().mean()
            out[label] = f"{m:.0f} min" if m == m else "—"
        elif key == "golden_decade":
            s = d.groupby("decade")["show_id"].count()
            out[label] = f"{int(s.idxmax())}s" if len(s) else "—"
        elif key == "golden_n":
            s = d.groupby("decade")["show_id"].count()
            out[label] = f"{int(s.max()) if len(s) else '—'}"
        elif key == "classic_share":
            out[label] = f"{len(d[d['release_year'] < 2000]) / len(d) * 100:.0f}%" if len(d) else "—"
        elif key == "newest_year":
            out[label] = f"{int(d['release_year'].max()) if len(d) else '—'}"
        else:
            out[label] = "—"
    return out


def _build_chart(kind: str, d: pd.DataFrame):
    if kind == "mix":
        v = d["type"].value_counts().reset_index(); v.columns = ["label", "value"]
        return charts.donut(v["label"].tolist(), v["value"].tolist(), "Content Mix")
    if kind == "growth":
        g = d[d["year_added"].notna()].groupby("year_added")["show_id"].count().reset_index()
        g.columns = ["label", "value"]
        return charts.line_area(g, "Titles Added per Year", "label", "value", height=330)
    if kind == "countries":
        c = d["primary_country"].replace("Not Available", pd.NA).dropna().value_counts().head(12).reset_index()
        c.columns = ["label", "value"]
        return charts.horizontal_bar(c, "Top Producing Countries", color=Colors.BLUE, height=330)
    if kind == "ratings":
        r = d["rating"].replace("Not Available", pd.NA).dropna().value_counts().head(10).reset_index()
        r.columns = ["label", "value"]
        return charts.vertical_bar(r, "Rating Distribution", color=Colors.GOLD, height=330)
    if kind == "genres":
        g = d["listed_in"].replace("Not Available", pd.NA).dropna().str.split(", ").explode().value_counts().head(12).reset_index()
        g.columns = ["label", "value"]
        return charts.horizontal_bar(g, "Top Genres", color=Colors.RED, height=330)
    if kind == "treemap":
        g = d["listed_in"].replace("Not Available", pd.NA).dropna().str.split(", ").explode().value_counts().head(20).reset_index()
        g.columns = ["genre", "count"]; g["parent"] = "All"
        return charts.treemap(g[["parent", "genre", "count"]], ["parent", "genre"], "count",
                              "Genre Hierarchy", height=330)
    if kind == "momentum":
        g = d[d["year_added"].notna()].copy()
        parts = []
        for _, r in g.iterrows():
            for gr in r["genres"]:
                parts.append((gr, r["year_added"]))
        m = pd.DataFrame(parts, columns=["genre", "year_added"])
        piv = m.groupby(["genre", "year_added"]).size().unstack(fill_value=0)
        piv = piv[piv.sum(axis=1) >= 5]
        early = piv[[c for c in piv.columns if c <= 2019]].sum(axis=1) if any(c <= 2019 for c in piv.columns) else pd.Series(0, index=piv.index)
        late = piv[[c for c in piv.columns if c > 2019]].sum(axis=1) if any(c > 2019 for c in piv.columns) else pd.Series(0, index=piv.index)
        mom = ((late - early) / early.replace(0, pd.NA)).dropna().sort_values(ascending=False).head(10).reset_index()
        mom.columns = ["label", "value"]
        mom = mom[mom["value"].notna()]
        return charts.horizontal_bar(mom, "Genre Momentum (2018+ vs earlier)", color=Colors.GREEN, height=330)
    if kind == "seasonality":
        d2 = d[d["year_added"].notna()]
        piv = d2.pivot_table(index="year_added", columns="month_added", values="show_id", aggfunc="count", fill_value=0)
        piv = piv.reindex(columns=list(range(1, 13)), fill_value=0)
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return charts.heatmap(piv.to_numpy(), months, [str(y) for y in piv.index], "Additions by Year × Month", height=330)
    if kind == "velocity":
        g = d[d["year_added"].notna()].groupby("year_added")["show_id"].count().reset_index()
        g.columns = ["label", "value"]
        return charts.line_area(g, "Velocity with Trend", "label", "value", height=330)
    if kind == "decades":
        dec = d.groupby("decade")["show_id"].count().reset_index()
        dec.columns = ["label", "value"]
        return charts.vertical_bar(dec, "Titles by Decade", color=Colors.PURPLE, height=330)
    if kind == "runtime":
        m = d["duration_min"].dropna()
        bins = pd.cut(m, bins=15).value_counts().sort_index().reset_index()
        bins.columns = ["label", "value"]
        return charts.vertical_bar(bins, "Runtime Distribution", color=Colors.CYAN, height=330)
    if kind == "seasons":
        s = d[d["type"] == "TV Show"]["duration_seasons"].dropna()
        v = s.value_counts().sort_index().head(12).reset_index()
        v.columns = ["label", "value"]
        return charts.vertical_bar(v, "Series by Season Count", color=Colors.ORANGE, height=330)
    if kind == "ratings_trend":
        d2 = d[d["year_added"].notna()]
        piv = d2.pivot_table(index="year_added", columns="rating", values="show_id", aggfunc="count", fill_value=0)
        keep = [c for c in ["TV-MA", "TV-14", "R", "PG-13"] if c in piv.columns]
        if not keep:
            keep = list(piv.columns)[:4]
        fig = go.Figure()
        for i, c in enumerate(keep):
            fig.add_trace(go.Scatter(x=piv.index, y=piv[c], name=c, mode="lines",
                                     line=dict(width=2.5)))
        fig.update_layout(title=dict(text="Rating Mix over Time"), height=330, hovermode="x unified")
        return fig
    if kind == "multicountry":
        multi = d[d["countries"].apply(lambda x: isinstance(x, list) and len(x) > 3)].copy()
        multi["n"] = multi["countries"].apply(len)
        multi = multi.nlargest(12, "n").reset_index()
        return charts.vertical_bar(pd.DataFrame({"label": multi["title"].str[:28], "value": multi["n"]}),
                                   "Multi-Country Productions", color=Colors.BLUE, height=330)
    if kind == "expansion":
        c = d["primary_country"].replace("Not Available", pd.NA).dropna().value_counts().head(15).reset_index()
        c.columns = ["label", "value"]
        return charts.horizontal_bar(c, "Market Momentum (top 15)", color=Colors.RED, height=330)
    if kind == "vintage":
        v = d["release_year"].value_counts().sort_index().reset_index()
        v.columns = ["label", "value"]
        return charts.line_area(v, "Catalogue by Release Year", "label", "value", color=Colors.GOLD, height=330)
    if kind == "genre_concentration":
        g = d["listed_in"].replace("Not Available", pd.NA).dropna().str.split(", ").explode().value_counts().head(8).reset_index()
        g.columns = ["label", "value"]
        return charts.donut(g["label"].tolist(), g["value"].tolist(), "Top-5 Genre Share", hole=0.7, height=330)
    raise ValueError(f"unknown chart kind {kind}")


def _export_png(fig, name: str) -> bytes:
    try:
        return pio.to_image(fig, format="png", width=1100, height=560, scale=2)
    except Exception:
        return b""


def render() -> None:
    df = clean_data()
    ui.section_header("📈", "Power BI Dashboard Gallery",
                      "Report-style dashboards with live previews, DAX snippets and PNG export")

    d = filters.apply(df)

    tab_gal, tab_studio = st.tabs(["🖼️ Gallery", "🛠️ Report Studio"])
    with tab_gal:
        st.markdown("### Choose a report")
        c1, c2 = st.columns([1.1, 1], gap="large")
        with c1:
            names = [f"{r['icon']} {r['name']}" for r in REPORTS]
            sel = st.selectbox("Report template", names)
        with c2:
            st.markdown('<div style="height:30px"></div>', unsafe_allow_html=True)
            open_studio = st.button("🛠️ Open in Studio", width="stretch", type="primary")

        report = REPORTS[names.index(sel)]
        kpis = _report_kpis(d, report["kpis"])
        ui.glass(f"""
        <div class="pbi-card">
          <div class="pbi-title">{report['icon']} {report['name']}
            <span class="pill red">Power BI · Live preview</span></div>
          <div class="pbi-desc">{report['desc']}</div>
          <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:.6rem;margin-bottom:.9rem">
            {''.join(_tile(v, k, i) for (k, v), i in zip(kpis.items(), report['kpis']))}
          </div>
          <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:.8rem">
            {''.join(f'<div class="tile" style="padding:.4rem"></div>' for _ in report['charts'][:2])}
          </div>
        </div>
        """, pad=False)
        st.caption("Full report opens in the Studio tab.")

        with st.expander("📐 DAX measures for this report"):
            st.code(report["dax"], language="dax")

        if open_studio:
            st.session_state["pbi_report"] = report["id"]
            st.rerun()

    with tab_studio:
        sel_id = st.session_state.get("pbi_report", "exec")
        report = next(r for r in REPORTS if r["id"] == sel_id)
        kpis = _report_kpis(d, report["kpis"])

        st.markdown(f"### 🛠️ {report['icon']} {report['name']} — studio")
        st.caption("Power BI-style tile grid rendered live from the filtered catalogue.")

        tiles = "".join(_tile(v, k, i[1]) for (k, v), i in zip(kpis.items(), report["kpis"]))
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:.7rem">
          {tiles}
        </div>""", unsafe_allow_html=True)
        st.markdown('<div style="height:.6rem"></div>', unsafe_allow_html=True)

        grid = report["charts"]
        row = st.columns(2)
        for i, kind in enumerate(grid):
            with row[i % 2]:
                fig = _build_chart(kind, d)
                charts.show(fig, height=340)
                png = _export_png(fig, f"{report['id']}_{kind}")
                if png:
                    st.download_button(f"⬇ {_DESCRIPTIONS.get(kind, kind)} · PNG",
                                       png, file_name=f"{report['id']}_{kind}.png",
                                       mime="image/png")

        with st.expander("📐 DAX measures"):
            st.code(report["dax"], language="dax")

    ui.footer()
