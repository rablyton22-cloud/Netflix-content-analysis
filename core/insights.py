"""Business insight generator: rule-based analysis over the catalogue.

Each detector inspects the (optionally filtered) dataframe and returns a list of
`Insight` objects ranked by a confidence score, producing natural-language
executive findings instead of raw numbers.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Callable

import pandas as pd

from core.data_loader import melt_genres

FOCUS_AREAS = [
    "Content Strategy",
    "Market Expansion",
    "Genre Momentum",
    "Audience & Ratings",
    "Production Trends",
]

DIRECTIONS = {"up": "▲", "down": "▼", "flat": "→"}


@dataclass
class Insight:
    title: str
    body: str
    metric: str
    value: str
    confidence: float          # 0..1
    direction: str = "up"
    icon: str = "💡"
    tags: list[str] = field(default_factory=list)

    @property
    def score(self) -> float:
        return self.confidence

    @property
    def id(self) -> str:
        return hashlib.md5(self.title.encode()).hexdigest()[:8]


# ------------------------------------------------------------------ helpers
def _series_top(s: pd.Series, n: int = 1) -> tuple[str, float]:
    top = s.value_counts().head(n)
    if len(top) == 0:
        return "n/a", 0.0
    return str(top.index[0]), float(top.iloc[0])


def _growth(series_counts: pd.Series, recent: int = 2) -> float:
    """% change of recent years vs the earlier window; NaN-safe."""
    s = series_counts.dropna()
    if len(s) < 2:
        return 0.0
    s = s.sort_index()
    cutoff = s.index.max() - recent
    old = s[s.index <= cutoff].sum()
    new = s[s.index > cutoff].sum()
    if old <= 0:
        return 0.0
    return (new - old) / old * 100


# ------------------------------------------------------------------ detectors
def _insight_strategy(df: pd.DataFrame) -> list[Insight]:
    out: list[Insight] = []
    tot = len(df)
    movies = (df["type"] == "Movie").sum()
    shows = (df["type"] == "TV Show").sum()
    share_movies = movies / tot * 100 if tot else 0

    if tot:
        out.append(
            Insight(
                "Portfolio balance",
                f"The catalogue is {share_movies:.0f}% movies and {100 - share_movies:.0f}% series. "
                "Series tend to drive watch-time, so a tilt toward TV shows usually signals a "
                "retention-led strategy.",
                "Movie share", f"{share_movies:.1f}%",
                confidence=0.82, direction="up" if share_movies < 70 else "flat",
                icon="⚖️", tags=["mix", "portfolio"],
            )
        )

    if len(df) >= 50:
        genre_counts = melt_genres(df)["genre"].value_counts()
        top, top_n = _series_top(genre_counts)
        share = top_n / len(df) * 100
        out.append(
            Insight(
                "Genre concentration",
                f"\"{top}\" is the dominant category at {share:.0f}% of titles. "
                "High concentration lowers differentiation but builds a clear brand identity.",
                "Top genre share", f"{share:.0f}%",
                confidence=0.70, direction="up", icon="🎯", tags=["genre"],
            )
        )

    recent = df[df["year_added"].notna()]
    if len(recent) >= 50:
        g = recent.groupby("year_added")["show_id"].count()
        growth = _growth(g)
        trend = "accelerating" if growth > 15 else ("slowing" if growth < -10 else "stable")
        out.append(
            Insight(
                "Catalogue velocity",
                f"Content additions have been {trend} with a {growth:+.0f}% shift between the "
                "recent window and the earlier period — an input metric for production budget planning.",
                "YoY change", f"{growth:+.0f}%",
                confidence=0.75, direction="up" if growth > 0 else "down", icon="🚀", tags=["growth"],
            )
        )
    return out


def _insight_market(df: pd.DataFrame) -> list[Insight]:
    out: list[Insight] = []
    if len(df) < 20:
        return out
    cc = df["primary_country"].replace("Not Available", pd.NA).dropna()
    top, top_n = _series_top(cc)
    share = top_n / len(cc) * 100 if len(cc) else 0
    out.append(
        Insight(
            "Primary producing market",
            f"{top} leads production with {top_n} titles ({share:.0f}% of the catalogue). "
            "Local-first production is a proven driver for international subscriber growth.",
            "Top market", f"{top} · {int(top_n)}",
            confidence=0.88, direction="up", icon="🌍", tags=["market"],
        )
    )
    counts = cc.value_counts()
    if len(counts) >= 3:
        top3 = list(counts.index[:3])
        share3 = counts.iloc[:3].sum() / len(cc) * 100
        out.append(
            Insight(
                "Market concentration",
                f"The top three markets ({', '.join(top3[:2])} and {top3[2]}) account for "
                f"{share3:.0f}% of production. Consider diversifying to hedge against market risk.",
                "Top-3 share", f"{share3:.0f}%",
                confidence=0.64, direction="down" if share3 > 75 else "flat", icon="🏢", tags=["market"],
            )
        )
    return out


def _insight_genre(df: pd.DataFrame) -> list[Insight]:
    out: list[Insight] = []
    if len(df) < 30:
        return out
    long = melt_genres(df)
    counts = long["genre"].value_counts().head(12)
    growth = {}
    for g in counts.index:
        sub = long[long["genre"] == g].merge(df[["show_id", "year_added"]], on="show_id")
        sub = sub[sub["year_added"].notna()]
        growth[g] = _growth(sub.groupby("year_added").size(), recent=2)
    df_g = pd.DataFrame({"count": counts, "growth": growth}).sort_values("growth", ascending=False)

    if len(df_g):
        hot = df_g.index[0]
        out.append(
            Insight(
                "Rising genre",
                f"\"{hot}\" grew {df_g.iloc[0]['growth']:+.0f}% in the recent window. "
                "High-growth categories are where new commissions have the least competition.",
                "Genre momentum", f"{hot} · {df_g.iloc[0]['growth']:+.0f}%",
                confidence=0.72, direction="up", icon="🔥", tags=["genre", "momentum"],
            )
        )
        sat = df_g.sort_values("count").index[0]
        sat_n = df_g.sort_values("count")["count"].iloc[0]
        out.append(
            Insight(
                "Underserved niche",
                f"\"{sat}\" is the least served category in the catalogue ({int(sat_n)} titles). "
                "A niche play here could differentiate the slate against competitors.",
                "Niche size", f"{int(sat_n)} titles",
                confidence=0.58, direction="flat", icon="🧩", tags=["genre", "opportunity"],
            )
        )
    return out


def _insight_audience(df: pd.DataFrame) -> list[Insight]:
    out: list[Insight] = []
    if len(df) < 20:
        return out
    r = df["rating"].replace("Not Available", pd.NA).dropna()
    top, top_n = _series_top(r)
    share = top_n / len(r) * 100 if len(r) else 0
    adult = r.isin(["TV-MA", "R", "NC-17"]).mean() * 100
    family = r.isin(["TV-Y", "TV-Y7", "TV-Y7-FV", "G", "PG"]).mean() * 100
    out.append(
        Insight(
            "Ratings mix",
            f"{share:.0f}% of titles carry \"{top}\". Adult-oriented content is {adult:.0f}% and "
            f"family-friendly is {family:.0f}% — the balance drives the addressable audience size.",
            "Adult share", f"{adult:.0f}%",
            confidence=0.80, direction="up" if adult > 40 else "flat", icon="👥", tags=["ratings"],
        )
    )
    out.append(
        Insight(
            "Family-friendly capacity",
            f"Only {family:.0f}% of the catalogue is family-safe. Expanding G/PG/TV-Y titles "
            "directly targets the household segment and reduces churn among co-viewing subscribers.",
            "Family share", f"{family:.0f}%",
            confidence=0.66, direction="up" if family < 20 else "flat", icon="👨‍👩‍👧‍👦", tags=["ratings"],
        )
    )
    return out


def _insight_production(df: pd.DataFrame) -> list[Insight]:
    out: list[Insight] = []
    if len(df) < 20:
        return out
    dur = df["duration_min"].dropna()
    if len(dur):
        out.append(
            Insight(
                "Runtime economics",
                f"Average movie runtime is {dur.mean():.0f} minutes (median {dur.median():.0f}). "
                "Shorter runtimes increase daily viewing counts and session frequency.",
                "Avg runtime", f"{dur.mean():.0f} min",
                confidence=0.60, direction="down" if dur.mean() < 100 else "flat", icon="⏱️", tags=["runtime"],
            )
        )
    yc = df.groupby("release_year")["show_id"].count()
    out.append(
        Insight(
            "Golden era",
            f"The catalogue peaks in the {int(yc.idxmax())}s with {int(yc.max())} titles from that decade. "
            "Classic-library depth is a strong differentiator for nostalgia-driven viewing.",
            "Peak decade", f"{int(yc.idxmax())}s",
            confidence=0.74, direction="up", icon="🏆", tags=["history"],
        )
    )
    return out


DETECTORS: dict[str, Callable[[pd.DataFrame], list[Insight]]] = {
    "Content Strategy": _insight_strategy,
    "Market Expansion": _insight_market,
    "Genre Momentum": _insight_genre,
    "Audience & Ratings": _insight_audience,
    "Production Trends": _insight_production,
}


def generate_insights(df: pd.DataFrame, focus: str, top_k: int = 5) -> list[Insight]:
    """Generate ranked insights for a focus area over the given dataframe."""
    detector = DETECTORS.get(focus, _insight_strategy)
    insights = [i for i in detector(df) if i.value not in ("n/a", "")]
    insights.sort(key=lambda i: i.score, reverse=True)
    return insights[:top_k]


def executive_summary(insights: list[Insight]) -> str:
    """Compose a one-paragraph executive briefing from the top insights."""
    if not insights:
        return "Not enough data in the current filter to produce a briefing."
    head = insights[0]
    lines = [
        f"{head.title}: {head.body}",
        f"Secondary signal — {insights[1].title}: {insights[1].body}" if len(insights) > 1 else "",
        f"Watch item — {insights[-1].title} at {insights[-1].confidence:.0f}% confidence."
        if len(insights) > 2 else "",
    ]
    return " ".join(l for l in lines if l)
