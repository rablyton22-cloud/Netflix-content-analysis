"""Self-contained design system: injected once into the app."""
from __future__ import annotations

import streamlit as st

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root {
  --n-red: #E50914;
  --n-red-dark: #B20710;
  --n-red-glow: rgba(229, 9, 20, 0.35);
  --n-gold: #F5C518;
  --n-bg: #0B0B0F;
  --n-panel: rgba(20, 20, 31, 0.75);
  --n-card: rgba(26, 26, 40, 0.55);
  --n-raised: rgba(34, 34, 54, 0.85);
  --n-text: #E8E8EC;
  --n-muted: #9A9AB0;
  --n-green: #2EBD85;
  --n-blue: #4C9AFF;
  --n-purple: #9D4EDD;
  --n-cyan: #22D3EE;
  --n-orange: #FF8A3D;
  --n-line: rgba(255,255,255,0.08);
  --n-font-display: 'Bebas Neue', 'Oswald', sans-serif;
  --n-font-body: 'Inter', 'Segoe UI', sans-serif;
}

html, body, [class*="css"] {
  font-family: var(--n-font-body);
}

/* ------------------------------------------------ app background */
[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(1200px 700px at 85% -10%, rgba(229,9,20,0.18), transparent 60%),
    radial-gradient(1000px 600px at -10% 30%, rgba(76,154,255,0.10), transparent 55%),
    radial-gradient(900px 700px at 50% 110%, rgba(157,78,221,0.12), transparent 60%),
    linear-gradient(180deg, #0B0B0F 0%, #0D0D16 100%);
  color: var(--n-text);
}

[data-testid="stHeader"] { background: transparent; }
#MainMenu, [data-testid="stToolbar"] { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
.block-container { padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1280px; }

/* floating ambient orbs */
.stApp::before, .stApp::after {
  content: "";
  position: fixed;
  width: 42vw; height: 42vw;
  max-width: 640px; max-height: 640px;
  border-radius: 50%;
  filter: blur(120px);
  opacity: .14;
  z-index: 0;
  pointer-events: none;
  animation: orb 18s ease-in-out infinite alternate;
}
.stApp::before { background: #E50914; top: -12%; right: -8%; }
.stApp::after  { background: #4C9AFF; bottom: -14%; left: -10%; animation-delay: -9s; }
@keyframes orb {
  from { transform: translate3d(0,0,0) scale(1); }
  to   { transform: translate3d(-60px, 40px, 0) scale(1.15); }
}

/* ------------------------------------------------- page transition */
div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] {
  animation: pageIn .4s cubic-bezier(.2,.7,.2,1) both;
}
@keyframes pageIn {
  0%   { opacity: 0; transform: translateY(14px); }
  100% { opacity: 1; transform: translateY(0); }
}

@keyframes revealUp {
  0%   { opacity: 0; transform: translateY(26px); }
  100% { opacity: 1; transform: translateY(0); }
}
.reveal { animation: revealUp .7s cubic-bezier(.2,.7,.2,1) both; }
.reveal.d1 { animation-delay: .08s; } .reveal.d2 { animation-delay: .16s; }
.reveal.d3 { animation-delay: .24s; } .reveal.d4 { animation-delay: .32s; }
.reveal.d5 { animation-delay: .40s; } .reveal.d6 { animation-delay: .48s; }

/* ------------------------------------------------- glass system */
.glass {
  background: linear-gradient(160deg, rgba(255,255,255,0.06), rgba(255,255,255,0.015));
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 18px;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.45);
  position: relative;
  overflow: hidden;
}
.glass::after {
  content: ""; position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(115deg, transparent 20%, rgba(255,255,255,0.06) 45%, transparent 65%);
  background-size: 250% 100%;
  animation: sheen 6s ease-in-out infinite;
}
@keyframes sheen { 0%,55% { background-position: 120% 0; } 100% { background-position: -120% 0; } }
.glass.pad { padding: 1.25rem; }
.glass.grow { transition: transform .3s ease, box-shadow .3s ease, border-color .3s ease; }
.glass.grow:hover {
  transform: translateY(-4px);
  border-color: rgba(229,9,20,0.5);
  box-shadow: 0 18px 46px rgba(0,0,0,0.6), 0 0 30px rgba(229,9,20,0.18);
}
.glass.grow:hover::after { background-position: 0% 0; }

/* --------------------------------------------------- hero */
.hero {
  position: relative;
  border-radius: 26px;
  overflow: hidden;
  min-height: 460px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: clamp(2rem, 6vw, 4.5rem);
  background:
    radial-gradient(900px 420px at 78% 20%, rgba(229,9,20,0.55), transparent 55%),
    radial-gradient(600px 400px at 15% 90%, rgba(157,78,221,0.35), transparent 55%),
    linear-gradient(120deg, #14141F 0%, #1A0B10 55%, #0B0B0F 100%);
  border: 1px solid rgba(255,255,255,0.10);
  box-shadow: 0 30px 90px rgba(0,0,0,0.7);
}
.hero::before {
  content: ""; position: absolute; inset: 0;
  background:
    repeating-linear-gradient(90deg, transparent 0 140px, rgba(255,255,255,0.035) 141px),
    linear-gradient(180deg, transparent 60%, rgba(0,0,0,0.5));
}
.hero::after {
  content: ""; position: absolute; inset: 0;
  background-image:
    radial-gradient(rgba(255,255,255,0.5) 1px, transparent 1.4px);
  background-size: 34px 34px;
  mask-image: radial-gradient(700px 300px at 50% 0%, black, transparent);
  opacity: .35;
}
.hero-eyebrow {
  display: inline-flex; align-items: center; gap: .5rem;
  font-size: .78rem; letter-spacing: .18em; text-transform: uppercase;
  color: var(--n-gold);
  border: 1px solid rgba(245,197,24,0.35);
  background: rgba(245,197,24,0.08);
  padding: .35rem .8rem; border-radius: 999px;
  width: fit-content; margin-bottom: 1.1rem;
  animation: pulseDot 2.4s ease-in-out infinite;
}
@keyframes pulseDot { 0%,100% { box-shadow: 0 0 0 0 rgba(245,197,24,0.4);} 50% { box-shadow: 0 0 0 7px rgba(245,197,24,0);} }
.hero-title {
  font-family: var(--n-font-display);
  font-size: clamp(3.4rem, 9vw, 6.2rem);
  line-height: .95;
  letter-spacing: .02em;
  margin: 0;
  color: #fff;
  text-shadow: 0 6px 40px rgba(0,0,0,0.6);
}
.hero-title .accent {
  color: var(--n-red);
  -webkit-text-stroke: 2px rgba(229,9,20,0.25);
}
.hero-sub {
  max-width: 620px;
  color: var(--n-muted);
  font-size: 1.06rem;
  line-height: 1.65;
  margin-top: 1.1rem;
}
.hero-cta { display: flex; flex-wrap: wrap; gap: .8rem; margin-top: 1.6rem; }

/* ------------------------------------------------- buttons */
.btn {
  display: inline-flex; align-items: center; gap: .5rem;
  border-radius: 12px; padding: .72rem 1.5rem;
  font-weight: 700; font-size: .92rem; letter-spacing: .01em;
  text-decoration: none; cursor: pointer; transition: all .25s ease;
  border: 1px solid transparent;
}
.btn-primary {
  background: linear-gradient(135deg, #E50914, #B20710);
  color: #fff !important;
  box-shadow: 0 8px 28px rgba(229,9,20,0.45);
}
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 14px 40px rgba(229,9,20,0.6); }
.btn-ghost {
  background: rgba(255,255,255,0.05);
  color: var(--n-text) !important;
  border-color: rgba(255,255,255,0.18);
  backdrop-filter: blur(8px);
}
.btn-ghost:hover { background: rgba(255,255,255,0.12); transform: translateY(-2px); }

/* --------------------------------------------------- KPI counters */
.kpi-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 1rem; }
.kpi {
  border-radius: 18px; padding: 1.15rem 1.25rem;
  background: linear-gradient(160deg, rgba(255,255,255,0.07), rgba(255,255,255,0.02));
  border: 1px solid rgba(255,255,255,0.10);
  backdrop-filter: blur(14px);
  position: relative; overflow: hidden;
  transition: transform .3s ease, box-shadow .3s ease;
}
.kpi:hover { transform: translateY(-4px) scale(1.01); box-shadow: 0 16px 40px rgba(0,0,0,0.5); }
.kpi .kpi-icon {
  position: absolute; top: .7rem; right: .9rem; font-size: 1.6rem; opacity: .9;
}
.kpi .kpi-label { font-size: .72rem; letter-spacing: .14em; text-transform: uppercase; color: var(--n-muted); font-weight: 600; }
.kpi .kpi-value {
  font-family: var(--n-font-display);
  font-size: clamp(1.9rem, 4vw, 2.6rem);
  line-height: 1.05; margin-top: .2rem;
  background: linear-gradient(120deg, #fff, #c9c9dc);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.kpi .kpi-bar { height: 3px; margin-top: .65rem; border-radius: 2px; background: rgba(255,255,255,0.08); }
.kpi .kpi-bar > span { display: block; height: 100%; border-radius: 2px; }
.kpi .kpi-foot { margin-top: .45rem; font-size: .72rem; color: var(--n-muted); }

/* --------------------------------------------------- section headers */
.sec-head { display: flex; align-items: center; gap: .7rem; margin: 1.6rem 0 .9rem; }
.sec-head .sec-ico {
  width: 38px; height: 38px; display: grid; place-items: center;
  font-size: 1.05rem; border-radius: 11px;
  background: linear-gradient(135deg, rgba(229,9,20,0.25), rgba(229,9,20,0.05));
  border: 1px solid rgba(229,9,20,0.4);
}
.sec-head h2 { font-size: 1.5rem; font-weight: 800; margin: 0; letter-spacing: -.01em; }
.sec-head .sec-sub { color: var(--n-muted); font-size: .86rem; margin-top: .1rem; }
.sec-head .sec-line { flex: 1; height: 1px; margin-left: .4rem; background: linear-gradient(90deg, rgba(255,255,255,0.18), transparent); }

/* --------------------------------------------------- pills / badges */
.pill {
  display: inline-flex; align-items: center; gap: .3rem;
  padding: .24rem .62rem; border-radius: 999px;
  font-size: .72rem; font-weight: 600; letter-spacing: .02em;
  border: 1px solid var(--n-line);
  background: rgba(255,255,255,0.04);
  color: var(--n-muted);
}
.pill.red   { color: #ff8a8f; border-color: rgba(229,9,20,0.5); background: rgba(229,9,20,0.12); }
.pill.gold  { color: #ffd968; border-color: rgba(245,197,24,0.45); background: rgba(245,197,24,0.10); }
.pill.green { color: #7ff0bf; border-color: rgba(46,189,133,0.45); background: rgba(46,189,133,0.10); }
.pill.blue  { color: #a8ccff; border-color: rgba(76,154,255,0.45); background: rgba(76,154,255,0.10); }
.pill.purple{ color: #d2a6ff; border-color: rgba(157,78,221,0.45); background: rgba(157,78,221,0.10); }
.pill.cyan  { color: #9de9ff; border-color: rgba(34,211,238,0.45); background: rgba(34,211,238,0.10); }

/* --------------------------------------------------- netflix N logo */
.n-logo {
  font-family: var(--n-font-display);
  display: inline-grid; place-items: center;
  width: 34px; height: 34px; border-radius: 9px;
  background: linear-gradient(135deg, #E50914, #99030a);
  color: #fff; font-size: 1.35rem; line-height: 1;
  box-shadow: 0 4px 18px rgba(229,9,20,0.55);
  transform: skew(-6deg);
}

/* --------------------------------------------------- sidebar */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0E0E17 0%, #101020 100%);
  border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding: 1rem .9rem; }
.side-brand { display: flex; align-items: center; gap: .7rem; padding: .3rem .2rem 1rem; }
.side-brand .side-title { font-weight: 800; font-size: .98rem; line-height: 1.15; }
.side-brand .side-title small { display: block; color: var(--n-muted); font-weight: 500; font-size: .68rem; letter-spacing: .06em; }

/* navigation radio -> premium nav items */
[data-testid="stSidebar"] [data-testid="stRadio"] > div { gap: .3rem; }
[data-testid="stSidebar"] [data-testid="stRadio"] label {
  display: flex; align-items: center; gap: .7rem;
  width: 100%;
  padding: .6rem .8rem;
  margin: .1rem 0;
  border-radius: 12px;
  cursor: pointer;
  font-size: .92rem; font-weight: 500; color: var(--n-muted);
  border: 1px solid transparent;
  transition: all .22s ease;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
  background: rgba(255,255,255,0.06); color: var(--n-text);
  transform: translateX(3px);
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
  background: linear-gradient(90deg, rgba(229,9,20,0.22), rgba(229,9,20,0.05));
  border-color: rgba(229,9,20,0.45);
  color: #fff; font-weight: 700;
  box-shadow: inset 3px 0 0 var(--n-red);
}
[data-testid="stSidebar"] [data-testid="stRadio"] label input { display: none; }
[data-testid="stSidebar"] [data-testid="stRadio"] label div:first-child { display: none; }
[data-testid="stSidebar"] hr { border-color: var(--n-line); }

/* --------------------------------------------------- form widgets */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stTextArea"] textarea {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  border-radius: 12px !important;
  color: var(--n-text) !important;
  caret-color: var(--n-red);
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--n-red) !important;
  box-shadow: 0 0 0 3px rgba(229,9,20,0.18) !important;
}
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
  background: rgba(255,255,255,0.05) !important;
  border-radius: 12px !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
}
[data-testid="stSlider"] [role="slider"] { background: var(--n-red); border: 2px solid #fff; }
[data-testid="stSlider"] [data-testid="stSliderTickBar"] * { color: var(--n-muted); }
[data-testid="stBaseButton-primary"] { border-radius: 12px !important; }
[data-testid="stBaseButton-primary"]:hover { transform: translateY(-1px); box-shadow: 0 8px 24px rgba(229,9,20,0.4); }
[data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-tertiary"] { border-radius: 12px !important; }
[data-testid="stBaseButton-secondary"]:hover, [data-testid="stBaseButton-tertiary"]:hover { background: rgba(255,255,255,0.09) !important; }

[data-testid="stExpander"] {
  background: var(--n-card);
  border: 1px solid var(--n-line);
  border-radius: 16px;
  backdrop-filter: blur(10px);
}
[data-testid="stExpander"] details { border-radius: 16px; }
[data-testid="stExpander"] summary { font-weight: 600; }

/* tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] { gap: .3rem; border-bottom: 1px solid var(--n-line); }
[data-testid="stTabs"] [data-baseweb="tab"] {
  border-radius: 10px 10px 0 0;
  padding: .55rem 1rem;
  font-weight: 600; color: var(--n-muted);
}
[data-testid="stTabs"] [data-baseweb="tab"]:hover { background: rgba(255,255,255,0.05); }
[data-testid="stTabs"] [aria-selected="true"] {
  color: #fff;
  box-shadow: inset 0 2px 0 var(--n-red);
  background: rgba(255,255,255,0.04);
}

/* dataframe */
[data-testid="stDataFrame"] { border: 1px solid var(--n-line); border-radius: 14px; overflow: hidden; }

/* code blocks */
[data-testid="stCode"] { border-radius: 14px !important; border: 1px solid var(--n-line) !important; }
code { color: #ff9ea4; }

/* --------------------------------------------------- result / search cards */
.result-card {
  display: flex; gap: 1rem; align-items: flex-start;
  padding: 1rem 1.1rem; border-radius: 14px;
  background: var(--n-card);
  border: 1px solid var(--n-line);
  transition: all .25s ease;
}
.result-card:hover { transform: translateY(-2px); border-color: rgba(229,9,20,0.4); background: var(--n-raised); }
.result-card .rc-poster {
  width: 64px; height: 90px; flex: 0 0 auto; border-radius: 8px;
  display: grid; place-items: center; font-size: 1.5rem;
  background: linear-gradient(135deg, #2a0a0e, #101020);
  border: 1px solid rgba(229,9,20,0.35);
  box-shadow: inset 0 0 30px rgba(229,9,20,0.12);
}
.result-card .rc-title { font-weight: 800; font-size: 1.02rem; }
.result-card .rc-meta { font-size: .78rem; color: var(--n-muted); margin-top: .2rem; }
.result-card .rc-desc { font-size: .84rem; color: var(--n-muted); margin-top: .45rem; line-height: 1.55; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

/* --------------------------------------------------- insight cards */
.insight-card { padding: 1.25rem; border-radius: 16px; margin-bottom: .9rem; }
.insight-card .ic-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; }
.insight-card .ic-icon { font-size: 1.6rem; }
.insight-card .ic-title { font-weight: 800; font-size: 1.05rem; margin: 0; }
.insight-card .ic-body { color: var(--n-muted); font-size: .88rem; line-height: 1.6; margin: .55rem 0 .8rem; }
.conf-meter { height: 6px; border-radius: 3px; background: rgba(255,255,255,0.08); overflow: hidden; }
.conf-meter > span { display: block; height: 100%; border-radius: 3px; background: linear-gradient(90deg, var(--n-red), var(--n-gold)); }
.conf-tag { font-size: .7rem; color: var(--n-muted); display: flex; justify-content: space-between; margin-top: .35rem; }

/* --------------------------------------------------- timeline */
.timeline { position: relative; padding-left: 26px; }
.timeline::before { content: ""; position: absolute; left: 8px; top: 4px; bottom: 4px; width: 2px;
  background: linear-gradient(180deg, var(--n-red), rgba(229,9,20,0.05)); border-radius: 2px; }
.tl-item { position: relative; padding-bottom: 1.3rem; }
.tl-item::before { content: ""; position: absolute; left: -25px; top: 4px; width: 12px; height: 12px; border-radius: 50%;
  background: var(--n-red); box-shadow: 0 0 0 4px rgba(229,9,20,0.2), 0 0 14px rgba(229,9,20,0.6); }
.tl-item .tl-date { font-size: .72rem; letter-spacing: .12em; text-transform: uppercase; color: var(--n-gold); font-weight: 700; }
.tl-item .tl-title { font-weight: 800; margin-top: .15rem; }
.tl-item .tl-text { color: var(--n-muted); font-size: .85rem; line-height: 1.55; }

/* --------------------------------------------------- skill bars */
.skill { margin-bottom: 1rem; }
.skill .sk-head { display: flex; justify-content: space-between; font-size: .85rem; font-weight: 600; margin-bottom: .35rem; }
.skill .sk-track { height: 8px; border-radius: 4px; background: rgba(255,255,255,0.08); overflow: hidden; }
.skill .sk-fill { display: block; height: 100%; width: 0; border-radius: 4px;
  background: linear-gradient(90deg, var(--n-red), var(--n-gold));
  animation: skfill 1.2s cubic-bezier(.2,.7,.2,1) forwards; }
@keyframes skfill { to { width: var(--w); } }

/* --------------------------------------------------- story / quote */
.quote {
  border-left: 4px solid var(--n-red);
  padding: .9rem 1.2rem; margin: 1.2rem 0;
  background: rgba(229,9,20,0.06);
  border-radius: 0 14px 14px 0;
  font-style: italic; color: var(--n-muted); line-height: 1.7;
}
.big-number {
  font-family: var(--n-font-display); font-size: clamp(3rem, 7vw, 5rem);
  line-height: 1; margin: 0;
  background: linear-gradient(120deg, var(--n-red), #ff6a6f);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.chapter-num { font-family: var(--n-font-display); font-size: 4.5rem; line-height: 1; color: rgba(229,9,20,0.28); }

/* --------------------------------------------------- footer */
.app-footer {
  margin-top: 3rem; padding: 1.6rem 0 .4rem;
  border-top: 1px solid var(--n-line);
  color: var(--n-muted); font-size: .8rem;
  display: flex; flex-wrap: wrap; gap: .6rem 1.4rem; justify-content: space-between; align-items: center;
}
.app-footer .foot-brand { display: flex; align-items: center; gap: .5rem; font-weight: 700; color: var(--n-text); }

/* --------------------------------------------------- scrollbar */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.14); border-radius: 6px; }
::-webkit-scrollbar-thumb:hover { background: var(--n-red); }

/* --------------------------------------------------- SQL console */
.sql-editor {
  font-family: 'JetBrains Mono', 'Cascadia Code', Consolas, monospace;
  font-size: .86rem; line-height: 1.6;
  color: #d6e2ff;
  background: #0A0A12 !important;
  border: 1px solid rgba(76,154,255,0.25) !important;
  border-radius: 14px !important;
}
.sql-chip { font-family: 'JetBrains Mono', Consolas, monospace; font-size: .74rem; }
.sql-key { color: #ff6a9c; font-weight: 700; } .sql-str { color: #9de9a6; }
.sql-num { color: #ffd27a; } .sql-fn { color: #6fb3ff; } .sql-cmt { color: #5c5c72; font-style: italic; }

/* --------------------------------------------------- powerbi gallery */
.pbi-card { padding: 1.2rem; }
.pbi-card .pbi-title { font-weight: 800; font-size: 1.08rem; display: flex; align-items: center; gap: .55rem; }
.pbi-card .pbi-desc { color: var(--n-muted); font-size: .85rem; line-height: 1.6; margin: .5rem 0 .9rem; }
.pbi-thumb {
  border-radius: 12px; overflow: hidden; border: 1px solid var(--n-line);
  background: linear-gradient(160deg, #13131f, #0b0b12);
  padding: .9rem; display: grid; gap: .5rem;
}
.pbi-thumb .tile { border-radius: 8px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07); }
.pbi-thumb .tile-kpi { display: flex; justify-content: space-between; align-items: baseline; padding: .5rem .7rem; }
.pbi-thumb .tile-kpi b { font-family: var(--n-font-display); font-size: 1.15rem; }

/* --------------------------------------------------- responsive */
@media (max-width: 768px) {
  .block-container { padding: 1rem .9rem 3rem; }
  .hero { min-height: 400px; padding: 2rem 1.4rem; }
  .hero-title { font-size: clamp(2.6rem, 12vw, 4rem); }
  .kpi-row { grid-template-columns: repeat(2, 1fr); }
  .sec-head h2 { font-size: 1.25rem; }
  .app-footer { flex-direction: column; align-items: flex-start; }
}
@media (max-width: 460px) {
  .kpi-row { grid-template-columns: 1fr; }
}
"""


def inject() -> None:
    """Inject the global design system (idempotent per page render)."""
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
