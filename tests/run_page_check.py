"""Per-page render check via streamlit.testing.v1.AppTest.

Usage:  python tests/run_page_check.py <PageName>
Runs in its own process so engine threads never accumulate across pages.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from streamlit.testing.v1 import AppTest

PAGES = ["Home", "Dashboard", "Insights", "SQL Console", "Data Cleaning",
         "Power BI", "World Map", "Story", "About"]


def check(page: str) -> list[str]:
    at = AppTest.from_file("app.py", default_timeout=180)
    at.run()
    if page != "Home":
        radios = at.radio
        assert radios, "navigation radio not rendered"
        radios[0].set_value(page)
        at.run()
    return [e.value for e in at.exception]


if __name__ == "__main__":
    page = sys.argv[1]
    errs = check(page)
    print(f"{page}: {'OK' if not errs else 'FAIL ' + repr(errs)}", flush=True)
    os._exit(0 if not errs else 1)
