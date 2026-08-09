"""Reusable UI primitives built on top of the design system."""
from __future__ import annotations

import html

import streamlit as st

from components.kpi import kpi_grid
from core.config import Colors

JS_REVEAL = """
<script>
(function(){
  const io = new IntersectionObserver((es) => {
    es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, {threshold: 0.15});
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));
})();
</script>
"""


def reveal(html_fragment: str, delay: str = "") -> None:
    """Wrap an HTML fragment in a scroll-reveal container."""
    cls = "reveal" + (f" {delay}" if delay else "")
    st.markdown(f'<div class="{cls}">{html_fragment}</div>', unsafe_allow_html=True)
    if not delay:
        st.markdown(JS_REVEAL, unsafe_allow_html=True)


def glass(inner: str, *, grow: bool = False, pad: bool = True) -> str:
    cls = "glass" + (" grow" if grow else "") + (" pad" if pad else "")
    return f'<div class="{cls}">{inner}</div>'


def section_header(icon: str, title: str, subtitle: str = "") -> None:
    sub = f'<div class="sec-sub">{html.escape(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f'<div class="sec-head"><div class="sec-ico">{icon}</div>'
        f'<div><h2>{html.escape(title)}</h2>{sub}</div>'
        f'<div class="sec-line"></div></div>',
        unsafe_allow_html=True,
    )


def pill(text: str, tone: str = "") -> str:
    return f'<span class="pill {tone}">{html.escape(text)}</span>'


def metric_line(inner: str, grow: bool = True, pad: bool = True) -> None:
    st.markdown(glass(inner, grow=grow, pad=pad), unsafe_allow_html=True)


def hero(title: str, accent: str, subtitle: str, eyebrow: str) -> None:
    """Netflix-style hero banner."""
    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-eyebrow">✦ {html.escape(eyebrow)}</div>
          <h1 class="hero-title">{html.escape(title)} <span class="accent">{html.escape(accent)}</span></h1>
          <p class="hero-sub">{html.escape(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def footer() -> None:
    st.markdown(
        f"""
        <div class="app-footer">
          <div class="foot-brand"><span class="n-logo">N</span> Netflix Content Analysis</div>
          <div>Built with Streamlit · Plotly · DuckDB</div>
          <div>© 2026 · data: Netflix Titles (8807 rows)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def spacer(height: int = 10) -> None:
    st.markdown(f'<div style="height:{height}px"></div>', unsafe_allow_html=True)


def color_from_index(i: int) -> str:
    return [Colors.RED, Colors.GOLD, Colors.BLUE, Colors.GREEN, Colors.PURPLE,
            Colors.CYAN, Colors.ORANGE, Colors.PINK][i % 8]


def info_banner(icon: str, text: str, tone: str = "red") -> None:
    st.markdown(
        f'<div style="display:flex;gap:.7rem;align-items:center;background:rgba(255,255,255,0.04);'
        f'border:1px solid var(--n-line);border-left:3px solid var(--n-{tone});'
        f'border-radius:12px;padding:.8rem 1rem;color:var(--n-muted);font-size:.88rem;">'
        f'<span>{icon}</span><span>{html.escape(text)}</span></div>',
        unsafe_allow_html=True,
    )


def show_kpis(kpis: list[dict]) -> None:
    kpi_grid(kpis)
