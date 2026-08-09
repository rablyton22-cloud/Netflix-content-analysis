"""Global cross-page filters, rendered in the sidebar and applied to the catalogue."""
from __future__ import annotations

import re

import pandas as pd
import streamlit as st

from core.data_loader import TOP_RATINGS

_DEFAULTS = {
    "f_types": ["Movie", "TV Show"],
    "f_ratings": [],
    "f_years": (1925, 2026),
    "f_countries": [],
    "f_genres": [],
}


def _country_options(df: pd.DataFrame) -> list[str]:
    return df["primary_country"].replace("Not Available", pd.NA).dropna().value_counts().head(24).index.tolist()


def _genre_options(df: pd.DataFrame) -> list[str]:
    return df["listed_in"].replace("Not Available", pd.NA).dropna().str.split(", ").explode().value_counts().head(18).index.tolist()


def render(df: pd.DataFrame) -> None:
    """Draw the global filter panel into the sidebar."""
    with st.expander("🌐 Global Filters", expanded=False):
        types = st.multiselect("Content type", ["Movie", "TV Show"],
                               default=_DEFAULTS["f_types"], key="f_types")
        years = st.slider("Release year", 1925, 2026, _DEFAULTS["f_years"], key="f_years")
        ratings = st.multiselect("Ratings", TOP_RATINGS, key="f_ratings", default=[])
        countries = st.multiselect("Country", _country_options(df), key="f_countries")
        genres = st.multiselect("Genres", _genre_options(df), key="f_genres")

        st.markdown("---")
        if st.button("↺ Reset filters", width="stretch"):
            for k, v in _DEFAULTS.items():
                st.session_state.pop(k, None)
            st.rerun()


def get() -> dict:
    return {k: st.session_state.get(k, _DEFAULTS[k]) for k in _DEFAULTS}


def apply(df: pd.DataFrame, f: dict | None = None) -> pd.DataFrame:
    """Return the catalogue filtered by the global filter state."""
    f = f or get()
    mask = df["type"].isin(f["f_types"])
    mask &= df["release_year"].between(*f["f_years"])
    if f["f_ratings"]:
        mask &= df["rating"].isin(f["f_ratings"])
    if f["f_countries"]:
        mask &= df["primary_country"].isin(f["f_countries"])
    if f["f_genres"]:
        joined = "|".join(re.escape(g) for g in f["f_genres"])
        mask &= df["listed_in"].fillna("").str.contains(joined, regex=True, na=False)
    return df[mask]
