"""Story — a guided data narrative across the decade of streaming."""
from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from components import charts, ui
from core.config import Colors
from core.data_loader import clean_data

CHAPTERS = [
    {
        "id": "pilot", "num": "01", "icon": "🎬",
        "title": "A Catalogue Is Born",
        "quote": "“Content is king, but distribution is queen — and she wears the pants.”",
        "body": (
            "In 2013 Netflix started commissioning original content and the catalogue began to "
            "compound. What began as a DVD-rental library became a global production engine. This "
            "chapter traces the raw material: every title added, every market reached, every genre "
            "that scaled — the DNA of modern streaming."
        ),
        "chart": "growth", "big": None,
    },
    {
        "id": "golden", "num": "02", "icon": "🏆",
        "title": "The Golden Age of Content",
        "quote": "“Peak TV wasn't a bubble — it was a business model.”",
        "body": (
            "The catalogue peaks in the 2010s, when originals replaced acquisitions as the growth "
            "engine. Movies still outnumber series two-to-one, but the series share of new additions "
            "keeps climbing — a sign that retention, not acquisition, became the metric that matters."
        ),
        "chart": "decades", "big": ("8,807", "titles analysed"),
    },
    {
        "id": "genre", "num": "03", "icon": "🎭",
        "title": "The Genre Portfolio",
        "quote": "“Dramas build the brand, comedy fills the hours, documentaries win the awards.”",
        "body": (
            "Genre is Netflix's real portfolio. Dramas and comedies anchor the slate while "
            "international shows quietly dominate the tail. The treemap below is the actual shelf "
            "layout of the streaming age."
        ),
        "chart": "treemap", "big": None,
    },
    {
        "id": "global", "num": "04", "icon": "🌍",
        "title": "Going Global",
        "quote": "“The world doesn't watch American TV anymore — the world watches TV.”",
        "body": (
            "The United States still leads, but India and the UK are closing fast, and nearly 120 "
            "markets have produced at least one title. Every country that reaches a critical mass of "
            "content becomes a local moat against competitors."
        ),
        "chart": "countries", "big": ("120+", "producing markets"),
    },
    {
        "id": "appetite", "num": "05", "icon": "📺",
        "title": "Appetite & Ratings",
        "quote": "“Mature stories are the flagship; family-safe content is the moat.”",
        "body": (
            "Ratings reveal strategy: TV-MA leads the slate while a smaller family-friendly shelf "
            "targets households. The mix between adult and family content defines how large the "
            "addressable audience really is."
        ),
        "chart": "ratings", "big": None,
    },
    {
        "id": "era", "num": "06", "icon": "⏳",
        "title": "Vintage & Legacy",
        "quote": "“Libraries age like wine — the classics keep compounding.”",
        "body": (
            "Nearly a century of cinema is preserved in one dataset: 1925 relics, 1970s masterpieces, "
            "2000s blockbusters. Deep catalogue history is the quiet differentiator of the platform era."
        ),
        "chart": "vintage", "big": ("1925", "oldest release"),
    },
    {
        "id": "trailer", "num": "07", "icon": "🔮",
        "title": "What the Numbers Say Next",
        "quote": "“The next episode is written by the data.”",
        "body": (
            "Global additions, rising genres and short-form series all point one way: local-first "
            "production, more seasons, shorter runtimes. The story isn't over — it's compounding."
        ),
        "chart": "momentum", "big": None,
    },
]

_TIMELINE = [
    ("1925", "Silent Cinema", "The oldest release in the catalogue — the seed of a century of cinema."),
    ("2013", "Originals Begin", "Netflix commissions its first original series, changing the model forever."),
    ("2016", "Global Rollout", "The service reaches 190+ countries in a single day."),
    ("2019", "Peak Catalogue", "Additions hit their ceiling as the library crosses 5,000 titles."),
    ("2021", "The Dataset End", "The catalogue snapshot closes — 8,807 titles ready for analysis."),
]


def _chart_for(kind: str, d: pd.DataFrame):
    if kind == "growth":
        g = d[d["year_added"].notna()].groupby("year_added")["show_id"].count().reset_index()
        g.columns = ["label", "value"]
        return charts.line_area(g, "Titles Added per Year", "label", "value", color=Colors.RED, height=360)
    if kind == "decades":
        dec = d.groupby("decade")["show_id"].count().reset_index()
        dec.columns = ["label", "value"]
        return charts.vertical_bar(dec, "Titles by Decade", color=Colors.PURPLE, height=360)
    if kind == "treemap":
        g = d["listed_in"].replace("Not Available", pd.NA).dropna().str.split(", ").explode().value_counts().head(24).reset_index()
        g.columns = ["genre", "count"]; g["parent"] = "All"
        return charts.treemap(g[["parent", "genre", "count"]], ["parent", "genre"], "count",
                              "Genre Hierarchy", height=380)
    if kind == "countries":
        c = d["primary_country"].replace("Not Available", pd.NA).dropna().value_counts().head(12).reset_index()
        c.columns = ["label", "value"]
        return charts.horizontal_bar(c, "Top Producing Markets", color=Colors.BLUE, height=360)
    if kind == "ratings":
        r = d["rating"].replace("Not Available", pd.NA).dropna().value_counts().head(10).reset_index()
        r.columns = ["label", "value"]
        return charts.vertical_bar(r, "Rating Distribution", color=Colors.GOLD, height=360)
    if kind == "vintage":
        v = d["release_year"].value_counts().sort_index().reset_index()
        v.columns = ["label", "value"]
        return charts.line_area(v, "Catalogue by Release Year", "label", "value", color=Colors.GOLD, height=360)
    if kind == "momentum":
        parts = []
        for _, r in d[d["year_added"].notna()].iterrows():
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
        return charts.horizontal_bar(mom, "Rising Genres (recent vs earlier)", color=Colors.GREEN, height=360)
    raise ValueError(kind)


def render() -> None:
    df = clean_data()
    ui.section_header("🎬", "The Story of Streaming",
                      "A guided narrative over 8,807 titles — chapter by chapter")

    if "story_i" not in st.session_state:
        st.session_state["story_i"] = 0
    i = st.session_state["story_i"]
    ch = CHAPTERS[i]

    st.markdown(
        f'<div class="hero" style="min-height:300px">'
        f'<div class="hero-eyebrow">Chapter {ch["num"]} of {len(CHAPTERS):02d} · {ch["icon"]}</div>'
        f'<h1 class="hero-title" style="font-size:clamp(2.4rem,6vw,4.2rem)">{html.escape(ch["title"])}</h1>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="quote">{ch["quote"]}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="color:var(--n-muted);font-size:1rem;line-height:1.8;max-width:820px">{ch["body"]}</div>',
        unsafe_allow_html=True,
    )

    if ch["big"]:
        num, label = ch["big"]
        st.markdown(
            f'<div class="big-number" style="margin-top:1.2rem">{num}</div>'
            f'<div style="color:var(--n-muted);letter-spacing:.1em;text-transform:uppercase;font-size:.8rem">{label}</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
    charts.show(_chart_for(ch["chart"], df))

    c1, c2, c3 = st.columns([1, 2.4, 1], gap="large")
    with c1:
        if st.button("◀ Previous", width="stretch", disabled=(i == 0)):
            st.session_state["story_i"] = max(0, i - 1)
            st.rerun()
    with c2:
        progress = (i + 1) / len(CHAPTERS)
        st.progress(progress, text=f"Chapter {i + 1} / {len(CHAPTERS)}")
    with c3:
        if st.button("Next ▶", width="stretch", disabled=(i == len(CHAPTERS) - 1),
                     type="primary"):
            st.session_state["story_i"] = min(len(CHAPTERS) - 1, i + 1)
            st.rerun()

    ui.section_header("🕰️", "Timeline", "Key milestones in the data's own history")
    tl = "".join(
        f'<div class="tl-item"><div class="tl-date">{y}</div><div class="tl-title">{t}</div>'
        f'<div class="tl-text">{d}</div></div>'
        for y, t, d in _TIMELINE
    )
    st.markdown(f'<div class="timeline glass pad">{tl}</div>', unsafe_allow_html=True)

    ui.footer()
