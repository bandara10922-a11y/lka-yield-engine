import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO

# --- 1. PRO-TERMINAL CONFIG ---
st.set_page_config(page_title="LKA Sovereign Intelligence V3", layout="wide", page_icon="🏛️")

# Custom Dark Theme Styling
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }
    div[data-testid="stExpander"] { border: 1px solid #30363d; background-color: #0d1117; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #161b22; border-radius: 4px 4px 0px 0px; padding: 10px 20px; color: #8b949e; }
    .stTabs [aria-selected="true"] { background-color: #1f6feb !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE MASTER DATASET (VERIFIED MARCH 20, 2026) ---
# Sourced from CBSL Daily Economic Indicators & Weekly Auction Results
hist_data = {
    "Auction_Date": ["2026-03-18", "2026-03-11", "2026-03-04", "2026-02-25", "2026-02-18", "2026-02-11"],
    "Yield_91D": [7.61, 7.61, 7.63, 7.63, 7.75, 7.82],
    "Yield_182D": [7.91, 7.91, 7.92, 7.92, 8.05, 8.12],
    "Yield_364D": [8.23, 8.23, 8.23, 8.24, 8.35, 8.48],
    "Inflation_CCPI": [1.6, 1.6, 1.6, 1.7, 1.7, 1.8],
    "OPR_Policy": [7.75, 7.75, 7.75, 7.75, 8.25, 8.25],
    "GOR_Reserves_USD_B": [7.10, 7.08, 7.05, 7.02, 6.95, 6.88]
}
df_hist = pd.DataFrame(hist_data)
df_hist["Auction_Date"] = pd.to_datetime(df_hist["Auction_Date"])

# --- 3. SIDEBAR CONTROLS (MACRO INPUTS) ---
st.sidebar.title("🎛️ Terminal Controls")
st.sidebar.caption("LKA Market Intelligence | March 2026")

with st.sidebar.expander("🌍 REAL-TIME MACRO", expanded=True):
    # Selected date-based defaults
    selected_date = st.selectbox("Select Data Anchor", df_hist["Auction_Date"])
    curr = df_hist[df_hist["Auction_Date"] == selected_date].iloc[0]
    
    opr = st.number_input("Policy Rate (OPR %)", value=curr['OPR_Policy'])
    ccpi = st.number_input("Inflation (CCPI YoY %)", value=curr['Inflation_CCPI'])
    reserves = st.number_input("GOR Reserves ($B)", value=curr['GOR_Reserves_USD_B'])
    debt_gdp = st.slider("Debt-to-GDP %", 80, 140, 96)

with st.sidebar.expander("💵 FX & USD HEDGING", expanded=True):
    usd_lkr_spot = st.number_input("USD/LKR Spot", value=309.61)
    fwd_points = st.number_input("3M Forward Points (LKR)", value=4.50)
    us_3m = st.number_input("US 3M Bill Yield (%)", value=5.10)

# --- 4. CALCULATION ENGINE ---
# Yield Analytics
hedging_cost = (fwd_points / usd_lkr_spot) * (365 / 91) * 100
real_91 = curr['Yield_91D'] - ccpi
real_182 = curr['Yield_182D'] - ccpi
real_364 = curr['Yield_364D'] - ccpi

# --- 5. MAIN DASHBOARD ---
st.title("🏛️ Sri Lanka Sovereign Intelligence")
st.caption(f"AS AT MARCH 20, 2026 | LKR SPOT: {usd_lkr_spot} | CCPI: {ccpi}% | RESERVES: ${reserves}B")

# High-Level Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("91D Benchmark", f"{curr['Yield_91D']}%", f"{curr['Yield_91D'] - opr:.2f}% vs Policy")
m2.metric("Avg Real Yield", f"{(real_91+real_182+real_364)/3:.2f}%", "Positive")
m3.metric("Annual Hedging Cost", f"{hedging_cost:.2f}%", "USD/LKR")
m4.metric("3M Term Premium", f"{curr['Yield_364D'] - curr['Yield_91D']:.2f}%", "Spread")

st.markdown("---")

# TABS FOR GRANULAR ANALYSIS
tabs = st.tabs(["📊 Detailed Tenor Analysis", "🌎 USD Carry Trade", "📈 Yield Curve Trends", "🗃️ Data Vault (CSV Export)"])

# TAB 1: DETAILED TENOR ANALYSIS
with tabs[0]:
    st.subheader("Treasury Bill Yield Breakdown")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### < 91 Days")
        st.write(f"**Primary Yield:** {curr['Yield_91D']}%")
        st.write(f"**Real Yield:** {real_91:.2f}%")
        st.progress(curr['Yield_91D']/12)
        st.caption("Status: Oversubscribed")

    with col2:
        st.markdown("### < 182 Days")
        st.write(f"**Primary Yield:** {curr['Yield_182D']}%")
        st.write(f"**Real Yield:** {real_182:.2f}%")
        st.progress(curr['Yield_182D']/12)
        st.caption("Status: Stable Demand")

    with col3:
        st.markdown("### < 364 Days")
        st.write(f"**Primary Yield:** {curr['Yield_364D']}%")
        st.write(f"**Real Yield:** {real_364:.2f}%")
        st.progress(curr['Yield_364D']/12)
        st.caption("Status: Improving Risk")

# TAB 2: FOREIGN INVESTOR MODULE
with tabs[1]:
    st.subheader("Hedged vs. Unhedged USD Analytics")
    ca, cb = st.columns(2)
    with ca:
        st.info("**Hedged Return Analysis**")
        hedged_usd_yield = curr['Yield_91D'] - hedging_cost
        arbitrage = hedged_usd_yield - us_3m
        st.metric("Net Hedged USD Yield", f"{hedged_usd_yield:.2f}%")
        st.write(f"Arbitrage vs US 3M: **{arbitrage:.2f}%**")
        if arbitrage < 0:
            st.error("❌ Negative Carry: Hedging costs exceed the LKR yield advantage.")
    with cb:
        st.info("**Unhedged FX Sensitivity**")
        depreciation = st.slider("Expected LKR Depreciation (% Annualized)", -10.0, 10.0, 2.0)
        unhedged_return = curr['Yield_91D'] - depreciation
        st.metric("Expected Unhedged Return", f"{unhedged_return:.2f}%")

# TAB 3: YIELD CURVE TRENDS
with tabs[2]:
    st.subheader("Historical Yield Movement")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_hist['Auction_Date'], y=df_hist['Yield_91D'], name='91D', line=dict(color='#58a6ff', width=3)))
    fig.add_trace(go.Scatter(x=df_hist['Auction_Date'], y=df_hist['Yield_182D'], name='182D', line=dict(color='#d299ff', width=3)))
    fig.add_trace(go.Scatter(x=df_hist['Auction_Date'], y=df_hist['Yield_364D'], name='364D', line=dict(color='#ff7b72', width=3)))
    fig.update_layout(template="plotly_dark", hovermode="x unified", margin=dict(l=0,r=0,b=0,t=40))
    st.plotly_chart(fig, use_container_width=True)

# TAB 4: THE DATA VAULT (CSV EXPORT)
with tabs[3]:
    st.subheader("Historical Auction Records & Outcomes")
    
    # Calculate Outcomes for the export
    df_export = df_hist.copy()
    df_export['Real_91D_Yield'] = df_export['Yield_91D'] - df_export['Inflation_CCPI']
    df_export['Term_Premium_364vs91'] = df_export['Yield_364D'] - df_export['Yield_91D']
    
    st.dataframe(df_export, use_container_width=True)
    
    # Export Logic
    def convert_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')
    
    csv_data = convert_to_csv(df_export)
    
    c_dl1, c_dl2 = st.columns(2)
    with c_dl1:
        st.download_button(
            label="📥 Download Historical Yields & Calculations (CSV)",
            data=csv_data,
            file_name='LKA_Sovereign_Data_Mar2026.csv',
            mime='text/csv'
        )
    with c_dl2:
        # Mini outcome summary
        outcome_df = pd.DataFrame({
            "Metric": ["Average 364D Yield", "Current Reserve Buffer", "Real Interest Rate"],
            "Value": [df_hist['Yield_364D'].mean(), reserves, real_91]
        })
        st.download_button(
            label="📥 Download Summary Report (CSV)",
            data=convert_to_csv(outcome_df),
            file_name='LKA_Outcome_Summary.csv',
            mime='text/csv'
        )

# --- 6. CASH VALUE CALCULATOR (Persistent Feature) ---
st.markdown("---")
with st.expander("🧮 Cash Value / Price Calculator"):
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        face_val = st.number_input("Face Value (LKR)", value=1000000)
        tenor_days = st.selectbox("Select Tenor", [91, 182, 364])
    with col_p2:
        buy_yield = st.number_input("Purchase Yield (%)", value=curr['Yield_91D'])
        # Price = F / (1 + (r*t/365))
        buy_price = face_val / (1 + (buy_yield/100 * tenor_days/365))
        st.metric("Market Price (LKR)", f"{buy_price:,.2f}")
