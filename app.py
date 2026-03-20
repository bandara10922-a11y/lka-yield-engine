{\rtf1\ansi\ansicpg1252\cocoartf2758
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import yfinance as yf\
import pandas as pd\
import numpy as np\
import plotly.graph_objects as go\
from statsmodels.tsa.holtwinters import ExponentialSmoothing\
import datetime\
\
# --- SYSTEM CONFIG & AUTHENTICATION ---\
st.set_page_config(page_title="LKA Sovereign Yield Engine PRO", layout="wide")\
\
def check_password():\
    if "authenticated" not in st.session_state:\
        st.session_state.authenticated = False\
    \
    if not st.session_state.authenticated:\
        st.title("\uc0\u55357 \u56592  Terminal Access Restricted")\
        user = st.text_input("Username")\
        pw = st.text_input("Password", type="password")\
        if st.button("Login"):\
            if user == "Admin101" and pw == "NSB101@@":\
                st.session_state.authenticated = True\
                st.rerun()\
            else:\
                st.error("Invalid Credentials")\
        return False\
    return True\
\
if check_password():\
    # --- DATA SOURCE DIRECTORY ---\
    st.sidebar.title("\uc0\u55357 \u57056  Command Center")\
    \
    with st.sidebar.expander("\uc0\u55357 \u56524  Data Source Directory", expanded=False):\
        st.markdown("""\
        - **OPR & GOR:** [CBSL Weekly Indicators](https://www.cbsl.gov.lk/en/statistics/economic-indicators/weekly-indicators)\
        - **CCPI Inflation:** [Dept. Census & Stats](http://www.statistics.gov.lk/)\
        - **T-Bill Auction Results:** [CBSL Press Releases](https://www.cbsl.gov.lk/en/news)\
        - **Debt/GDP:** [Ministry of Finance Reports](https://www.treasury.gov.lk/)\
        """)\
\
    # --- INPUT INTERFACE ---\
    st.sidebar.subheader("Manual Macro Inputs")\
    opr = st.sidebar.number_input("Overnight Policy Rate (OPR) %", value=7.75, step=0.25)\
    ccpi = st.sidebar.number_input("YoY CCPI Inflation %", value=1.6, step=0.1)\
    gor = st.sidebar.number_input("Reserves (GOR $B)", value=7.1)\
    bid_to_cover = st.sidebar.slider("Auction Bid-to-Cover Ratio", 0.5, 4.0, 1.8)\
    debt_gdp = st.sidebar.slider("Debt-to-GDP %", 80, 130, 105)\
    \
    guidance = st.sidebar.selectbox("Forward Guidance Signal", ["Dovish", "Neutral", "Hawkish"])\
    \
    # --- LIVE DATA FETCHING ---\
    @st.cache_data(ttl=3600)\
    def get_market_data():\
        tickers = \{"Oil": "BZ=F", "US10Y": "^TNX"\}\
        data = \{k: yf.Ticker(v).history(period="1d")['Close'].iloc[-1] for k, v in tickers.items()\}\
        return data\
\
    market = get_market_data()\
\
    # --- ECONOMETRIC CALCULATION ENGINE ---\
    # Synthetic Yield Spreads\
    # 91D as base, 182D (+50-80bps), 364D (+120-200bps)\
    term_premium_182 = 0.65 + (debt_gdp - 100)*0.05\
    term_premium_364 = 1.45 + (debt_gdp - 100)*0.10\
    \
    # 91D Model Logic\
    base_91 = opr + (market['US10Y']*0.4) + max(0, (ccpi-5)*0.3) + max(0, (5-gor)*1.5)\
    if guidance == "Hawkish": base_91 += 0.5\
    elif guidance == "Dovish": base_91 -= 0.5\
    \
    y91 = base_91 + (2.0 - bid_to_cover)\
    y182 = y91 + term_premium_182\
    y364 = y91 + term_premium_364\
\
    # --- UI DASHBOARD ---\
    st.title("Sovereign Yield Risk Engine: Sri Lanka")\
    \
    # 6. Executive Heatmap\
    c1, c2, c3, c4 = st.columns(4)\
    c1.metric("91D Forecast", f"\{y91:.2f\}%", f"\{guidance\}")\
    c2.metric("182D Forecast", f"\{y182:.2f\}%")\
    c3.metric("364D Forecast", f"\{y364:.2f\}%")\
    c4.metric("Confidence Level", "High" if bid_to_cover > 1.5 else "Low", delta_color="inverse")\
\
    tabs = st.tabs(["Yield Curve", "Time-Series", "Scenarios", "Auction Analytics", "Technical Analysis"])\
\
    # 1. Yield Curve\
    with tabs[0]:\
        fig = go.Figure()\
        fig.add_trace(go.Scatter(x=['91D', '182D', '364D'], y=[y91-0.5, y182-0.4, y364-0.3], name="Current Yield", line=dict(dash='dash')))\
        fig.add_trace(go.Scatter(x=['91D', '182D', '364D'], y=[y91, y182, y364], name="Forecasted Yield", line=dict(width=4, color='gold')))\
        fig.update_layout(title="LKA Sovereign Yield Curve Projection", template="plotly_dark")\
        st.plotly_chart(fig, use_container_width=True)\
\
    # 2. Time-Series (Exponential Smoothing Simulation)\
    with tabs[1]:\
        st.subheader("3-Month Projection (Moving Average & Smoothing)")\
        periods = 90\
        hist_data = np.random.normal(y91, 0.2, 100) # Simulated historical\
        model = ExponentialSmoothing(hist_data, trend='add', seasonal=None).fit()\
        forecast = model.forecast(periods)\
        \
        fig_ts = go.Figure()\
        fig_ts.add_trace(go.Scatter(y=hist_data, name="Historical"))\
        fig_ts.add_trace(go.Scatter(x=np.arange(100, 100+periods), y=forecast, name="Smoothing Forecast", line=dict(color='cyan')))\
        st.plotly_chart(fig_ts, use_container_width=True)\
\
    # 3. Scenario Analysis\
    with tabs[2]:\
        col_sc1, col_sc2, col_sc3 = st.columns(3)\
        col_sc1.info(f"**Bull Case (IMF Gold Star):** \{y91-1.5:.2f\}%")\
        col_sc2.warning(f"**Base Case:** \{y91:.2f\}%")\
        col_sc3.error(f"**Bear Case (Oil Shock):** \{y91+3.2:.2f\}%")\
\
    # 4. Auction Analytics\
    with tabs[3]:\
        st.subheader("Auction Market Microstructure")\
        st.write(f"**Current Bid-to-Cover:** \{bid_to_cover\}x")\
        st.progress(bid_to_cover/4.0)\
        st.write("Interpretation: " + ("Oversubscribed - Rates Stable" if bid_to_cover > 1.2 else "Under-subscribed - Risk of Yield Spike"))\
\
    # 5. Technical Analysis\
    with tabs[4]:\
        st.subheader("Momentum Indicators")\
        st.markdown(f"""\
        - **Primary Trend:** \{'Bullish (Rising Rates)' if y91 > (y91-0.5) else 'Bearish (Falling Rates)'\}\
        - **Support Level:** \{y91 - 0.75:.2f\}%\
        - **Resistance Level:** \{y91 + 1.10:.2f\}%\
        """)\
\
    # --- REPORT GENERATION ---\
    st.markdown("---")\
    if st.button("Generate Professional Macro Report"):\
        report = f"""\
        # MACROECONOMIC ADVISORY REPORT: SRI LANKA YIELD OUTLOOK\
        **Date:** \{datetime.date.today()\}\
        **Focus:** 91-Day Treasury Bills\
        \
        ## Executive Summary\
        Following the OPR stabilization at \{opr\}%, our engine projects a 91-day yield of \{y91:.2f\}%. \
        The primary drivers are the US10Y global floor and a Debt-to-GDP weight of \{debt_gdp\}%.\
        \
        ## Forward Guidance\
        The CBSL stance is currently **\{guidance.upper()\}**. \
        This suggests a market positioning favoring \{'short-term liquidity' if guidance == 'Dovish' else 'term-premium protection'\}.\
        \
        ## Risk Assessment\
        The Bid-to-Cover ratio of \{bid_to_cover\} indicates \{ 'healthy market appetite' if bid_to_cover > 1.5 else 'fragile auction dynamics'\}.\
        """\
        st.download_button("Download Report as TXT", report, file_name="LKA_Yield_Report.txt")}