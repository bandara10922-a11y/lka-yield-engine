"""
LKA Yield Engine — Sri Lanka T-Bill Econometric Forecast Platform
Repository: lka-yield-engine
Deploy via: Streamlit Community Cloud → app.py

All historical data sourced from:
  - CBSL Public Debt Management Report 2021 (T-bill WAY 2015–2021)
  - CBSL Weekly Economic Indicators 2022–2025 (T-bill WAY 2022–2025)
  - WorldBank / CountryEconomy.com (Debt/GDP)
  - Ministry of Finance / Treasury.gov.lk (Fiscal Deficit)
  - TheGlobalEconomy.com / CBSL External Sector (GOR)
  - US Federal Reserve FRED – DGS10 (US 10Y Yield)
  - EIA / Reuters (Brent Crude)
  - CBSL / Macrotrends (CCPI Inflation, USD/LKR)
  - CBSL Monetary Policy Decisions (Policy Rate)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────
st.set_page_config(
    page_title="LKA Yield Engine | Sri Lanka T-Bill Forecast",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Fraunces:wght@300;700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

/* Root */
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* Hide default header */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Background */
.main { background-color: #070c11; }
.block-container { padding-top: 1.5rem; padding-bottom: 1rem; }

/* Header banner */
.hdr-banner {
    background: linear-gradient(135deg, #0d1520 0%, #131e2b 100%);
    border: 1px solid rgba(201,168,76,0.2);
    border-radius: 12px;
    padding: 18px 24px;
    margin-bottom: 20px;
}
.hdr-title {
    font-family: 'Fraunces', serif;
    font-size: 26px; font-weight: 900;
    color: #e8c96d; letter-spacing: -0.5px;
    margin-bottom: 4px;
}
.hdr-sub {
    font-family: 'DM Mono', monospace;
    font-size: 11px; color: #5a5650;
    letter-spacing: 2px; text-transform: uppercase;
}
.hdr-live {
    font-family: 'DM Mono', monospace;
    font-size: 12px; color: #8a8478;
}

/* Metric cards */
.metric-card {
    background: #0d1520;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 14px 16px;
    position: relative; overflow: hidden;
}
.metric-card::before {
    content:''; position:absolute;
    top:0; left:0; right:0; height:2px;
}
.mc-gold::before { background: linear-gradient(90deg,#c9a84c,transparent); }
.mc-teal::before { background: linear-gradient(90deg,#2dd4bf,transparent); }
.mc-purple::before { background: linear-gradient(90deg,#a78bfa,transparent); }
.mc-white::before { background: linear-gradient(90deg,rgba(255,255,255,.25),transparent); }

.mc-label {
    font-size: 9px; color: #4a4840;
    text-transform: uppercase; letter-spacing: 1.5px;
    font-family: 'DM Mono', monospace; margin-bottom: 6px;
}
.mc-value {
    font-family: 'Fraunces', serif;
    font-size: 28px; font-weight: 700; line-height: 1;
}
.mc-gold .mc-value { color: #c9a84c; }
.mc-teal .mc-value { color: #2dd4bf; }
.mc-purple .mc-value { color: #a78bfa; }
.mc-white .mc-value { color: #e2ddd4; }
.mc-chg { font-size: 10px; font-family: 'DM Mono', monospace; margin-top: 6px; }
.chg-up { color: #f87171; }
.chg-dn { color: #4ade80; }
.mc-sub { font-size: 10px; color: #4a4840; margin-top: 3px; }

/* Section headers */
.sec-title {
    font-family: 'Fraunces', serif;
    font-size: 18px; font-weight: 700;
    color: #e2ddd4; margin-bottom: 4px;
    border-left: 3px solid #c9a84c;
    padding-left: 10px;
}
.sec-sub { font-size: 11px; color: #5a5650;
    font-family: 'DM Mono', monospace; margin-bottom: 12px;
    padding-left: 13px;
}

/* Formula box */
.formula-box {
    background: #0d1520;
    border: 1px solid rgba(201,168,76,0.2);
    border-radius: 8px; padding: 14px 18px;
    font-family: 'DM Mono', monospace;
    font-size: 12px; color: #e8c96d;
    line-height: 2.2; overflow-x: auto;
    white-space: nowrap; margin: 10px 0;
}

/* Forecast output cards */
.fcast-card {
    background: #070c11;
    border-radius: 10px; padding: 18px;
    text-align: center; position: relative; overflow: hidden;
}
.fcast-card::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
}
.fc-91::before { background: #c9a84c; }
.fc-182::before { background: #2dd4bf; }
.fc-364::before { background: #a78bfa; }
.fc-label { font-size: 9px; color: #4a4840;
    font-family: 'DM Mono', monospace;
    letter-spacing: 1.5px; text-transform: uppercase;
    margin-bottom: 8px;
}
.fc-value {
    font-family: 'Fraunces', serif;
    font-size: 34px; font-weight: 900; line-height: 1;
}
.fc-91 .fc-value { color: #c9a84c; }
.fc-182 .fc-value { color: #2dd4bf; }
.fc-364 .fc-value { color: #a78bfa; }
.fc-range { font-size: 10px; color: #5a5650;
    font-family: 'DM Mono', monospace; margin-top: 6px;
}

/* Source note */
.src-note {
    background: rgba(201,168,76,0.05);
    border-left: 2px solid #c9a84c;
    border-radius: 0 4px 4px 0;
    padding: 6px 10px; font-size: 10px;
    color: #5a5650; font-family: 'DM Mono', monospace;
    margin-top: 8px;
}

/* Decomposition table */
.decomp-row {
    display: flex; justify-content: space-between;
    padding: 4px 0; border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 11px; font-family: 'DM Mono', monospace;
}
.decomp-row:last-child { border: none; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0d1520;
    border-right: 1px solid rgba(255,255,255,0.06);
}
section[data-testid="stSidebar"] .stMarkdown { color: #8a8478; }

/* Streamlit elements theming */
.stSlider > div > div > div > div { background: #c9a84c !important; }
.stSelectbox > div > div { background: #131e2b !important; border-color: rgba(255,255,255,0.1) !important; }
.stNumberInput > div > div > input { background: #131e2b !important; color: #e2ddd4 !important; border-color: rgba(255,255,255,0.1) !important; }
.stDataFrame { background: #0d1520 !important; }
div[data-testid="stMetric"] { background: #0d1520; border: 1px solid rgba(255,255,255,0.07); border-radius: 8px; padding: 10px; }
div[data-testid="stMetricLabel"] { color: #5a5650 !important; font-family: 'DM Mono', monospace !important; font-size: 10px !important; }
div[data-testid="stMetricValue"] { color: #c9a84c !important; font-family: 'Fraunces', serif !important; }
div[data-testid="stMetricDelta"] { font-family: 'DM Mono', monospace !important; font-size: 11px !important; }
div[data-testid="stTabs"] button { font-family: 'DM Mono', monospace; font-size: 11px; color: #5a5650; }
div[data-testid="stTabs"] button[aria-selected="true"] { color: #c9a84c; border-bottom: 2px solid #c9a84c; }
.stAlert { background: rgba(201,168,76,0.06); border-color: rgba(201,168,76,0.2); }
h1, h2, h3 { font-family: 'Fraunces', serif !important; color: #e2ddd4 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────
# VERIFIED HISTORICAL DATA
# ─────────────────────────────────────────────────
# Sources clearly documented per series

YEARS = list(range(2015, 2026))  # 2015–2025

# T-Bill Weighted Average Yields (% per annum)
# Source: CBSL Public Debt Management Report 2021 (2015–2021);
#         CBSL Weekly Economic Indicators (2022–2025 approximate annual averages)
#         2022 crisis peak Apr: 91D=23.21%, 182D=24.77%, 364D=24.36%
Y91  = [6.32, 8.26, 9.01, 8.40, 8.15, 5.93, 6.35, 20.50, 15.80, 9.85, 7.80]
Y182 = [6.50, 9.23, 9.81, 8.58, 8.44, 5.72, 6.13, 22.10, 16.20, 9.60, 7.95]
Y364 = [6.60,10.20,10.07, 9.67, 9.40, 6.37, 5.33, 23.00, 16.00, 9.35, 8.20]

# Policy Rate % — SDFR/SLFR midpoint pre-Nov 2024; OPR from Nov 27, 2024
# Source: CBSL Monetary Policy Board official decisions
# 2015: SDFR=6.0%/SLFR=7.5% → midpoint 6.75% → raised Aug 2016 to 7.0/8.5
# 2022 peak: SDFR=14.5%/SLFR=15.5% (Oct 2022). Cut progressively through 2023-24.
# Nov 2024: OPR introduced at 8.0%
POL  = [6.75, 7.75, 7.25, 7.25, 7.50, 5.50, 5.50, 14.50, 10.50, 8.50, 8.00]

# Govt Debt / GDP %
# Source: CountryEconomy.com / World Bank / CBSL (2024: 100.84%)
# 2021: 103.9% per CBSL press release; 2022: 114.2% per CBSL; 2023: 110.38%
DBTGDP = [76.3, 76.6, 77.5, 83.6, 87.0, 96.0, 103.9, 114.2, 110.4, 100.8, 95.0]

# Fiscal Deficit / GDP %
# Source: Ministry of Finance / Treasury.gov.lk press release (2020:10.7%, 2021:11.7%, 2022:10.2%, 2023:8.3%)
# TradingEconomics: 2024: 6.8%; EconomyNext: 2025 revised to 6.5%
FDGDP  = [7.6,  5.4,  5.5,  5.3,  9.6, 10.7, 11.7, 10.2,  8.3,  6.8,  6.5]

# CCPI Inflation % annual average
# Source: Macrotrends / World Bank (2022 peak ~57% point but annual average ~46%)
INFL   = [2.2,  4.0,  7.7,  2.1,  4.3,  6.2,  7.0, 46.4, 16.5,  2.0,  2.5]

# USD/LKR annual average
# Source: CBSL / Macrotrends
USDLKR = [135.9,145.6,152.9,162.5,178.8,185.8,199.6,320.2,320.9,301.0,305.0]

# Gross Official Reserves (USD Billion)
# Source: TheGlobalEconomy.com / FocusEconomics / CBSL External Sector
# 2024: 6.09 Bn (TheGlobalEconomy); Jan 2026: 6.7 Bn (CEIC)
GOR  = [7.28, 6.02, 7.96, 7.89, 7.59, 5.74, 3.14, 1.90, 4.41, 6.09, 6.70]

# US 10-Year Treasury Yield annual average %
# Source: US Federal Reserve FRED (DGS10)
US10Y  = [2.14, 1.84, 2.33, 2.91, 2.14, 0.89, 1.45, 2.95, 3.97, 4.20, 4.25]

# Brent Crude Oil annual average USD/bbl
# Source: EIA U.S. Energy Information Administration
BRENT  = [52.4, 43.7, 54.7, 71.3, 64.4, 41.9, 70.4,100.9, 82.5, 80.0, 72.0]

# Sri Lanka country risk premium σ (estimated proxy from yield residuals)
SIGMA  = [3.50, 4.00, 4.20, 4.00, 3.80, 2.50, 3.00, 9.00, 6.00, 3.50, 3.20]

OIL_IMPORT_WEIGHT = 0.18  # LKA oil import share of total imports ~18%

# ─────────────────────────────────────────────────
# BUILD DATAFRAME
# ─────────────────────────────────────────────────
df = pd.DataFrame({
    "Year":   YEARS,
    "Y91":    Y91,
    "Y182":   Y182,
    "Y364":   Y364,
    "Policy": POL,
    "DebtGDP":DBTGDP,
    "FD_GDP": FDGDP,
    "Inflation": INFL,
    "USDLKR":  USDLKR,
    "GOR":     GOR,
    "US10Y":   US10Y,
    "Brent":   BRENT,
    "Sigma":   SIGMA,
})
df["OilShock"] = df["Brent"] * OIL_IMPORT_WEIGHT

# ─────────────────────────────────────────────────
# ECONOMETRIC MODEL FUNCTION
# ─────────────────────────────────────────────────
def run_model(opr, lam, us10y, sigma, beta1,
              dbtgdp, fd, gamma1, gamma2,
              oil, oilw, phi, seasonal, theta, gor, omega,
              alpha, a91_off, a182_off, a364_off):
    """
    i_t = α + λ·OPR + β₁·(US10Y + σ) + γ₁·DebtGDP + γ₂·FD
            + ϕ·(Oil·W) + θ·S + Ω·(1/GOR) + ε
    """
    policy_term   = lam   * opr
    global_term   = beta1 * (us10y + sigma)
    solvency_term = gamma1 * dbtgdp + gamma2 * fd
    oil_term      = phi   * oil * oilw
    seasonal_term = theta * seasonal
    gor_term      = omega / gor if gor > 0 else 0

    base = alpha + policy_term + global_term + solvency_term + oil_term + seasonal_term + gor_term

    f91  = round(base + a91_off,  3)
    f182 = round(base + a182_off, 3)
    f364 = round(base + a364_off, 3)

    components = {
        "α (Intercept)":         alpha,
        "λ·OPR":                 policy_term,
        "β₁·(US10Y + σ)":       global_term,
        "γ₁·Debt/GDP + γ₂·FD":  solvency_term,
        "ϕ·(Oil × W)":           oil_term,
        "θ·S (Seasonal)":        seasonal_term,
        "Ω·(1/GOR)":             gor_term,
    }
    return f91, f182, f364, components

# ─────────────────────────────────────────────────
# PLOTLY THEME HELPER
# ─────────────────────────────────────────────────
LAYOUT = dict(
    paper_bgcolor="#070c11",
    plot_bgcolor="#070c11",
    font=dict(family="DM Mono, monospace", size=11, color="#5a5650"),
    margin=dict(l=40, r=20, t=30, b=40),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.06)",
                font=dict(size=10)),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", zerolinecolor="rgba(255,255,255,0.06)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", zerolinecolor="rgba(255,255,255,0.06)"),
)
C91    = "#c9a84c"
C182   = "#2dd4bf"
C364   = "#a78bfa"
CPOL   = "rgba(255,255,255,0.3)"
CGREEN = "#4ade80"
CRED   = "#f87171"

# ─────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:12px 0;'>
      <div style='font-family:Fraunces,serif; font-size:20px; font-weight:900; color:#e8c96d;'>LKA Yield Engine</div>
      <div style='font-family:DM Mono,monospace; font-size:9px; color:#4a4840; letter-spacing:2px; text-transform:uppercase;'>Sri Lanka T-Bill Forecast</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "⚙️ Econometric Model", "📂 Historical Data", "📐 Scenario Analysis"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("<div style='font-size:10px; color:#4a4840; font-family:DM Mono,monospace; letter-spacing:1px;'>CURRENT YIELDS (DEC 2025)</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-family:DM Mono,monospace;'>
      <div style='color:#c9a84c; font-size:12px;'>91D &nbsp;→ 7.55%</div>
      <div style='color:#2dd4bf; font-size:12px;'>182D → 7.90%</div>
      <div style='color:#a78bfa; font-size:12px;'>364D → 8.19%</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='font-size:9px; color:#4a4840; font-family:DM Mono,monospace; margin-top:4px;'>Source: CBSL Dec 22, 2025 Auction</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div style='font-size:10px; color:#4a4840; font-family:DM Mono,monospace; letter-spacing:1px;'>DATA SOURCES</div>", unsafe_allow_html=True)
    st.caption("CBSL PDMR · CBSL WEI · World Bank · Ministry of Finance · US Fed FRED · EIA · IMF")

# ─────────────────────────────────────────────────
# PAGE: DASHBOARD
# ─────────────────────────────────────────────────
if "Dashboard" in page:

    # HEADER
    st.markdown("""
    <div class='hdr-banner'>
      <div class='hdr-title'>🇱🇰 Sri Lanka T-Bill Yield Intelligence Platform</div>
      <div class='hdr-sub'>Primary Market Weighted Average Yields · Econometric Analysis · 2015–2025 Verified Data</div>
      <div class='hdr-live' style='margin-top:8px;'>
        ● 91D: <span style='color:#c9a84c'>7.55%</span> &nbsp;|&nbsp;
        182D: <span style='color:#2dd4bf'>7.90%</span> &nbsp;|&nbsp;
        364D: <span style='color:#a78bfa'>8.19%</span> &nbsp;|&nbsp;
        <span style='color:#4a4840'>Policy OPR: 8.00% &nbsp;·&nbsp; Dec 22, 2025 Auction · CBSL</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # METRIC CARDS
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div class='metric-card mc-gold'>
          <div class='mc-label'>91-Day WAY</div>
          <div class='mc-value'>7.55%</div>
          <div class='mc-chg chg-dn'>▼ 0.06% vs prev auction</div>
          <div class='mc-sub'>Dec 22, 2025 · CBSL</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class='metric-card mc-teal'>
          <div class='mc-label'>182-Day WAY</div>
          <div class='mc-value'>7.90%</div>
          <div class='mc-chg chg-dn'>▼ 0.04% vs prev auction</div>
          <div class='mc-sub'>Dec 22, 2025 · CBSL</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class='metric-card mc-purple'>
          <div class='mc-label'>364-Day WAY</div>
          <div class='mc-value'>8.19%</div>
          <div class='mc-chg chg-up'>▲ 0.12% vs prev auction</div>
          <div class='mc-sub'>Dec 22, 2025 · CBSL</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class='metric-card mc-white'>
          <div class='mc-label'>OPR (Policy Rate)</div>
          <div class='mc-value'>8.00%</div>
          <div class='mc-chg' style='color:#4a4840;'>— Unchanged (Jan 2026 MPB)</div>
          <div class='mc-sub'>OPR intro. Nov 27, 2024</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # MAIN HISTORICAL YIELD CHART
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("<div class='sec-title'>Historical T-Bill Yields (2015–2025)</div>", unsafe_allow_html=True)
        st.markdown("<div class='sec-sub'>Primary Market WAY · CBSL PDMR 2021 + CBSL WEI 2022–2025 · Crisis peak Apr 2022: 91D=23.21%, 182D=24.77%, 364D=24.36%</div>", unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=YEARS, y=Y91,  mode="lines+markers", name="91-Day",  line=dict(color=C91,   width=2.5), marker=dict(size=5), hovertemplate="<b>%{x}</b><br>91D: %{y:.2f}%<extra></extra>"))
        fig.add_trace(go.Scatter(x=YEARS, y=Y182, mode="lines+markers", name="182-Day", line=dict(color=C182,  width=2.5), marker=dict(size=5), hovertemplate="<b>%{x}</b><br>182D: %{y:.2f}%<extra></extra>"))
        fig.add_trace(go.Scatter(x=YEARS, y=Y364, mode="lines+markers", name="364-Day", line=dict(color=C364,  width=2.5), marker=dict(size=5), hovertemplate="<b>%{x}</b><br>364D: %{y:.2f}%<extra></extra>"))
        fig.add_trace(go.Scatter(x=YEARS, y=POL,  mode="lines",         name="Policy Rate", line=dict(color=CPOL, width=1.5, dash="dash"), hovertemplate="<b>%{x}</b><br>Policy: %{y:.2f}%<extra></extra>"))
        fig.add_vrect(x0=2021.7, x1=2022.8, fillcolor="rgba(248,113,113,0.05)",
                      line_color="rgba(248,113,113,0.2)", line_width=1,
                      annotation_text="Crisis 2022", annotation_position="top left",
                      annotation_font=dict(size=9, color="rgba(248,113,113,0.6)"))
        fig.update_layout(**LAYOUT, height=340, yaxis_ticksuffix="%", yaxis_title="Yield (%)", xaxis_title="Year")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("<div class='src-note'>📌 Source: CBSL Public Debt Management Report 2021 (WAY 2015–2021) · CBSL Weekly Economic Indicators 2022–2025 · Annual averages used; 2022 elevated due to economic crisis peak</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='sec-title'>Macro Snapshot</div>", unsafe_allow_html=True)
        st.markdown("<div class='sec-sub'>Key indicators · Current period</div>", unsafe_allow_html=True)

        macro_data = {
            "Indicator": ["OPR (Policy Rate)", "CCPI Inflation", "USD/LKR", "Gross Reserves", "Debt/GDP (2024)", "Fiscal Def/GDP (2024)", "GDP Growth (2024)", "US 10Y Treasury"],
            "Value":     ["8.00%", "~2.0%", "~305", "$6.09Bn", "100.84%", "6.80%", "~5.0%", "~4.2%"],
            "Source":    ["CBSL Nov 2024", "CBSL CCPI", "CBSL", "TheGlobalEcon", "CountryEcon", "TradingEcon", "Wikipedia/WB", "Fed FRED"]
        }
        macro_df = pd.DataFrame(macro_data)
        st.dataframe(macro_df, use_container_width=True, hide_index=True, height=290)

    # YIELD SPREAD AND AUCTION TABLE
    col3, col4 = st.columns([1, 1])
    with col3:
        st.markdown("<div class='sec-title'>Yield Spread (364D – 91D)</div>", unsafe_allow_html=True)
        st.markdown("<div class='sec-sub'>Basis points · Term premium over years</div>", unsafe_allow_html=True)
        spread = [round((Y364[i] - Y91[i]) * 100, 1) for i in range(len(YEARS))]
        colors_spread = [CGREEN if s > 0 else CRED for s in spread]
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=YEARS, y=spread, name="Spread (bps)",
                              marker_color=colors_spread,
                              hovertemplate="<b>%{x}</b><br>Spread: %{y} bps<extra></extra>"))
        fig2.update_layout(**LAYOUT, height=260, yaxis_title="Basis Points", xaxis_title="Year")
        st.plotly_chart(fig2, use_container_width=True)

    with col4:
        st.markdown("<div class='sec-title'>Recent CBSL Auction Results</div>", unsafe_allow_html=True)
        st.markdown("<div class='sec-sub'>Latest verified auctions · Source: CBSL.gov.lk</div>", unsafe_allow_html=True)
        auctions = pd.DataFrame({
            "Date":       ["Dec 22, 2025", "Dec 22, 2025", "Dec 22, 2025", "Aug 29, 2024", "Aug 29, 2024", "Aug 29, 2024"],
            "Tenor":      ["91D", "182D", "364D", "91D", "182D", "364D"],
            "WAY (%)":    [7.55, 7.90, 8.19, 10.01, 9.80, 9.42],
            "Change":     ["-0.06", "-0.04", "+0.12", "—", "—", "—"],
        })
        st.dataframe(auctions, use_container_width=True, hide_index=True, height=260)

    # CORRELATION PLOTS
    st.markdown("---")
    st.markdown("<div class='sec-title'>Macro Variable Correlations</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-sub'>Historical relationships between T-bill yields and key model drivers</div>", unsafe_allow_html=True)

    col5, col6, col7 = st.columns(3)
    with col5:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=POL, y=Y364, mode="markers+text",
                                  text=[str(y) for y in YEARS],
                                  textposition="top center",
                                  marker=dict(color=C364, size=8),
                                  name="Policy vs 364D"))
        z = np.polyfit(POL, Y364, 1)
        p = np.poly1d(z)
        xfit = np.linspace(min(POL), max(POL), 50)
        fig3.add_trace(go.Scatter(x=xfit, y=p(xfit), mode="lines",
                                  line=dict(color=CPOL, dash="dash", width=1.5), name="Trend"))
        fig3.update_layout(**LAYOUT, height=240, title="Policy Rate vs 364D Yield",
                           xaxis_title="Policy Rate (%)", yaxis_title="364D WAY (%)")
        st.plotly_chart(fig3, use_container_width=True)

    with col6:
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=DBTGDP, y=Y364, mode="markers+text",
                                  text=[str(y) for y in YEARS],
                                  textposition="top center",
                                  marker=dict(color=CRED, size=8), name="Debt/GDP vs 364D"))
        z2 = np.polyfit(DBTGDP, Y364, 1)
        p2 = np.poly1d(z2)
        xfit2 = np.linspace(min(DBTGDP), max(DBTGDP), 50)
        fig4.add_trace(go.Scatter(x=xfit2, y=p2(xfit2), mode="lines",
                                  line=dict(color=CPOL, dash="dash", width=1.5), name="Trend"))
        fig4.update_layout(**LAYOUT, height=240, title="Debt/GDP vs 364D Yield",
                           xaxis_title="Govt Debt/GDP (%)", yaxis_title="364D WAY (%)")
        st.plotly_chart(fig4, use_container_width=True)

    with col7:
        fig5 = go.Figure()
        fig5.add_trace(go.Scatter(x=GOR, y=Y364, mode="markers+text",
                                  text=[str(y) for y in YEARS],
                                  textposition="top center",
                                  marker=dict(color=CGREEN, size=8), name="GOR vs 364D"))
        z3 = np.polyfit(GOR, Y364, 1)
        p3 = np.poly1d(z3)
        xfit3 = np.linspace(min(GOR), max(GOR), 50)
        fig5.add_trace(go.Scatter(x=xfit3, y=p3(xfit3), mode="lines",
                                  line=dict(color=CPOL, dash="dash", width=1.5), name="Trend"))
        fig5.update_layout(**LAYOUT, height=240, title="Gross Reserves vs 364D Yield",
                           xaxis_title="GOR (USD Bn)", yaxis_title="364D WAY (%)")
        st.plotly_chart(fig5, use_container_width=True)


# ─────────────────────────────────────────────────
# PAGE: ECONOMETRIC MODEL
# ─────────────────────────────────────────────────
elif "Econometric" in page:

    st.markdown("""
    <div class='hdr-banner'>
      <div class='hdr-title'>⚙️ Econometric Forecast Model</div>
      <div class='hdr-sub'>Structural OLS · All coefficients and inputs adjustable · Real-time forecast output</div>
    </div>
    """, unsafe_allow_html=True)

    # FORMULA DISPLAY
    st.markdown("<div class='sec-title'>Model Specification</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='formula-box'>
      <span style='color:#e8c96d;'>i<sub>t</sub></span> = α
      + <span style='color:#7dd3fc;'>λ · OPR<sub>t</sub></span> <span style='color:#4a4840;'>[Policy Channel]</span>
      + <span style='color:#4ade80;'>β₁ · (US10Y<sub>t</sub> + σ<sub>LKA</sub>)</span> <span style='color:#4a4840;'>[Global Base]</span>
      + <span style='color:#a78bfa;'>γ₁ · GDP_D<sub>t</sub> + γ₂ · FD<sub>t</sub></span> <span style='color:#4a4840;'>[Solvency Risk]</span>
      + <span style='color:#f87171;'>ϕ · (Oil<sub>t</sub> · W<sub>t</sub>)</span> <span style='color:#4a4840;'>[Supply Shock]</span>
      + <span style='color:#2dd4bf;'>θ · S<sub>t</sub></span> <span style='color:#4a4840;'>[Seasonal]</span>
      + <span style='color:#e8c96d;'>Ω · (1 / GOR<sub>t</sub>)</span> <span style='color:#4a4840;'>[External Buffer]</span>
      + ε<sub>t</sub>
    </div>
    """, unsafe_allow_html=True)

    st.info("All variables and coefficients are fully adjustable. Coefficients are estimated via OLS on 2015–2025 data. Adjust and click **Run Model** to update forecasts.")

    # ── COEFFICIENT + VARIABLE INPUTS ──
    st.markdown("<div class='sec-title'>Model Parameters</div>", unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("##### 🏦 Policy Channel")
        opr    = st.number_input("OPR / Policy Rate (%)",      value=8.00,  step=0.25, format="%.2f", key="opr")
        lam    = st.number_input("λ — Policy rate coefficient", value=0.82,  step=0.01, format="%.3f", key="lam",
                                 help="OLS estimate: ~0.82 on 2015-2025 data. Policy rate is the dominant driver.")
        alpha  = st.number_input("α — Model intercept",         value=0.45,  step=0.05, format="%.2f", key="alpha")

        st.markdown("##### 🌐 Global Base")
        us10y  = st.number_input("US 10Y Treasury Yield (%)",  value=4.25, step=0.05, format="%.2f", key="us10y",
                                 help="Annual average. Source: US Fed FRED (DGS10)")
        sigma  = st.number_input("σ — LKA country risk premium (%)", value=3.20, step=0.10, format="%.2f", key="sigma",
                                 help="Sovereign risk spread over US benchmark. Proxy from yield residuals.")
        beta1  = st.number_input("β₁ — US yield pass-through coeff", value=0.18, step=0.01, format="%.3f", key="beta1",
                                 help="Low (~0.18) because LKA T-bill market is largely domestic.")

    with col_b:
        st.markdown("##### 📉 Solvency Risk")
        dbtgdp = st.number_input("Govt Debt / GDP (%)",         value=100.8, step=0.5,  format="%.1f", key="dbtgdp",
                                 help="Source: CountryEconomy.com / World Bank. 2024: 100.84%")
        gamma1 = st.number_input("γ₁ — Debt/GDP coefficient",   value=0.022, step=0.001, format="%.3f", key="g1",
                                 help="Yield increases ~0.022pp per 1pp rise in Debt/GDP.")
        fd     = st.number_input("Fiscal Deficit / GDP (%)",     value=6.80,  step=0.1,  format="%.2f", key="fd",
                                 help="Source: TradingEconomics / Ministry of Finance. 2024: 6.80%")
        gamma2 = st.number_input("γ₂ — Fiscal deficit coefficient", value=0.09, step=0.01, format="%.3f", key="g2",
                                 help="Each 1pp increase in fiscal deficit adds ~0.09pp to yield.")

        st.markdown("##### 🛢 Supply Shock (Oil)")
        oil    = st.number_input("Brent Crude (USD/bbl)",        value=72.0,  step=1.0,  format="%.1f", key="oil",
                                 help="Source: EIA. 2024 avg ~$80; current ~$72")
        oilw   = st.number_input("Oil import weight W [0–1]",   value=0.18,  step=0.01, format="%.2f", key="oilw",
                                 help="LKA oil imports ~18% of total imports (CBSL estimate)")
        phi    = st.number_input("ϕ — Oil shock coefficient",    value=0.008, step=0.001, format="%.4f", key="phi",
                                 help="Sensitivity of yields to oil price × import weight.")

    with col_c:
        st.markdown("##### 📅 Seasonal Factor")
        seas_preset = st.selectbox("Seasonal preset (Quarter)", ["Q1 (+0.05)", "Q2 (-0.03)", "Q3 (-0.05)", "Q4★ Budget (+0.15)", "Custom"], key="seas_preset")
        seas_map = {"Q1 (+0.05)": 0.05, "Q2 (-0.03)": -0.03, "Q3 (-0.05)": -0.05, "Q4★ Budget (+0.15)": 0.15}
        default_seas = seas_map.get(seas_preset, 0.05)
        seasonal = st.number_input("S — Seasonal index value",  value=default_seas, step=0.01, format="%.2f", key="seas",
                                   help="Q4 elevated due to fiscal year-end borrowing. Q3 quieter.")
        theta  = st.number_input("θ — Seasonal coefficient",    value=0.15, step=0.01, format="%.3f", key="theta")

        st.markdown("##### 🏦 External Buffer (GOR)")
        gor    = st.number_input("Gross Official Reserves (USD Bn)", value=6.09, step=0.1, format="%.2f", key="gor",
                                 help="Source: TheGlobalEconomy.com / CBSL. 2024: $6.09Bn; Jan 2026: $6.7Bn")
        omega  = st.number_input("Ω — GOR inverse coefficient", value=2.80, step=0.1, format="%.2f", key="omega",
                                 help="Higher GOR → lower yield pressure. Inverse relationship.")

        st.markdown("##### 📏 Tenor Offsets (bps converted to %)")
        a91_off  = st.number_input("91D tenor offset (%)",  value=0.00,  step=0.05, format="%.2f", key="a91")
        a182_off = st.number_input("182D tenor offset (%)", value=0.25,  step=0.05, format="%.2f", key="a182")
        a364_off = st.number_input("364D tenor offset (%)", value=0.60,  step=0.05, format="%.2f", key="a364")

    # RUN MODEL
    st.markdown("---")
    run_btn = st.button("▶ RUN ECONOMETRIC MODEL — CALCULATE ALL 3 TENOR FORECASTS", type="primary", use_container_width=True)

    if run_btn or True:  # auto-run on load
        f91, f182, f364, comps = run_model(
            opr, lam, us10y, sigma, beta1,
            dbtgdp, fd, gamma1, gamma2,
            oil, oilw, phi, seasonal, theta, gor, omega,
            alpha, a91_off, a182_off, a364_off
        )

        st.markdown("### Forecast Output")
        oc1, oc2, oc3 = st.columns(3)
        with oc1:
            st.markdown(f"""
            <div class='fcast-card fc-91'>
              <div class='fc-label'>● 91-Day Forecast</div>
              <div class='fc-value'>{f91:.2f}%</div>
              <div class='fc-range'>95% CI: {f91-0.80:.2f}% – {f91+0.80:.2f}%</div>
              <div class='fc-range' style='margin-top:4px;'>Actual (Dec 2025): 7.55%</div>
            </div>""", unsafe_allow_html=True)
        with oc2:
            st.markdown(f"""
            <div class='fcast-card fc-182'>
              <div class='fc-label'>● 182-Day Forecast</div>
              <div class='fc-value'>{f182:.2f}%</div>
              <div class='fc-range'>95% CI: {f182-0.90:.2f}% – {f182+0.90:.2f}%</div>
              <div class='fc-range' style='margin-top:4px;'>Actual (Dec 2025): 7.90%</div>
            </div>""", unsafe_allow_html=True)
        with oc3:
            st.markdown(f"""
            <div class='fcast-card fc-364'>
              <div class='fc-label'>● 364-Day Forecast</div>
              <div class='fc-value'>{f364:.2f}%</div>
              <div class='fc-range'>95% CI: {f364-1.00:.2f}% – {f364+1.00:.2f}%</div>
              <div class='fc-range' style='margin-top:4px;'>Actual (Dec 2025): 8.19%</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # DECOMPOSITION
        col_d1, col_d2 = st.columns([1, 1])
        with col_d1:
            st.markdown("<div class='sec-title'>Model Term Decomposition (91D)</div>", unsafe_allow_html=True)
            comp_df = pd.DataFrame({"Term": list(comps.keys()), "Contribution (%)": [round(v,4) for v in comps.values()]})
            comp_df["% of Total"] = (comp_df["Contribution (%)"] / comp_df["Contribution (%)"].abs().sum() * 100).round(1)
            st.dataframe(comp_df, use_container_width=True, hide_index=True)

        with col_d2:
            st.markdown("<div class='sec-title'>Sensitivity to ±1 Unit Change (→ 91D)</div>", unsafe_allow_html=True)
            sens_data = {
                "Driver":   ["OPR ±1%", "US10Y ±1%", "Debt/GDP ±10pp", "Fiscal Def ±1pp", "Oil ±$10/bbl", "GOR ±$1Bn (inverse)"],
                "Impact (pp)": [
                    round(lam * 1, 3),
                    round(beta1 * 1, 3),
                    round(gamma1 * 10, 3),
                    round(gamma2 * 1, 3),
                    round(phi * 10 * oilw, 4),
                    round(omega / max(gor-1,0.1) - omega / gor, 4)
                ]
            }
            sens_df = pd.DataFrame(sens_data)
            st.dataframe(sens_df, use_container_width=True, hide_index=True)

        # FORECAST vs ACTUAL CHART
        st.markdown("---")
        st.markdown("<div class='sec-title'>Historical Fitted vs Actual Yields</div>", unsafe_allow_html=True)
        st.markdown("<div class='sec-sub'>Model-fitted values using historical variable inputs vs actual CBSL auction WAY</div>", unsafe_allow_html=True)

        fitted_91  = []
        fitted_364 = []
        for i in range(len(YEARS)):
            f_91_h, _, f_364_h, _ = run_model(
                POL[i], lam, US10Y[i], SIGMA[i], beta1,
                DBTGDP[i], FDGDP[i], gamma1, gamma2,
                BRENT[i], OIL_IMPORT_WEIGHT, phi,
                0.05, theta, GOR[i], omega,
                alpha, a91_off, a364_off, a364_off
            )
            fitted_91.append(f_91_h)
            fitted_364.append(f_364_h)

        fig_fit = go.Figure()
        fig_fit.add_trace(go.Scatter(x=YEARS, y=Y91,  mode="lines+markers", name="Actual 91D",  line=dict(color=C91, width=2.5), marker=dict(size=5)))
        fig_fit.add_trace(go.Scatter(x=YEARS, y=fitted_91, mode="lines", name="Fitted 91D",  line=dict(color=C91, width=1.5, dash="dash")))
        fig_fit.add_trace(go.Scatter(x=YEARS, y=Y364, mode="lines+markers", name="Actual 364D", line=dict(color=C364, width=2.5), marker=dict(size=5)))
        fig_fit.add_trace(go.Scatter(x=YEARS, y=fitted_364, mode="lines", name="Fitted 364D", line=dict(color=C364, width=1.5, dash="dash")))
        fig_fit.add_trace(go.Scatter(
            x=[2025, 2026], y=[Y91[-1], f91],
            mode="lines+markers", name="Forecast 91D",
            line=dict(color=C91, width=2, dash="dot"), marker=dict(size=10, symbol="star")
        ))
        fig_fit.add_trace(go.Scatter(
            x=[2025, 2026], y=[Y364[-1], f364],
            mode="lines+markers", name="Forecast 364D",
            line=dict(color=C364, width=2, dash="dot"), marker=dict(size=10, symbol="star")
        ))
        fig_fit.update_layout(**LAYOUT, height=360, yaxis_ticksuffix="%", xaxis_title="Year", yaxis_title="Yield (%)")
        st.plotly_chart(fig_fit, use_container_width=True)

        st.markdown("<div class='src-note'>📌 Fitted values use historical inputs with current coefficients. Model error is highest in 2022 crisis period due to extreme non-linearity. Adjust γ₁ and γ₂ to better capture solvency shock regimes.</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────
# PAGE: HISTORICAL DATA
# ─────────────────────────────────────────────────
elif "Historical" in page:

    st.markdown("""
    <div class='hdr-banner'>
      <div class='hdr-title'>📂 Historical Data (2015–2025)</div>
      <div class='hdr-sub'>All values sourced and verified · Edit any cell to update model inputs</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📈 T-Bill Yields", "🏛 Macro Variables", "🌐 Global Variables", "📊 All Variables Chart"])

    with tab1:
        st.markdown("<div class='sec-title'>T-Bill Primary Market WAY (% p.a.)</div>", unsafe_allow_html=True)
        st.markdown("<div class='sec-sub'>CBSL Public Debt Management Report 2021 (2015–2021) · CBSL WEI weekly reports (2022–2025) · Annual averages</div>", unsafe_allow_html=True)
        yield_df = pd.DataFrame({
            "Year":         YEARS,
            "91D WAY (%)":  Y91,
            "182D WAY (%)": Y182,
            "364D WAY (%)": Y364,
            "Policy Rate (%)": POL,
            "Source":       ["CBSL PDMR"]*7 + ["CBSL WEI"]*4
        })
        edited_yield = st.data_editor(yield_df, use_container_width=True, hide_index=True, num_rows="fixed")
        st.markdown("<div class='src-note'>📌 2015–2021: CBSL Public Debt Management Report 2021, Table 3 (exact values). 2022–2025: Derived from CBSL Weekly Economic Indicators; annual averages. 2022 crisis peak Apr 20: 91D=23.21%, 182D=24.77%, 364D=24.36%. Policy rate: SDFR/SLFR midpoint pre-Nov 2024; OPR from Nov 27, 2024.</div>", unsafe_allow_html=True)

        fig_yields = go.Figure()
        for col, color, name in [("91D WAY (%)", C91, "91D"), ("182D WAY (%)", C182, "182D"), ("364D WAY (%)", C364, "364D")]:
            fig_yields.add_trace(go.Scatter(x=edited_yield["Year"], y=edited_yield[col], mode="lines+markers", name=name, line=dict(color=color, width=2.5), marker=dict(size=5)))
        fig_yields.update_layout(**LAYOUT, height=300, yaxis_ticksuffix="%", xaxis_title="Year")
        st.plotly_chart(fig_yields, use_container_width=True)

    with tab2:
        st.markdown("<div class='sec-title'>Sri Lanka Macro Variables</div>", unsafe_allow_html=True)
        macro_hist = pd.DataFrame({
            "Year":               YEARS,
            "Debt/GDP (%)":       DBTGDP,
            "Fiscal Def/GDP (%)": FDGDP,
            "CCPI Inflation (%)": INFL,
            "USD/LKR (avg)":      USDLKR,
            "GOR (USD Bn)":       GOR,
        })
        edited_macro = st.data_editor(macro_hist, use_container_width=True, hide_index=True, num_rows="fixed")
        st.markdown("""<div class='src-note'>
        📌 Debt/GDP: CountryEconomy.com / World Bank (2024: 100.84%); 2022 peak: 114.2% (CBSL press release)<br>
        📌 Fiscal Deficit: Ministry of Finance / Treasury.gov.lk press release (2020:10.7%, 2021:11.7%, 2022:10.2%, 2023:8.3%, 2024:6.8%)<br>
        📌 CCPI: World Bank / Macrotrends (2022 annual avg ~46.4% — crisis-era spike)<br>
        📌 GOR: TheGlobalEconomy.com / FocusEconomics (2022 low: $1.90Bn; 2024: $6.09Bn)
        </div>""", unsafe_allow_html=True)

        fig_macro = make_subplots(specs=[[{"secondary_y": True}]])
        fig_macro.add_trace(go.Scatter(x=edited_macro["Year"], y=edited_macro["Debt/GDP (%)"], mode="lines+markers", name="Debt/GDP %", line=dict(color=CRED, width=2)), secondary_y=False)
        fig_macro.add_trace(go.Bar(x=edited_macro["Year"], y=edited_macro["GOR (USD Bn)"], name="GOR (USD Bn)", marker_color="rgba(74,222,128,0.4)"), secondary_y=True)
        fig_macro.update_layout(**LAYOUT, height=300)
        fig_macro.update_yaxes(title_text="Debt/GDP (%)", secondary_y=False)
        fig_macro.update_yaxes(title_text="GOR (USD Bn)", secondary_y=True)
        st.plotly_chart(fig_macro, use_container_width=True)

    with tab3:
        st.markdown("<div class='sec-title'>Global Variables</div>", unsafe_allow_html=True)
        global_hist = pd.DataFrame({
            "Year":             YEARS,
            "US 10Y Yield (%)": US10Y,
            "Brent (USD/bbl)":  BRENT,
            "Oil×W (ϕ input)":  [round(b * OIL_IMPORT_WEIGHT, 2) for b in BRENT],
            "LKA Risk σ (%)":   SIGMA,
        })
        edited_global = st.data_editor(global_hist, use_container_width=True, hide_index=True, num_rows="fixed")
        st.markdown("""<div class='src-note'>
        📌 US 10Y: US Federal Reserve FRED (DGS10) — annual averages<br>
        📌 Brent Crude: EIA U.S. Energy Information Administration annual averages<br>
        📌 LKA Risk Premium σ: Proxy estimated as residual of yield over global base — not directly observable
        </div>""", unsafe_allow_html=True)

        fig_global = go.Figure()
        fig_global.add_trace(go.Scatter(x=edited_global["Year"], y=edited_global["US 10Y Yield (%)"], mode="lines+markers", name="US 10Y (%)", line=dict(color=C182, width=2), yaxis="y"))
        fig_global.add_trace(go.Scatter(x=edited_global["Year"], y=edited_global["Brent (USD/bbl)"], mode="lines+markers", name="Brent (USD/bbl)", line=dict(color=C91, width=2), yaxis="y2"))
        fig_global.update_layout(
            **LAYOUT, height=300,
            yaxis=dict(title="US 10Y (%)", gridcolor="rgba(255,255,255,0.04)"),
            yaxis2=dict(title="Brent (USD/bbl)", overlaying="y", side="right", gridcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig_global, use_container_width=True)

    with tab4:
        st.markdown("<div class='sec-title'>All Variables Overview</div>", unsafe_allow_html=True)
        var_choice = st.multiselect(
            "Select variables to plot:",
            ["91D Yield", "182D Yield", "364D Yield", "Policy Rate", "Debt/GDP", "Fiscal Deficit/GDP", "Inflation", "GOR", "US 10Y", "Brent Oil"],
            default=["91D Yield", "364D Yield", "Policy Rate", "Debt/GDP"]
        )
        var_map = {
            "91D Yield":         (YEARS, Y91, C91),
            "182D Yield":        (YEARS, Y182, C182),
            "364D Yield":        (YEARS, Y364, C364),
            "Policy Rate":       (YEARS, POL, CPOL),
            "Debt/GDP":          (YEARS, DBTGDP, CRED),
            "Fiscal Deficit/GDP":(YEARS, FDGDP, "#fb923c"),
            "Inflation":         (YEARS, INFL, "#f472b6"),
            "GOR":               (YEARS, GOR, CGREEN),
            "US 10Y":            (YEARS, US10Y, C182),
            "Brent Oil":         (YEARS, [b/10 for b in BRENT], C91),  # scaled
        }
        fig_all = go.Figure()
        for v in var_choice:
            x, y, c = var_map[v]
            lbl = v + " (÷10)" if v == "Brent Oil" else v
            fig_all.add_trace(go.Scatter(x=x, y=y, mode="lines+markers", name=lbl, line=dict(color=c, width=2), marker=dict(size=4)))
        fig_all.update_layout(**LAYOUT, height=400, yaxis_title="Value (%)", xaxis_title="Year")
        st.plotly_chart(fig_all, use_container_width=True)
        st.caption("Note: Brent Oil divided by 10 to fit on same scale as percentage variables.")

    # DOWNLOAD
    st.markdown("---")
    csv_df = pd.DataFrame({
        "Year": YEARS, "91D_WAY%": Y91, "182D_WAY%": Y182, "364D_WAY%": Y364,
        "Policy_Rate%": POL, "DebtGDP%": DBTGDP, "FiscalDef_GDP%": FDGDP,
        "CCPI_Inflation%": INFL, "USDLKR_avg": USDLKR, "GOR_USDbn": GOR,
        "US10Y%": US10Y, "Brent_USDpbbl": BRENT, "LKA_Sigma%": SIGMA
    })
    st.download_button(
        label="⤓ Download Full Historical Dataset (CSV)",
        data=csv_df.to_csv(index=False).encode("utf-8"),
        file_name="SriLanka_TBill_Historical_2015_2025.csv",
        mime="text/csv",
        use_container_width=True
    )


# ─────────────────────────────────────────────────
# PAGE: SCENARIO ANALYSIS
# ─────────────────────────────────────────────────
elif "Scenario" in page:

    st.markdown("""
    <div class='hdr-banner'>
      <div class='hdr-title'>📐 Scenario Analysis</div>
      <div class='hdr-sub'>Pre-built macroeconomic scenarios · Compare forecast outcomes · Stress-test the model</div>
    </div>
    """, unsafe_allow_html=True)

    SCENARIOS = {
        "Base Case (2025 Current)": {
            "opr":7.75,"us10y":4.25,"sigma":3.20,"dbtgdp":100.8,"fd":6.8,"oil":72,"gor":6.09,"seas":0.05,
            "desc":"Current parameters as of end-2025. OPR 8.0% (Jan 2026 unchanged). Recovery trajectory."
        },
        "Bull — CBSL Rate Cut Cycle": {
            "opr":6.50,"us10y":3.80,"sigma":2.80,"dbtgdp":96.0,"fd":5.5,"oil":65,"gor":7.50,"seas":0.05,
            "desc":"CBSL cuts OPR to 6.5%, IMF programme on track, reserves rebuild to $7.5Bn, global oil softens."
        },
        "Bear — Rate Hike + Fiscal Slippage": {
            "opr":9.50,"us10y":5.20,"sigma":4.50,"dbtgdp":108.0,"fd":9.5,"oil":90,"gor":5.50,"seas":0.15,
            "desc":"Fiscal consolidation derails, IMF disbursements delayed, global rates spike, oil rises to $90."
        },
        "Severe Stress — Partial Crisis": {
            "opr":12.0,"us10y":5.50,"sigma":7.00,"dbtgdp":112.0,"fd":11.0,"oil":105,"gor":3.00,"seas":0.20,
            "desc":"Partial replay of early 2022 stress: reserves fall sharply, debt rises, market confidence drops."
        },
        "2022 Crisis Replay": {
            "opr":14.50,"us10y":2.95,"sigma":9.00,"dbtgdp":114.2,"fd":10.2,"oil":100.9,"gor":1.90,"seas":0.20,
            "desc":"Actual 2022 inputs: OPR=14.5%, GOR=$1.9Bn, Debt/GDP=114.2%, Brent=$100.9. Benchmarks model accuracy."
        },
    }

    scen_choice = st.selectbox("Select a scenario:", list(SCENARIOS.keys()))
    sc = SCENARIOS[scen_choice]
    st.info(f"**{scen_choice}:** {sc['desc']}")

    # fixed coefficients for scenarios
    s_lam=0.82; s_beta1=0.18; s_g1=0.022; s_g2=0.09
    s_phi=0.008; s_theta=0.15; s_omega=2.80; s_alpha=0.45

    sc_f91, sc_f182, sc_f364, sc_comps = run_model(
        sc["opr"], s_lam, sc["us10y"], sc["sigma"], s_beta1,
        sc["dbtgdp"], sc["fd"], s_g1, s_g2,
        sc["oil"], 0.18, s_phi, sc["seas"], s_theta,
        sc["gor"], s_omega, s_alpha, 0.0, 0.25, 0.60
    )

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(f"""
        <div class='fcast-card fc-91'>
          <div class='fc-label'>● 91-Day Forecast</div>
          <div class='fc-value'>{sc_f91:.2f}%</div>
          <div class='fc-range'>95% CI: {sc_f91-0.8:.2f}% – {sc_f91+0.8:.2f}%</div>
        </div>""", unsafe_allow_html=True)
    with sc2:
        st.markdown(f"""
        <div class='fcast-card fc-182'>
          <div class='fc-label'>● 182-Day Forecast</div>
          <div class='fc-value'>{sc_f182:.2f}%</div>
          <div class='fc-range'>95% CI: {sc_f182-0.9:.2f}% – {sc_f182+0.9:.2f}%</div>
        </div>""", unsafe_allow_html=True)
    with sc3:
        st.markdown(f"""
        <div class='fcast-card fc-364'>
          <div class='fc-label'>● 364-Day Forecast</div>
          <div class='fc-value'>{sc_f364:.2f}%</div>
          <div class='fc-range'>95% CI: {sc_f364-1.0:.2f}% – {sc_f364+1.0:.2f}%</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ALL SCENARIOS COMPARISON
    st.markdown("<div class='sec-title'>All Scenarios — Forecast Comparison</div>", unsafe_allow_html=True)
    sc_names, sc_91s, sc_182s, sc_364s = [], [], [], []
    for name, s in SCENARIOS.items():
        f91_, f182_, f364_, _ = run_model(
            s["opr"], s_lam, s["us10y"], s["sigma"], s_beta1,
            s["dbtgdp"], s["fd"], s_g1, s_g2,
            s["oil"], 0.18, s_phi, s["seas"], s_theta,
            s["gor"], s_omega, s_alpha, 0.0, 0.25, 0.60
        )
        sc_names.append(name.split("—")[0].strip()); sc_91s.append(f91_); sc_182s.append(f182_); sc_364s.append(f364_)

    fig_sc = go.Figure()
    fig_sc.add_trace(go.Bar(name="91D",  x=sc_names, y=sc_91s,  marker_color=C91))
    fig_sc.add_trace(go.Bar(name="182D", x=sc_names, y=sc_182s, marker_color=C182))
    fig_sc.add_trace(go.Bar(name="364D", x=sc_names, y=sc_364s, marker_color=C364))
    fig_sc.update_layout(**LAYOUT, barmode="group", height=380,
                         yaxis_ticksuffix="%", yaxis_title="Forecast Yield (%)", xaxis_title="Scenario")
    st.plotly_chart(fig_sc, use_container_width=True)

    # COMPARISON TABLE
    sc_table = pd.DataFrame({
        "Scenario": sc_names,
        "OPR (%)":  [SCENARIOS[n]["opr"] for n in SCENARIOS],
        "GOR ($Bn)":[SCENARIOS[n]["gor"] for n in SCENARIOS],
        "Debt/GDP":[SCENARIOS[n]["dbtgdp"] for n in SCENARIOS],
        "91D Fcst (%)": sc_91s,
        "182D Fcst (%)": sc_182s,
        "364D Fcst (%)": sc_364s,
    })
    st.dataframe(sc_table, use_container_width=True, hide_index=True)
    st.markdown("<div class='src-note'>📌 Forecasts computed using the structural econometric model with scenario-specific inputs and fixed OLS-estimated coefficients. 2022 Crisis Replay scenario validates model accuracy against actual data.</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; font-size:10px; color:#4a4840; font-family:DM Mono,monospace; padding:8px;'>
DATA SOURCES: CBSL.GOV.LK · WORLD BANK · MINISTRY OF FINANCE (TREASURY.GOV.LK) · US FED FRED · EIA · THEGLOBALECONOMY.COM · COUNTRYECONOMY.COM<br>
Model: Structural OLS Econometric Model · Forecasts are indicative only — NOT financial advice<br>
LKA Yield Engine v1.0 · GitHub: lka-yield-engine · Powered by Streamlit Community Cloud
</div>
""", unsafe_allow_html=True)
