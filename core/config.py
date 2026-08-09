"""Global configuration: brand, paths, color system, page registry."""
from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "netflix_titles.csv.csv"
ASSETS_DIR = BASE_DIR / "assets"
LOTTIE_DIR = ASSETS_DIR / "lottie"

BRAND = "Netflix Content Analysis"
BRAND_TAGLINE = "Streaming intelligence, beautifully visualised."

# ---------------------------------------------------------------- color system
class Colors:
    BG_MAIN = "#0B0B0F"
    BG_PANEL = "#14141F"
    BG_CARD = "#1A1A28"
    BG_RAISED = "#222236"
    RED = "#E50914"
    RED_DARK = "#B20710"
    RED_GLOW = "rgba(229, 9, 20, 0.45)"
    GOLD = "#F5C518"
    TEXT = "#E8E8EC"
    MUTED = "#9A9AB0"
    GREEN = "#2EBD85"
    BLUE = "#4C9AFF"
    PURPLE = "#9D4EDD"
    CYAN = "#22D3EE"
    ORANGE = "#FF8A3D"
    PINK = "#FF5E9C"
    LINE = "rgba(255,255,255,0.08)"
    WHITE = "#FFFFFF"


# ---------------------------------------------------------------- fonts
FONT_DISPLAY = "'Bebas Neue', 'Oswald', sans-serif"
FONT_BODY = "'Inter', 'Segoe UI', sans-serif"

# ---------------------------------------------------------------- page registry
PAGES = [
    ("Home", "🏠", "Landing hero"),
    ("Dashboard", "📊", "Analytics"),
    ("Insights", "💡", "Business insights"),
    ("SQL Console", "🗄️", "Query engine"),
    ("Data Cleaning", "🧹", "Pipeline"),
    ("Power BI", "📈", "Report gallery"),
    ("World Map", "🌍", "Geospatial"),
    ("Story", "🎬", "Narrative"),
    ("About", "👤", "Profile"),
]
