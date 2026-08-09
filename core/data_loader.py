"""Data loading + cleaning pipeline with caching and step-by-step transparency."""
from __future__ import annotations

import re
from typing import Any

import pandas as pd
import streamlit as st

from core.config import DATA_PATH

_PLACEHOLDER = "Not Available"

RAW_COLUMNS = [
    "show_id", "type", "title", "director", "cast", "country",
    "date_added", "release_year", "rating", "duration", "listed_in", "description",
]

_RATING_FIX = {
    "74 min": "PG-13", "84 min": "TV-MA", "66 min": "R",
}

_CLEANING_STEPS = [
    {
        "id": "whitespace",
        "title": "Trim whitespace",
        "desc": "Strip leading/trailing spaces from every text column.",
        "code": (
            'text_cols = df.select_dtypes("object").columns\n'
            "for c in text_cols:\n"
            "    df[c] = df[c].str.strip()"
        ),
        "impact": "Removes invisible duplicates (e.g. 'United States ' vs 'United States').",
    },
    {
        "id": "placeholders",
        "title": "Impute missing values",
        "desc": "Fill missing director / cast / country / date_added with a neutral placeholder so filtering never breaks.",
        "code": (
            'for c in ["director", "cast", "country", "date_added", "rating", "duration"]:\n'
            '    df[c] = df[c].fillna("Not Available")'
        ),
        "impact": "Eliminates NaN cells from categorical columns.",
    },
    {
        "id": "dates",
        "title": "Parse add dates",
        "desc": "Convert `date_added` into a real datetime and extract the calendar year it joined the catalogue.",
        "code": (
            'df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")\n'
            'df["year_added"] = df["date_added"].dt.year\n'
            'df["month_added"] = df["date_added"].dt.month'
        ),
        "impact": "Enables time-series analysis of catalogue growth.",
    },
    {
        "id": "duration",
        "title": "Normalise duration",
        "desc": "Split duration into a numeric field: minutes for movies, seasons for shows. Fixes rows where a rating leaked into the duration column.",
        "code": (
            'mask = df["duration"].str.contains("min", na=False)\n'
            'df["duration_min"] = df["duration"].str.extract(r"(\\d+)\\s*min").astype(float)\n'
            'df["duration_seasons"] = df["duration"].str.extract(r"(\\d+)\\s*Season").astype(float)\n'
            'df["rating"] = df["rating"].replace({"74 min": "PG-13", "84 min": "TV-MA", "66 min": "R"})'
        ),
        "impact": "Gives a clean numeric axis for runtime analysis.",
    },
    {
        "id": "categorical",
        "title": "Normalise categories",
        "desc": "Split comma separated `country` and `listed_in` into real lists and keep a single primary country.",
        "code": (
            'df["countries"] = df["country"].str.split(", ")\n'
            'df["genres"] = df["listed_in"].str.split(", ")\n'
            'df["primary_country"] = df["countries"].str[0]'
        ),
        "impact": "Supports multi-country attribution and genre breakdowns.",
    },
    {
        "id": "enrich",
        "title": "Engineer features",
        "desc": "Derive decade, catalogue age band, rating tier and content age for deeper analytics.",
        "code": (
            'df["decade"] = (df["release_year"] // 10 * 10)\n'
            'df["age_tier"] = pd.cut(df["release_year"], bins=[1920, 1970, 2000, 2015, 2025], labels=["Classic", "Retro", "Modern", "Current"])\n'
            'df["catalogue_age"] = 2025 - df["release_year"]'
        ),
        "impact": "Enables vintage and cohort analysis.",
    },
    {
        "id": "dedupe",
        "title": "Drop duplicates",
        "desc": "Remove rows that share title + type + release year (true content duplicates).",
        "code": (
            'df = df.drop_duplicates(subset=["title", "type", "release_year"])'
        ),
        "impact": "Guards against double counting in KPI counters.",
    },
    {
        "id": "dtypes",
        "title": "Finalise dtypes",
        "desc": "Cast numeric columns and reset the index for a clean tidy frame.",
        "code": (
            'df["release_year"] = df["release_year"].astype("Int64")\n'
            "df = df.reset_index(drop=True)"
        ),
        "impact": "Stable, typed schema ready for SQL + Plotly.",
    },
]


@st.cache_data(show_spinner="Loading Netflix catalogue…")
def load_raw() -> pd.DataFrame:
    """Read the untouched raw CSV exactly as shipped."""
    return pd.read_csv(DATA_PATH, encoding="utf-8", low_memory=False)


@st.cache_data(show_spinner="Running cleaning pipeline…")
def clean_data() -> pd.DataFrame:
    """Apply the full documented cleaning pipeline."""
    df = load_raw().copy()

    # 1. whitespace
    for c in df.select_dtypes("object").columns:
        df[c] = df[c].astype(str).str.strip()

    # 2. placeholders
    for c in ["director", "cast", "country", "date_added", "rating", "duration", "listed_in", "title"]:
        df[c] = df[c].replace({"nan": "", "None": "", "Not Available": ""})
        df[c] = df[c].replace("", pd.NA)

    # 3. dates
    df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
    df["year_added"] = df["date_added"].dt.year
    df["month_added"] = df["date_added"].dt.month

    # 4. duration
    df["duration_min"] = df["duration"].astype(str).str.extract(r"(\d+)\s*min").astype(float)
    df["duration_seasons"] = df["duration"].astype(str).str.extract(r"(\d+)\s*Seasons?").astype(float)
    df["rating"] = df["rating"].replace(_RATING_FIX)

    # 5. categorical lists
    df["countries"] = df["country"].where(df["country"].notna(), _PLACEHOLDER).str.split(", ")
    df["genres"] = df["listed_in"].where(df["listed_in"].notna(), _PLACEHOLDER).str.split(", ")
    df["primary_country"] = df["countries"].str[0]

    # 6. enrich
    df["decade"] = (df["release_year"] // 10 * 10).astype("Int64")
    df["age_tier"] = pd.cut(
        df["release_year"], bins=[1920, 1970, 2000, 2015, 2025],
        labels=["Classic", "Retro", "Modern", "Current"],
    )
    df["catalogue_age"] = 2025 - df["release_year"]

    # 7. dedupe
    df = df.drop_duplicates(subset=["title", "type", "release_year"])

    # 8. dtypes
    df["release_year"] = df["release_year"].astype("Int64")
    df = df.reset_index(drop=True)
    return df


@st.cache_data(show_spinner=False)
def cleaning_report() -> pd.DataFrame:
    """Per-step before/after metrics used by the Data Cleaning page."""
    df = load_raw()
    rows: list[dict[str, Any]] = []
    prev = df
    for step in _CLEANING_STEPS:
        after = _apply_step(prev.copy(), step["id"])
        rows.append(
            {
                "step": step["title"],
                "rows_before": len(prev),
                "rows_after": len(after),
                "cols_before": prev.shape[1],
                "cols_after": after.shape[1],
                "missing_before": int(prev.isna().sum().sum()),
                "missing_after": int(after.isna().sum().sum()),
            }
        )
        prev = after
    return pd.DataFrame(rows)


def _apply_step(df: pd.DataFrame, step_id: str) -> pd.DataFrame:
    """Re-apply a single cleaning step (mirror of `clean_data`)."""
    if step_id == "whitespace":
        for c in df.select_dtypes("object").columns:
            df[c] = df[c].astype(str).str.strip()
    elif step_id == "placeholders":
        for c in ["director", "cast", "country", "date_added", "rating", "duration", "listed_in", "title"]:
            df[c] = df[c].astype(str).replace({"nan": "", "None": ""}).replace("", pd.NA)
    elif step_id == "dates":
        df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
    elif step_id == "duration":
        df["duration_min"] = df["duration"].astype(str).str.extract(r"(\d+)\s*min").astype(float)
        df["duration_seasons"] = df["duration"].astype(str).str.extract(r"(\d+)\s*Seasons?").astype(float)
    elif step_id == "categorical":
        df["countries"] = df["country"].astype(str).str.split(", ")
        df["genres"] = df["listed_in"].astype(str).str.split(", ")
        df["primary_country"] = df["countries"].str[0]
    elif step_id == "enrich":
        df["decade"] = (df["release_year"] // 10 * 10)
    elif step_id == "dedupe":
        df = df.drop_duplicates(subset=["title", "type", "release_year"])
    elif step_id == "dtypes":
        df = df.reset_index(drop=True)
    return df


def quality_score(df: pd.DataFrame) -> float:
    """Heuristic 0–100 data quality score."""
    completeness = 1 - (df.isna().sum().sum() / (df.shape[0] * df.shape[1]))
    hashable = df.drop(columns=["genres", "countries"], errors="ignore")
    duplicates = 1 - (hashable.duplicated().sum() / max(len(df), 1))
    typed = sum(1 for c in ["year_added", "duration_min"] if c in df and not df[c].isna().all()) / 2
    return round(100 * (0.55 * completeness + 0.25 * duplicates + 0.20 * typed))


def melt_genres(df: pd.DataFrame) -> pd.DataFrame:
    """Long-form dataframe with one row per title × genre."""
    parts = []
    for _, row in df.iterrows():
        for g in row["genres"] or [_PLACEHOLDER]:
            parts.append((row["show_id"], g.strip()))
    return pd.DataFrame(parts, columns=["show_id", "genre"])


def melt_countries(df: pd.DataFrame) -> pd.DataFrame:
    """Long-form dataframe with one row per title × producing country."""
    parts = []
    for _, row in df.iterrows():
        for c in row["countries"] or [_PLACEHOLDER]:
            parts.append((row["show_id"], c.strip()))
    return pd.DataFrame(parts, columns=["show_id", "country"])


TOP_RATINGS = [
    "TV-MA", "TV-14", "R", "PG-13", "TV-PG", "PG",
    "TV-Y7", "TV-Y", "TV-G", "TV-Y7-FV", "G", "NR", "NC-17",
]

@st.cache_data(show_spinner=False)
def search_titles(df: pd.DataFrame, query: str, limit: int = 12) -> pd.DataFrame:
    """Fuzzy-ish keyword search over title / cast / director / genres."""
    q = query.strip().lower()
    if not q:
        return pd.DataFrame()
    mask = (
        df["title"].str.lower().str.contains(q, na=False, regex=False)
        | df["cast"].fillna("").str.lower().str.contains(q, na=False, regex=False)
        | df["director"].fillna("").str.lower().str.contains(q, na=False, regex=False)
        | df["listed_in"].fillna("").str.lower().str.contains(q, na=False, regex=False)
    )
    return df.loc[mask].head(limit)


ALL_YEARS = range(1925, 2026)
