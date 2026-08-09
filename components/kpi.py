"""Animated KPI counters (count-up on view) rendered via components.html."""
from __future__ import annotations

import html

import streamlit as st

from core.config import Colors

_JS = """
<script>
(function(){
  const seen = new Set();
  const fmt = (n, d) => {
    const v = Number(n).toFixed(d);
    return Number(v).toLocaleString('en-US', {maximumFractionDigits: d, minimumFractionDigits: d});
  };
  const animate = (el) => {
    if (seen.has(el)) return;
    seen.add(el);
    const target = parseFloat(el.dataset.target);
    const decimals = parseInt(el.dataset.decimals || '0', 10);
    const dur = parseInt(el.dataset.dur || '1200', 10);
    const start = performance.now();
    const step = (now) => {
      const p = Math.min((now - start) / dur, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      el.textContent = fmt(target * eased, decimals);
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = fmt(target, decimals);
    };
    requestAnimationFrame(step);
  };
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) { animate(e.target); io.unobserve(e.target); } });
  }, {threshold: 0.3});
  document.querySelectorAll('.kpi .kpi-value').forEach(el => io.observe(el));
})();
</script>
"""


def animated_kpi(*, label: str, value: float, icon: str = "📊", color: str = Colors.RED,
                 suffix: str = "", decimals: int = 0, duration: int = 1200,
                 foot: str = "", bar_width: int = 100) -> None:
    """Render a glassmorphism KPI card with a JS count-up animation."""
    safe = html.escape(label)
    safe_foot = html.escape(foot)
    card_id = f"kpi-{abs(hash((label, str(value), icon))) % 999999}"
    html_block = f"""
    <div class="kpi" id="{card_id}">
      <div class="kpi-icon">{icon}</div>
      <div class="kpi-label">{safe}</div>
      <div class="kpi-value" data-target="{value}" data-decimals="{decimals}" data-dur="{duration}">
        0{suffix}</div>
      <div class="kpi-bar"><span style="width:{bar_width}%;background:linear-gradient(90deg,{color},{color}99)"></span></div>
      {f'<div class="kpi-foot">{safe_foot}</div>' if foot else ''}
    </div>
    """
    st.markdown(f'<div class="kpi-row">{html_block}</div>', unsafe_allow_html=True)


def kpi_grid(kpis: list[dict]) -> None:
    """Render several animated KPI cards inside one responsive grid."""
    cards = "".join(
        f"""
        <div class="kpi">
          <div class="kpi-icon">{k.get('icon', '📊')}</div>
          <div class="kpi-label">{html.escape(k['label'])}</div>
          <div class="kpi-value" data-target="{k['value']}" data-decimals="{k.get('decimals', 0)}" data-dur="{k.get('duration', 1200)}">
            0{k.get('suffix', '')}</div>
          <div class="kpi-bar"><span style="width:{k.get('bar', 100)}%;background:linear-gradient(90deg,{k.get('color', Colors.RED)},{k.get('color', Colors.RED)}99)"></span></div>
          {f'<div class="kpi-foot">{html.escape(k["foot"])}</div>' if k.get('foot') else ''}
        </div>
        """
        for k in kpis
    )
    st.markdown(f'<div class="kpi-row">{cards}</div>', unsafe_allow_html=True)
    st.markdown(_JS, unsafe_allow_html=True)
