"""SQL Console — DuckDB playground over the cleaned catalogue."""
from __future__ import annotations

import html
import re
import time

import duckdb
import streamlit as st

from components import ui
from core.data_loader import clean_data

EXAMPLE_QUERIES = {
    "Top 10 genres by title count": """
SELECT genre, COUNT(*) AS titles
FROM (SELECT UNNEST(genres) AS genre FROM netflix)
GROUP BY genre
ORDER BY titles DESC
LIMIT 10;
""".strip(),
    "Content added per year (movies vs shows)": """
SELECT year_added,
       COUNT(*) FILTER (WHERE type = 'Movie')  AS movies,
       COUNT(*) FILTER (WHERE type = 'TV Show') AS shows
FROM netflix
WHERE year_added IS NOT NULL
GROUP BY year_added
ORDER BY year_added;
""".strip(),
    "Longest movies in the catalogue": """
SELECT title, release_year, duration_min
FROM netflix
WHERE type = 'Movie' AND duration_min IS NOT NULL
ORDER BY duration_min DESC
LIMIT 15;
""".strip(),
    "Multi-country productions": """
SELECT title, type, release_year, countries
FROM netflix
WHERE list_length(countries) > 3
ORDER BY list_length(countries) DESC
LIMIT 15;
""".strip(),
    "Directors with the most titles": """
SELECT director, COUNT(*) AS titles
FROM netflix
WHERE director != 'Not Available'
GROUP BY director
ORDER BY titles DESC
LIMIT 15;
""".strip(),
    "Youngest catalogue countries (avg release year)": """
SELECT primary_country, COUNT(*) AS titles, ROUND(AVG(release_year)) AS avg_release_year
FROM netflix
WHERE primary_country != 'Not Available'
GROUP BY primary_country
HAVING COUNT(*) >= 20
ORDER BY avg_release_year DESC
LIMIT 15;
""".strip(),
    "Rating mix in the last 5 years": """
SELECT rating, COUNT(*) AS titles,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM netflix
WHERE release_year >= 2017
  AND rating NOT IN ('Not Available')
GROUP BY rating
ORDER BY titles DESC;
""".strip(),
    "Longest-running series by seasons": """
SELECT title, duration_seasons, release_year
FROM netflix
WHERE type = 'TV Show' AND duration_seasons IS NOT NULL
ORDER BY duration_seasons DESC
LIMIT 15;
""".strip(),
    "Genre momentum 2018→2021": """
SELECT genre,
       COUNT(*) FILTER (WHERE year_added BETWEEN 2018 AND 2019) AS early,
       COUNT(*) FILTER (WHERE year_added BETWEEN 2020 AND 2021) AS late
FROM (SELECT UNNEST(genres) AS genre, year_added FROM netflix)
WHERE year_added IS NOT NULL
GROUP BY genre
ORDER BY late - early DESC
LIMIT 12;
""".strip(),
    "Titles added per month (seasonality)": """
SELECT month_added, COUNT(*) AS titles
FROM netflix
WHERE month_added IS NOT NULL
GROUP BY month_added
ORDER BY month_added;
""".strip(),
}

_SQL_KEYWORDS = r"\b(SELECT|FROM|WHERE|GROUP\s+BY|ORDER\s+BY|LIMIT|HAVING|AS|BY|AND|OR|NOT|NULL|COUNT|SUM|AVG|ROUND|FILTER|OVER|BETWEEN|UNNEST|CASE|WHEN|THEN|ELSE|END|JOIN|ON|IN|IS|DESC|ASC|FILTER)\b"


def _highlight_sql(sql: str) -> str:
    """Very light SQL syntax highlighter -> HTML."""
    def repl(m):
        w = m.group(0)
        return f'<span class="sql-key">{w}</span>'

    out = re.sub(_SQL_KEYWORDS, repl, html.escape(sql), flags=re.IGNORECASE)
    out = re.sub(r"(\d+\.?\d*)", r'<span class="sql-num">\1</span>', out)
    out = re.sub(r"('[^']*')", r'<span class="sql-str">\1</span>', out)
    return out


@st.cache_resource(show_spinner="Booting DuckDB engine…")
def _get_engine():
    con = duckdb.connect()
    df = clean_data()
    con.register("netflix", df)
    return con, df


def _run_query(con, sql: str):
    t0 = time.perf_counter()
    res = con.execute(sql).fetchdf()
    return res, time.perf_counter() - t0


def _schema_panel(con, df) -> None:
    st.markdown("### 🗂️ Schema — `netflix`")
    schema = con.execute("DESCRIBE netflix").fetchdf()
    st.dataframe(schema, width="stretch", height=360)
    ui.info_banner("ℹ️", "The catalogue is materialised as a DuckDB table named `netflix`. "
                         "Use UNNEST on `genres` / `countries` list columns for per-item analysis.")


def render() -> None:
    ui.section_header("🗄️", "SQL Console",
                      "Query the 8,807-row catalogue with DuckDB — zero setup, real SQL")

    con, df = _get_engine()

    tab_console, tab_examples, tab_schema = st.tabs(["🖥️ Console", "📚 Example Queries", "🗂️ Schema"])
    with tab_console:
        c1, c2 = st.columns([3.4, 1], gap="large")
        with c1:
            sql = st.text_area(
                "Query", value=st.session_state.get("sql_editor", EXAMPLE_QUERIES["Top 10 genres by title count"]),
                height=210, key="sql_editor", label_visibility="collapsed",
                help="Write any SQL — DuckDB powers the engine.",
            )
        with c2:
            st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
            run = st.button("▶ Run query", width="stretch", type="primary")
            if st.button("↺ Reset", width="stretch"):
                st.session_state.pop("sql_results", None)
                st.session_state.pop("sql_meta", None)
                st.rerun()

        if run and sql.strip():
            with st.spinner("Executing…"):
                try:
                    res, dt = _run_query(con, sql)
                    st.session_state["sql_results"] = res
                    st.session_state["sql_meta"] = {
                        "sql": sql, "rows": len(res), "cols": list(res.columns), "time": dt,
                    }
                    hist = st.session_state.setdefault("sql_history", [])
                    hist.append(sql)
                except Exception as e:
                    st.error(f"Query failed: {e}")

        meta = st.session_state.get("sql_meta")
        if meta:
            st.markdown(
                f'<div style="display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:.6rem">'
                f'<span class="pill green">✔ {meta["rows"]:,} rows</span>'
                f'<span class="pill blue">⚡ {meta["time"] * 1000:.0f} ms</span>'
                f'<span class="pill purple">{len(meta["cols"])} columns</span></div>',
                unsafe_allow_html=True,
            )
            st.markdown('<div class="sql-editor" style="padding:.9rem">'
                        + _highlight_sql(meta["sql"]) + '</div>', unsafe_allow_html=True)
            st.dataframe(st.session_state["sql_results"], width="stretch", height=420)
        else:
            ui.info_banner("💡", "Pick a query from the right, or write your own SQL below and press ▶ Run.")

        if st.session_state.get("sql_history"):
            with st.expander("🕘 Query history"):
                for q in reversed(st.session_state["sql_history"][-8:]):
                    st.markdown(f'<div class="sql-chip" style="color:var(--n-muted)">{html.escape(q)}</div>',
                                unsafe_allow_html=True)
                    st.divider()

    with tab_examples:
        st.markdown("### Copy a production-grade starter query")
        for name, q in EXAMPLE_QUERIES.items():
            with st.expander(name):
                st.code(q, language="sql")
                st.markdown(f'<span class="pill cyan">🔍 {name}</span>', unsafe_allow_html=True)
                if st.button("⚡ Load into console", key=f"load-{name}"):
                    st.session_state["sql_editor"] = q
                    st.rerun()

    with tab_schema:
        _schema_panel(con, df)

    ui.footer()
