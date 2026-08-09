"""Interactive Plotly chart library with a cohesive dark, glassy aesthetic."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

from core.config import Colors

_RED = Colors.RED
_GOLD = Colors.GOLD

PALETTE = [_RED, _GOLD, "#4C9AFF", "#2EBD85", "#9D4EDD", "#22D3EE", "#FF8A3D", "#FF5E9C"]

pio.templates["nca"] = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Inter, Segoe UI, sans-serif", "color": Colors.MUTED, "size": 12},
        "title": {"font": {"color": Colors.TEXT, "size": 18, "family": "Inter"},
                  "x": 0, "xanchor": "left", "yanchor": "top"},
        "margin": {"l": 20, "r": 20, "t": 56, "b": 20},
        "legend": {"bgcolor": "rgba(0,0,0,0)", "orientation": "h", "y": -0.18,
                   "font": {"color": Colors.MUTED}},
        "colorway": PALETTE,
        "hoverlabel": {"bgcolor": "#1E1E2F", "bordercolor": "rgba(255,255,255,0.15)",
                       "font": {"color": Colors.TEXT}},
        "xaxis": {"gridcolor": "rgba(255,255,255,0.05)", "zerolinecolor": "rgba(255,255,255,0.08)",
                  "linecolor": "rgba(255,255,255,0.1)", "tickcolor": "rgba(255,255,255,0.1)"},
        "yaxis": {"gridcolor": "rgba(255,255,255,0.05)", "zerolinecolor": "rgba(255,255,255,0.08)",
                  "linecolor": "rgba(255,255,255,0.1)", "tickcolor": "rgba(255,255,255,0.1)"},
        "coloraxis": {"colorbar": {"outlinewidth": 0, "thickness": 12}},
    }
}
pio.templates.default = "plotly_dark+nca"


def _base(fig: go.Figure, height: int = 380) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=16, r=16, t=58, b=16),
        showlegend=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", zeroline=False)
    return fig


def show(fig: go.Figure, *, height: int = 380, **kwargs) -> None:
    """Render a figure with the shared layout + styling."""
    import streamlit as st
    fig = _base(fig, height=height)
    st.plotly_chart(fig, width="stretch", **kwargs)


# ------------------------------------------------------------------ factories
def donut(labels: list[str], values: list[float], title: str, hole: float = 0.72,
          colors: list[str] | None = None, height: int = 360) -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=hole,
        marker=dict(colors=colors or PALETTE, line=dict(color="#0B0B0F", width=2)),
        textinfo="label+percent", textfont=dict(color=Colors.TEXT, size=11),
        hovertemplate="<b>%{label}</b><br>%{value:,} titles · %{percent}<extra></extra>",
    ))
    fig.update_layout(title=dict(text=title))
    return fig


def horizontal_bar(df: pd.DataFrame, title: str, color: str = _RED,
                   x: str = "value", y: str = "label", height: int = 380) -> go.Figure:
    df = df.head(12)
    fig = go.Figure(go.Bar(
        x=df[x], y=df[y], orientation="h",
        marker=dict(color=df[x], colorscale=[[0, "rgba(229,9,20,0.35)"], [1, color]],
                    line=dict(width=0)),
        hovertemplate="<b>%{y}</b>: %{x:,}<extra></extra>",
    ))
    fig.update_layout(title=dict(text=title), yaxis=dict(autorange="reversed"))
    fig.update_traces(texttemplate="%{x:,}", textposition="outside",
                      textfont=dict(color=Colors.MUTED, size=11))
    return fig


def vertical_bar(df: pd.DataFrame, title: str, color: str = _RED,
                 x: str = "label", y: str = "value", height: int = 380) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=df[x], y=df[y],
        marker=dict(color=color, opacity=0.9, line=dict(width=0)),
        hovertemplate="<b>%{x}</b>: %{y:,}<extra></extra>",
    ))
    fig.update_layout(title=dict(text=title))
    return fig


def line_area(df: pd.DataFrame, title: str, x: str, y: str, color: str = _RED,
              height: int = 380, filled: bool = True) -> go.Figure:
    fig = go.Figure()
    ys = y if isinstance(y, list) else [y]
    colors = PALETTE if isinstance(y, list) else [color]
    for i, col in enumerate(ys):
        mode = "lines+markers" if len(df) <= 20 else "lines"
        fig.add_trace(go.Scatter(
            x=df[x], y=df[col], name=col, mode=mode,
            line=dict(color=colors[i % len(colors)], width=3),
            fill="tozeroy" if filled else None,
            fillcolor=f"rgba(229,9,20,0.10)" if colors[i % len(colors)] == _RED else f"rgba(245,197,24,0.10)",
            hovertemplate="<b>%{x}</b>: %{y:,}<extra></extra>",
        ))
    fig.update_layout(title=dict(text=title), hovermode="x unified")
    return fig


def heatmap(z: np.ndarray, x: list, y: list, title: str, height: int = 420) -> go.Figure:
    fig = go.Figure(go.Heatmap(
        z=z, x=x, y=y,
        colorscale=[[0, "#101020"], [0.4, "#5C0710"], [0.75, "#B20710"], [1, "#FF8A90"]],
        hovertemplate="<b>%{y} · %{x}</b><br>%{z:,} titles<extra></extra>",
    ))
    fig.update_layout(title=dict(text=title), height=height)
    return fig


def treemap(df: pd.DataFrame, path: list[str], values: str, title: str, height: int = 420) -> go.Figure:
    fig = px.treemap(df, path=path, values=values, title=title,
                     color=values, color_continuous_scale=["#1c1c30", _RED, _GOLD])
    fig.update_traces(textinfo="label+value", textfont=dict(size=12),
                      marker=dict(line=dict(color="#0B0B0F", width=1)))
    fig.update_layout(coloraxis_showscale=False)
    return fig


def choropleth(df: pd.DataFrame, title: str, height: int = 460) -> go.Figure:
    fig = go.Figure(go.Choropleth(
        locations=df["iso"], z=df["titles"], text=df["country"],
        colorscale=[[0, "#12121f"], [0.35, "#5C0710"], [0.7, "#B20710"], [1, "#FF5A60"]],
        colorbar=dict(thickness=12, outlinewidth=0, tickfont=dict(color=Colors.MUTED)),
        hovertemplate="<b>%{text}</b><br>%{z:,} titles<extra></extra>",
        showscale=False,
    ))
    fig.update_layout(title=dict(text=title))
    fig.update_geos(
        showcountries=True, countrycolor="rgba(255,255,255,0.10)",
        showocean=True, oceancolor="rgba(8,8,14,0.6)",
        showland=True, landcolor="#131320",
        showframe=False, showcoastlines=False, coastlinecolor="rgba(255,255,255,0.08)",
        bgcolor="rgba(0,0,0,0)", projection_type="natural earth",
    )
    return fig


def bubble(df: pd.DataFrame, x: str, y: str, size: str, color: str, text: str,
           title: str, height: int = 420) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=df[x], y=df[y], mode="markers+text",
        marker=dict(size=df[size].fillna(5).clip(lower=4).to_numpy() * 2,
                    color=df[color], colorscale=[[0, "#B20710"], [1, _GOLD]],
                    line=dict(color="rgba(255,255,255,0.35)", width=1),
                    showscale=False, opacity=0.85),
        text=df[text], textposition="top center",
        textfont=dict(size=10, color=Colors.MUTED),
        hovertemplate="<b>%{text}</b><br>%{xaxis.title.text}: %{x:,}<br>%{yaxis.title.text}: %{y:,}<extra></extra>",
    ))
    fig.update_layout(title=dict(text=title), xaxis=dict(title=x), yaxis=dict(title=y))
    return fig


def sparkline(values: list[float], color: str = _RED, height: int = 60) -> go.Figure:
    fig = go.Figure(go.Scatter(
        y=values, mode="lines",
        line=dict(color=color, width=2.4),
        fill="tozeroy", fillcolor=f"{color}22",
        hoverinfo="skip",
    ))
    fig.update_layout(
        height=height, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False), yaxis=dict(visible=False),
    )
    return fig


def gauge(value: float, title: str, max_val: float = 100, height: int = 240) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value, number={"font": {"size": 40, "color": Colors.TEXT}},
        title={"text": title, "font": {"size": 15, "color": Colors.TEXT}},
        gauge=dict(
            axis=dict(range=[0, max_val], tickcolor=Colors.MUTED),
            bar=dict(color=_RED),
            bgcolor="rgba(255,255,255,0.05)",
            borderwidth=0,
            steps=[dict(range=[0, max_val * 0.6], color="rgba(255,255,255,0.04)"),
                   dict(range=[max_val * 0.6, max_val], color="rgba(255,255,255,0.07)")],
        ),
    ))
    fig.update_layout(height=height, margin=dict(l=20, r=20, t=40, b=10))
    return fig
