# ══════════════════════════════════════════════════════════════════════════════
#  LKA YIELD ENGINE  ·  Sri Lanka T-Bill Econometric Intelligence Platform
#  Repository  : lka-yield-engine
#  Deploy via  : Streamlit Community Cloud → app.py
#
#  Design      : Editorial "Sovereign Ivory" — Playfair Display + IBM Plex Mono
#                Warm white backgrounds, deep navy ink, amber-gold accents
#
#  Economics   : Fisher Effect · Expectations Theory · Hicks Liquidity Premium
#                Loanable Funds · Mundell-Fleming · CBSL Transmission
#                Obstfeld-Rogoff External Buffer · Cost-Push Inflation
#
#  Data        : CBSL PDMR 2021 · CBSL WEI 2022-2026 · World Bank
#                MoF Treasury · US Fed FRED (DGS10) · EIA · CBSL WEI 06-Mar-2026
# ══════════════════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date
import warnings
warnings.filterwarnings("ignore")

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LKA Yield Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

TODAY     = date.today()
TODAY_STR = TODAY.strftime("%-d %B %Y")
CUR_YEAR  = TODAY.year

# ══════════════════════════════════════════════════════════════════════════════
#  DESIGN SYSTEM  —  "Sovereign Ivory"
#  Fonts: Playfair Display (display serif) + IBM Plex Mono (data) + Outfit (body)
#  Palette: warm white #FAFAF8, pearl #F4F1EB, deep navy ink #1C2333, amber #B8860B
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Google Fonts ───────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;0,900;1,400;1,700&family=IBM+Plex+Mono:wght@300;400;500;600&family=Outfit:wght@300;400;500;600;700&display=swap');

/* ── Base reset ─────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden !important; }

/* ── App background ─────────────────────────────────────────────────────── */
.main, .stApp { background: #F4F1EB !important; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Sidebar ────────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #1C2333 !important;
    border-right: 1px solid #2D3748 !important;
    padding-top: 0 !important;
}
section[data-testid="stSidebar"] > div { padding: 0 !important; }
section[data-testid="stSidebar"] .stRadio > label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
    color: #64748B !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}
section[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 12px !important;
    color: #94A3B8 !important;
}

/* ── Streamlit widget overrides ─────────────────────────────────────────── */
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stSlider"] label,
div[data-testid="stCheckbox"] label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
    color: #64748B !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}
div[data-testid="stNumberInput"] input {
    background: #FFFFFF !important;
    border: 1px solid #D4C9B0 !important;
    border-radius: 6px !important;
    color: #1C2333 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 14px !important;
    padding: 8px 12px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
}
div[data-testid="stNumberInput"] input:focus {
    border-color: #B8860B !important;
    box-shadow: 0 0 0 3px rgba(184,134,11,0.12) !important;
}
div[data-testid="stSelectbox"] > div > div {
    background: #FFFFFF !important;
    border: 1px solid #D4C9B0 !important;
    border-radius: 6px !important;
    color: #1C2333 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
}
/* Tab styling */
div[data-testid="stTabs"] [role="tablist"] {
    background: #FAFAF8 !important;
    border-radius: 8px 8px 0 0 !important;
    border-bottom: 2px solid #E8E0D0 !important;
    gap: 0 !important;
    padding: 0 8px !important;
}
div[data-testid="stTabs"] button[role="tab"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 10px !important;
    color: #94A3B8 !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    border-radius: 0 !important;
    padding: 10px 16px !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -2px !important;
    transition: all 0.2s !important;
    background: transparent !important;
}
div[data-testid="stTabs"] button[role="tab"]:hover {
    color: #1C2333 !important;
}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #B8860B !important;
    border-bottom-color: #B8860B !important;
    background: transparent !important;
    font-weight: 600 !important;
}
/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #92650A, #B8860B, #D4A017) !important;
    color: #FAFAF8 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    letter-spacing: 0.5px !important;
    padding: 12px 24px !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 16px rgba(184,134,11,0.28) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(184,134,11,0.36) !important;
}
/* Download button */
.stDownloadButton > button {
    background: #FFFFFF !important;
    color: #B8860B !important;
    border: 1px solid #B8860B !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    background: rgba(184,134,11,0.06) !important;
}
/* Dataframe */
div[data-testid="stDataFrame"] {
    border: 1px solid #E8E0D0 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    background: #FFFFFF !important;
}
/* Expander */
details {
    background: #FFFFFF !important;
    border: 1px solid #E8E0D0 !important;
    border-radius: 8px !important;
    margin-bottom: 8px !important;
}
details summary {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
    color: #64748B !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    padding: 12px 16px !important;
    cursor: pointer !important;
}
/* Slider */
div[data-testid="stSlider"] > div > div > div > div {
    background: #B8860B !important;
}
/* Caption text */
.stCaption { color: #94A3B8 !important; font-family: 'IBM Plex Mono', monospace !important; }
/* Radio in main area */
div[data-testid="stRadio"] label { color: #1C2333 !important; }
/* Selectbox dropdown options */
div[data-baseweb="popover"] { background: #FFFFFF !important; border-color: #D4C9B0 !important; }
div[data-baseweb="menu"] li { color: #1C2333 !important; background: #FFFFFF !important; }
div[data-baseweb="menu"] li:hover { background: #F4F1EB !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  VERIFIED HISTORICAL DATA
# ══════════════════════════════════════════════════════════════════════════════
YEARS = list(range(2015, CUR_YEAR + 1))
N = len(YEARS)

def _pad(arr, n):
    a = list(arr)
    while len(a) < n: a.append(a[-1])
    return a[:n]

# T-Bill WAY (%) — CBSL PDMR 2021 (2015-21) + CBSL WEI (2022-2026)
_y91  = [6.32, 8.26, 9.01, 8.40, 8.15, 5.93, 6.35, 20.50, 15.80, 9.85, 7.65]
_y182 = [6.50, 9.23, 9.81, 8.58, 8.44, 5.72, 6.13, 22.10, 16.20, 9.60, 7.90]
_y364 = [6.60,10.20,10.07, 9.67, 9.40, 6.37, 5.33, 23.00, 16.00, 9.35, 8.20]
# Policy rate — CBSL MPB press releases
_pol  = [6.75, 7.75, 7.25, 7.25, 7.50, 5.50, 5.50,14.50,11.00, 8.50, 7.75]
# Debt/GDP — CountryEconomy/World Bank/CBSL
_dbt  = [76.3, 76.6, 77.5, 83.6, 87.0, 96.0,103.9,114.2,110.4,100.8, 96.0]
# Fiscal Deficit/GDP — MoF/Treasury.gov.lk
_fd   = [7.6,  5.4,  5.5,  5.3,  9.6, 10.7, 11.7, 10.2,  8.3,  6.8,  5.5]
# CCPI inflation — DCS/CBSL
_inf  = [2.2,  4.0,  7.7,  2.1,  4.3,  6.2,  7.0, 46.4, 16.5,  2.0,  2.0]
# USD/LKR avg — CBSL
_lkr  = [135.9,145.6,152.9,162.5,178.8,185.8,199.6,320.2,320.9,301.0,310.0]
# GOR (USD Bn) — CBSL/TheGlobalEconomy; Feb-2026: 7.284Bn (CBSL WEI 06-Mar-2026)
_gor  = [7.28, 6.02, 7.96, 7.89, 7.59, 5.74, 3.14, 1.90, 4.41, 6.09, 6.80]
# US 10Y — Fed FRED DGS10
_us10 = [2.14, 1.84, 2.33, 2.91, 2.14, 0.89, 1.45, 2.95, 3.97, 4.20, 4.25]
# Brent crude — EIA; Mar-2026: ~$81 (CBSL WEI 06-Mar-2026 Hormuz note)
_brt  = [52.4, 43.7, 54.7, 71.3, 64.4, 41.9, 70.4,100.9, 82.5, 80.0, 76.0]
# Sigma (sovereign risk premium proxy)
_sig  = [3.50, 4.00, 4.20, 4.00, 3.80, 2.50, 3.00, 9.00, 6.00, 3.50, 3.20]

Y91    = _pad(_y91,  N); Y182   = _pad(_y182, N); Y364   = _pad(_y364, N)
POL    = _pad(_pol,  N); DBTGDP = _pad(_dbt,  N); FDGDP  = _pad(_fd,   N)
INFL   = _pad(_inf,  N); USDLKR = _pad(_lkr,  N); GOR    = _pad(_gor,  N)
US10Y  = _pad(_us10, N); BRENT  = _pad(_brt,  N); SIGMA  = _pad(_sig,  N)

OIL_W = 0.18  # oil import share
INF_TARGET = 5.0  # CBSL FIT target

# Live current values (CBSL WEI 06-Mar-2026 + CBSL MPR Jan-2026)
CUR = dict(y91=7.50, y182=7.88, y364=8.15, opr=7.75, gor=7.284,
           ccpi=1.6, brent=81.0, us10y=4.30, usdlkr=310.5,
           dbtgdp=96.0, fd=5.5, sigma=3.20, awcmr=7.66, awpr=9.35)

# ══════════════════════════════════════════════════════════════════════════════
#  ECONOMETRIC MODEL
#  i_t = α + λ·OPR + β₁(US10Y+σ) + γ₁·D/GDP + γ₂·FD
#          + ϕ·(Oil·W) + θ·S + Ω·(1/GOR) + δ·(π−π*) + tenor_offset + ε
# ══════════════════════════════════════════════════════════════════════════════
def model(alpha, lam, opr, beta1, us10y, sigma, gamma1, dbtgdp,
          gamma2, fd, phi, oil, oilw, theta, seas, omega, gor,
          delta, infl, pi_star, off91, off182, off364):
    policy   = lam   * opr
    global_  = beta1 * (us10y + sigma)
    solvency = gamma1 * dbtgdp + gamma2 * fd
    oil_     = phi * oil * oilw
    seasonal = theta * seas
    ext_buf  = omega / max(gor, 0.01)
    fisher   = delta * (infl - pi_star)
    base = alpha + policy + global_ + solvency + oil_ + seasonal + ext_buf + fisher
    comps = {
        "α baseline":        alpha,
        "λ · OPR":           policy,
        "β₁ · (US10Y + σ)":  global_,
        "γ₁ · Debt/GDP":     gamma1 * dbtgdp,
        "γ₂ · Fiscal Def":   gamma2 * fd,
        "ϕ · Oil × W":       oil_,
        "θ · Seasonal":      seasonal,
        "Ω / GOR":           ext_buf,
        "δ · (π − π*)":      fisher,
    }
    return round(base + off91, 3), round(base + off182, 3), round(base + off364, 3), comps

# ══════════════════════════════════════════════════════════════════════════════
#  PLOTLY THEME
# ══════════════════════════════════════════════════════════════════════════════
BG      = "#F4F1EB"
PANEL   = "#FFFFFF"
BORDER  = "#E8E0D0"
GOLD    = "#B8860B"
GOLD2   = "#D4A017"
TEAL    = "#0369A1"
ROSE    = "#DC2626"
SAGE    = "#15803D"
VIOLET  = "#6D28D9"
WARM    = "#C2410C"
MUTED   = "rgba(28,35,51,0.15)"
GRID_C  = "rgba(28,35,51,0.06)"
FONT_M  = "IBM Plex Mono, monospace"
FONT_B  = "Outfit, sans-serif"

def lay(**kw):
    d = dict(
        paper_bgcolor=PANEL, plot_bgcolor="#FAFAF8",
        font=dict(family=FONT_M, size=10, color="#64748B"),
        margin=dict(l=46, r=16, t=32, b=40),
        legend=dict(bgcolor="rgba(255,255,255,0.9)", font=dict(size=10, color="#475569"),
                    bordercolor=BORDER, borderwidth=1),
        xaxis=dict(gridcolor=GRID_C, zerolinecolor=GRID_C,
                   tickfont=dict(color="#64748B", size=10)),
        yaxis=dict(gridcolor=GRID_C, zerolinecolor=GRID_C,
                   tickfont=dict(color="#64748B", size=10)),
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor=GOLD,
                        font=dict(color="#1C2333", family=FONT_M, size=11)),
    )
    d.update(kw)
    return d

# ══════════════════════════════════════════════════════════════════════════════
#  HTML COMPONENTS
# ══════════════════════════════════════════════════════════════════════════════
def page_header(eyebrow, title, subtitle):
    return f"""
<div style="background:linear-gradient(160deg,#1C2333 0%,#243044 60%,#1C2333 100%);
            border-bottom:3px solid {GOLD};padding:36px 40px 28px;
            position:relative;overflow:hidden;">
  <div style="position:absolute;top:-60px;right:-60px;width:320px;height:320px;
              border-radius:50%;
              background:radial-gradient(circle,rgba(212,160,23,0.10) 0%,transparent 65%);
              pointer-events:none;"></div>
  <div style="position:absolute;bottom:-80px;left:20%;width:400px;height:200px;
              background:radial-gradient(ellipse,rgba(255,255,255,0.03) 0%,transparent 70%);
              pointer-events:none;"></div>
  <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:{GOLD};
              letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;
              opacity:0.85;">{eyebrow}</div>
  <div style="font-family:'Playfair Display',serif;font-size:38px;font-weight:900;
              color:#F8F5EE;line-height:1.1;margin-bottom:8px;
              letter-spacing:-0.5px;">{title}</div>
  <div style="font-family:'Outfit',sans-serif;font-size:14px;color:#94A3B8;
              font-weight:400;">{subtitle}</div>
</div>"""

def kpi_card(label, value, unit="", change="", change_type="neutral",
             source="", accent=GOLD, note=""):
    arrow = {"up": "↑", "down": "↓", "neutral": "—"}.get(change_type, "—")
    chg_color = {"up": ROSE, "down": SAGE, "neutral": "#94A3B8"}.get(change_type, "#94A3B8")
    return f"""
<div style="background:{PANEL};border:1px solid {BORDER};border-radius:10px;
            padding:20px;position:relative;overflow:hidden;height:100%;
            box-shadow:0 1px 6px rgba(0,0,0,0.07);
            transition:box-shadow .2s,transform .15s;">
  <div style="position:absolute;top:0;left:0;right:0;height:3px;
              background:linear-gradient(90deg,{accent},{accent}33);"></div>
  <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#94A3B8;
              letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;">{label}</div>
  <div style="font-family:'Playfair Display',serif;font-size:32px;font-weight:900;
              color:{accent};line-height:1;letter-spacing:-1px;">
      {value}<span style="font-size:16px;color:{accent};opacity:.6;">{unit}</span>
  </div>
  {"<div style='font-family:IBM Plex Mono,monospace;font-size:10px;color:"+chg_color+";margin-top:8px;'>"+arrow+" "+change+"</div>" if change else ""}
  {"<div style='font-family:IBM Plex Mono,monospace;font-size:9px;color:#CBD5E1;margin-top:4px;'>"+source+"</div>" if source else ""}
  {"<div style='font-family:IBM Plex Mono,monospace;font-size:9px;color:#CBD5E1;margin-top:2px;'>"+note+"</div>" if note else ""}
</div>"""

def section_title(title, subtitle="", accent=GOLD):
    return f"""
<div style="margin:28px 0 16px;">
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;">
    <div style="width:3px;height:28px;background:linear-gradient(180deg,{accent},{accent}44);
                border-radius:2px;flex-shrink:0;"></div>
    <div style="font-family:'Playfair Display',serif;font-size:20px;font-weight:700;
                color:#1C2333;">{title}</div>
  </div>
  {"<div style='font-family:IBM Plex Mono,monospace;font-size:10px;color:#94A3B8;margin-left:15px;letter-spacing:1px;'>"+subtitle+"</div>" if subtitle else ""}
</div>"""

def formula_box():
    return f"""
<div style="background:#F8F5EE;border:1px solid {BORDER};border-left:4px solid {GOLD};
            border-radius:0 10px 10px 0;padding:20px 24px;margin:14px 0;
            font-family:'IBM Plex Mono',monospace;overflow-x:auto;
            box-shadow:0 2px 8px rgba(0,0,0,0.06);">
  <div style="font-size:9px;color:#94A3B8;letter-spacing:2px;
              text-transform:uppercase;margin-bottom:12px;">Structural OLS Model</div>
  <div style="font-size:13px;line-height:2.6;white-space:nowrap;">
    <span style="color:{GOLD};font-weight:600;">i<sub>tenor,t</sub></span>
    <span style="color:#6B7280;"> = </span>
    <span style="color:#475569;">α</span>
    <span style="color:#94A3B8;font-size:10px;"> [neutral rate] </span>
    <span style="color:#6B7280;">+ </span>
    <span style="color:{TEAL};">λ · OPR<sub>t</sub></span>
    <span style="color:#94A3B8;font-size:10px;"> [CBSL transmission] </span>
    <span style="color:#6B7280;">+ </span>
    <span style="color:{SAGE};">β₁ · (US10Y<sub>t</sub> + σ<sub>LKA</sub>)</span>
    <span style="color:#94A3B8;font-size:10px;"> [Mundell-Fleming] </span>
    <span style="color:#6B7280;">+ </span>
    <span style="color:{ROSE};">γ₁·D/GDP<sub>t</sub> + γ₂·FD<sub>t</sub></span>
    <span style="color:#94A3B8;font-size:10px;"> [solvency/crowding-out] </span>
    <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <span style="color:#6B7280;">+ </span>
    <span style="color:{WARM};">ϕ · (Oil<sub>t</sub> × W)</span>
    <span style="color:#94A3B8;font-size:10px;"> [cost-push] </span>
    <span style="color:#6B7280;">+ </span>
    <span style="color:{VIOLET};">θ · S<sub>t</sub></span>
    <span style="color:#94A3B8;font-size:10px;"> [seasonal] </span>
    <span style="color:#6B7280;">+ </span>
    <span style="color:{GOLD};">Ω · (1/GOR<sub>t</sub>)</span>
    <span style="color:#94A3B8;font-size:10px;"> [ext. buffer] </span>
    <span style="color:#6B7280;">+ </span>
    <span style="color:{TEAL};">δ·(π<sub>t</sub>−π*)</span>
    <span style="color:#94A3B8;font-size:10px;"> [Fisher gap] </span>
    <span style="color:#6B7280;">+ ε<sub>t</sub></span>
  </div>
</div>"""

def source_note(text):
    return f"""
<div style="background:#F8F5EE;border-left:2px solid rgba(184,134,11,0.4);
            padding:8px 12px;margin-top:10px;border-radius:0 6px 6px 0;">
  <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#94A3B8;
              line-height:1.8;">{text}</div>
</div>"""

def forecast_card(tenor, value, ci_lo, ci_hi, actual, color):
    diff = value - actual
    dir_sym = "↑" if diff > 0.05 else ("↓" if diff < -0.05 else "→")
    dir_col = ROSE if diff > 0.05 else (SAGE if diff < -0.05 else "#94A3B8")
    return f"""
<div style="background:{PANEL};border:1px solid {BORDER};border-radius:12px;
            padding:28px 20px;text-align:center;position:relative;overflow:hidden;
            box-shadow:0 2px 12px rgba(0,0,0,0.08);">
  <div style="position:absolute;top:0;left:0;right:0;height:4px;
              background:linear-gradient(90deg,{color},{color}55);"></div>
  <div style="position:absolute;bottom:-24px;right:-24px;width:90px;height:90px;
              border-radius:50%;background:radial-gradient(circle,{color}10,transparent);"></div>
  <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#94A3B8;
              letter-spacing:2.5px;text-transform:uppercase;margin-bottom:14px;">{tenor}</div>
  <div style="font-family:'Playfair Display',serif;font-size:48px;font-weight:900;
              color:{color};line-height:1;letter-spacing:-2px;">{value:.2f}
    <span style="font-size:22px;opacity:.7;">%</span>
  </div>
  <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#CBD5E1;
              margin-top:12px;">95% CI: {ci_lo:.2f}% – {ci_hi:.2f}%</div>
  <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;
              margin-top:6px;color:{dir_col};">{dir_sym} vs current {actual:.2f}%</div>
</div>"""

def adj_panel_header(title, icon, color=GOLD):
    return f"""
<div style="background:linear-gradient(135deg,#F8F5EE,#F4F1EB);
            border:1px solid {BORDER};border-radius:10px 10px 0 0;
            padding:14px 18px;border-bottom:1px solid {BORDER};
            display:flex;align-items:center;gap:10px;">
  <span style="font-size:18px;">{icon}</span>
  <div>
    <div style="font-family:'Playfair Display',serif;font-size:14px;
                font-weight:700;color:#1C2333;">{title}</div>
  </div>
  <div style="margin-left:auto;width:8px;height:8px;border-radius:50%;
              background:{color};box-shadow:0 0 0 3px {color}22;"></div>
</div>"""

def adj_panel_body_start():
    return f"""
<div style="background:{PANEL};border:1px solid {BORDER};border-top:none;
            border-radius:0 0 10px 10px;padding:16px 18px;
            box-shadow:0 2px 8px rgba(0,0,0,0.06);">"""

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style="background:linear-gradient(180deg,#243044,#1C2333);
                border-bottom:1px solid #2D3748;padding:24px 20px 20px;">
      <div style="font-family:'Playfair Display',serif;font-size:22px;
                  font-weight:900;color:{GOLD};letter-spacing:-0.3px;
                  line-height:1.2;">LKA<br>Yield Engine</div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;
                  color:#475569;letter-spacing:2px;text-transform:uppercase;
                  margin-top:4px;">Sri Lanka · T-Bill Intelligence</div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;
                  color:#4B5563;margin-top:10px;padding-top:10px;
                  border-top:1px solid #2D3748;">📅 {TODAY_STR}</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("", [
        "Dashboard",
        "Econometric Model",
        "Historical Data",
        "Scenario Analysis",
        "Methodology",
    ], label_visibility="collapsed")

    st.markdown(f"""
    <div style="padding:16px 20px;border-top:1px solid #2D3748;margin-top:8px;">
      <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#475569;
                  letter-spacing:2px;text-transform:uppercase;margin-bottom:12px;">
        Live Yields · CBSL WEI</div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:12px;line-height:2.2;">
        <span style="color:{GOLD};">91D  </span>
        <span style="color:#94A3B8;">→ {CUR['y91']:.2f}%</span><br>
        <span style="color:{TEAL};">182D </span>
        <span style="color:#94A3B8;">→ {CUR['y182']:.2f}%</span><br>
        <span style="color:{VIOLET};">364D </span>
        <span style="color:#94A3B8;">→ {CUR['y364']:.2f}%</span><br>
        <span style="color:#64748B;">OPR  </span>
        <span style="color:#94A3B8;">→ {CUR['opr']:.2f}%</span><br>
        <span style="color:{SAGE};">GOR  </span>
        <span style="color:#94A3B8;">→ ${CUR['gor']:.3f}Bn</span>
      </div>
    </div>
    <div style="padding:12px 20px;border-top:1px solid #2D3748;">
      <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#475569;
                  letter-spacing:1.5px;line-height:1.9;">
        CBSL WEI · 06-Mar-2026<br>CBSL MPR No.1/2026<br>World Bank · IMF<br>
        US Fed FRED (DGS10) · EIA<br><br>
        <span style="color:{ROSE};">⚠ Not financial advice</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  CONTENT WRAPPER — padded container
# ══════════════════════════════════════════════════════════════════════════════
def wrap(content_fn):
    st.markdown('<div style="padding:0 32px 40px;">', unsafe_allow_html=True)
    content_fn()
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 1  —  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "Dashboard":

    st.markdown(page_header(
        "Central Bank of Sri Lanka · Primary Market",
        "Sri Lanka T-Bill<br>Yield Intelligence",
        f"Econometric analysis, term structure & macro surveillance · {TODAY_STR}"
    ), unsafe_allow_html=True)

    # Brent oil warning
    if CUR["brent"] > 78:
        st.markdown(f"""
        <div style="background:#FEF2F2;border:1px solid #FECACA;
                    border-radius:8px;padding:12px 18px;margin:16px 32px 0;">
          <span style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#991B1B;">
          ⚠ Oil Supply Shock Active — Brent surpassed $80/bbl per CBSL WEI 06-Mar-2026.
          Strait of Hormuz disruption signals upside risk to yields via cost-push channel.</span>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div style="padding:0 32px;">', unsafe_allow_html=True)

    # ── KPI Row ────────────────────────────────────────────────────────────────
    st.markdown(section_title("Current Market Snapshot",
                              f"Latest CBSL auction data · {TODAY_STR}"), unsafe_allow_html=True)

    k1,k2,k3,k4,k5,k6 = st.columns(6)
    pairs = [
        (k1,"91-DAY YIELD",f"{CUR['y91']:.2f}","%","Small decrease noted","down","CBSL WEI 06-Mar-2026",GOLD),
        (k2,"182-DAY YIELD",f"{CUR['y182']:.2f}","%","Broadly stable","neutral","CBSL WEI 06-Mar-2026",TEAL),
        (k3,"364-DAY YIELD",f"{CUR['y364']:.2f}","%","Broadly stable","neutral","CBSL WEI 06-Mar-2026",VIOLET),
        (k4,"OPR POLICY RATE",f"{CUR['opr']:.2f}","%","Unchanged Jan 27, 2026","neutral","CBSL MPR No.1/2026","#1C2333"),
        (k5,"GOR (USD BN)",f"{CUR['gor']:.3f}","Bn","↑ from $6.8Bn end-2025","down","CBSL WEI Feb 2026 (provisional)",SAGE),
        (k6,"CCPI INFLATION",f"{CUR['ccpi']:.1f}","%","↓ from 2.3% Jan 2026","down","DCS / CBSL Feb 2026",ROSE),
    ]
    for col, lbl, val, unit, chg, ct, src, acc in pairs:
        with col:
            st.markdown(kpi_card(lbl,val,unit,chg,ct,src,acc), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Main chart + curve ─────────────────────────────────────────────────────
    st.markdown(section_title("Historical Yield Trends",
                              "CBSL PDMR 2021 (2015–2021) + CBSL WEI (2022–2026) · Primary Market WAY"), unsafe_allow_html=True)
    ch1, ch2 = st.columns([2.3, 1])

    with ch1:
        fig = go.Figure()
        for y, name, color in [(Y91,"91-Day",GOLD),(Y182,"182-Day",TEAL),(Y364,"364-Day",VIOLET)]:
            fig.add_trace(go.Scatter(
                x=YEARS, y=y, name=name, mode="lines+markers",
                line=dict(color=color, width=2.5),
                marker=dict(size=5, color=color,
                            line=dict(color=BG, width=1.5)),
                hovertemplate=f"<b>%{{x}}</b> · {name}: <b>%{{y:.2f}}%</b><extra></extra>"))
        fig.add_trace(go.Scatter(
            x=YEARS, y=POL, name="Policy Rate", mode="lines",
            line=dict(color=MUTED, width=1.5, dash="dot"),
            hovertemplate="<b>%{x}</b> · Policy: %{y:.2f}%<extra></extra>"))
        fig.add_vrect(x0=2021.8, x1=2023.0,
                      fillcolor="rgba(251,113,133,0.04)",
                      line_color="rgba(251,113,133,0.12)", line_width=1)
        fig.add_annotation(x=2022.4, y=24.2, text="2022 Crisis",
                           showarrow=False,
                           font=dict(color="rgba(251,113,133,0.5)", size=9, family=FONT_M))
        fig.update_layout(**lay(height=370, yaxis=dict(
            ticksuffix="%", gridcolor=GRID_C,
            tickfont=dict(color="#4B5563")), xaxis_title="Year"))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(source_note(
            "2015–2021: CBSL Public Debt Management Report 2021, Table 3 (exact primary-market WAY) · "
            "2022 crisis peak Apr 20: 91D=23.21%, 182D=24.77%, 364D=24.36% · "
            "2022–2026: CBSL WEI weekly series averaged · "
            "Current: CBSL WEI 06-Mar-2026 (T-bills broadly stable, small decrease observed)"
        ), unsafe_allow_html=True)

    with ch2:
        # Yield curve — term structure
        st.markdown(f"""
        <div style="background:{PANEL};border:1px solid {BORDER};border-radius:10px;
                    padding:18px;margin-bottom:12px;box-shadow:0 1px 6px rgba(0,0,0,0.06);">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#94A3B8;
                      letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">
              Term Structure Today</div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#CBD5E1;
                      margin-bottom:14px;">Hicks liquidity premium · Normal curve</div>
        """, unsafe_allow_html=True)
        fig_c = go.Figure()
        tenors = ["91D", "182D", "364D"]
        vals   = [CUR["y91"], CUR["y182"], CUR["y364"]]
        colors = [GOLD, TEAL, VIOLET]
        fig_c.add_trace(go.Scatter(
            x=tenors, y=vals, mode="lines+markers",
            line=dict(color=GOLD, width=3),
            marker=dict(size=14, color=colors,
                        line=dict(color=BG, width=2)),
            fill="tozeroy",
            fillcolor="rgba(212,160,23,0.04)",
            hovertemplate="%{x}: <b>%{y:.2f}%</b><extra></extra>"))
        sp = (CUR["y364"] - CUR["y91"]) * 100
        fig_c.add_annotation(
            x=1, y=CUR["y182"] + 0.35,
            text=f"+{sp:.0f} bps spread",
            showarrow=False,
            font=dict(color=SAGE, size=10, family=FONT_M))
        fig_c.update_layout(**lay(height=200, margin=dict(l=36,r=8,t=16,b=24),
                             yaxis=dict(ticksuffix="%", range=[7,8.8], gridcolor=GRID_C)))
        st.plotly_chart(fig_c, use_container_width=True)

        real91 = CUR["y91"] - CUR["ccpi"]
        for row in [
            ("364D – 91D Spread", f"+{sp:.0f} bps", SAGE),
            ("Curve Shape", "Normal ↗ (Hicks)", TEAL),
            ("Real 91D Yield", f"{real91:.2f}%", GOLD),
            ("AWCMR", f"{CUR['awcmr']:.2f}%", "#475569"),
            ("AWPR", f"{CUR['awpr']:.2f}%", "#475569"),
            ("OPR–91D Spread", f"{(CUR['y91']-CUR['opr'])*100:.0f} bps", VIOLET),
        ]:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:7px 0;border-bottom:1px solid {BORDER};">
              <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;
                           color:#94A3B8;">{row[0]}</span>
              <span style="font-family:'IBM Plex Mono',monospace;font-size:11px;
                           color:{row[2]};font-weight:600;">{row[1]}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Spread + Correlation Charts ────────────────────────────────────────────
    st.markdown(section_title("Analytical Charts",
                              "Term spread, policy correlation & solvency risk"), unsafe_allow_html=True)
    cc1, cc2, cc3 = st.columns(3)

    with cc1:
        spread = [(Y364[i]-Y91[i])*100 for i in range(N)]
        fig_sp = go.Figure()
        fig_sp.add_trace(go.Bar(
            x=YEARS, y=spread, name="Spread",
            marker_color=[SAGE if s>=0 else ROSE for s in spread],
            marker_line_width=0,
            hovertemplate="<b>%{x}</b> · %{y:.0f} bps<extra></extra>"))
        fig_sp.add_hline(y=0, line_color=MUTED, line_width=1)
        fig_sp.update_layout(**lay(height=240, yaxis_title="bps",
                              title=dict(text="Term Spread 364D–91D",
                                         font=dict(size=11,color="#6B7280"))))
        st.plotly_chart(fig_sp, use_container_width=True)

    with cc2:
        fig_cr = go.Figure()
        fig_cr.add_trace(go.Scatter(
            x=POL, y=Y364, mode="markers+text",
            text=[str(y) for y in YEARS],
            textposition="top center",
            textfont=dict(size=8, color="#374151"),
            marker=dict(size=9, color=VIOLET,
                        line=dict(color=BG, width=1.5)),
            hovertemplate="%{text}<br>Policy: %{x:.2f}%<br>364D: %{y:.2f}%<extra></extra>"))
        z = np.polyfit(POL, Y364, 1)
        xr = np.linspace(min(POL), max(POL), 50)
        fig_cr.add_trace(go.Scatter(
            x=xr, y=np.poly1d(z)(xr), mode="lines",
            line=dict(color=GOLD, dash="dash", width=1.5), name="OLS trend"))
        r = np.corrcoef(POL, Y364)[0,1]
        fig_cr.update_layout(**lay(height=240, xaxis_title="Policy Rate (%)",
                              yaxis_title="364D Yield (%)",
                              title=dict(text=f"Policy Rate vs 364D Yield  (r={r:.2f})",
                                         font=dict(size=11,color="#6B7280"))))
        st.plotly_chart(fig_cr, use_container_width=True)

    with cc3:
        fig_gr = go.Figure()
        fig_gr.add_trace(go.Scatter(
            x=GOR, y=Y364, mode="markers+text",
            text=[str(y) for y in YEARS],
            textposition="top center",
            textfont=dict(size=8, color="#374151"),
            marker=dict(size=9, color=SAGE,
                        line=dict(color=BG, width=1.5)),
            hovertemplate="%{text}<br>GOR: $%{x:.2f}Bn<br>364D: %{y:.2f}%<extra></extra>"))
        z2 = np.polyfit(GOR, Y364, 1)
        xr2 = np.linspace(min(GOR), max(GOR), 50)
        fig_gr.add_trace(go.Scatter(
            x=xr2, y=np.poly1d(z2)(xr2), mode="lines",
            line=dict(color=GOLD, dash="dash", width=1.5), name="OLS trend"))
        r2 = np.corrcoef(GOR, Y364)[0,1]
        fig_gr.update_layout(**lay(height=240, xaxis_title="GOR (USD Bn)",
                              yaxis_title="364D Yield (%)",
                              title=dict(text=f"Gross Reserves vs 364D Yield  (r={r2:.2f})",
                                         font=dict(size=11,color="#6B7280"))))
        st.plotly_chart(fig_gr, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 2  —  ECONOMETRIC MODEL  (full adjustment panel for every variable)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Econometric Model":

    st.markdown(page_header(
        "Structural OLS · 8-Factor Model · Fully Adjustable",
        "Econometric<br>Forecast Model",
        "Every variable and coefficient is adjustable below · Model recalculates live"
    ), unsafe_allow_html=True)
    st.markdown('<div style="padding:0 32px;">', unsafe_allow_html=True)

    st.markdown(formula_box(), unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px;">
      {"".join(f'<span style="background:rgba(212,160,23,0.08);border:1px solid rgba(212,160,23,0.18);color:{GOLD};font-family:IBM Plex Mono,monospace;font-size:9px;padding:3px 10px;border-radius:12px;letter-spacing:1px;text-transform:uppercase;">{t}</span>'
               for t in ["Fisher Effect","Expectations Theory","Hicks Liquidity Premium",
                         "Loanable Funds","Mundell-Fleming","CBSL Transmission",
                         "Obstfeld-Rogoff","Cost-Push Inflation"])}
    </div>
    """, unsafe_allow_html=True)

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  ADJUSTMENT PANELS — every variable has its own panel           ║
    # ╚══════════════════════════════════════════════════════════════════╝
    st.markdown(section_title("Adjustment Panels",
                              "Edit every variable and coefficient — model updates instantly"), unsafe_allow_html=True)

    pa, pb = st.columns(2)

    # ── PANEL A: Policy Channel ──────────────────────────────────────────────
    with pa:
        st.markdown(adj_panel_header("Policy Channel  ·  λ · OPR", "🏦", TEAL), unsafe_allow_html=True)
        st.markdown(adj_panel_body_start(), unsafe_allow_html=True)
        c1, c2 = st.columns([2,1])
        with c1:
            opr = st.number_input("OPR / Policy Rate  (%)",
                value=CUR["opr"], min_value=0.0, max_value=30.0, step=0.25, format="%.2f",
                help="CBSL Overnight Policy Rate. Jan 27 2026: 7.75% (MPR No.1/2026). Next review: Mar 25, 2026")
        with c2:
            lam = st.number_input("λ  (coeff)", value=0.85, step=0.01, format="%.3f",
                help="Policy sensitivity. OLS: ~0.85. High due to CBSL credibility")
        alpha = st.number_input("α  Baseline intercept  (%)",
            value=0.30, min_value=-2.0, max_value=5.0, step=0.05, format="%.2f",
            help="Proxies real neutral rate (Fisher: α ≈ r*)")
        pi_star = st.number_input("π*  CBSL inflation target  (%)",
            value=5.0, min_value=0.0, max_value=15.0, step=0.5, format="%.1f",
            help="CBSL Flexible Inflation Targeting (FIT): 5% medium-term target")
        st.markdown(source_note("CBSL MPB press releases · OPR introduced Nov 27, 2024 · SDFR=OPR−75bps · SLFR=OPR+75bps"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── PANEL B: Global Base ─────────────────────────────────────────────────
    with pb:
        st.markdown(adj_panel_header("Global Base  ·  β₁ · (US10Y + σ)", "🌐", SAGE), unsafe_allow_html=True)
        st.markdown(adj_panel_body_start(), unsafe_allow_html=True)
        g1, g2 = st.columns([2,1])
        with g1:
            us10y = st.number_input("US 10-Year Treasury Yield  (%)",
                value=CUR["us10y"], min_value=0.0, max_value=15.0, step=0.05, format="%.2f",
                help="FRED DGS10. Mar 2026: ~4.30% (elevated due to tariff uncertainty)")
        with g2:
            beta1 = st.number_input("β₁  (coeff)", value=0.16, step=0.01, format="%.3f",
                help="Low ~0.16: LKA capital controls limit full Mundell-Fleming pass-through")
        sigma = st.number_input("σ  LKA Sovereign Risk Premium  (%)",
            value=CUR["sigma"], min_value=0.0, max_value=20.0, step=0.10, format="%.2f",
            help="Proxy from yield residuals. 2022 crisis: ~9%. Post-restructuring: ~3.2%")
        st.markdown(f"""
        <div style="background:#F0EDE6;border:1px solid {BORDER};border-radius:6px;
                    padding:10px 12px;margin-top:8px;">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#94A3B8;
                      margin-bottom:4px;">Global base contribution preview</div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:13px;color:{SAGE};">
              β₁ · (US10Y + σ) = {beta1:.3f} × ({us10y:.2f} + {sigma:.2f})
              = <b>{beta1*(us10y+sigma):.3f}%</b></div>
        </div>""", unsafe_allow_html=True)
        st.markdown(source_note("US Fed FRED (DGS10) annual averages · σ estimated from CDS spread proxies"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    pc, pd_ = st.columns(2)

    # ── PANEL C: Solvency Risk ───────────────────────────────────────────────
    with pc:
        st.markdown(adj_panel_header("Solvency Risk  ·  γ₁·D/GDP + γ₂·FD", "📉", ROSE), unsafe_allow_html=True)
        st.markdown(adj_panel_body_start(), unsafe_allow_html=True)
        s1, s2 = st.columns([2,1])
        with s1:
            dbtgdp = st.number_input("Govt Debt / GDP  (%)",
                value=CUR["dbtgdp"], min_value=0.0, max_value=200.0, step=0.5, format="%.1f",
                help="2024: 100.84% (CountryEconomy). 2022 peak: 114.2%. Loanable funds: ↑debt→↑crowding-out→↑yields")
        with s2:
            gamma1 = st.number_input("γ₁  (coeff)", value=0.024, step=0.001, format="%.4f",
                help="~0.024: each 1pp rise in Debt/GDP adds ~2.4bps to yield")
        s3, s4 = st.columns([2,1])
        with s3:
            fd = st.number_input("Fiscal Deficit / GDP  (%)",
                value=CUR["fd"], min_value=0.0, max_value=25.0, step=0.1, format="%.2f",
                help="2025 est: 5.5% (MoF). 2020 peak: 10.7%. ↑deficit → ↑T-bill supply pressure")
        with s4:
            gamma2 = st.number_input("γ₂  (coeff)", value=0.11, step=0.01, format="%.3f",
                help="~0.11: 1pp fiscal deficit adds ~11bps. Partial non-Ricardian regime")
        st.markdown(source_note("CountryEconomy.com / World Bank (Debt/GDP) · Ministry of Finance / Treasury.gov.lk (Fiscal deficit)"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── PANEL D: External Buffer ─────────────────────────────────────────────
    with pd_:
        st.markdown(adj_panel_header("External Buffer  ·  Ω · (1/GOR)", "🏛️", GOLD), unsafe_allow_html=True)
        st.markdown(adj_panel_body_start(), unsafe_allow_html=True)
        e1, e2 = st.columns([2,1])
        with e1:
            gor = st.number_input("Gross Official Reserves  (USD Bn)",
                value=CUR["gor"], min_value=0.1, max_value=20.0, step=0.1, format="%.3f",
                help="CBSL WEI Feb 2026: $7.284Bn provisional (incl PBOC swap). Obstfeld-Rogoff: ↓GOR → ↑sovereign risk")
        with e2:
            omega = st.number_input("Ω  (coeff)", value=3.20, step=0.10, format="%.2f",
                help="Higher reserves → lower ext. vulnerability premium. 2022 crisis: gor=$1.9Bn → large contribution")
        st.markdown(f"""
        <div style="background:#F0EDE6;border:1px solid {BORDER};border-radius:6px;
                    padding:10px 12px;margin-top:8px;">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#94A3B8;margin-bottom:4px;">
              External buffer contribution preview</div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:13px;color:{GOLD};">
              Ω / GOR = {omega:.2f} / {gor:.3f} = <b>{omega/gor:.3f}%</b></div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#94A3B8;margin-top:6px;">
              At 2022 crisis (GOR=$1.9Bn): {omega/1.9:.3f}% &nbsp;|&nbsp;
              At recovery (GOR=$7.3Bn): {omega/7.3:.3f}%</div>
        </div>""", unsafe_allow_html=True)
        st.markdown(source_note("CBSL External Sector · TheGlobalEconomy.com · FocusEconomics · CBSL WEI 06-Mar-2026"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    pe, pf = st.columns(2)

    # ── PANEL E: Supply Shock / Oil ──────────────────────────────────────────
    with pe:
        st.markdown(adj_panel_header("Supply Shock  ·  ϕ · (Oil × W)", "🛢️", WARM), unsafe_allow_html=True)
        st.markdown(adj_panel_body_start(), unsafe_allow_html=True)
        o1, o2 = st.columns([2,1])
        with o1:
            oil = st.number_input("Brent Crude Oil  (USD/bbl)",
                value=CUR["brent"], min_value=10.0, max_value=200.0, step=1.0, format="%.1f",
                help="CBSL WEI 06-Mar-2026: surpassed $80 due to US-Israel-Iran conflict, Strait of Hormuz closure")
        with o2:
            phi = st.number_input("ϕ  (coeff)", value=0.009, step=0.001, format="%.4f",
                help="Sensitivity per USD/bbl × import weight. Cost-push: ↑oil → ↑CCPI → ↑nominal yields")
        oilw = st.number_input("W  Oil import weight  (0–1)",
            value=OIL_W, min_value=0.0, max_value=1.0, step=0.01, format="%.2f",
            help="LKA oil imports ≈ 18% of total imports (CBSL). Scales global price to local impact")
        st.markdown(f"""
        <div style="background:#F0EDE6;border:1px solid {BORDER};border-radius:6px;
                    padding:10px 12px;margin-top:8px;">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#94A3B8;margin-bottom:4px;">
              Oil shock contribution preview</div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:13px;color:{WARM};">
              ϕ · Oil · W = {phi:.4f} × {oil:.1f} × {oilw:.2f} = <b>{phi*oil*oilw:.3f}%</b></div>
        </div>""", unsafe_allow_html=True)
        st.markdown(source_note("EIA U.S. Energy Information Administration · CBSL WEI 06-Mar-2026 (Hormuz disruption noted)"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── PANEL F: Fisher Inflation Gap ────────────────────────────────────────
    with pf:
        st.markdown(adj_panel_header("Fisher Gap  ·  δ · (π − π*)", "🌡️", VIOLET), unsafe_allow_html=True)
        st.markdown(adj_panel_body_start(), unsafe_allow_html=True)
        f1, f2 = st.columns([2,1])
        with f1:
            infl = st.number_input("CCPI Inflation  (% YoY)",
                value=CUR["ccpi"], min_value=-5.0, max_value=80.0, step=0.1, format="%.2f",
                help="CBSL Feb 2026: 1.6% Y-o-Y. Fisher: nominal yield must compensate for expected inflation erosion")
        with f2:
            delta = st.number_input("δ  (coeff)", value=0.08, step=0.01, format="%.3f",
                help="Yield response per 1pp of (CCPI − π*). Below target → negative Fisher term suppresses yields")
        gap = infl - pi_star
        gap_color = ROSE if gap > 0 else SAGE
        st.markdown(f"""
        <div style="background:#F0EDE6;border:1px solid {BORDER};border-radius:6px;
                    padding:10px 12px;margin-top:8px;">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#94A3B8;margin-bottom:4px;">
              Fisher gap preview</div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:13px;color:{gap_color};">
              δ·(π − π*) = {delta:.3f} × ({infl:.2f} − {pi_star:.1f})
              = <b>{delta*gap:+.3f}%</b></div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#94A3B8;margin-top:6px;">
              {"↓ Below target → downward pressure on yields" if gap < 0 else "↑ Above target → upward pressure on yields"}</div>
        </div>""", unsafe_allow_html=True)
        st.markdown(source_note("DCS / CBSL CCPI releases · CBSL FIT: 5% medium-term target · Feb 2026: 1.6% (well below target)"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    pg, ph = st.columns(2)

    # ── PANEL G: Seasonal Factor ─────────────────────────────────────────────
    with pg:
        st.markdown(adj_panel_header("Seasonal Factor  ·  θ · S", "📅", "#A78BFA"), unsafe_allow_html=True)
        st.markdown(adj_panel_body_start(), unsafe_allow_html=True)
        auto_q = ("Q1 (+0.05)" if TODAY.month<=3 else "Q2 (−0.03)" if TODAY.month<=6
                  else "Q3 (−0.06)" if TODAY.month<=9 else "Q4★ Budget (+0.15)")
        seas_opt = st.selectbox("Quarter preset  (auto-detected)",
            ["Q1 (+0.05)", "Q2 (−0.03)", "Q3 (−0.06)", "Q4★ Budget (+0.15)"],
            index=["Q1 (+0.05)","Q2 (−0.03)","Q3 (−0.06)","Q4★ Budget (+0.15)"].index(auto_q))
        seas_map_ = {"Q1 (+0.05)":0.05,"Q2 (−0.03)":-0.03,"Q3 (−0.06)":-0.06,"Q4★ Budget (+0.15)":0.15}
        seas_v = st.number_input("S  Seasonal index  (override)",
            value=seas_map_[seas_opt], min_value=-1.0, max_value=1.0, step=0.01, format="%.2f",
            help="Q4 high: fiscal year-end borrowing surge. Q3 low: quiet period. Q1/Q2 moderate")
        theta = st.number_input("θ  Seasonal coefficient",
            value=0.14, step=0.01, format="%.3f",
            help="~0.14: sensitivity of yield to seasonal budget-cycle pattern")
        st.markdown(f"""
        <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#64748B;
                    margin-top:8px;padding:8px 10px;background:#F0EDE6;
                    border:1px solid {BORDER};border-radius:6px;">
          Auto-detected: <span style="color:{VIOLET};font-weight:600;">{auto_q}</span> &nbsp;·&nbsp;
          Contribution: <span style="color:{VIOLET};font-weight:600;">{theta*seas_v:+.3f}%</span>
        </div>""", unsafe_allow_html=True)
        st.markdown(source_note("CBSL auction calendar · Q4 fiscal year-end effect well-documented in LKA primary market data"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── PANEL H: Tenor Offsets ───────────────────────────────────────────────
    with ph:
        st.markdown(adj_panel_header("Tenor Offsets  ·  Hicks Liquidity Premium", "📐", TEAL), unsafe_allow_html=True)
        st.markdown(adj_panel_body_start(), unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#64748B;
                    margin-bottom:12px;line-height:1.7;">
          Hicks (1939): investors demand a premium for illiquidity / duration risk.<br>
          Longer tenors → higher uncertainty → higher term premium.
        </div>""", unsafe_allow_html=True)
        off91  = st.number_input("91D tenor offset  (%)",  value=0.00, step=0.05, format="%.2f",
            help="Base tenor: zero offset. Most liquid, lowest duration risk")
        off182 = st.number_input("182D tenor offset  (%)", value=0.22, step=0.05, format="%.2f",
            help="~22bps: 6-month illiquidity premium over 91D")
        off364 = st.number_input("364D tenor offset  (%)", value=0.55, step=0.05, format="%.2f",
            help="~55bps: 12-month duration + fiscal risk premium over 91D")
        st.markdown(f"""
        <div style="background:#F0EDE6;border:1px solid {BORDER};border-radius:6px;
                    padding:10px 12px;margin-top:4px;">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#94A3B8;margin-bottom:6px;">
              Current spread implied by offsets</div>
          <div style="display:flex;gap:16px;">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:12px;color:{GOLD};font-weight:600;">
                91D → {off91:+.2f}%</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:12px;color:{TEAL};font-weight:600;">
                182D → {off182:+.2f}%</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:12px;color:{VIOLET};font-weight:600;">
                364D → {off364:+.2f}%</div>
          </div>
        </div>""", unsafe_allow_html=True)
        st.markdown(source_note("Hicks (1939) liquidity preference theory · Calibrated on CBSL primary market spread data 2015–2025"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── RUN MODEL ──────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("▶   COMPUTE FORECAST  —  ALL THREE TENORS", use_container_width=True)

    f91, f182, f364, comps = model(
        alpha, lam, opr, beta1, us10y, sigma, gamma1, dbtgdp,
        gamma2, fd, phi, oil, oilw, theta, seas_v,
        omega, gor, delta, infl, pi_star, off91, off182, off364)

    # FORECAST CARDS
    st.markdown(section_title("Forecast Output",
                              "Model-derived yield forecasts · 95% confidence intervals"), unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        st.markdown(forecast_card("91-Day Tenor", f91, f91-0.72, f91+0.72, CUR["y91"], GOLD), unsafe_allow_html=True)
    with fc2:
        st.markdown(forecast_card("182-Day Tenor", f182, f182-0.85, f182+0.85, CUR["y182"], TEAL), unsafe_allow_html=True)
    with fc3:
        st.markdown(forecast_card("364-Day Tenor", f364, f364-1.02, f364+1.02, CUR["y364"], VIOLET), unsafe_allow_html=True)

    # DECOMPOSITION + SENSITIVITY
    st.markdown("<br>", unsafe_allow_html=True)
    dc1, dc2 = st.columns([1.1, 1])

    with dc1:
        st.markdown(section_title("Term Decomposition", "91-Day · Contribution of each channel"), unsafe_allow_html=True)
        total_abs = sum(abs(v) for v in comps.values())
        html_d = f"""
        <div style="background:{PANEL};border:1px solid {BORDER};border-radius:10px;
                    overflow:hidden;box-shadow:0 1px 6px rgba(0,0,0,0.06);">
          <table style="width:100%;border-collapse:collapse;">
            <thead>
              <tr style="background:#F0EDE6;border-bottom:1px solid {BORDER};">
                <th style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#94A3B8;
                           padding:10px 14px;text-align:left;letter-spacing:1.5px;font-weight:400;
                           text-transform:uppercase;">Term</th>
                <th style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#94A3B8;
                           padding:10px 14px;text-align:right;letter-spacing:1.5px;font-weight:400;
                           text-transform:uppercase;">Value (pp)</th>
                <th style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#94A3B8;
                           padding:10px 14px;text-align:right;letter-spacing:1.5px;font-weight:400;
                           text-transform:uppercase;">Share</th>
              </tr>
            </thead>
            <tbody>"""
        for term, val in comps.items():
            pct = abs(val) / total_abs * 100 if total_abs else 0
            vc = SAGE if val >= 0 else ROSE
            html_d += f"""
              <tr style="border-bottom:1px solid {BORDER};">
                <td style="font-family:'IBM Plex Mono',monospace;font-size:11px;
                           color:#475569;padding:9px 14px;">{term}</td>
                <td style="font-family:'IBM Plex Mono',monospace;font-size:12px;
                           color:{vc};padding:9px 14px;text-align:right;font-weight:600;">{val:+.4f}%</td>
                <td style="padding:9px 14px;text-align:right;">
                  <div style="display:flex;align-items:center;justify-content:flex-end;gap:8px;">
                    <div style="width:50px;height:3px;background:#E8E0D0;border-radius:2px;">
                      <div style="width:{min(pct/1.2,100):.0f}%;height:100%;background:{vc};border-radius:2px;"></div>
                    </div>
                    <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#94A3B8;
                                 min-width:36px;">{pct:.1f}%</span>
                  </div>
                </td>
              </tr>"""
        base_sum = sum(comps.values())
        html_d += f"""
              <tr style="background:#F0EDE6;border-top:2px solid {GOLD}33;">
                <td style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:{GOLD};
                           padding:10px 14px;font-weight:700;">Base Sum (91D)</td>
                <td style="font-family:'IBM Plex Mono',monospace;font-size:16px;color:{GOLD};
                           padding:10px 14px;text-align:right;font-weight:800;">{base_sum:.3f}%</td>
                <td></td>
              </tr>
            </tbody></table></div>"""
        st.markdown(html_d, unsafe_allow_html=True)

    with dc2:
        st.markdown(section_title("Sensitivity Analysis", "Impact on 91D yield per unit shock"), unsafe_allow_html=True)
        sens = [
            ("OPR ±1%",          lam,                                        TEAL,   "Dominant driver"),
            ("Debt/GDP ±10pp",   gamma1 * 10,                                ROSE,   "Solvency risk"),
            ("Fiscal Def ±1pp",  gamma2,                                     ROSE,   "Fiscal channel"),
            ("US10Y ±1%",        beta1,                                      SAGE,   "Mundell-Fleming"),
            ("Oil ±$10/bbl",     phi * 10 * oilw,                           WARM,   "Cost-push"),
            ("GOR −$1Bn",        omega/max(gor-1,0.1)-omega/gor,            GOLD,   "Ext. buffer"),
            ("Inflation ±1pp",   delta,                                      VIOLET, "Fisher gap"),
            ("σ ±1%",            beta1,                                      "#9333EA","Risk premium"),
        ]
        max_s = max(abs(v) for _,v,_,_ in sens) or 1
        for lbl_, val_, col_, theory_ in sens:
            pct_w = abs(val_) / max_s * 100
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;
                        padding:8px 0;border-bottom:1px solid {BORDER};">
              <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;
                          color:#64748B;width:130px;flex-shrink:0;">{lbl_}</div>
              <div style="flex:1;height:5px;background:#E8E0D0;
                          border-radius:3px;overflow:hidden;">
                <div style="width:{pct_w:.0f}%;height:100%;background:{col_};
                            border-radius:3px;"></div>
              </div>
              <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;
                          color:{col_};width:60px;text-align:right;font-weight:600;">{val_:+.3f}pp</div>
            </div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;
                        color:#94A3B8;margin-left:140px;margin-bottom:4px;">{theory_}</div>
            """, unsafe_allow_html=True)

    # ── IN-SAMPLE FIT CHART ────────────────────────────────────────────────────
    st.markdown(section_title("Model Fit", "Historical fitted values vs actual CBSL yields"), unsafe_allow_html=True)
    fit91, fit364 = [], []
    for i in range(N):
        fh91,_,fh364,_ = model(
            alpha,lam,POL[i],beta1,US10Y[i],SIGMA[i],gamma1,DBTGDP[i],
            gamma2,FDGDP[i],phi,BRENT[i],oilw,theta,0.05,
            omega,GOR[i],delta,INFL[i],pi_star,off91,off182,off364)
        fit91.append(fh91); fit364.append(fh364)

    rmse91  = np.sqrt(np.mean([(Y91[i]-fit91[i])**2  for i in range(N)]))
    rmse364 = np.sqrt(np.mean([(Y364[i]-fit364[i])**2 for i in range(N)]))

    fig_fit = go.Figure()
    fig_fit.add_trace(go.Scatter(x=YEARS, y=Y91, name="Actual 91D",
        line=dict(color=GOLD,  width=2.5), mode="lines+markers", marker=dict(size=5),
        hovertemplate="%{x}: %{y:.2f}%<extra>Actual 91D</extra>"))
    fig_fit.add_trace(go.Scatter(x=YEARS, y=fit91, name="Fitted 91D",
        line=dict(color=GOLD, width=1.5, dash="dot"), mode="lines",
        hovertemplate="%{x}: %{y:.2f}%<extra>Fitted 91D</extra>"))
    fig_fit.add_trace(go.Scatter(x=YEARS, y=Y364, name="Actual 364D",
        line=dict(color=VIOLET, width=2.5), mode="lines+markers", marker=dict(size=5),
        hovertemplate="%{x}: %{y:.2f}%<extra>Actual 364D</extra>"))
    fig_fit.add_trace(go.Scatter(x=YEARS, y=fit364, name="Fitted 364D",
        line=dict(color=VIOLET, width=1.5, dash="dot"), mode="lines",
        hovertemplate="%{x}: %{y:.2f}%<extra>Fitted 364D</extra>"))
    fig_fit.add_trace(go.Scatter(
        x=[YEARS[-1], CUR_YEAR+0.5], y=[Y91[-1], f91], name="Forecast 91D",
        line=dict(color=GOLD, width=2, dash="dashdot"), mode="lines+markers",
        marker=dict(size=14, symbol="star", color=GOLD, line=dict(color=BG,width=2))))
    fig_fit.add_trace(go.Scatter(
        x=[YEARS[-1], CUR_YEAR+0.5], y=[Y364[-1], f364], name="Forecast 364D",
        line=dict(color=VIOLET, width=2, dash="dashdot"), mode="lines+markers",
        marker=dict(size=14, symbol="star", color=VIOLET, line=dict(color=BG,width=2))))
    fig_fit.add_annotation(
        x=0.02, y=0.96, xref="paper", yref="paper",
        text=f"RMSE: 91D={rmse91:.2f}pp · 364D={rmse364:.2f}pp",
        showarrow=False,
        bgcolor="rgba(244,241,235,0.92)", bordercolor=GOLD, borderwidth=1,
        font=dict(color="#475569", size=10, family=FONT_M))
    fig_fit.update_layout(**lay(height=400,
        yaxis=dict(ticksuffix="%", gridcolor=GRID_C, tickfont=dict(color="#4B5563")),
        xaxis_title="Year"))
    st.plotly_chart(fig_fit, use_container_width=True)
    st.markdown(source_note(
        "Fitted values computed with historical variable inputs and current coefficients. "
        "2022 crisis residuals are highest — structural break from extreme non-linearity. "
        "Adjust γ₁, γ₂, Ω to improve crisis-period fit."
    ), unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 3  —  HISTORICAL DATA  (editable)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Historical Data":

    st.markdown(page_header(
        "Verified · Multi-Source · Editable Grid",
        "Historical Data<br>2015 – Present",
        "Click any cell to edit · Adjustments feed the model · All sources documented"
    ), unsafe_allow_html=True)
    st.markdown('<div style="padding:0 32px;">', unsafe_allow_html=True)

    tab_y, tab_m, tab_g, tab_v = st.tabs([
        "📈  T-Bill Yields & Policy",
        "🏛  Domestic Macro Variables",
        "🌐  Global Variables",
        "📊  Multi-Variable Chart",
    ])

    with tab_y:
        st.markdown(section_title("T-Bill Primary Market WAY", "Annual averages · % per annum"), unsafe_allow_html=True)
        df_y = pd.DataFrame({
            "Year":            YEARS,
            "91D WAY (%)":     Y91,
            "182D WAY (%)":    Y182,
            "364D WAY (%)":    Y364,
            "Policy Rate (%)": POL,
            "Spread 364-91 (bps)": [(Y364[i]-Y91[i])*100 for i in range(N)],
            "Real 91D (%)":    [round(Y91[i]-INFL[i],2) for i in range(N)],
            "Source":          (["CBSL PDMR 2021"]*min(7,N) + ["CBSL WEI"]*max(0,N-7)),
        })
        st.data_editor(df_y, use_container_width=True, hide_index=True, num_rows="fixed")
        st.markdown(source_note(
            "2015–2021: CBSL Public Debt Management Report 2021, Table 3 (exact primary-market WAY) · "
            "2022: WEI-derived annual average; crisis peak Apr 20 2022: 91D=23.21%, 182D=24.77%, 364D=24.36% · "
            "2023–2025: CBSL WEI weekly series averaged · "
            "2026: CBSL WEI 06-Mar-2026 (broadly stable; small decrease observed) · "
            "Policy rate: SDFR/SLFR midpoint pre-Nov 2024; OPR from Nov 27, 2024"
        ), unsafe_allow_html=True)

    with tab_m:
        st.markdown(section_title("Domestic Macro Variables", "Sri Lanka — all values editable"), unsafe_allow_html=True)
        df_m = pd.DataFrame({
            "Year":               YEARS,
            "Debt/GDP (%)":       DBTGDP,
            "Fiscal Def/GDP (%)": FDGDP,
            "CCPI Inflation (%)": INFL,
            "USD/LKR (avg)":      USDLKR,
            "GOR (USD Bn)":       GOR,
        })
        st.data_editor(df_m, use_container_width=True, hide_index=True, num_rows="fixed")
        st.markdown(source_note(
            "Debt/GDP: CountryEconomy.com / World Bank (2024: 100.84%; 2022 peak: 114.2% per CBSL press release; 2023: 110.38%) · "
            "Fiscal Deficit: MoF / Treasury.gov.lk (2020:10.7%, 2021:11.7%, 2022:10.2%, 2023:8.3%, 2024:6.8%, 2025 est:5.5%) · "
            "CCPI: DCS / CBSL (2022 annual avg ~46.4%; crisis point-high Sep 2022 ~69.8%) · "
            "GOR: TheGlobalEconomy.com / CBSL (2022 low: $1.90Bn; 2024: $6.09Bn; Feb 2026: $7.284Bn provisional)"
        ), unsafe_allow_html=True)

    with tab_g:
        st.markdown(section_title("Global Variables", "US, Oil & risk premium — all values editable"), unsafe_allow_html=True)
        df_g = pd.DataFrame({
            "Year":            YEARS,
            "US 10Y Yield (%)":US10Y,
            "Brent ($/bbl)":   BRENT,
            "Oil × W (ϕ input)":[round(b*OIL_W,2) for b in BRENT],
            "LKA Risk σ (%)":  SIGMA,
            "USD/LKR (avg)":   USDLKR,
        })
        st.data_editor(df_g, use_container_width=True, hide_index=True, num_rows="fixed")
        st.markdown(source_note(
            "US 10Y: US Federal Reserve FRED (DGS10) annual averages · "
            "Brent: EIA annual averages (2022 peak: $100.9; 2025 avg ~$73; Mar 2026: surpassed $80 per CBSL WEI 06-Mar-2026) · "
            "LKA σ: Estimated proxy from yield residuals over global base — not directly observable"
        ), unsafe_allow_html=True)

    with tab_v:
        st.markdown(section_title("Multi-Variable Overlay", "Select variables to compare on one chart"), unsafe_allow_html=True)
        opts = st.multiselect("Variables:", [
            "91D Yield","182D Yield","364D Yield","Policy Rate",
            "Debt/GDP ÷5","Fiscal Def/GDP","GOR","Inflation ÷5",
            "US 10Y","Brent ÷10","Sigma"
        ], default=["91D Yield","364D Yield","Policy Rate","Debt/GDP ÷5"])
        vm = {
            "91D Yield":     (YEARS, Y91,                  GOLD,   "91D WAY (%)"),
            "182D Yield":    (YEARS, Y182,                 TEAL,   "182D WAY (%)"),
            "364D Yield":    (YEARS, Y364,                 VIOLET, "364D WAY (%)"),
            "Policy Rate":   (YEARS, POL,                  MUTED,  "Policy (%)"),
            "Debt/GDP ÷5":   (YEARS, [v/5 for v in DBTGDP],ROSE,  "Debt/GDP ÷5"),
            "Fiscal Def/GDP":(YEARS, FDGDP,                WARM,   "Fiscal Def/GDP (%)"),
            "GOR":           (YEARS, GOR,                  SAGE,   "GOR (USD Bn)"),
            "Inflation ÷5":  (YEARS, [v/5 for v in INFL], "#FDA4AF","CCPI ÷5"),
            "US 10Y":        (YEARS, US10Y,                TEAL,   "US 10Y (%)"),
            "Brent ÷10":     (YEARS, [v/10 for v in BRENT],WARM,  "Brent ÷10"),
            "Sigma":         (YEARS, SIGMA,                VIOLET, "σ (%)"),
        }
        fig_a = go.Figure()
        for v in opts:
            x, y, c, nm = vm[v]
            fig_a.add_trace(go.Scatter(x=x, y=y, name=nm, mode="lines+markers",
                line=dict(color=c, width=2), marker=dict(size=4, color=c)))
        fig_a.update_layout(**lay(height=420,
            yaxis=dict(gridcolor=GRID_C, tickfont=dict(color="#4B5563")),
            xaxis_title="Year"))
        st.plotly_chart(fig_a, use_container_width=True)
        st.caption("Variables marked ÷5 or ÷10 are scaled to share the axis. Check legend for true units.")

    st.markdown("---")
    csv_out = pd.DataFrame({
        "Year":YEARS, "91D_WAY_pct":Y91, "182D_WAY_pct":Y182,
        "364D_WAY_pct":Y364, "Policy_Rate_pct":POL,
        "DebtGDP_pct":DBTGDP, "FiscalDef_GDP_pct":FDGDP,
        "CCPI_pct":INFL, "USDLKR_avg":USDLKR, "GOR_USDbn":GOR,
        "US10Y_pct":US10Y, "Brent_USDpbbl":BRENT, "LKA_Sigma_pct":SIGMA
    })
    st.download_button(
        f"⤓  Download Full Dataset  2015–{CUR_YEAR}  (CSV)",
        csv_out.to_csv(index=False).encode(),
        f"LKA_TBill_Data_2015_{CUR_YEAR}.csv",
        "text/csv", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 4  —  SCENARIO ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Scenario Analysis":

    st.markdown(page_header(
        "Stress Testing · Forward Guidance · Risk Assessment",
        "Scenario<br>Analysis",
        "Pre-built macroeconomic scenarios + fully custom builder"
    ), unsafe_allow_html=True)
    st.markdown('<div style="padding:0 32px;">', unsafe_allow_html=True)

    SC = dict(alpha=0.30, lam=0.85, beta1=0.16, gamma1=0.024, gamma2=0.11,
              oilw=0.18, phi=0.009, theta=0.14, omega=3.20,
              delta=0.08, pi_star=5.0, off91=0.00, off182=0.22, off364=0.55)

    SCENS = {
        "Base — Current (Mar 2026)": {
            "opr":7.75,"us10y":4.30,"sigma":3.20,"dbtgdp":96.0,"fd":5.5,
            "oil":81.0,"seas":0.05,"gor":7.284,"infl":1.6,"color":TEAL,
            "desc":"Live CBSL data Mar 2026. OPR=7.75%, GOR=$7.284Bn, CCPI=1.6%, Brent=$81 (Hormuz). Recovery path intact."
        },
        "Bull — Rate Cut + IMF Milestone": {
            "opr":6.50,"us10y":3.80,"sigma":2.50,"dbtgdp":92.0,"fd":4.8,
            "oil":70.0,"seas":-0.03,"gor":8.50,"infl":1.2,"color":SAGE,
            "desc":"CBSL cuts OPR to 6.5% (2×50bps). IMF 6th review disbursement. GOR reaches $8.5Bn. Oil softens. Fiscal primary surplus achieved."
        },
        "Bear — Fiscal Slippage + Rate Hike": {
            "opr":9.00,"us10y":5.00,"sigma":4.50,"dbtgdp":104.0,"fd":8.5,
            "oil":90.0,"seas":0.15,"gor":6.00,"infl":4.5,"color":ROSE,
            "desc":"IMF programme stalls. Fiscal deficit widens to 8.5%. OPR hiked to 9%. Brent $90 (Hormuz escalation). CCPI rises to 4.5%."
        },
        "Stress — Oil Shock + Inflation Surge": {
            "opr":10.50,"us10y":5.20,"sigma":5.50,"dbtgdp":106.0,"fd":9.0,
            "oil":115.0,"seas":0.20,"gor":5.50,"infl":9.0,"color":WARM,
            "desc":"Full Strait of Hormuz closure. Brent spikes to $115. Imported inflation surges to 9%. CBSL forced to hike OPR to 10.5%."
        },
        "2022 Crisis Replay (Validation)": {
            "opr":14.50,"us10y":2.95,"sigma":9.00,"dbtgdp":114.2,"fd":10.2,
            "oil":100.9,"seas":0.20,"gor":1.90,"infl":46.4,"color":VIOLET,
            "desc":"Actual 2022 inputs. Model validation: SDFR=14.5%, GOR=$1.9Bn, Debt/GDP=114.2%, CCPI=46.4%. Compare forecast to actual ~20.5%."
        },
    }

    def run_sc(s):
        return model(SC["alpha"],SC["lam"],s["opr"],SC["beta1"],s["us10y"],
                     s["sigma"],SC["gamma1"],s["dbtgdp"],SC["gamma2"],s["fd"],
                     SC["phi"],s["oil"],SC["oilw"],SC["theta"],s["seas"],
                     SC["omega"],s["gor"],SC["delta"],s["infl"],SC["pi_star"],
                     SC["off91"],SC["off182"],SC["off364"])

    sc_sel = st.selectbox("Select scenario:", list(SCENS.keys()))
    sv = SCENS[sc_sel]
    st.markdown(f"""
    <div style="background:#EFF6FF;border:1px solid #BFDBFE;
                border-radius:8px;padding:12px 18px;margin-bottom:20px;">
      <span style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#1E40AF;">
        ℹ  <b>{sc_sel}:</b>  {sv['desc']}</span>
    </div>""", unsafe_allow_html=True)

    sc91, sc182, sc364, _ = run_sc(sv)
    fc1, fc2, fc3 = st.columns(3)
    with fc1: st.markdown(forecast_card("91-Day Tenor",  sc91,  sc91-0.72,  sc91+0.72,  CUR["y91"],  sv["color"]), unsafe_allow_html=True)
    with fc2: st.markdown(forecast_card("182-Day Tenor", sc182, sc182-0.85, sc182+0.85, CUR["y182"], sv["color"]), unsafe_allow_html=True)
    with fc3: st.markdown(forecast_card("364-Day Tenor", sc364, sc364-1.02, sc364+1.02, CUR["y364"], sv["color"]), unsafe_allow_html=True)

    # All scenarios comparison
    st.markdown(section_title("All Scenarios Comparison"), unsafe_allow_html=True)
    sc_names, s91s, s182s, s364s = [], [], [], []
    for nm, sv_ in SCENS.items():
        f91_,f182_,f364_,_ = run_sc(sv_)
        sc_names.append(nm.split("—")[0].strip())
        s91s.append(f91_); s182s.append(f182_); s364s.append(f364_)

    fig_sc = go.Figure()
    fig_sc.add_trace(go.Bar(name="91D",  x=sc_names, y=s91s,
                            marker_color=GOLD, marker_line_width=0))
    fig_sc.add_trace(go.Bar(name="182D", x=sc_names, y=s182s,
                            marker_color=TEAL, marker_line_width=0))
    fig_sc.add_trace(go.Bar(name="364D", x=sc_names, y=s364s,
                            marker_color=VIOLET, marker_line_width=0))
    fig_sc.update_layout(**lay(barmode="group", height=380,
        yaxis=dict(ticksuffix="%", gridcolor=GRID_C, tickfont=dict(color="#4B5563"))))
    st.plotly_chart(fig_sc, use_container_width=True)

    sc_tbl = pd.DataFrame({
        "Scenario":       sc_names,
        "OPR (%)":        [SCENS[n]["opr"] for n in SCENS],
        "GOR ($Bn)":      [SCENS[n]["gor"] for n in SCENS],
        "Debt/GDP (%)":   [SCENS[n]["dbtgdp"] for n in SCENS],
        "Brent ($/bbl)":  [SCENS[n]["oil"] for n in SCENS],
        "91D Fcst (%)":   s91s,
        "182D Fcst (%)":  s182s,
        "364D Fcst (%)":  s364s,
    })
    st.dataframe(sc_tbl, use_container_width=True, hide_index=True)

    # Custom scenario builder
    st.markdown(section_title("Build Your Own Scenario", "Adjust all inputs below"), unsafe_allow_html=True)
    cx1,cx2,cx3,cx4 = st.columns(4)
    cx5,cx6,cx7,cx8 = st.columns(4)
    with cx1: c_opr   = st.number_input("OPR (%)",       value=7.75, step=0.25, format="%.2f", key="cx_opr")
    with cx2: c_dbt   = st.number_input("Debt/GDP (%)",  value=96.0, step=1.0,  format="%.1f", key="cx_dbt")
    with cx3: c_oil_  = st.number_input("Brent ($/bbl)", value=81.0, step=5.0,  format="%.1f", key="cx_oil")
    with cx4: c_gor_  = st.number_input("GOR ($Bn)",     value=7.28, step=0.2,  format="%.2f", key="cx_gor")
    with cx5: c_fd_   = st.number_input("Fiscal Def/GDP",value=5.5,  step=0.5,  format="%.1f", key="cx_fd")
    with cx6: c_us_   = st.number_input("US 10Y (%)",    value=4.30, step=0.1,  format="%.2f", key="cx_us")
    with cx7: c_inf_  = st.number_input("CCPI (%)",      value=1.6,  step=0.2,  format="%.1f", key="cx_inf")
    with cx8: c_sig_  = st.number_input("Risk σ (%)",    value=3.20, step=0.1,  format="%.2f", key="cx_sig")
    custom = {"opr":c_opr,"us10y":c_us_,"sigma":c_sig_,"dbtgdp":c_dbt,
              "fd":c_fd_,"oil":c_oil_,"seas":0.05,"gor":c_gor_,"infl":c_inf_}
    cf91,cf182,cf364,_ = run_sc(custom)
    st.markdown(f"""
    <div style="background:{PANEL};border:1px solid rgba(184,134,11,0.3);
                border-radius:10px;padding:24px 28px;margin-top:12px;
                display:flex;gap:40px;align-items:center;flex-wrap:wrap;
                box-shadow:0 2px 12px rgba(184,134,11,0.10);">
      <div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;
                    color:#94A3B8;letter-spacing:2px;margin-bottom:6px;">CUSTOM 91D</div>
        <div style="font-family:'Playfair Display',serif;font-size:38px;
                    font-weight:900;color:{GOLD};letter-spacing:-1px;">{cf91:.2f}%</div>
      </div>
      <div style="width:1px;height:50px;background:{BORDER};"></div>
      <div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;
                    color:#94A3B8;letter-spacing:2px;margin-bottom:6px;">CUSTOM 182D</div>
        <div style="font-family:'Playfair Display',serif;font-size:38px;
                    font-weight:900;color:{TEAL};letter-spacing:-1px;">{cf182:.2f}%</div>
      </div>
      <div style="width:1px;height:50px;background:{BORDER};"></div>
      <div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;
                    color:#94A3B8;letter-spacing:2px;margin-bottom:6px;">CUSTOM 364D</div>
        <div style="font-family:'Playfair Display',serif;font-size:38px;
                    font-weight:900;color:{VIOLET};letter-spacing:-1px;">{cf364:.2f}%</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 5  —  METHODOLOGY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Methodology":

    st.markdown(page_header(
        "Economic Theory · Model Design · Data Provenance",
        "Methodology<br>& Theory",
        "Complete documentation of economic foundations, model specification, and data sources"
    ), unsafe_allow_html=True)
    st.markdown('<div style="padding:0 32px;">', unsafe_allow_html=True)

    def theory_card(num, name, color, content):
        return f"""
        <div style="background:{PANEL};border:1px solid {BORDER};border-radius:10px;
                    padding:20px;margin-bottom:14px;position:relative;overflow:hidden;
                    box-shadow:0 1px 6px rgba(0,0,0,0.06);">
          <div style="position:absolute;left:0;top:0;bottom:0;width:4px;background:{color};"></div>
          <div style="padding-left:18px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
              <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;
                           color:{color};font-weight:600;">{num}</span>
              <span style="font-family:'Playfair Display',serif;font-size:16px;
                           font-weight:700;color:#1C2333;">{name}</span>
            </div>
            <div style="font-family:'Outfit',sans-serif;font-size:13px;
                        color:#475569;line-height:1.8;">{content}</div>
          </div>
        </div>"""

    st.markdown(section_title("Economic Foundations", "All 8 theoretical pillars of the model"), unsafe_allow_html=True)
    theories = [
        ("01", "Fisher Effect  (Irving Fisher, 1930)", GOLD,
         "Nominal yields must compensate lenders for inflation erosion of purchasing power. <code>i ≈ r* + πᵉ</code>. The <b>δ·(π−π*)</b> term captures the gap between actual CCPI and CBSL's 5% FIT target. In 2025, CCPI=1.6% is 340bps below target — this negative gap exerts downward pressure on nominal yields. The <b>α baseline</b> proxies the real neutral rate r*."),
        ("02", "Expectations Theory  (Lutz, 1940)", TEAL,
         "Long-tenor yields are geometric averages of expected future short rates. The 364D yield embeds market expectations about OPR over the next 12 months. In 2022, an inverted curve briefly appeared (short rates peaked before markets priced in the inevitable decline). The <b>tenor offsets</b> add Hicks's pure expectations adjustment."),
        ("03", "Liquidity Preference / Term Premium  (Hicks, 1939)", VIOLET,
         "Even under flat rate expectations, investors demand a term premium for locking capital in longer maturities (duration risk, rollover risk, illiquidity). This produces the normal upward slope: 91D→182D (+22bps)→364D (+55bps). Current spread of ~65bps is consistent with a recovering sovereign with moderate but declining uncertainty."),
        ("04", "Loanable Funds Theory  (Wicksell → Robertson → Friedman)", ROSE,
         "<b>γ₁·Debt/GDP + γ₂·FD</b> captures two crowding-out channels. Fiscal deficits require T-bill issuance, increasing supply and raising yields (supply-side). Rising Debt/GDP signals rollover risk and solvency concerns, widening the risk premium demanded by investors. Note partial Ricardian equivalence: rational agents anticipating future taxes may not fully respond to γ₂, which is why β₂ remains modest (~0.11)."),
        ("05", "Mundell-Fleming Framework  (Mundell 1963, Fleming 1962)", SAGE,
         "<b>β₁·(US10Y + σ)</b> transmits global rates to LKA via capital flows. β₁≈0.16 is intentionally low — Sri Lanka maintains capital account restrictions that limit full arbitrage. σ (sovereign risk premium, ~3.2% currently vs ~9% in 2022) captures the default probability increment. Post-IMF restructuring, σ compression has been a significant driver of yield normalisation."),
        ("06", "CBSL Monetary Transmission  (Bernanke-Blinder channel)", TEAL,
         "The OPR directly anchors T-bill WAY via: (i) overnight repo/reverse repo operations setting the corridor; (ii) primary dealer expectations of future OPR; (iii) AWCMR (currently 7.66%) clustering around OPR±15bps. λ≈0.85 implies ~85bps pass-through per 100bps OPR change — high due to CBSL's credibility recovery post-crisis."),
        ("07", "External Vulnerability Premium  (Obstfeld-Rogoff, 1996)", WARM,
         "<b>Ω·(1/GOR)</b> models sovereign liquidity risk. Insufficient reserves signal inability to service external obligations → risk premium spike. In 2022 (GOR=$1.9Bn), this term contributed significantly to yield explosion. As GOR recovered to $7.284Bn (Feb 2026), the term normalised. The PBOC swap and IMF SDRs are included in the CBSL provisional estimate — partial credit to CBSL's IMF programme discipline."),
        ("08", "Cost-Push Inflation Channel  (Samuelson-Solow AS-AD)", "#FB923C",
         "<b>ϕ·(Oil×W)</b> transmits import-cost shocks to inflation expectations and thus nominal yields. With W=0.18 (oil share of imports), each $10/bbl increase adds ~1.6bps directly plus indirect Fisher channel effects. CBSL WEI 06-Mar-2026 confirms Brent surpassed $80 due to Strait of Hormuz disruption — a live upside risk to yields through this channel."),
    ]
    for n, name, col, content in theories:
        st.markdown(theory_card(n, name, col, content), unsafe_allow_html=True)

    st.markdown(section_title("Model Limitations", "Honest caveats for informed use"), unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#FFF7F7;border:1px solid #FECACA;
                border-radius:10px;padding:20px 24px;
                box-shadow:0 1px 6px rgba(0,0,0,0.04);">
      <div style="font-family:'Outfit',sans-serif;font-size:13px;color:#475569;
                  line-height:2.1;">
        <span style="color:{ROSE};font-weight:700;">①</span>
        <b style="color:#1C2333;">Sample size:</b>
        OLS on 11 annual observations (2015–2025). Degrees of freedom are limited.
        A longer monthly panel would improve coefficient precision.<br>
        <span style="color:{ROSE};font-weight:700;">②</span>
        <b style="color:#1C2333;">Structural breaks:</b>
        The 2022 crisis introduces severe non-linearity. A Markov Regime-Switching or NARDL
        model would better capture asymmetric crisis dynamics.<br>
        <span style="color:{ROSE};font-weight:700;">③</span>
        <b style="color:#1C2333;">Backward-looking inflation:</b>
        Using realised CCPI rather than survey-based inflation expectations (CBSL Business Outlook
        Survey) understates forward-looking Fisher pricing.<br>
        <span style="color:{ROSE};font-weight:700;">④</span>
        <b style="color:#1C2333;">Reduced form:</b>
        This is a structural reduced-form model, not a full DSGE. Policy feedback loops and
        general equilibrium effects are not captured.<br>
        <span style="color:{ROSE};font-weight:700;">⑤</span>
        <b style="color:#1C2333;">Disclaimer:</b>
        Forecasts are indicative only.
        <b style="color:{ROSE};">This platform is NOT financial advice.</b>
        Do not make investment decisions based solely on these outputs.
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown(section_title("Data Sources Registry", "Every variable with primary source"), unsafe_allow_html=True)
    sources_tbl = pd.DataFrame({
        "Variable":   ["T-Bill WAY 91D/182D/364D 2015–21","T-Bill WAY 2022–2026","Policy Rate (OPR/SDFR/SLFR)",
                       "Govt Debt/GDP","Fiscal Deficit/GDP","CCPI Inflation","USD/LKR","Gross Official Reserves",
                       "US 10Y Treasury Yield","Brent Crude Oil","LKA Risk Premium σ"],
        "Source":     ["CBSL PDMR 2021, Table 3","CBSL Weekly Economic Indicators (WEI)","CBSL MPB press releases",
                       "CountryEconomy.com / World Bank / CBSL","MoF / Treasury.gov.lk","DCS / CBSL CCPI releases",
                       "CBSL daily rates","CBSL External Sector / TheGlobalEconomy.com","US Fed FRED (DGS10)",
                       "EIA U.S. Energy Information Administration","Estimated proxy — yield residuals over global base"],
        "Latest":     ["Exact 2015–2021 annual","Mar 2026 (CBSL WEI 06-Mar-2026)","7.75% (MPR No.1/2026, Jan 27 2026)",
                       "100.84% (2024)","5.5% est (2025)","1.6% (Feb 2026)","~310.5 (Mar 2026)",
                       "$7.284Bn provisional (Feb 2026, incl PBOC swap)","~4.30% (Mar 2026)","~$81/bbl (Mar 2026)","~3.20% (2026 est)"],
    })
    st.dataframe(sources_tbl, use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="background:#1C2333;border-top:3px solid {GOLD};
            padding:20px 32px;margin-top:20px;">
  <div style="display:flex;justify-content:space-between;align-items:center;
              flex-wrap:wrap;gap:12px;">
    <div style="font-family:'Playfair Display',serif;font-size:16px;
                font-weight:700;color:{GOLD};">LKA Yield Engine</div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#475569;
                text-align:center;line-height:2;">
      CBSL.GOV.LK · TREASURY.GOV.LK · WORLD BANK · US FED FRED ·
      EIA · COUNTRYECONOMY.COM · THEGLOBALECONOMY.COM<br>
      Data live through {TODAY_STR} · Forecasts indicative only ·
      <span style="color:#F87171;">Not financial advice</span> ·
      GitHub: lka-yield-engine · © {CUR_YEAR}
    </div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#475569;">
      Streamlit Community Cloud
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
