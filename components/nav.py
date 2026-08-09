"""Sidebar navigation primitives."""
from __future__ import annotations

import streamlit as st

NAV_KEY = "nav_radio"
TARGET_KEY = "nav_target"


def go(page: str) -> None:
    """Request navigation to a page. The target is consumed before the radio renders."""
    st.session_state[TARGET_KEY] = page
    st.rerun()


def sync() -> None:
    """Apply a pending navigation target to the radio *before* it instantiates."""
    target = st.session_state.pop(TARGET_KEY, None)
    if target:
        st.session_state[NAV_KEY] = target


def current() -> str:
    return st.session_state.get(NAV_KEY, "Home")
