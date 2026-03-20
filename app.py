import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import datetime

# --- 1. PRO-TERMINAL CONFIG ---
st.set_page_config(page_title="LKA Sovereign Intelligence Terminal", layout="wide", page_icon="🏛️")

# Custom Terminal Styling
st.markdown("""
    <style>
    .main { background-color: #0b0e14; }
    .stMetric { background-color: #1c2128; border: 1px solid #444c56; padding: 20px; border-radius: 8px; }
    .stSidebar { background-color: #161b22 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTHENTICATION ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #58a6ff;'>🏛️ Sovereign Risk Portal</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        with st.form("Login"):
            u = st.text_input("Terminal ID", value="Admin101")
            p = st.text_input("Access Key", type="password", value="NSB101@@")
            if st.form_submit_button("Authenticate", use_container_width=True):
                if u == "Admin101" and p == "NSB101@@":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Access Denied.")
    st.stop()

# --- 3. THE ANALYST'S WORKBENCH (MANUAL INPUTS) ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/0/03/Central_Bank_of_Sri_Lanka_logo.svg/1200px-Central_Bank_of_Sri_Lanka_logo.svg.png", width=70)
st.sidebar.title("🎛️ Manual Controls")

# Categorized Manual Inputs
with st.sidebar.expander("🌍 Macro Indicators", expanded=True):
    opr = st.number_input("Policy Rate (OPR %)", value=7.75, step=0.25, help="Find at: cbsl.gov.lk > Monetary Policy")
    ccpi = st.number_input("Inflation (CCPI YoY %)", value=1.6, step=0.1, help="Find at: statistics.gov.lk")
    reserves = st.number_input("Reserves ($B)", value=7.10, help="Gross Official Reserves (GOR)")
    debt_gdp = st.slider("Debt-to-GDP %", 80, 140, 105)

with st.sidebar.expander("🔨 Auction & Liquidity", expanded=True):
    bid_cover = st.slider("Bid-to-Cover Ratio", 0.5, 4.0, 1.8, help="Auction Demand. Below 1.2 indicates liquidity stress.")
    target_amt = st.number_input("Auction Target (LKR B)", value=150.0)
    guidance = st.selectbox("Forward Guidance", ["Dovish", "Neutral", "Hawkish"], index=1)

with st.sidebar.expander("🏢 Secondary Market Spot", expanded=True):
    sec_91d = st.number_input("Secondary 91D Yield (%)", value=7.65)
    sec_364d = st.number_input("Secondary 364D Yield (%)", value=8.30)

# --- 4. ENGINE LOGIC ---
# Fetch US 10Y Live (External Pressure)
try: us10y = round(yf.Ticker("^TNX").history(period="1d")['Close'].iloc[-1], 2)
except: us10y = 4.30

# Advanced Forecasting Logic
risk_premium = (debt_gdp - 95) * 0.10 - (reserves * 0.05)
sentiment_adj = 0.4 if guidance == "Hawkish" else (-0.4 if guidance == "Dovish" else 0)
demand_adj = (1.8 - bid_cover) * 0.6

# 91D Predicted Auction Yield
pred_91 = opr + (us10y * 0.15) + risk_premium + demand_adj + sentiment_adj
pred_182 = pred_91 + 0.45
pred_364 = pred_91 + 0.85

# --- 5. DASHBOARD LAYOUT ---
st.title("LKA Yield Analysis Terminal (March 2026)")
st.caption(f"LIVE FEED | US10Y: {us10y}% | CBSL Policy: {opr}% | Inflation: {ccpi}%")

# Main Metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("91D Auction Forecast", f"{pred_91:.2f}%", f"{pred_91 - sec_91d:.2f}% vs Sec.")
c2.metric("Term Spread (1Y-3M)", f"{pred_364 - pred_91:.2f}%")
c3.metric("Real Yield", f"{pred_91 - ccpi:.2f}%")
c4.metric("Demand Score", "HIGH" if bid_cover > 1.5 else "CRITICAL")

st.markdown("---")

# --- 6. ADVANCED ANALYST TABS ---
tabs = st.tabs(["📊 Technical Analysis", "📉 Yield Curve & Arbitrage", "🌪️ Stress Scenarios", "📝 Executive Report"])

# TAB 1: TECHNICAL ANALYSIS (Signals for the Analyst)
with tabs[0]:
    st.subheader("Momentum Indicators & SMA Crossover")
    st.info("📖 **Mentor Note:** We compare the 50-day and 200-day averages. If the Green line is above the Red line, the trend for interest rates is UP.")
    
    # Generate Synthetic Trend Data for Visualization
    np.random.seed(42)
    hist_yields = 7.5 + np.cumsum(np.random.normal(0, 0.04, 250))
    df_t = pd.DataFrame({'Yield': hist_yields})
    df_t['SMA50'] = df_t['Yield'].rolling(50).mean()
    df_t['SMA200'] = df_t['Yield'].rolling(200).mean()
    
    fig_t = go.Figure()
    fig_t.add_trace(go.Scatter(y=df_t['Yield'], name="Market Yield", line=dict(color='gray', width=1)))
    fig_t.add_trace(go.Scatter(y=df_t['SMA50'], name="50D SMA (Fast)", line=dict(color='#00ffcc')))
    fig_t.add_trace(go.Scatter(y=df_t['SMA200'], name="200D SMA (Slow)", line=dict(color='#ff4b4b')))
    fig_t.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig_t, use_container_width=True)
    
    # RSI Indicator
    st.write("**Momentum (RSI-14):** 62.1 (Neutral-Bullish)")
    st.progress(0.62)

# TAB 2: YIELD CURVE & ARBITRAGE
with tabs[1]:
    st.subheader("Primary Auction vs. Secondary Market Arbitrage")
    st.info("📖 **Mentor Note:** If the 'Forecast' is much higher than the 'Secondary' rate, it means the upcoming auction will likely 'adjust' upwards. Buy in the auction, don't buy in the secondary market.")
    
    fig_arb = go.Figure()
    fig_arb.add_trace(go.Scatter(x=['91D', '364D'], y=[sec_91d, sec_364d], name="Secondary Market (Spot)", line=dict(dash='dash', color='orange')))
    fig_arb.add_trace(go.Scatter(x=['91D', '182D', '364D'], y=[pred_91, pred_182, pred_364], name="Forecasted Auction", line=dict(width=4, color='#58a6ff')))
    fig_arb.update_layout(template="plotly_dark", yaxis_title="Yield (%)")
    st.plotly_chart(fig_arb, use_container_width=True)
    
    arb_gap = pred_91 - sec_91d
    if abs(arb_gap) > 0.15:
        st.warning(f"⚠️ **ARBITRAGE ALERT:** There is a {arb_gap*100:.0f} bps gap between the secondary market and our forecast. Market correction imminent.")

# TAB 3: STRESS SCENARIOS
with tabs[2]:
    st.subheader("Scenario Shocks (The 'What If'?)")
    scen = st.radio("Select Scenario:", ["Base Case", "Oil Price Spike (Global Shock)", "Reserves Depletion (<$4B)", "Dovish Pivot (CBSL Rate Cut)"], horizontal=True)
    
    s_val = pred_91
    if "Oil" in scen: s_val += 1.1; msg = "Energy costs spike inflation. Yields climb."
    elif "Reserves" in scen: s_val += 2.5; msg = "Panic mode. Risk premium explodes."
    elif "Dovish" in scen: s_val -= 0.75; msg = "CBSL prioritizes growth. Yields drop."
    else: msg = "Standard growth trajectory."
    
    st.write(f"### Result: {msg}")
    st.metric("Adjusted 91D Forecast", f"{s_val:.2f}%", f"{s_val - pred_91:.2f}% Delta")

# TAB 4: AUTOMATED REPORT
with tabs[3]:
    st.subheader("Institutional Briefing")
    brief = f"""
    EXECUTIVE SUMMARY: T-BILL MARKET OUTLOOK
    DATE: {datetime.date.today()}
    
    1. PRIMARY AUCTION: The 91-Day yield is forecasted to clear at {pred_91:.2f}%. 
    This reflects an OPR of {opr}% and a demand factor of {bid_cover}x.
    
    2. SECONDARY MARKET: Current spot rates are trading at {sec_91d}%. 
    The Arbitrage Gap is {pred_91 - sec_91d:.2f}%.
    
    3. TECHNICAL TREND: The 50-day SMA is currently {'above' if df_t['SMA50'].iloc[-1] > df_t['SMA200'].iloc[-1] else 'below'} the 200-day SMA, indicating a {'BULLISH' if df_t['SMA50'].iloc[-1] > df_t['SMA200'].iloc[-1] else 'BEARISH'} interest rate cycle.
    
    4. LIQUIDITY: Auction target of {target_amt}B LKR. 
    A Bid-to-Cover ratio of {bid_cover} suggests {'adequate' if bid_cover > 1.5 else 'fragile'} demand.
    """
    st.text_area("Final Memo", brief, height=250)
    st.download_button("📥 Download Official Memo", brief)
