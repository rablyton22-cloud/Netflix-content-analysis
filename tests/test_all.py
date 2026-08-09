"""Run the page-checker for every page in a fresh subprocess each time."""
from __future__ import annotations

import os
import subprocess
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = ["Home", "Dashboard", "Insights", "SQL Console", "Data Cleaning",
         "Power BI", "World Map", "Story", "About"]


def main() -> int:
    failures = []
    for page in PAGES:
        print(f"▶ {page} ...", flush=True)
        proc = subprocess.run(
            [sys.executable, os.path.join(HERE, "run_page_check.py"), page],
            capture_output=True, text=True, timeout=600,
        )
        out = (proc.stdout or "").strip().splitlines()
        tail = out[-1] if out else ""
        print(textwrap.indent("\n".join(out[-3:]), "   "), flush=True)
        if proc.returncode != 0 or "OK" not in tail:
            failures.append((page, proc.returncode, proc.stderr[-2000:]))

    if failures:
        print("\nFAILURES:", flush=True)
        for page, code, err in failures:
            print(f"  {page}: exit={code}\n{err}", flush=True)
        return 1
    print("\nALL PAGES OK", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
