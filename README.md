# Netflix Content Analysis Dashboard 🎬

A premium, production-grade **Streamlit** application that turns the 8,807-row
Netflix catalogue into a cinematic analytics product — glassmorphism UI, animated
counters, offline Lottie animations, interactive Plotly charts and a full
analytics workbench.

## ✨ Features

| Page | What it does |
| --- | --- |
| **Home** | Netflix-style hero landing with animated KPI strip and feature launcher |
| **Dashboard** | Search, global filters, animated KPI counters, 8 interactive Plotly charts, titles explorer + CSV export |
| **Insights** | Rule-based business insight generator with confidence scores, trend arrows and an executive briefing export |
| **SQL Console** | Live DuckDB playground — 10 production starter queries, syntax-highlighted results, query history, schema explorer |
| **Data Cleaning** | Auditable 8-step pipeline with before/after metrics, missing-data heatmaps and quality gauge |
| **Power BI** | Report-style dashboard gallery (6 templates) with live tile previews, DAX snippets and PNG export via Kaleido |
| **World Map** | ISO-coded choropleth of production footprint with country drill-down |
| **Story** | Chaptered data narrative with timeline, big numbers and supporting charts |
| **About** | Analyst profile, animated skill bars, timeline and contact cards |

## 🧰 Stack

- **Streamlit 1.60** — shell, widgets, caching, AppTest harness
- **Pandas / NumPy** — cleaning pipeline + feature engineering
- **Plotly** — interactive charts with a custom dark theme
- **DuckDB** — in-app SQL engine over the catalogue
- **Kaleido** — PNG export of Power BI report charts
- **streamlit-lottie** — animations built **offline** as generated Lottie JSON (no CDN)
- **Custom CSS** — glassmorphism, hover effects, animated counters, responsive grid

## 🚀 Quick start

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the printed Local URL (default `http://localhost:8501`).

## 🗂️ Project layout

```
app.py                  # entry point: theme, sidebar nav, routing
.streamlit/config.toml  # dark theme + server options
core/
  config.py             # brand, colours, page registry
  data_loader.py        # caching + 8-step cleaning pipeline
  filters.py            # shared sidebar filters
  insights.py           # business insight detectors
  geocode.py            # country → ISO-3 mapping
components/
  style.py              # full design system (CSS)
  ui.py                 # glass cards, sections, pills, hero, footer
  kpi.py                # animated count-up counters
  charts.py             # Plotly chart library
  lottie_loader.py      # offline Lottie animation factory
  nav.py                # session-safe navigation
pages/                  # one module per page (home, dashboard, insights, …)
tests/
  test_all.py           # runs every page in a fresh subprocess
  run_page_check.py     # per-page AppTest render check
```

## 🧪 Tests

```bash
python tests/test_all.py
```

Each page is rendered headlessly through `streamlit.testing.v1.AppTest` in its own
subprocess and asserted to be exception-free.

## 🧹 Data pipeline

The raw CSV is cleaned through 8 documented steps — whitespace, imputation, date
parsing, duration normalisation, categorical splitting, feature engineering,
deduplication and dtype finalisation. The cleaned frame (22 columns) drives every
page and can be downloaded from the app.

---

Built as a premium SaaS-style analytics shell — data engineering, visual design and
storytelling in one product.
