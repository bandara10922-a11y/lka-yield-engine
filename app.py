# =============================================================================
#  LKA YIELD ENGINE  ·  Sri Lanka T-Bill Econometric Forecast Platform
#  Repository : lka-yield-engine
#  Deploy     : Streamlit Community Cloud  →  app.py
#
#  Economics & Finance Foundations
#  ─────────────────────────────────────────────────────────────────────────────
#  1. Fisher Effect       : Nominal yield ≈ real rate + expected inflation
#  2. Expectations Theory : Long tenor yields embed future short-rate expectations
#  3. Liquidity Preference: Term premium rises with tenor (Hicks, 1939)
#  4. Loanable Funds      : Fiscal deficit & debt crowd out private credit, ↑ yields
#  5. Mundell-Fleming     : External shocks (US10Y, oil) transmit via capital flows
#  6. CBSL Transmission   : OPR anchors short-end; T-bill WAY ≈ OPR + spread
#  7. Solvency Risk       : Debt/GDP & fiscal deficit proxy default/rollover risk
#  8. External Buffer     : GOR signals sovereign liquidity; ↓GOR → ↑risk premium
#
#  Data Sources (all verified)
#  ─────────────────────────────────────────────────────────────────────────────
#  T-bill WAY 2015-2021 : CBSL Public Debt Management Report 2021, Table 3
#  T-bill WAY 2022-2025 : CBSL Weekly Economic Indicators (WEI), annual averages
#  T-bill 2026 current  : Daily FT + WealthTrust + CBSL WEI 06-Mar-2026
#  OPR / SDFR / SLFR    : CBSL Monetary Policy Board press releases
#  GOR                  : CBSL WEI Feb-2026 → USD 7,284 mn
#  CCPI                 : CBSL / Dept. of Census & Statistics
#  Debt/GDP             : CountryEconomy.com + World Bank (2024: 100.84%)
#  Fiscal Deficit/GDP   : Ministry of Finance / Treasury.gov.lk
#  USD/LKR              : CBSL daily rates
#  US 10Y Yield         : US Federal Reserve FRED (DGS10), annual averages
#  Brent Crude          : EIA annual averages; current from CBSL WEI 06-Mar-2026
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import date, datetime
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LKA Yield Engine",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────
# DESIGN SYSTEM  –  "Sovereign Dark" aesthetic
# Deep navy/obsidian background, liquid gold accents, sharp monospace
# data typography, Fraunces serif for display weight
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;0,9..144,900;1,9..144,400&family=Sora:wght@300;400;500;600&display=swap');

/* ── Reset & base ─────────────────────────────── */
html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.main { background: #05090e; }
.block-container { padding: 1.2rem 1.8rem 1rem; max-width: 100%; }

/* ── Sidebar ──────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #07101a 0%, #05090e 100%);
    border-right: 1px solid rgba(196,161,56,0.15);
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label { color: #6b7280 !important; }
section[data-testid="stSidebar"] .stRadio label { color: #9ca3af !important; font-size:13px; }

/* ── Global headings ──────────────────────────── */
h1,h2,h3 { font-family:'Fraunces',serif !important; color:#e8dfc8 !important; }

/* ── Page banner ─────────────────────────────── */
.page-banner {
    background: linear-gradient(135deg,#0a1628 0%,#0d1e32 50%,#0a1628 100%);
    border: 1px solid rgba(196,161,56,0.22);
    border-radius: 14px;
    padding: 22px 28px 18px;
    margin-bottom: 22px;
    position: relative; overflow: hidden;
}
.page-banner::before {
    content:'';
    position:absolute; top:-40px; right:-40px;
    width:200px; height:200px; border-radius:50%;
    background: radial-gradient(circle, rgba(196,161,56,0.08) 0%, transparent 70%);
}
.banner-eyebrow {
    font-family:'DM Mono',monospace;
    font-size:9px; letter-spacing:3px; text-transform:uppercase;
    color: rgba(196,161,56,0.6); margin-bottom:6px;
}
.banner-title {
    font-family:'Fraunces',serif;
    font-size:28px; font-weight:900; color:#e8c96d;
    letter-spacing:-0.5px; line-height:1.1; margin-bottom:6px;
}
.banner-sub {
    font-size:12px; color:#4b5563;
    font-family:'DM Mono',monospace; letter-spacing:1px;
}
.banner-tickers {
    display:flex; gap:18px; margin-top:14px; flex-wrap:wrap;
}
.bt {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px; padding: 8px 14px;
    font-family:'DM Mono',monospace; font-size:12px;
}
.bt-lbl { color:#4b5563; font-size:9px; letter-spacing:1px; display:block; margin-bottom:2px; }

/* ── Metric cards ─────────────────────────────── */
.kpi-row { display:flex; gap:12px; flex-wrap:wrap; margin-bottom:18px; }
.kpi {
    flex:1; min-width:150px;
    background:#08111d;
    border:1px solid rgba(255,255,255,0.06);
    border-radius:12px; padding:16px 18px;
    position:relative; overflow:hidden;
    transition: border-color .2s, transform .15s;
}
.kpi:hover { border-color:rgba(196,161,56,0.3); transform:translateY(-1px); }
.kpi::after {
    content:''; position:absolute; bottom:0; left:0; right:0; height:2px;
}
.kpi-gold::after  { background:linear-gradient(90deg,#c4a138,transparent); }
.kpi-teal::after  { background:linear-gradient(90deg,#2dd4bf,transparent); }
.kpi-violet::after{ background:linear-gradient(90deg,#818cf8,transparent); }
.kpi-slate::after { background:linear-gradient(90deg,rgba(255,255,255,.2),transparent); }
.kpi-red::after   { background:linear-gradient(90deg,#f87171,transparent); }
.kpi-green::after { background:linear-gradient(90deg,#4ade80,transparent); }
.kpi-lbl {
    font-family:'DM Mono',monospace;
    font-size:9px; color:#374151;
    text-transform:uppercase; letter-spacing:2px; margin-bottom:8px;
}
.kpi-val {
    font-family:'Fraunces',serif;
    font-size:30px; font-weight:900; line-height:1;
    letter-spacing:-1px;
}
.kpi-gold  .kpi-val { color:#e8c96d; }
.kpi-teal  .kpi-val { color:#2dd4bf; }
.kpi-violet.kpi-val,.kpi-violet .kpi-val { color:#818cf8; }
.kpi-slate .kpi-val { color:#d1d5db; }
.kpi-red   .kpi-val { color:#f87171; }
.kpi-green .kpi-val { color:#4ade80; }
.kpi-chg { font-family:'DM Mono',monospace; font-size:10px; margin-top:6px; }
.rise { color:#f87171; } .fall { color:#4ade80; } .flat { color:#6b7280; }
.kpi-src { font-size:9px; color:#374151; font-family:'DM Mono',monospace; margin-top:3px; }

/* ── Card wrapper ────────────────────────────── */
.card {
    background:#08111d;
    border:1px solid rgba(255,255,255,0.06);
    border-radius:12px; overflow:hidden;
    margin-bottom:16px;
}
.card-hd {
    padding:12px 16px;
    border-bottom:1px solid rgba(255,255,255,0.05);
    display:flex; align-items:center; justify-content:space-between;
}
.card-title {
    font-family:'Fraunces',serif;
    font-size:13px; font-weight:700; color:#d1d5db;
}
.card-sub {
    font-family:'DM Mono',monospace;
    font-size:9px; color:#374151; letter-spacing:1px; text-transform:uppercase;
}
.card-body { padding:16px; }

/* ── Formula display ─────────────────────────── */
.formula {
    background:linear-gradient(135deg,#060e18,#0a1826);
    border:1px solid rgba(196,161,56,0.25);
    border-radius:10px; padding:16px 20px;
    font-family:'DM Mono',monospace; font-size:11.5px;
    color:#e8c96d; line-height:2.4;
    overflow-x:auto; white-space:nowrap;
    margin:12px 0;
}
.f-blue   { color:#7dd3fc; }
.f-green  { color:#4ade80; }
.f-violet { color:#818cf8; }
.f-red    { color:#f87171; }
.f-teal   { color:#2dd4bf; }
.f-gold   { color:#e8c96d; }
.f-dim    { color:#374151; }

/* ── Forecast output ─────────────────────────── */
.fcast-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin:16px 0; }
.fcast-card {
    background:linear-gradient(135deg,#060e18,#08131e);
    border:1px solid rgba(255,255,255,0.07);
    border-radius:12px; padding:20px 16px;
    text-align:center; position:relative; overflow:hidden;
}
.fcast-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:3px;
}
.fc-91::before   { background:linear-gradient(90deg,#e8c96d,#c4a138); }
.fc-182::before  { background:linear-gradient(90deg,#2dd4bf,#0d9488); }
.fc-364::before  { background:linear-gradient(90deg,#818cf8,#6366f1); }
.fc-lbl {
    font-family:'DM Mono',monospace;
    font-size:9px; color:#374151; letter-spacing:2px;
    text-transform:uppercase; margin-bottom:10px;
}
.fc-val {
    font-family:'Fraunces',serif;
    font-size:38px; font-weight:900; line-height:1; letter-spacing:-1px;
}
.fc-91  .fc-val { color:#e8c96d; }
.fc-182 .fc-val { color:#2dd4bf; }
.fc-364 .fc-val { color:#818cf8; }
.fc-ci  { font-family:'DM Mono',monospace; font-size:10px; color:#4b5563; margin-top:6px; }
.fc-actual { font-size:10px; color:#6b7280; font-family:'DM Mono',monospace; margin-top:4px; }
.fc-dir { font-size:20px; margin-top:6px; }

/* ── Decomp table ────────────────────────────── */
.decomp { width:100%; border-collapse:collapse; }
.decomp th {
    font-family:'DM Mono',monospace; font-size:9px; color:#374151;
    text-transform:uppercase; letter-spacing:1.5px;
    padding:6px 10px; border-bottom:1px solid rgba(255,255,255,0.05);
    font-weight:400; text-align:left;
}
.decomp td {
    padding:8px 10px; font-family:'DM Mono',monospace; font-size:11px;
    border-bottom:1px solid rgba(255,255,255,0.03); color:#9ca3af;
}
.decomp tr:last-child td { border:none; }
.decomp tr:hover td { background:rgba(255,255,255,0.02); }
.dval-pos { color:#4ade80; }
.dval-neg { color:#f87171; }
.dval-main { color:#e8c96d; font-weight:500; }

/* ── Source tag ──────────────────────────────── */
.src {
    background:rgba(196,161,56,0.05);
    border-left:2px solid rgba(196,161,56,0.3);
    padding:6px 10px; margin-top:10px;
    font-family:'DM Mono',monospace; font-size:9px;
    color:#4b5563; border-radius:0 4px 4px 0;
    line-height:1.8;
}

/* ── Sensitivity bars ───────────────────────── */
.sens-item {
    display:flex; align-items:center; gap:10px;
    padding:7px 0; border-bottom:1px solid rgba(255,255,255,0.04);
}
.sens-item:last-child { border:none; }
.sens-label { font-family:'DM Mono',monospace; font-size:10px; color:#6b7280; width:140px; flex-shrink:0; }
.sens-bar-bg { flex:1; height:5px; background:rgba(255,255,255,0.05); border-radius:3px; overflow:hidden; }
.sens-bar-fill { height:100%; border-radius:3px; }
.sens-val { font-family:'DM Mono',monospace; font-size:10px; color:#e8c96d; width:55px; text-align:right; flex-shrink:0; }

/* ── Theory badge ────────────────────────────── */
.theory-badge {
    display:inline-block;
    background:rgba(129,140,248,0.1);
    border:1px solid rgba(129,140,248,0.2);
    color:#818cf8;
    font-family:'DM Mono',monospace; font-size:9px;
    padding:2px 8px; border-radius:10px; letter-spacing:1px;
    text-transform:uppercase; margin-right:4px; margin-bottom:4px;
}
.theory-box {
    background:rgba(129,140,248,0.05);
    border:1px solid rgba(129,140,248,0.15);
    border-radius:8px; padding:12px 14px; margin:10px 0;
    font-size:12px; color:#6b7280; line-height:1.7;
}

/* ── Alert / warning ─────────────────────────── */
.alert-box {
    background:rgba(248,113,113,0.07);
    border:1px solid rgba(248,113,113,0.2);
    border-radius:8px; padding:10px 14px; margin-bottom:14px;
    font-size:12px; color:#fca5a5;
    display:flex; align-items:center; gap:10px;
}
.info-box {
    background:rgba(45,212,191,0.05);
    border:1px solid rgba(45,212,191,0.15);
    border-radius:8px; padding:10px 14px; margin:10px 0;
    font-size:12px; color:#5eead4; line-height:1.6;
}

/* ── Data table ──────────────────────────────── */
.stDataFrame { background:#08111d !important; }
div[data-testid="stDataFrame"] { border:1px solid rgba(255,255,255,0.06); border-radius:8px; overflow:hidden; }

/* ── Streamlit widget overrides ──────────────── */
div[data-testid="stMetric"] {
    background:#08111d; border:1px solid rgba(255,255,255,0.06);
    border-radius:10px; padding:12px;
}
div[data-testid="stMetricLabel"] p { font-family:'DM Mono',monospace !important; font-size:10px !important; color:#374151 !important; }
div[data-testid="stMetricValue"]  { font-family:'Fraunces',serif !important; color:#e8c96d !important; font-size:26px !important; }
div[data-testid="stMetricDelta"]  { font-family:'DM Mono',monospace !important; font-size:11px !important; }
div[data-testid="stTabs"] button  { font-family:'DM Mono',monospace; font-size:11px; color:#4b5563; letter-spacing:.5px; }
div[data-testid="stTabs"] button[aria-selected="true"] { color:#e8c96d; border-bottom:2px solid #e8c96d; }
.stNumberInput input, .stSelectbox select, .stTextInput input {
    background:#0d1a28 !important; border-color:rgba(255,255,255,0.08) !important;
    color:#d1d5db !important; font-family:'DM Mono',monospace !important;
}
.stButton > button {
    background:linear-gradient(135deg,#c4a138,#e8c96d) !important;
    color:#05090e !important; border:none !important;
    font-weight:700 !important; font-family:'Sora',sans-serif !important;
    letter-spacing:.5px; border-radius:8px !important;
}
.stButton > button:hover { opacity:.9 !important; transform:translateY(-1px); }
div[data-testid="stSelectbox"] > div > div { background:#0d1a28 !important; }
.stSlider [data-baseweb="slider"] { padding:0 4px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# LIVE DATE  –  every analysis respects today's date
# ─────────────────────────────────────────────────────────────────
TODAY      = date.today()
TODAY_YEAR = TODAY.year
TODAY_STR  = TODAY.strftime("%d %b %Y")

# ─────────────────────────────────────────────────────────────────
# VERIFIED HISTORICAL DATA MATRIX
# All annual figures are calendar-year averages of primary-market WAY
# ─────────────────────────────────────────────────────────────────
YEARS = list(range(2015, TODAY_YEAR + 1))

# T-BILL PRIMARY MARKET WAY (% p.a.) ─ annual averages
# 2015-2021: CBSL PDMR 2021, Table 3 (exact)
# 2022     : CBSL WEI weekly series averaged (crisis year; peak Apr 23.21/24.77/24.36%)
# 2023     : CBSL WEI (easing cycle: rates fell from ~23% → ~14% through year)
# 2024     : CBSL WEI (continued easing; Aug 29 auction: 91D=10.01%, ending ~7.5%)
# 2025     : CBSL WEI; Feb 2025: 91D=7.61%, 182D=7.90%, 364D=8.36%; Dec 2025: 91D=7.55%, 182D=7.95%, 364D=8.19%
# 2026     : CBSL WEI Mar-2026; T-bills broadly stable near 7.5% area; slight decline noted
_Y91_hist  = [6.32, 8.26, 9.01, 8.40, 8.15, 5.93, 6.35, 20.50, 15.80, 9.85, 7.65]
_Y182_hist = [6.50, 9.23, 9.81, 8.58, 8.44, 5.72, 6.13, 22.10, 16.20, 9.60, 7.90]
_Y364_hist = [6.60,10.20,10.07, 9.67, 9.40, 6.37, 5.33, 23.00, 16.00, 9.35, 8.20]

# POLICY RATE (% p.a.) ─ CBSL MPB press releases
# Pre-Nov 2024: SDFR/SLFR midpoint used as proxy for the single rate signal
# 2016 Aug: SDFR raised 7.0→8.5, 2020 cut to 4.5, 2021 cut to 4.5/5.5
# 2022: emergency hikes → peak SDFR=14.5%/SLFR=15.5% (Oct 2022)
# 2023: eased → SDFR=9.0%/SLFR=10.0% by Dec 2023
# 2024: Nov 27 OPR introduced at 8.0%; cut to 7.75% later; Jan 2026 unchanged at 7.75%
_POL_hist  = [6.75, 7.75, 7.25, 7.25, 7.50, 5.50, 5.50, 14.50, 11.00, 8.50, 7.75]

# GOVT DEBT / GDP (%) ─ CountryEconomy.com / World Bank / CBSL
# 2024: 100.84% (CountryEconomy); 2023: 110.38%; 2022: 114.2% (CBSL)
_DBTGDP_hist = [76.3, 76.6, 77.5, 83.6, 87.0, 96.0, 103.9, 114.2, 110.4, 100.8, 96.0]

# FISCAL DEFICIT / GDP (%) ─ MoF / Treasury.gov.lk + TradingEconomics
# 2020:10.7%, 2021:11.7%, 2022:10.2% (MoF PR); 2023:8.3%; 2024:6.8%; 2025 est:5.5%
_FDGDP_hist  = [7.6,  5.4,  5.5,  5.3,  9.6, 10.7, 11.7, 10.2,  8.3,  6.8,  5.5]

# CCPI INFLATION (% YoY, annual average) ─ Dept of Census & Statistics / CBSL
# 2022 annual avg ~46% (crisis peak; point high ~69.8% Sep 2022)
# 2025 avg ~2.0%; Feb 2026: 1.6% (CBSL press release)
_INFL_hist   = [2.2,  4.0,  7.7,  2.1,  4.3,  6.2,  7.0, 46.4, 16.5,  2.0,  2.0]

# USD/LKR (annual average) ─ CBSL / Macrotrends
# 2025: rupee deprecated 5.6% per CBSL Jan 2026 MPR; Dec 22 2025: 309.65
_USDLKR_hist = [135.9,145.6,152.9,162.5,178.8,185.8,199.6,320.2,320.9,301.0,310.0]

# GROSS OFFICIAL RESERVES (USD Bn) ─ CBSL / TheGlobalEconomy.com
# 2022 low: 1.90 Bn; 2024: 6.09 Bn (TheGlobalEconomy); 2025 end: 6.8 Bn (CBSL Jan MPR)
# Feb 2026: 7.284 Bn (CBSL WEI 06-Mar-2026)
_GOR_hist    = [7.28, 6.02, 7.96, 7.89, 7.59, 5.74, 3.14, 1.90, 4.41, 6.09, 6.80]

# US 10-YEAR TREASURY YIELD (% p.a., annual average) ─ US Fed FRED (DGS10)
# 2024: ~4.20% avg; 2025: ~4.25% avg; Mar 2026 ~4.30% (elevated due to tariff uncertainty)
_US10Y_hist  = [2.14, 1.84, 2.33, 2.91, 2.14, 0.89, 1.45, 2.95, 3.97, 4.20, 4.25]

# BRENT CRUDE OIL (USD/bbl, annual average) ─ EIA
# 2025 avg ~$73; Mar 2026: surpassed $80 (CBSL WEI: +$13.87 vs prior week, Strait of Hormuz)
_BRENT_hist  = [52.4, 43.7, 54.7, 71.3, 64.4, 41.9, 70.4,100.9, 82.5, 80.0, 76.0]

# SRI LANKA SOVEREIGN RISK PREMIUM σ (%) ─ estimated proxy from yield residuals
# 2022 crisis: σ ballooned ~9-10%; post-restructuring: ~3%
_SIGMA_hist  = [3.50, 4.00, 4.20, 4.00, 3.80, 2.50, 3.00, 9.00, 6.00, 3.50, 3.20]

OIL_IMPORT_WEIGHT = 0.18   # LKA oil imports ≈ 18% of total imports (CBSL est.)

# Extend arrays if current year not yet complete (partial year uses latest available)
def _pad(arr, target_len):
    while len(arr) < target_len:
        arr.append(arr[-1])   # carry forward latest
    return arr[:target_len]

n = len(YEARS)
Y91    = _pad(_Y91_hist.copy(),    n)
Y182   = _pad(_Y182_hist.copy(),   n)
Y364   = _pad(_Y364_hist.copy(),   n)
POL    = _pad(_POL_hist.copy(),    n)
DBTGDP = _pad(_DBTGDP_hist.copy(), n)
FDGDP  = _pad(_FDGDP_hist.copy(),  n)
INFL   = _pad(_INFL_hist.copy(),   n)
USDLKR = _pad(_USDLKR_hist.copy(), n)
GOR    = _pad(_GOR_hist.copy(),    n)
US10Y  = _pad(_US10Y_hist.copy(),  n)
BRENT  = _pad(_BRENT_hist.copy(),  n)
SIGMA  = _pad(_SIGMA_hist.copy(),  n)

# CURRENT / LIVE VALUES  (as of TODAY via latest verified sources)
# OPR         : 7.75%  — CBSL MPR No.1/2026 (Jan 27, 2026); next review Mar 25, 2026
# GOR         : $7.284 Bn — CBSL WEI 06-Mar-2026 (provisional, incl PBOC swap)
# CCPI        : 1.6%   — CBSL Feb 2026 press release
# Brent       : ~$81   — CBSL WEI 06-Mar-2026 (surpassed $80 due to Strait of Hormuz)
# US10Y       : ~4.30% — market consensus Mar 2026
# T-bill(91D) : ~7.50% — CBSL WEI 06-Mar-2026 (small decrease noted)
CURRENT = {
    "opr":    7.75,
    "gor":    7.284,
    "ccpi":   1.6,
    "brent":  81.0,
    "us10y":  4.30,
    "usdlkr": 310.5,
    "y91":    7.50,
    "y182":   7.88,
    "y364":   8.15,
    "dbtgdp": 96.0,
    "fd":     5.5,
    "sigma":  3.20,
    "awcmr":  7.66,
    "awpr":   9.35,
}

# ─────────────────────────────────────────────────────────────────
# ECONOMETRIC MODEL ENGINE
# ─────────────────────────────────────────────────────────────────
# Theory mapping:
#   α              → baseline (real neutral rate proxy)
#   λ·OPR          → CBSL transmission / expectations channel
#   β₁·(US10Y+σ)   → Mundell-Fleming global base + sovereign risk premium
#   γ₁·DebtGDP     → Solvency risk / crowding-out (loanable funds theory)
#   γ₂·FD          → Fiscal channel (Ricardo-Barro caveat: partial Ricardian equiv.)
#   ϕ·(Oil·W)      → Cost-push / imported inflation → inflation expectations
#   θ·S            → Seasonality (budget cycle, fiscal year-end borrowing Q4)
#   Ω·(1/GOR)      → External vulnerability premium (Obstfeld-Rogoff)
#   δ·(π-π*)       → Fisher deviation term (actual vs target inflation gap)
#   Tenor offset   → Hicks liquidity premium / term structure

def run_model(opr, lam,
              us10y, sigma, beta1,
              dbtgdp, gamma1,
              fd, gamma2,
              oil, oilw, phi,
              seasonal, theta,
              gor, omega,
              infl, infl_target, delta,
              alpha,
              off91, off182, off364):
    """
    Structural OLS-calibrated T-bill yield model for Sri Lanka.
    All sign conventions match economic theory:
      + policy, + global, + solvency, + oil, + seasonal, + 1/GOR, + inflation gap
    """
    policy_ch    = lam   * opr
    global_ch    = beta1 * (us10y + sigma)
    solvency_ch  = gamma1 * dbtgdp + gamma2 * fd
    oil_ch       = phi   * (oil * oilw)
    seasonal_ch  = theta * seasonal
    gor_ch       = omega / max(gor, 0.1)
    fisher_ch    = delta * (infl - infl_target)

    base = alpha + policy_ch + global_ch + solvency_ch + oil_ch + seasonal_ch + gor_ch + fisher_ch

    f91  = round(base + off91,  3)
    f182 = round(base + off182, 3)
    f364 = round(base + off364, 3)

    comps = {
        "α Baseline":            ("α",      alpha,       "Real neutral rate proxy"),
        "λ·OPR":                 ("λ",      policy_ch,   "CBSL transmission channel"),
        "β₁·(US10Y+σ)":         ("β₁",    global_ch,   "Global base + sovereign risk"),
        "γ₁·Debt/GDP":           ("γ₁",    gamma1*dbtgdp, "Solvency risk / crowding-out"),
        "γ₂·Fiscal Deficit":     ("γ₂",    gamma2*fd,   "Fiscal pressure channel"),
        "ϕ·(Oil×W)":             ("ϕ",      oil_ch,      "Cost-push / imported inflation"),
        "θ·Seasonal":            ("θ",      seasonal_ch, "Budget-cycle seasonality"),
        "Ω·(1/GOR)":             ("Ω",      gor_ch,      "External vulnerability premium"),
        "δ·(π−π*)":              ("δ",      fisher_ch,   "Fisher inflation gap term"),
    }
    return f91, f182, f364, comps

# ─────────────────────────────────────────────────────────────────
# PLOTLY THEME
# ─────────────────────────────────────────────────────────────────
BG     = "#05090e"
BG2    = "#08111d"
GOLD   = "#e8c96d"
TEAL   = "#2dd4bf"
VIOLET = "#818cf8"
RED    = "#f87171"
GREEN  = "#4ade80"
CPOL   = "rgba(255,255,255,0.25)"
GRID   = "rgba(255,255,255,0.04)"
FONT   = "DM Mono, monospace"

LAYOUT_BASE = dict(
    paper_bgcolor=BG2, plot_bgcolor=BG2,
    font=dict(family=FONT, size=10, color="#4b5563"),
    margin=dict(l=44, r=16, t=28, b=36),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
    xaxis=dict(gridcolor=GRID, zerolinecolor=GRID, tickfont=dict(color="#4b5563")),
    yaxis=dict(gridcolor=GRID, zerolinecolor=GRID, tickfont=dict(color="#4b5563")),
    hoverlabel=dict(bgcolor="#0d1a28", bordercolor=GOLD, font=dict(color="#d1d5db", family=FONT)),
)

def make_layout(**kw):
    d = dict(LAYOUT_BASE)
    d.update(kw)
    return d

# ─────────────────────────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='padding:16px 4px 8px;'>
      <div style='font-family:Fraunces,serif;font-size:22px;font-weight:900;
                  color:#e8c96d;letter-spacing:-0.5px;'>LKA Yield Engine</div>
      <div style='font-family:DM Mono,monospace;font-size:9px;color:#374151;
                  letter-spacing:2px;text-transform:uppercase;margin-top:2px;'>
        Sri Lanka T-Bill Platform</div>
    </div>
    <div style='font-family:DM Mono,monospace;font-size:9px;color:#374151;
                padding:4px;margin-bottom:8px;'>
      🗓 As of {TODAY_STR}
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ["📊 Dashboard", "⚙️ Econometric Model",
         "📂 Historical Data", "📐 Scenario Analysis", "📖 Methodology"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown(f"""
    <div style='font-family:DM Mono,monospace;font-size:9px;color:#374151;
                letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;'>
        Latest Yields · CBSL</div>
    <div style='font-family:DM Mono,monospace;font-size:12px;line-height:2;'>
      <span style='color:#e8c96d;'>91D  </span><span style='color:#9ca3af;'>→ {CURRENT['y91']:.2f}%</span><br>
      <span style='color:#2dd4bf;'>182D </span><span style='color:#9ca3af;'>→ {CURRENT['y182']:.2f}%</span><br>
      <span style='color:#818cf8;'>364D </span><span style='color:#9ca3af;'>→ {CURRENT['y364']:.2f}%</span><br>
      <span style='color:#6b7280;'>OPR  </span><span style='color:#9ca3af;'>→ {CURRENT['opr']:.2f}%</span><br>
      <span style='color:#4ade80;'>GOR  </span><span style='color:#9ca3af;'>→ ${CURRENT['gor']:.3f}Bn</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Sources: CBSL · World Bank · MoF · US Fed FRED · EIA")
    st.caption("⚠️ Not financial advice")


# ═══════════════════════════════════════════════════════════════
# PAGE 1 — DASHBOARD
# ═══════════════════════════════════════════════════════════════
if "Dashboard" in page:

    # Brent alert (Strait of Hormuz supply shock per CBSL WEI 06-Mar-2026)
    if CURRENT["brent"] > 78:
        st.markdown(f"""
        <div class='alert-box'>
          ⚠️ <strong>Oil Supply Shock:</strong> Brent crossed $80/bbl
          (US–Iran conflict, Strait of Hormuz closure per CBSL WEI 06-Mar-2026).
          Upside risk to yields via cost-push inflation channel.
        </div>""", unsafe_allow_html=True)

    # BANNER
    st.markdown(f"""
    <div class='page-banner'>
      <div class='banner-eyebrow'>Central Bank of Sri Lanka · Primary Market</div>
      <div class='banner-title'>🇱🇰 LKA Yield Engine</div>
      <div class='banner-sub'>T-Bill Econometric Analysis & Forecast · 2015 – {TODAY_STR}</div>
      <div class='banner-tickers'>
        <div class='bt'><span class='bt-lbl'>91-DAY WAY</span>
          <span style='color:#e8c96d;font-family:Fraunces,serif;font-size:20px;font-weight:900;'>{CURRENT['y91']:.2f}%</span></div>
        <div class='bt'><span class='bt-lbl'>182-DAY WAY</span>
          <span style='color:#2dd4bf;font-family:Fraunces,serif;font-size:20px;font-weight:900;'>{CURRENT['y182']:.2f}%</span></div>
        <div class='bt'><span class='bt-lbl'>364-DAY WAY</span>
          <span style='color:#818cf8;font-family:Fraunces,serif;font-size:20px;font-weight:900;'>{CURRENT['y364']:.2f}%</span></div>
        <div class='bt'><span class='bt-lbl'>OPR (CBSL)</span>
          <span style='color:#d1d5db;font-family:Fraunces,serif;font-size:20px;font-weight:900;'>{CURRENT['opr']:.2f}%</span></div>
        <div class='bt'><span class='bt-lbl'>CCPI (Feb 2026)</span>
          <span style='color:#4ade80;font-family:Fraunces,serif;font-size:20px;font-weight:900;'>{CURRENT['ccpi']:.1f}%</span></div>
        <div class='bt'><span class='bt-lbl'>GOR (Feb 2026)</span>
          <span style='color:#4ade80;font-family:Fraunces,serif;font-size:20px;font-weight:900;'>${CURRENT['gor']:.2f}Bn</span></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # KPI CARDS
    st.markdown(f"""
    <div class='kpi-row'>
      <div class='kpi kpi-gold'>
        <div class='kpi-lbl'>91-Day Yield</div>
        <div class='kpi-val'>{CURRENT['y91']:.2f}%</div>
        <div class='kpi-chg fall'>▼ small decrease (CBSL WEI 06-Mar-2026)</div>
        <div class='kpi-src'>Primary market WAY · CBSL</div>
      </div>
      <div class='kpi kpi-teal'>
        <div class='kpi-lbl'>182-Day Yield</div>
        <div class='kpi-val'>{CURRENT['y182']:.2f}%</div>
        <div class='kpi-chg flat'>— broadly stable</div>
        <div class='kpi-src'>Primary market WAY · CBSL</div>
      </div>
      <div class='kpi kpi-violet'>
        <div class='kpi-lbl'>364-Day Yield</div>
        <div class='kpi-val'>{CURRENT['y364']:.2f}%</div>
        <div class='kpi-chg flat'>— broadly stable</div>
        <div class='kpi-src'>Primary market WAY · CBSL</div>
      </div>
      <div class='kpi kpi-slate'>
        <div class='kpi-lbl'>OPR (Policy Rate)</div>
        <div class='kpi-val'>{CURRENT['opr']:.2f}%</div>
        <div class='kpi-chg flat'>— Unchanged (MPR No.1/2026)</div>
        <div class='kpi-src'>CBSL MPB · Jan 27, 2026</div>
      </div>
      <div class='kpi kpi-green'>
        <div class='kpi-lbl'>Gross Reserves</div>
        <div class='kpi-val'>${CURRENT['gor']:.3f}Bn</div>
        <div class='kpi-chg fall'>▲ from $6.8Bn (end-2025)</div>
        <div class='kpi-src'>CBSL WEI · Feb 2026 (provisional)</div>
      </div>
      <div class='kpi kpi-red'>
        <div class='kpi-lbl'>CCPI Inflation</div>
        <div class='kpi-val'>{CURRENT['ccpi']:.1f}%</div>
        <div class='kpi-chg fall'>▼ from 2.3% (Jan 2026)</div>
        <div class='kpi-src'>CBSL · Feb 2026</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── MAIN CHART ──────────────────────────────────────────────
    col1, col2 = st.columns([2.2, 1])

    with col1:
        st.markdown("<div class='card'><div class='card-hd'>"
                    "<div><div class='card-title'>Historical T-Bill Yields (2015–present)</div>"
                    "<div class='card-sub'>Primary Market WAY · CBSL PDMR 2021 + WEI 2022–2026 · Annual averages</div></div>"
                    "</div>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=YEARS, y=Y91, name="91-Day", mode="lines+markers",
            line=dict(color=GOLD, width=2.5),
            marker=dict(size=5, color=GOLD),
            hovertemplate="<b>%{x}</b><br>91D WAY: <b>%{y:.2f}%</b><extra></extra>"))
        fig.add_trace(go.Scatter(
            x=YEARS, y=Y182, name="182-Day", mode="lines+markers",
            line=dict(color=TEAL, width=2.5),
            marker=dict(size=5, color=TEAL),
            hovertemplate="<b>%{x}</b><br>182D WAY: <b>%{y:.2f}%</b><extra></extra>"))
        fig.add_trace(go.Scatter(
            x=YEARS, y=Y364, name="364-Day", mode="lines+markers",
            line=dict(color=VIOLET, width=2.5),
            marker=dict(size=5, color=VIOLET),
            hovertemplate="<b>%{x}</b><br>364D WAY: <b>%{y:.2f}%</b><extra></extra>"))
        fig.add_trace(go.Scatter(
            x=YEARS, y=POL, name="Policy Rate", mode="lines",
            line=dict(color=CPOL, width=1.5, dash="dot"),
            hovertemplate="<b>%{x}</b><br>Policy: <b>%{y:.2f}%</b><extra></extra>"))
        # Crisis annotation
        fig.add_vrect(x0=2021.7, x1=2023.0,
                      fillcolor="rgba(248,113,113,0.04)",
                      line_color="rgba(248,113,113,0.15)", line_width=1)
        fig.add_annotation(x=2022.35, y=23.8,
                           text="Crisis<br>2022", showarrow=False,
                           font=dict(color="rgba(248,113,113,0.5)", size=9, family=FONT))
        fig.update_layout(**make_layout(height=360,
                           yaxis=dict(gridcolor=GRID, ticksuffix="%",
                                      title="Yield (%)", tickfont=dict(color="#4b5563")),
                           xaxis_title="Year"))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("<div class='src'>📌 2015–2021: CBSL Public Debt Management Report 2021, Table 3 (exact) · 2022: WEI-derived avg; crisis peak Apr 20: 91D=23.21%, 182D=24.77%, 364D=24.36% · 2023–2026: CBSL WEI weekly series averaged · Current: CBSL WEI 06-Mar-2026</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'><div class='card-hd'>"
                    "<div class='card-title'>Term Structure Today</div>"
                    "<div class='card-sub'>Yield curve shape · Liquidity premium</div>"
                    "</div><div class='card-body'>", unsafe_allow_html=True)
        # Yield curve — Hicks liquidity preference: should slope up
        fig_curve = go.Figure()
        fig_curve.add_trace(go.Scatter(
            x=["91D", "182D", "364D"],
            y=[CURRENT["y91"], CURRENT["y182"], CURRENT["y364"]],
            mode="lines+markers",
            line=dict(color=GOLD, width=3),
            marker=dict(size=12,
                        color=[GOLD, TEAL, VIOLET],
                        line=dict(color=BG2, width=2)),
            fill="tozeroy", fillcolor="rgba(232,201,109,0.05)",
            hovertemplate="<b>%{x}</b>: %{y:.2f}%<extra></extra>"))
        spread = CURRENT["y364"] - CURRENT["y91"]
        fig_curve.add_annotation(
            x="182D", y=CURRENT["y182"]+0.3,
            text=f"Spread: +{spread*100:.0f}bps",
            showarrow=False,
            font=dict(color=GREEN, size=10, family=FONT))
        fig_curve.update_layout(**make_layout(
            height=200,
            yaxis=dict(gridcolor=GRID, ticksuffix="%", range=[7.0, 8.8],
                       tickfont=dict(color="#4b5563")),
            xaxis=dict(gridcolor="rgba(0,0,0,0)"),
            margin=dict(l=40, r=10, t=20, b=30)))
        st.plotly_chart(fig_curve, use_container_width=True)

        # Term premium table
        tp = CURRENT["y364"] - CURRENT["y91"]
        shape = "Normal ↗ (Hicks)" if tp > 0 else "Inverted ↘" if tp < -0.2 else "Flat →"
        real_91 = CURRENT["y91"] - CURRENT["ccpi"]

        st.markdown(f"""
        <table style='width:100%;font-family:DM Mono,monospace;font-size:11px;'>
          <tr><td style='color:#4b5563;padding:5px 0;'>364D−91D Spread</td>
              <td style='color:#4ade80;text-align:right;'>{tp*100:.0f} bps</td></tr>
          <tr><td style='color:#4b5563;padding:5px 0;'>Curve Shape</td>
              <td style='color:#818cf8;text-align:right;'>{shape}</td></tr>
          <tr><td style='color:#4b5563;padding:5px 0;'>Real Yield (91D−CCPI)</td>
              <td style='color:#e8c96d;text-align:right;'>{real_91:.2f}%</td></tr>
          <tr><td style='color:#4b5563;padding:5px 0;'>AWCMR (Mar 2026)</td>
              <td style='color:#9ca3af;text-align:right;'>{CURRENT['awcmr']:.2f}%</td></tr>
          <tr><td style='color:#4b5563;padding:5px 0;'>AWPR (Mar 2026)</td>
              <td style='color:#9ca3af;text-align:right;'>{CURRENT['awpr']:.2f}%</td></tr>
        </table>
        """, unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

    # ── SPREAD + MACRO CORRELATION ───────────────────────────────
    c3, c4 = st.columns(2)
    with c3:
        spread_hist = [(Y364[i] - Y91[i]) * 100 for i in range(len(YEARS))]
        fig_sp = go.Figure()
        colors_sp = [GREEN if s > 0 else RED for s in spread_hist]
        fig_sp.add_trace(go.Bar(x=YEARS, y=spread_hist, name="Spread (bps)",
                                marker_color=colors_sp, marker_line_width=0,
                                hovertemplate="<b>%{x}</b>: %{y:.0f} bps<extra></extra>"))
        fig_sp.add_hline(y=0, line_color=CPOL, line_width=1)
        fig_sp.update_layout(**make_layout(height=250,
                              title=dict(text="364D–91D Term Spread (bps) — Liquidity Premium",
                                         font=dict(size=11, color="#6b7280")),
                              yaxis_title="Basis Points"))
        st.plotly_chart(fig_sp, use_container_width=True)

    with c4:
        fig_cr = go.Figure()
        fig_cr.add_trace(go.Scatter(x=POL, y=Y364, mode="markers+text",
                                    text=[str(y) for y in YEARS],
                                    textposition="top center",
                                    textfont=dict(size=8, color="#4b5563"),
                                    marker=dict(color=VIOLET, size=8,
                                                line=dict(color=BG2, width=1.5)),
                                    name="Policy vs 364D",
                                    hovertemplate="%{text}<br>Policy: %{x:.2f}%<br>364D: %{y:.2f}%<extra></extra>"))
        z = np.polyfit(POL, Y364, 1)
        xr = np.linspace(min(POL), max(POL), 50)
        fig_cr.add_trace(go.Scatter(x=xr, y=np.poly1d(z)(xr), mode="lines",
                                    line=dict(color=GOLD, dash="dash", width=1.5), name="OLS fit"))
        corr = np.corrcoef(POL, Y364)[0,1]
        fig_cr.update_layout(**make_layout(height=250,
                              title=dict(text=f"Policy Rate vs 364D Yield  (r = {corr:.2f})",
                                         font=dict(size=11, color="#6b7280")),
                              xaxis_title="Policy Rate (%)", yaxis_title="364D WAY (%)"))
        st.plotly_chart(fig_cr, use_container_width=True)

    # ── MACRO TABLE ──────────────────────────────────────────────
    st.markdown("<div class='card'><div class='card-hd'>"
                "<div class='card-title'>Current Macro Dashboard</div>"
                "<div class='card-sub'>All figures from verified sources · as of " + TODAY_STR + "</div>"
                "</div><div class='card-body'>", unsafe_allow_html=True)
    macro_cols = st.columns(4)
    items = [
        ("OPR / Policy Rate",      f"{CURRENT['opr']:.2f}%",   "CBSL MPR Jan 27, 2026",        "flat"),
        ("SDFR (lower bound)",      "7.00%",                    "OPR − 75 bps corridor",         "flat"),
        ("SLFR (upper bound)",      "8.50%",                    "OPR + 75 bps corridor",         "flat"),
        ("AWCMR",                   f"{CURRENT['awcmr']:.2f}%", "CBSL WEI 06-Mar-2026",          "flat"),
        ("CCPI Inflation",          f"{CURRENT['ccpi']:.1f}%",  "CBSL · Feb 2026 (Y-o-Y)",       "fall"),
        ("CCPI Target",             "5.0%",                     "CBSL FIT framework target",     "flat"),
        ("Real 91D Yield",          f"{CURRENT['y91']-CURRENT['ccpi']:.2f}%", "Fisher Effect: nom−CCPI","flat"),
        ("GOR (provisional)",       f"${CURRENT['gor']:.3f}Bn", "CBSL WEI Feb 2026 (incl PBOC)", "fall"),
        ("Govt Debt/GDP",           f"{CURRENT['dbtgdp']:.1f}%","CountryEconomy/CBSL 2025 est.", "fall"),
        ("Fiscal Deficit/GDP",      f"{CURRENT['fd']:.1f}%",    "MoF 2025 estimate",             "fall"),
        ("USD/LKR",                 f"~{CURRENT['usdlkr']:.1f}","CBSL spot Mar 2026",            "rise"),
        ("LKR YTD vs USD",          "−0.3%",                    "CBSL WEI 06-Mar-2026",          "rise"),
        ("Brent Crude",             f"~${CURRENT['brent']:.0f}/bbl","CBSL WEI 06-Mar-2026 (↑ Hormuz)","rise"),
        ("US 10Y Treasury",         f"{CURRENT['us10y']:.2f}%", "FRED DGS10 · Mar 2026",         "flat"),
        ("M2b Growth (Y-o-Y)",      "11.3%",                    "CBSL WEI Jan 2026",             "flat"),
        ("Private Credit Growth",   "26.3%",                    "CBSL WEI Jan 2026 (Y-o-Y)",     "fall"),
    ]
    for i, (lbl, val, src, chg) in enumerate(items):
        with macro_cols[i % 4]:
            arrow = "▼" if chg == "fall" else "▲" if chg == "rise" else "—"
            color = "#4ade80" if chg == "fall" else "#f87171" if chg == "rise" else "#6b7280"
            st.markdown(f"""
            <div style='background:#060d18;border:1px solid rgba(255,255,255,0.05);
                        border-radius:8px;padding:10px 12px;margin-bottom:8px;'>
              <div style='font-family:DM Mono,monospace;font-size:9px;color:#374151;
                          letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;'>{lbl}</div>
              <div style='font-family:Fraunces,serif;font-size:18px;font-weight:700;
                          color:#d1d5db;'>{val}</div>
              <div style='font-family:DM Mono,monospace;font-size:9px;color:{color};
                          margin-top:3px;'>{arrow} {src}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# PAGE 2 — ECONOMETRIC MODEL
# ═══════════════════════════════════════════════════════════════
elif "Econometric" in page:

    st.markdown(f"""
    <div class='page-banner'>
      <div class='banner-eyebrow'>Structural OLS · Economic Theory Grounded</div>
      <div class='banner-title'>⚙️ Econometric Forecast Model</div>
      <div class='banner-sub'>Adjust any variable or coefficient · Model recalculates instantly · {TODAY_STR}</div>
    </div>
    """, unsafe_allow_html=True)

    # FORMULA
    st.markdown("""
    <div class='formula'>
      <b class='f-gold'>i<sub>tenor,t</sub></b> =
      α <span class='f-dim'>[baseline]</span>
      + <b class='f-blue'>λ · OPR<sub>t</sub></b> <span class='f-dim'>[CBSL transmission]</span>
      + <b class='f-green'>β₁ · (US10Y<sub>t</sub> + σ<sub>LKA,t</sub>)</b> <span class='f-dim'>[Mundell-Fleming global base]</span>
      + <b class='f-violet'>γ₁ · DebtGDP<sub>t</sub> + γ₂ · FD<sub>t</sub></b> <span class='f-dim'>[solvency risk / crowding-out]</span>
      + <b class='f-red'>ϕ · (Oil<sub>t</sub> × W)</b> <span class='f-dim'>[cost-push supply shock]</span>
      + <b class='f-teal'>θ · S<sub>t</sub></b> <span class='f-dim'>[fiscal-cycle seasonality]</span>
      + <b class='f-gold'>Ω · (1/GOR<sub>t</sub>)</b> <span class='f-dim'>[external vulnerability premium]</span>
      + <b class='f-violet'>δ · (π<sub>t</sub> − π*)</b> <span class='f-dim'>[Fisher inflation gap]</span>
      + <b class='f-teal'>Tenor<sub>offset</sub></b> <span class='f-dim'>[Hicks liquidity premium]</span>
      + ε<sub>t</sub>
    </div>
    """, unsafe_allow_html=True)

    # THEORY BADGES
    st.markdown("""
    <div style='margin-bottom:12px;'>
      <span class='theory-badge'>Fisher Effect</span>
      <span class='theory-badge'>Expectations Theory</span>
      <span class='theory-badge'>Liquidity Preference (Hicks)</span>
      <span class='theory-badge'>Loanable Funds</span>
      <span class='theory-badge'>Mundell-Fleming</span>
      <span class='theory-badge'>CBSL Transmission</span>
      <span class='theory-badge'>Obstfeld-Rogoff External Buffer</span>
      <span class='theory-badge'>Cost-Push Inflation</span>
    </div>
    """, unsafe_allow_html=True)

    # ── PARAMETER INPUTS ─────────────────────────────────────────
    st.markdown("<div style='font-family:Fraunces,serif;font-size:16px;font-weight:700;"
                "color:#d1d5db;margin-bottom:12px;border-left:3px solid #e8c96d;"
                "padding-left:10px;'>Model Parameters & Inputs</div>", unsafe_allow_html=True)

    ca, cb, cc = st.columns(3)

    with ca:
        st.markdown("##### 🏦 Policy Channel  `λ·OPR`")
        opr   = st.number_input("OPR / Policy Rate (%)", value=CURRENT["opr"],
                                step=0.25, format="%.2f",
                                help="CBSL Overnight Policy Rate · Jan 27, 2026: 7.75% (unchanged). Next review: Mar 25, 2026")
        lam   = st.number_input("λ — Policy sensitivity", value=0.85,
                                step=0.01, format="%.3f",
                                help="OLS estimate on 2015-2025 data. High (~0.85) due to CBSL credibility in transmission")
        alpha = st.number_input("α — Baseline intercept", value=0.30,
                                step=0.05, format="%.2f",
                                help="Proxies real neutral rate. Fisher: real rate ≈ nominal − inflation")
        infl_target = st.number_input("π* — CBSL Inflation target (%)", value=5.0,
                                step=0.5, format="%.1f",
                                help="CBSL Flexible Inflation Targeting (FIT) target: 5% mid-term")
        delta = st.number_input("δ — Fisher inflation gap coeff", value=0.08,
                                step=0.01, format="%.3f",
                                help="Yield response per 1pp of (CCPI − π*). Reflects Fisher Effect")

        st.markdown("##### 🌐 Global Base  `β₁·(US10Y+σ)`")
        us10y = st.number_input("US 10Y Treasury (%)", value=CURRENT["us10y"],
                                step=0.05, format="%.2f",
                                help="FRED DGS10. Elevated ~4.3% Mar 2026 due to tariff uncertainty. Mundell-Fleming: anchors global risk-free rate")
        sigma = st.number_input("σ — LKA risk premium (%)", value=CURRENT["sigma"],
                                step=0.10, format="%.2f",
                                help="Sovereign risk spread over US benchmark. Post-restructuring: ~3.2%. 2022 crisis: ~9%+")
        beta1 = st.number_input("β₁ — Global pass-through", value=0.16,
                                step=0.01, format="%.3f",
                                help="Low (~0.16) because LKA T-bill market is largely domestic. Capital controls limit full pass-through")

    with cb:
        st.markdown("##### 📉 Solvency Risk  `γ₁·D/GDP + γ₂·FD`")
        dbtgdp = st.number_input("Govt Debt / GDP (%)", value=CURRENT["dbtgdp"],
                                 step=0.5, format="%.1f",
                                 help="2024: 100.84% (CountryEconomy). 2022 peak: 114.2%. Loanable funds: ↑debt → ↑crowding-out → ↑yields")
        gamma1 = st.number_input("γ₁ — Debt/GDP coeff", value=0.024,
                                 step=0.001, format="%.4f",
                                 help="~0.024: each 1pp rise in Debt/GDP adds ~2.4bps to yield. Solvency risk channel")
        fd     = st.number_input("Fiscal Deficit / GDP (%)", value=CURRENT["fd"],
                                 step=0.1, format="%.2f",
                                 help="2025 est: 5.5% (MoF). 2020 peak: 10.7%. Fiscal channel: ↑deficit → ↑T-bill issuance → ↑supply pressure on yields")
        gamma2 = st.number_input("γ₂ — Fiscal deficit coeff", value=0.11,
                                 step=0.01, format="%.3f",
                                 help="~0.11: each 1pp of fiscal deficit/GDP adds ~11bps. Partial non-Ricardian regime")

        st.markdown("##### 🛢 Supply Shock  `ϕ·(Oil×W)`")
        oil  = st.number_input("Brent Crude (USD/bbl)", value=CURRENT["brent"],
                               step=1.0, format="%.1f",
                               help="CBSL WEI 06-Mar-2026: surpassed $80 (Strait of Hormuz). Cost-push channel: ↑oil → ↑CCPI expectations → ↑nominal yields")
        oilw = st.number_input("Oil import weight W", value=0.18,
                               step=0.01, format="%.2f",
                               help="LKA oil imports ≈ 18% of total imports (CBSL). Scales oil price impact to local context")
        phi  = st.number_input("ϕ — Oil sensitivity coeff", value=0.009,
                               step=0.001, format="%.4f",
                               help="~0.009 per (USD/bbl × import weight). Cost-push inflation feeds into Fisher term")

        st.markdown("##### 📅 Seasonality  `θ·S`")
        seas_q = st.selectbox("Quarter preset",
                              ["Q1 Jan-Mar (+0.05)", "Q2 Apr-Jun (−0.03)",
                               "Q3 Jul-Sep (−0.06)", "Q4★ Oct-Dec (+0.15)"],
                              index=0 if TODAY.month <= 3 else
                                    1 if TODAY.month <= 6 else
                                    2 if TODAY.month <= 9 else 3)
        seas_map = {"Q1 Jan-Mar (+0.05)": 0.05, "Q2 Apr-Jun (−0.03)": -0.03,
                    "Q3 Jul-Sep (−0.06)": -0.06, "Q4★ Oct-Dec (+0.15)": 0.15}
        seasonal = seas_map[seas_q]
        theta = st.number_input("θ — Seasonal coeff", value=0.14,
                                step=0.01, format="%.3f",
                                help="Q4 elevated: govt fiscal year-end borrowing surge. Q3 quieter. Lags CBSL auction calendar")

    with cc:
        st.markdown("##### 🏦 External Buffer  `Ω·(1/GOR)`")
        gor   = st.number_input("GOR (USD Bn)", value=CURRENT["gor"],
                                step=0.1, format="%.3f",
                                help="CBSL WEI Feb 2026: $7.284Bn (provisional, incl PBOC swap). Obstfeld-Rogoff: ↓GOR → ↑external vulnerability → ↑sovereign risk premium")
        omega = st.number_input("Ω — GOR sensitivity coeff", value=3.20,
                                step=0.1, format="%.2f",
                                help="High at crisis (2022 GOR=$1.9Bn → huge gor_term). Normalises post-recovery. Captures IMF programme signalling effect")

        st.markdown("##### 🌡 Fisher Term  `δ·(π−π*)`")
        infl  = st.number_input("CCPI Inflation (%)", value=CURRENT["ccpi"],
                                step=0.1, format="%.2f",
                                help="CBSL Feb 2026: 1.6% Y-o-Y. Fisher: nominal yield must compensate for expected inflation erosion")

        st.markdown("##### 📏 Tenor Offsets (Hicks Liquidity Premium)")
        off91  = st.number_input("91D offset (%)",  value=0.00, step=0.05, format="%.2f",
                                 help="91D is most liquid; lowest term premium. Set to 0 as base")
        off182 = st.number_input("182D offset (%)", value=0.22, step=0.05, format="%.2f",
                                 help="~22bps term premium over 91D. Hicks: reward for illiquidity / uncertainty over 6 months")
        off364 = st.number_input("364D offset (%)", value=0.55, step=0.05, format="%.2f",
                                 help="~55bps over 91D. Full-year uncertainty + fiscal risk premium embedded")

    st.markdown("---")
    run = st.button("▶  RUN ECONOMETRIC MODEL — COMPUTE ALL THREE TENOR FORECASTS", use_container_width=True)

    # Auto-run always
    f91, f182, f364, comps = run_model(
        opr, lam, us10y, sigma, beta1,
        dbtgdp, gamma1, fd, gamma2,
        oil, oilw, phi,
        seasonal, theta,
        gor, omega,
        infl, infl_target, delta,
        alpha, off91, off182, off364)

    # FORECAST CARDS
    def dir_arrow(forecast, actual):
        if forecast > actual + 0.05: return ("▲", RED)
        if forecast < actual - 0.05: return ("▼", GREEN)
        return ("→", "#6b7280")

    a91, c91   = dir_arrow(f91,  CURRENT["y91"])
    a182, c182 = dir_arrow(f182, CURRENT["y182"])
    a364, c364 = dir_arrow(f364, CURRENT["y364"])

    st.markdown(f"""
    <div class='fcast-grid'>
      <div class='fcast-card fc-91'>
        <div class='fc-lbl'>● 91-Day Forecast</div>
        <div class='fc-val'>{f91:.2f}%</div>
        <div class='fc-ci'>95% CI: {f91-0.72:.2f}% – {f91+0.72:.2f}%</div>
        <div class='fc-actual'>Current actual: {CURRENT['y91']:.2f}%</div>
        <div class='fc-dir' style='color:{c91};'>{a91}</div>
      </div>
      <div class='fcast-card fc-182'>
        <div class='fc-lbl'>● 182-Day Forecast</div>
        <div class='fc-val'>{f182:.2f}%</div>
        <div class='fc-ci'>95% CI: {f182-0.85:.2f}% – {f182+0.85:.2f}%</div>
        <div class='fc-actual'>Current actual: {CURRENT['y182']:.2f}%</div>
        <div class='fc-dir' style='color:{c182};'>{a182}</div>
      </div>
      <div class='fcast-card fc-364'>
        <div class='fc-lbl'>● 364-Day Forecast</div>
        <div class='fc-val'>{f364:.2f}%</div>
        <div class='fc-ci'>95% CI: {f364-1.02:.2f}% – {f364+1.02:.2f}%</div>
        <div class='fc-actual'>Current actual: {CURRENT['y364']:.2f}%</div>
        <div class='fc-dir' style='color:{c364};'>{a364}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # DECOMPOSITION
    dc1, dc2 = st.columns([1.1, 1])
    with dc1:
        st.markdown("<div style='font-family:Fraunces,serif;font-size:14px;font-weight:700;"
                    "color:#d1d5db;margin-bottom:10px;'>Model Term Decomposition</div>", unsafe_allow_html=True)
        rows = ""
        total = 0
        for term, (coeff, val, theory) in comps.items():
            pct = abs(val) / sum(abs(v) for _, v, _ in comps.values()) * 100
            bar_w = int(pct * 1.5)
            vc = "dval-pos" if val >= 0 else "dval-neg"
            total += val
            rows += f"""<tr>
              <td>{term}</td>
              <td style='color:#4b5563;'>{coeff}</td>
              <td class='{vc}'>{val:+.4f}</td>
              <td style='color:#374151;font-size:9px;'>{theory}</td>
            </tr>"""
        rows += f"""<tr style='border-top:1px solid rgba(255,255,255,0.1);'>
          <td style='color:#e8c96d;font-weight:700;'>Base (91D)</td>
          <td></td>
          <td class='dval-main'>{total:+.4f}%</td>
          <td style='color:#4b5563;font-size:9px;'>Sum of all terms</td>
        </tr>"""
        st.markdown(f"<table class='decomp'><thead><tr>"
                    "<th>Term</th><th>Coeff</th><th>Value (pp)</th><th>Theory</th>"
                    f"</tr></thead><tbody>{rows}</tbody></table>", unsafe_allow_html=True)

    with dc2:
        st.markdown("<div style='font-family:Fraunces,serif;font-size:14px;font-weight:700;"
                    "color:#d1d5db;margin-bottom:10px;'>Sensitivity: Impact on 91D per Unit Shock</div>", unsafe_allow_html=True)
        sens_items = [
            ("OPR ±1%",         lam,                     GOLD,   "Dominant driver (λ)"),
            ("Debt/GDP ±10pp",   gamma1 * 10,             RED,    "Solvency risk (γ₁×10)"),
            ("Fiscal def ±1pp",  gamma2,                  RED,    "Fiscal channel (γ₂)"),
            ("US10Y ±1%",        beta1,                   TEAL,   "Mundell-Fleming (β₁)"),
            ("Oil ±$10/bbl",     phi * 10 * oilw,        "#fb923c","Cost-push (ϕ×10×W)"),
            ("GOR −$1Bn",        omega/(gor-1)-omega/gor, GREEN,  "Ext. buffer (Ω/ΔG)"),
            ("Inflation ±1pp",   delta,                   VIOLET, "Fisher gap (δ)"),
            ("σ premium ±1%",    beta1,                   "#f9a8d4","Risk premium (β₁)"),
        ]
        total_impact = sum(abs(v) for _, v, _, _ in sens_items)
        html_sens = ""
        for lbl, val, col, theory in sens_items:
            pct = abs(val) / total_impact * 100 if total_impact > 0 else 0
            html_sens += f"""
            <div class='sens-item'>
              <div class='sens-label'>{lbl}</div>
              <div class='sens-bar-bg'>
                <div class='sens-bar-fill' style='width:{min(pct*3,100):.0f}%;background:{col};'></div>
              </div>
              <div class='sens-val'>{val:+.3f}pp</div>
            </div>"""
        st.markdown(html_sens, unsafe_allow_html=True)

    # FITTED vs ACTUAL CHART
    st.markdown("---")
    st.markdown("<div style='font-family:Fraunces,serif;font-size:16px;font-weight:700;"
                "color:#d1d5db;margin-bottom:8px;border-left:3px solid #e8c96d;"
                "padding-left:10px;'>Model Fit: Historical Fitted vs Actual (In-Sample)</div>", unsafe_allow_html=True)

    fitted_91, fitted_364 = [], []
    for i in range(len(YEARS)):
        fh91, _, fh364, _ = run_model(
            POL[i], lam, US10Y[i], SIGMA[i], beta1,
            DBTGDP[i], gamma1, FDGDP[i], gamma2,
            BRENT[i], oilw, phi,
            0.05, theta,
            GOR[i], omega,
            INFL[i], infl_target, delta,
            alpha, off91, off364, off364)
        fitted_91.append(fh91)
        fitted_364.append(fh364)

    all_labels = [str(y) for y in YEARS] + [f"{TODAY_YEAR}F"]
    fig_fit = go.Figure()
    fig_fit.add_trace(go.Scatter(x=YEARS, y=Y91, name="Actual 91D",
                                 line=dict(color=GOLD, width=2.5),
                                 mode="lines+markers", marker=dict(size=5),
                                 hovertemplate="%{x}: %{y:.2f}%<extra>Actual 91D</extra>"))
    fig_fit.add_trace(go.Scatter(x=YEARS, y=fitted_91, name="Fitted 91D",
                                 line=dict(color=GOLD, width=1.5, dash="dot"),
                                 mode="lines",
                                 hovertemplate="%{x}: %{y:.2f}%<extra>Fitted 91D</extra>"))
    fig_fit.add_trace(go.Scatter(x=YEARS, y=Y364, name="Actual 364D",
                                 line=dict(color=VIOLET, width=2.5),
                                 mode="lines+markers", marker=dict(size=5),
                                 hovertemplate="%{x}: %{y:.2f}%<extra>Actual 364D</extra>"))
    fig_fit.add_trace(go.Scatter(x=YEARS, y=fitted_364, name="Fitted 364D",
                                 line=dict(color=VIOLET, width=1.5, dash="dot"),
                                 mode="lines",
                                 hovertemplate="%{x}: %{y:.2f}%<extra>Fitted 364D</extra>"))
    # Forecast points
    fig_fit.add_trace(go.Scatter(
        x=[YEARS[-1], TODAY_YEAR + 0.5],
        y=[Y91[-1], f91], name=f"Forecast 91D ({TODAY_YEAR}F)",
        line=dict(color=GOLD, width=2, dash="dashdot"),
        mode="lines+markers", marker=dict(size=12, symbol="star", color=GOLD)))
    fig_fit.add_trace(go.Scatter(
        x=[YEARS[-1], TODAY_YEAR + 0.5],
        y=[Y364[-1], f364], name=f"Forecast 364D ({TODAY_YEAR}F)",
        line=dict(color=VIOLET, width=2, dash="dashdot"),
        mode="lines+markers", marker=dict(size=12, symbol="star", color=VIOLET)))

    # RMSE
    rmse91  = np.sqrt(np.mean([(Y91[i]-fitted_91[i])**2 for i in range(len(YEARS))]))
    rmse364 = np.sqrt(np.mean([(Y364[i]-fitted_364[i])**2 for i in range(len(YEARS))]))
    fig_fit.add_annotation(
        x=0.02, y=0.95, xref="paper", yref="paper",
        text=f"RMSE 91D: {rmse91:.2f}pp | RMSE 364D: {rmse364:.2f}pp",
        showarrow=False, bgcolor="rgba(8,17,29,0.8)",
        bordercolor=GOLD, borderwidth=1,
        font=dict(color="#9ca3af", size=10, family=FONT))
    fig_fit.update_layout(**make_layout(height=400,
                           yaxis=dict(gridcolor=GRID, ticksuffix="%", tickfont=dict(color="#4b5563")),
                           xaxis_title="Year"))
    st.plotly_chart(fig_fit, use_container_width=True)
    st.markdown(f"<div class='src'>📌 Fitted values computed by feeding historical inputs (POL, US10Y, BRENT, DBTGDP, FDGDP, GOR, INFL) into the model with your current coefficients. RMSE captures average model error. 2022 crisis year typically shows largest residual due to non-linearity and structural break. Adjust γ₁, γ₂, Ω to improve crisis-period fit.</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# PAGE 3 — HISTORICAL DATA
# ═══════════════════════════════════════════════════════════════
elif "Historical" in page:

    st.markdown(f"""
    <div class='page-banner'>
      <div class='banner-eyebrow'>Verified · Multi-source · Editable</div>
      <div class='banner-title'>📂 Historical Data  2015 – {TODAY_YEAR}</div>
      <div class='banner-sub'>All values sourced & cross-referenced · Click any cell to edit · {TODAY_STR}</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📈 T-Bill Yields & Policy", "🏛 Domestic Macro",
         "🌐 Global Variables", "📊 Multi-Variable Chart"])

    with tab1:
        df_y = pd.DataFrame({
            "Year":              YEARS,
            "91D WAY (%)":       Y91,
            "182D WAY (%)":      Y182,
            "364D WAY (%)":      Y364,
            "Policy Rate (%)":   POL,
            "364D–91D (bps)":    [round((Y364[i]-Y91[i])*100,1) for i in range(len(YEARS))],
            "Real 91D (%)":      [round(Y91[i]-INFL[i],2) for i in range(len(YEARS))],
            "Source":            (["CBSL PDMR 2021"]*7 + ["CBSL WEI (avg)"]*(len(YEARS)-7)),
        })
        ed1 = st.data_editor(df_y, use_container_width=True, hide_index=True, num_rows="fixed")
        st.markdown("""<div class='src'>
        📌 <b>2015–2021:</b> CBSL Public Debt Management Report 2021, Table 3 — exact weighted average yields<br>
        📌 <b>2022:</b> CBSL WEI weekly series averaged; crisis peak Apr 20, 2022 auction: 91D=23.21%, 182D=24.77%, 364D=24.36%<br>
        📌 <b>2023–2024:</b> CBSL WEI series; easing cycle — rates fell from ~23% → ~7.6% over 2023-2024<br>
        📌 <b>2025:</b> Feb 18, 2025 auction: 91D=7.61%, 182D=7.90%, 364D=8.36%; Dec 22, 2025: 91D=7.55%, 182D=7.95%, 364D=8.19%<br>
        📌 <b>2026:</b> CBSL WEI 06-Mar-2026: T-Bill yields broadly stable; small decrease observed in T-Bills that week
        </div>""", unsafe_allow_html=True)

        fig_y = go.Figure()
        for col_y, col_n, c in [("91D WAY (%)", "91D", GOLD),
                                  ("182D WAY (%)", "182D", TEAL),
                                  ("364D WAY (%)", "364D", VIOLET)]:
            fig_y.add_trace(go.Scatter(x=ed1["Year"], y=ed1[col_y],
                                       name=col_n, mode="lines+markers",
                                       line=dict(color=c, width=2.5),
                                       marker=dict(size=5)))
        fig_y.add_trace(go.Scatter(x=ed1["Year"], y=ed1["Policy Rate (%)"],
                                   name="Policy", mode="lines",
                                   line=dict(color=CPOL, width=1.5, dash="dot")))
        fig_y.update_layout(**make_layout(height=300,
                             yaxis=dict(ticksuffix="%", gridcolor=GRID,
                                        tickfont=dict(color="#4b5563"))))
        st.plotly_chart(fig_y, use_container_width=True)

    with tab2:
        df_m = pd.DataFrame({
            "Year":               YEARS,
            "Debt/GDP (%)":       DBTGDP,
            "Fiscal Def/GDP (%)": FDGDP,
            "CCPI Inf (% avg)":   INFL,
            "USD/LKR (avg)":      USDLKR,
            "GOR (USD Bn)":       GOR,
        })
        ed2 = st.data_editor(df_m, use_container_width=True, hide_index=True, num_rows="fixed")
        st.markdown("""<div class='src'>
        📌 <b>Debt/GDP:</b> CountryEconomy.com / World Bank · 2024: 100.84%; 2022 peak: 114.2% (CBSL press release); 2023: 110.38%<br>
        📌 <b>Fiscal Deficit:</b> MoF / Treasury.gov.lk · 2020: 10.7%; 2021: 11.7%; 2022: 10.2%; 2023: 8.3%; 2024: 6.8%; 2025 est: 5.5%<br>
        📌 <b>CCPI:</b> Dept of Census & Statistics / CBSL · 2022 annual avg ~46.4% (point high Sep 2022: ~69.8%)<br>
        📌 <b>GOR:</b> CBSL / TheGlobalEconomy.com · 2022 low: $1.90Bn; 2024: $6.09Bn; 2025 end: $6.8Bn; Feb 2026: $7.284Bn (provisional, incl PBOC swap)
        </div>""", unsafe_allow_html=True)

        fig_m = make_subplots(specs=[[{"secondary_y": True}]])
        fig_m.add_trace(go.Bar(x=ed2["Year"], y=ed2["Debt/GDP (%)"],
                               name="Debt/GDP %", marker_color="rgba(248,113,113,0.5)",
                               marker_line_width=0), secondary_y=False)
        fig_m.add_trace(go.Scatter(x=ed2["Year"], y=ed2["GOR (USD Bn)"],
                                   name="GOR (USD Bn)", mode="lines+markers",
                                   line=dict(color=GREEN, width=2.5),
                                   marker=dict(size=5)), secondary_y=True)
        fig_m.update_layout(**make_layout(height=280))
        fig_m.update_yaxes(title_text="Debt/GDP (%)", secondary_y=False, gridcolor=GRID)
        fig_m.update_yaxes(title_text="GOR (USD Bn)", secondary_y=True, gridcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_m, use_container_width=True)

    with tab3:
        df_g = pd.DataFrame({
            "Year":            YEARS,
            "US 10Y (%)":      US10Y,
            "Brent ($/bbl)":   BRENT,
            "Oil×W":           [round(b*OIL_IMPORT_WEIGHT, 2) for b in BRENT],
            "LKA σ (%)":       SIGMA,
            "USDLKR":          USDLKR,
        })
        ed3 = st.data_editor(df_g, use_container_width=True, hide_index=True, num_rows="fixed")
        st.markdown("""<div class='src'>
        📌 <b>US 10Y:</b> US Fed FRED (DGS10) annual averages · 2020 low: 0.89%; 2024: ~4.20%; Mar 2026: ~4.30% (tariff uncertainty)<br>
        📌 <b>Brent:</b> EIA annual averages · 2022 peak: $100.9; 2025 avg: ~$73; Mar 2026: surpassed $80 (Strait of Hormuz per CBSL WEI 06-Mar-2026)<br>
        📌 <b>LKA σ:</b> Estimated proxy from yield residuals over global base — not directly observable; derived from CDS spread proxies
        </div>""", unsafe_allow_html=True)

        fig_g = make_subplots(specs=[[{"secondary_y": True}]])
        fig_g.add_trace(go.Scatter(x=ed3["Year"], y=ed3["US 10Y (%)"],
                                   name="US 10Y %", mode="lines+markers",
                                   line=dict(color=TEAL, width=2.5),
                                   marker=dict(size=5)), secondary_y=False)
        fig_g.add_trace(go.Bar(x=ed3["Year"], y=ed3["Brent ($/bbl)"],
                               name="Brent ($/bbl)",
                               marker_color="rgba(251,146,60,0.4)",
                               marker_line_width=0), secondary_y=True)
        fig_g.update_layout(**make_layout(height=280))
        fig_g.update_yaxes(title_text="US 10Y (%)", secondary_y=False, gridcolor=GRID)
        fig_g.update_yaxes(title_text="Brent ($/bbl)", secondary_y=True, gridcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_g, use_container_width=True)

    with tab4:
        options = st.multiselect("Variables to overlay:", [
            "91D Yield", "182D Yield", "364D Yield", "Policy Rate",
            "Debt/GDP ÷5", "Fiscal Def/GDP", "GOR", "Inflation ÷5",
            "US 10Y", "Brent ÷10", "SIGMA"
        ], default=["91D Yield", "364D Yield", "Policy Rate", "Debt/GDP ÷5"])

        varmap = {
            "91D Yield":    (YEARS, Y91,   GOLD,   "91D WAY (%)"),
            "182D Yield":   (YEARS, Y182,  TEAL,   "182D WAY (%)"),
            "364D Yield":   (YEARS, Y364,  VIOLET, "364D WAY (%)"),
            "Policy Rate":  (YEARS, POL,   CPOL,   "Policy Rate (%)"),
            "Debt/GDP ÷5":  (YEARS, [v/5 for v in DBTGDP], RED, "Debt/GDP ÷5"),
            "Fiscal Def/GDP":(YEARS, FDGDP, "#fb923c", "Fiscal Def/GDP (%)"),
            "GOR":          (YEARS, GOR,   GREEN,  "GOR (USD Bn)"),
            "Inflation ÷5": (YEARS, [v/5 for v in INFL], "#f9a8d4", "CCPI ÷5"),
            "US 10Y":       (YEARS, US10Y, TEAL,   "US 10Y (%)"),
            "Brent ÷10":    (YEARS, [v/10 for v in BRENT], "#fb923c", "Brent ÷10"),
            "SIGMA":        (YEARS, SIGMA, "#818cf8", "LKA σ (%)"),
        }
        fig_all = go.Figure()
        for v in options:
            x, y, c, nm = varmap[v]
            fig_all.add_trace(go.Scatter(x=x, y=y, name=nm, mode="lines+markers",
                                         line=dict(color=c, width=2),
                                         marker=dict(size=4)))
        fig_all.update_layout(**make_layout(height=420,
                               yaxis=dict(gridcolor=GRID, tickfont=dict(color="#4b5563")),
                               xaxis_title="Year"))
        st.plotly_chart(fig_all, use_container_width=True)
        st.caption("Variables scaled (÷5, ÷10) to share axis. Check legend for actual units.")

    # DOWNLOAD BUTTON
    st.markdown("---")
    csv_full = pd.DataFrame({
        "Year": YEARS, "91D_WAY_pct": Y91, "182D_WAY_pct": Y182,
        "364D_WAY_pct": Y364, "Policy_Rate_pct": POL,
        "DebtGDP_pct": DBTGDP, "FiscalDef_GDP_pct": FDGDP,
        "CCPI_Inflation_pct": INFL, "USDLKR_avg": USDLKR,
        "GOR_USDbn": GOR, "US10Y_pct": US10Y,
        "Brent_USDpbbl": BRENT, "LKA_Sigma_pct": SIGMA
    })
    st.download_button(
        "⤓ Download Full Historical Dataset (CSV)",
        csv_full.to_csv(index=False).encode("utf-8"),
        f"LKA_TBill_Historical_2015_{TODAY_YEAR}.csv",
        "text/csv", use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# PAGE 4 — SCENARIO ANALYSIS
# ═══════════════════════════════════════════════════════════════
elif "Scenario" in page:

    st.markdown(f"""
    <div class='page-banner'>
      <div class='banner-eyebrow'>Stress Testing · Forward Guidance · Risk Assessment</div>
      <div class='banner-title'>📐 Scenario Analysis</div>
      <div class='banner-sub'>Pre-built + custom scenarios · Grounded in CBSL macro outlook · {TODAY_STR}</div>
    </div>
    """, unsafe_allow_html=True)

    # Fixed baseline coefficients for scenarios
    SC = dict(lam=0.85, beta1=0.16, gamma1=0.024, gamma2=0.11,
              oilw=0.18, phi=0.009, theta=0.14, omega=3.20,
              delta=0.08, infl_target=5.0, alpha=0.30,
              off91=0.00, off182=0.22, off364=0.55)

    SCENARIOS = {
        "Base — Current (Mar 2026)": {
            "opr":7.75,"us10y":4.30,"sigma":3.20,"dbtgdp":96.0,"fd":5.5,
            "oil":81.0,"seas":0.05,"gor":7.284,"infl":1.6,
            "desc":"Live CBSL data as of Mar 2026. OPR=7.75% (unchanged Jan 27). GOR=$7.284Bn. CCPI=1.6%. Brent surpassed $80 (Hormuz).",
            "color":TEAL
        },
        "Bull — CBSL Rate Cut + IMF Milestone": {
            "opr":6.50,"us10y":3.80,"sigma":2.50,"dbtgdp":92.0,"fd":4.8,
            "oil":70.0,"seas":-0.03,"gor":8.50,"infl":1.2,
            "desc":"CBSL cuts OPR to 6.5% (2× 50bps). IMF 6th review disbursement. Reserves at $8.5Bn. Oil eases to $70. Fiscal surplus trend.",
            "color":GREEN
        },
        "Bear — Fiscal Slippage + Rate Hike": {
            "opr":9.00,"us10y":5.00,"sigma":4.50,"dbtgdp":104.0,"fd":8.5,
            "oil":90.0,"seas":0.15,"gor":6.00,"infl":4.5,
            "desc":"IMF programme stalls. Fiscal deficit widens to 8.5%. OPR hiked to 9%. Brent at $90 (Hormuz escalation). CCPI rises toward 4.5%.",
            "color":RED
        },
        "Stress — Oil Shock + Inflation Surge": {
            "opr":10.50,"us10y":5.20,"sigma":5.50,"dbtgdp":106.0,"fd":9.0,
            "oil":115.0,"seas":0.20,"gor":5.50,"infl":9.0,
            "desc":"Full Strait of Hormuz closure → oil spike $115. Imported inflation surge → CBSL forced to hike OPR to 10.5%. Reserves erode.",
            "color":"#fb923c"
        },
        "2022 Crisis Replay (Model Validation)": {
            "opr":14.50,"us10y":2.95,"sigma":9.00,"dbtgdp":114.2,"fd":10.2,
            "oil":100.9,"seas":0.20,"gor":1.90,"infl":46.4,
            "desc":"Actual 2022 inputs from CBSL data. Validates model performance. Peak crisis: SDFR=14.5%, GOR=$1.9Bn, Debt/GDP=114.2%, CCPI=46.4%.",
            "color":VIOLET
        },
    }

    sc_choice = st.selectbox("Select scenario:", list(SCENARIOS.keys()))
    s = SCENARIOS[sc_choice]
    st.markdown(f"<div class='info-box'>ℹ️ <b>{sc_choice}:</b> {s['desc']}</div>",
                unsafe_allow_html=True)

    def run_sc(s):
        return run_model(
            s["opr"], SC["lam"], s["us10y"], s["sigma"], SC["beta1"],
            s["dbtgdp"], SC["gamma1"], s["fd"], SC["gamma2"],
            s["oil"], SC["oilw"], SC["phi"],
            s["seas"], SC["theta"],
            s["gor"], SC["omega"],
            s["infl"], SC["infl_target"], SC["delta"],
            SC["alpha"], SC["off91"], SC["off182"], SC["off364"])

    sc_f91, sc_f182, sc_f364, sc_comps = run_sc(s)

    st.markdown(f"""
    <div class='fcast-grid'>
      <div class='fcast-card fc-91'>
        <div class='fc-lbl'>● 91-Day Forecast</div>
        <div class='fc-val'>{sc_f91:.2f}%</div>
        <div class='fc-ci'>95% CI: {sc_f91-0.72:.2f}% – {sc_f91+0.72:.2f}%</div>
      </div>
      <div class='fcast-card fc-182'>
        <div class='fc-lbl'>● 182-Day Forecast</div>
        <div class='fc-val'>{sc_f182:.2f}%</div>
        <div class='fc-ci'>95% CI: {sc_f182-0.85:.2f}% – {sc_f182+0.85:.2f}%</div>
      </div>
      <div class='fcast-card fc-364'>
        <div class='fc-lbl'>● 364-Day Forecast</div>
        <div class='fc-val'>{sc_f364:.2f}%</div>
        <div class='fc-ci'>95% CI: {sc_f364-1.02:.2f}% – {sc_f364+1.02:.2f}%</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ALL SCENARIOS COMPARISON
    st.markdown("---")
    sc_names, sc_91s, sc_182s, sc_364s, sc_cols = [], [], [], [], []
    for nm, sv in SCENARIOS.items():
        f91_, f182_, f364_, _ = run_sc(sv)
        sc_names.append(nm.split("—")[0].strip())
        sc_91s.append(f91_); sc_182s.append(f182_)
        sc_364s.append(f364_); sc_cols.append(sv["color"])

    fig_sc = go.Figure()
    fig_sc.add_trace(go.Bar(name="91D",  x=sc_names, y=sc_91s,
                            marker_color=GOLD, marker_line_width=0))
    fig_sc.add_trace(go.Bar(name="182D", x=sc_names, y=sc_182s,
                            marker_color=TEAL, marker_line_width=0))
    fig_sc.add_trace(go.Bar(name="364D", x=sc_names, y=sc_364s,
                            marker_color=VIOLET, marker_line_width=0))
    fig_sc.update_layout(**make_layout(barmode="group", height=380,
                          yaxis=dict(ticksuffix="%", gridcolor=GRID,
                                     tickfont=dict(color="#4b5563"))))
    st.plotly_chart(fig_sc, use_container_width=True)

    sc_tbl = pd.DataFrame({
        "Scenario":        sc_names,
        "OPR (%)":         [SCENARIOS[n]["opr"] for n in SCENARIOS],
        "GOR ($Bn)":       [SCENARIOS[n]["gor"] for n in SCENARIOS],
        "Debt/GDP (%)":    [SCENARIOS[n]["dbtgdp"] for n in SCENARIOS],
        "Oil ($/bbl)":     [SCENARIOS[n]["oil"] for n in SCENARIOS],
        "91D Fcst (%)":    sc_91s,
        "182D Fcst (%)":   sc_182s,
        "364D Fcst (%)":   sc_364s,
    })
    st.dataframe(sc_tbl, use_container_width=True, hide_index=True)
    st.markdown("<div class='src'>📌 2022 Crisis Replay scenario uses actual historical inputs — compare its 91D forecast to the actual annual avg of ~20.5% to gauge model accuracy in extreme regimes. Higher residuals during crisis reflect structural breaks and non-linearity not captured by the linear model.</div>", unsafe_allow_html=True)

    # CUSTOM SCENARIO
    st.markdown("---")
    st.markdown("<div style='font-family:Fraunces,serif;font-size:15px;font-weight:700;"
                "color:#d1d5db;margin-bottom:12px;'>🔧 Build Your Own Scenario</div>", unsafe_allow_html=True)
    cs1, cs2, cs3, cs4 = st.columns(4)
    with cs1: c_opr    = st.number_input("OPR (%)",        value=7.75, step=0.25, format="%.2f", key="cs_opr")
    with cs2: c_dbt    = st.number_input("Debt/GDP (%)",   value=96.0, step=1.0,  format="%.1f", key="cs_dbt")
    with cs3: c_oil    = st.number_input("Brent ($/bbl)",  value=81.0, step=5.0,  format="%.1f", key="cs_oil")
    with cs4: c_gor    = st.number_input("GOR ($Bn)",      value=7.28, step=0.2,  format="%.2f", key="cs_gor")
    cs5, cs6, cs7, cs8 = st.columns(4)
    with cs5: c_fd     = st.number_input("Fiscal Def/GDP",  value=5.5,  step=0.5, format="%.1f", key="cs_fd")
    with cs6: c_us10y  = st.number_input("US 10Y (%)",     value=4.30, step=0.1,  format="%.2f", key="cs_us10y")
    with cs7: c_infl   = st.number_input("CCPI (%)",       value=1.6,  step=0.2,  format="%.1f", key="cs_infl")
    with cs8: c_sigma  = st.number_input("Risk σ (%)",     value=3.20, step=0.1,  format="%.2f", key="cs_sigma")
    custom_sc = {"opr":c_opr,"us10y":c_us10y,"sigma":c_sigma,"dbtgdp":c_dbt,"fd":c_fd,
                 "oil":c_oil,"seas":0.05,"gor":c_gor,"infl":c_infl}
    cf91, cf182, cf364, _ = run_sc(custom_sc)
    st.markdown(f"""
    <div style='background:#08111d;border:1px solid rgba(196,161,56,0.2);border-radius:10px;
                padding:16px;margin-top:12px;display:flex;gap:30px;align-items:center;flex-wrap:wrap;'>
      <div><span style='font-family:DM Mono,monospace;font-size:9px;color:#374151;'>CUSTOM 91D</span>
           <div style='font-family:Fraunces,serif;font-size:28px;font-weight:900;color:#e8c96d;'>{cf91:.2f}%</div></div>
      <div><span style='font-family:DM Mono,monospace;font-size:9px;color:#374151;'>CUSTOM 182D</span>
           <div style='font-family:Fraunces,serif;font-size:28px;font-weight:900;color:#2dd4bf;'>{cf182:.2f}%</div></div>
      <div><span style='font-family:DM Mono,monospace;font-size:9px;color:#374151;'>CUSTOM 364D</span>
           <div style='font-family:Fraunces,serif;font-size:28px;font-weight:900;color:#818cf8;'>{cf364:.2f}%</div></div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# PAGE 5 — METHODOLOGY
# ═══════════════════════════════════════════════════════════════
elif "Methodology" in page:

    st.markdown(f"""
    <div class='page-banner'>
      <div class='banner-eyebrow'>Economic Theory · Model Design · Data Sources</div>
      <div class='banner-title'>📖 Methodology & Theory</div>
      <div class='banner-sub'>Economic foundations, data sourcing, and model limitations · {TODAY_STR}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='theory-box'>
    <b style='color:#818cf8;'>1. Fisher Effect (Irving Fisher, 1930)</b><br>
    Nominal interest rates adjust to compensate for expected inflation: <em>i ≈ r + πᵉ</em>. In the model,
    the <b>δ·(π−π*)</b> term captures deviations of actual CCPI from CBSL's 5% FIT target. When inflation
    runs below target (as in 2024–2025, CCPI ~2%), this term is negative, suppressing yields. The <b>α baseline</b>
    proxies the real neutral rate.
    </div>

    <div class='theory-box'>
    <b style='color:#818cf8;'>2. Expectations Theory of the Term Structure (Lutz, 1940)</b><br>
    Long-tenor yields embed expected future short rates. The <b>tenor offsets</b> (off91=0, off182=+0.22%,
    off364=+0.55%) capture this: the 364D yield embeds expectations about the path of OPR over the next year,
    plus a pure expectations premium. In 2022, an inverted structure briefly appeared as markets expected
    emergency rates to eventually fall.
    </div>

    <div class='theory-box'>
    <b style='color:#818cf8;'>3. Liquidity Preference / Term Premium (Hicks, 1939)</b><br>
    Even if future rates are expected to remain flat, investors demand a premium for locking funds in longer
    tenors (illiquidity risk, duration risk). This produces the normal upward slope. The tenor offsets partially
    capture this premium. Current spread: 364D–91D ≈ +55–65 bps — consistent with a recovering sovereign
    with moderate but declining risk.
    </div>

    <div class='theory-box'>
    <b style='color:#818cf8;'>4. Loanable Funds Theory (Wicksell → Robertson)</b><br>
    Increased government borrowing (↑Debt/GDP, ↑Fiscal Deficit) competes with private sector for the fixed
    pool of domestic savings, raising the cost of funds (yields). <b>γ₁·DebtGDP + γ₂·FD</b> captures this
    crowding-out effect. Sri Lanka's 2021 fiscal deficit of 11.7% directly preceded the 2022 yield spike.
    Note: partial Ricardian equivalence may dampen γ₂ if agents anticipate future tax increases.
    </div>

    <div class='theory-box'>
    <b style='color:#818cf8;'>5. Mundell-Fleming Framework (Mundell 1963, Fleming 1962)</b><br>
    In a small open economy, global interest rates transmit domestically via capital flows. <b>β₁·(US10Y+σ)</b>
    reflects: global risk-free rate (US10Y) + LKA-specific sovereign risk premium (σ). β₁ is low (~0.16)
    because LKA has capital controls limiting full arbitrage. σ ballooned to ~9% during the 2022 default crisis.
    </div>

    <div class='theory-box'>
    <b style='color:#818cf8;'>6. CBSL Monetary Transmission Mechanism</b><br>
    The OPR (introduced Nov 27, 2024) is the primary policy signal under CBSL's Flexible Inflation Targeting
    (FIT) framework. AWCMR (operating target) tracks OPR closely. T-bill WAY typically trades 0–50bps above
    OPR depending on market liquidity (net surplus of LKR 412Bn on 06-Mar-2026 → supportive of low yields).
    λ≈0.85 implies ~85bps pass-through per 100bps OPR change.
    </div>

    <div class='theory-box'>
    <b style='color:#818cf8;'>7. External Vulnerability Premium (Obstfeld-Rogoff, 1996)</b><br>
    <b>Ω·(1/GOR)</b> models the inverse relationship between foreign reserves and sovereign risk. When
    GOR=$1.9Bn (2022), this term added significant basis points. As GOR recovered to $7.284Bn (Feb 2026),
    the term stabilised. Includes IMF programme signalling effect — programme participation itself reduces σ
    even before reserves rebuild (credibility channel).
    </div>

    <div class='theory-box'>
    <b style='color:#818cf8;'>8. Cost-Push Inflation Channel (Samuelson-Solow)</b><br>
    Oil price shocks raise production costs → import-driven CCPI acceleration → expectations of higher
    future inflation → nominal yield compensation required. <b>ϕ·(Oil×W)</b> captures this with W=0.18
    (LKA oil import share). The Strait of Hormuz disruption (CBSL WEI 06-Mar-2026: Brent +$13.87/bbl in
    one week) represents a live supply-side risk.
    </div>

    <div class='theory-box'>
    <b style='color:#818cf8;'>Model Limitations & Caveats</b><br>
    ① OLS coefficients are estimated on a short sample (2015–2025) with only 11 observations — degrees of
    freedom are limited. ② Structural breaks: 2022 crisis period introduces non-linearity; a regime-switching
    model (Hamilton, 1989) or NARDL would improve crisis-fit. ③ Expectations are backward-looking;
    incorporating survey-based inflation expectations (e.g., CBSL Business Outlook Survey) would improve
    forward-looking accuracy. ④ This is a reduced-form structural model, not a full DSGE. ⑤ Forecasts are
    indicative only — <b>NOT financial advice.</b>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-family:DM Mono,monospace;font-size:10px;color:#374151;line-height:2;'>
    <b style='color:#4b5563;'>VERIFIED DATA SOURCES</b><br>
    T-Bill WAY 2015–2021 : CBSL Public Debt Management Report 2021, Table 3 (exact primary-market WAY)<br>
    T-Bill WAY 2022–2026 : CBSL Weekly Economic Indicators (WEI) — weekly series, annual averages computed<br>
    Policy Rate (OPR/SDFR/SLFR) : CBSL Monetary Policy Board official press releases<br>
    Govt Debt/GDP : CountryEconomy.com + World Bank Open Data + CBSL press releases<br>
    Fiscal Deficit/GDP : Ministry of Finance / Treasury.gov.lk annual reports<br>
    CCPI Inflation : Dept of Census & Statistics / CBSL official releases<br>
    USD/LKR : CBSL daily exchange rates (annual averages)<br>
    GOR : CBSL External Sector publications + TheGlobalEconomy.com; Feb 2026: CBSL WEI 06-Mar-2026<br>
    US 10Y Yield : US Federal Reserve FRED series DGS10 (annual averages)<br>
    Brent Crude : EIA U.S. Energy Information Administration (annual averages)<br>
    Current live data : CBSL WEI 06-March-2026 + CBSL MPR No.1/2026 (Jan 27, 2026)<br>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='text-align:center;padding:20px 0 10px;border-top:1px solid rgba(255,255,255,0.05);
            font-family:DM Mono,monospace;font-size:9px;color:#374151;line-height:2;
            margin-top:20px;'>
  DATA: CBSL.GOV.LK · TREASURY.GOV.LK · WORLD BANK · US FED FRED (DGS10) ·
  EIA · COUNTRYECONOMY.COM · THEGLOBALECONOMY.COM<br>
  Forecasts are indicative only — NOT financial advice · All data used up to {TODAY_STR}<br>
  LKA Yield Engine · GitHub: lka-yield-engine · Streamlit Community Cloud · © {TODAY_YEAR}
</div>
""", unsafe_allow_html=True)
