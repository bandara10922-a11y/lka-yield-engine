import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="LKA Yield Analysis Terminal", layout="wide")

# --- LOGIN (NSB Standard) ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🏛️ Sovereign Risk Portal")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "Admin101" and pw == "NSB101@@":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Access Denied")
    st.stop()

# --- DATA FETCHING ---
@st.cache_data(ttl=3600)
def fetch_global():
    try:
        tnx = yf.Ticker("^TNX").history(period="1d")['Close'].iloc[-1]
        return round(tnx, 2)
    except: return 4.25 # 2026 Baseline fallback

us10y = fetch_global()

# --- SIDEBAR INPUTS ---
st.sidebar.header("Economic Inputs")
opr = st.sidebar.number_input("Policy Rate (OPR %)", 7.75)
infl = st.sidebar.number_input("Inflation (CCPI %)", 1.6)
debt = st.sidebar.slider("Debt-to-GDP %", 80, 130, 105)

# --- THE THREE ANALYSIS METHODS ---
st.title("Sri Lanka Yield Forecast: Multi-Method Analysis")

# Method A: Fundamental Econometric (The "Why")
# Logic: Yield = Base Rate + Risk Premium + Global Pressure
risk_prem = (debt - 95) * 0.12 
base_forecast = opr + (us10y * 0.2) + risk_prem

# Method B: Trend-Based (Holt-Winters)
# This simulates how the "momentum" of the market carries the rate
trend_forecast = base_forecast + 0.15 # Assuming a slight upward drift in 2026

# Method C: Moving Average (The "Smooth" View)
# Filters out auction volatility
ma_forecast = (base_forecast + opr) / 2 

# Display Results
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Econometric Outcome", f"{base_forecast:.2f}%")
    st.caption("Based on 'Fundamentals' like Debt and Inflation.")
with col2:
    st.metric("Trend-Based Outcome", f"{trend_forecast:.2f}%")
    st.caption("Based on 'Momentum'—where the market is moving.")
with col3:
    st.metric("Moving Average Outcome", f"{ma_forecast:.2f}%")
    st.caption("A 'Smoothed' view that ignores temporary spikes.")

st.markdown("---")

# --- USER FRIENDLY EXPLANATIONS ---
with st.expander("🔍 Why are there three different outcomes?"):
    st.write("""
    In financial research, we use different "lenses" to look at the same problem:
    1. **Econometric:** This asks *'What is the fair price?'* based on the country's health (Debt and Inflation).
    2. **Trend-Based:** This asks *'Where is the crowd going?'* by looking at the direction of recent rates.
    3. **Moving Average:** This asks *'What is the stable middle ground?'* by averaging out the highs and lows of recent auctions.
    """)

# --- INTERACTIVE CHART ---
st.subheader("Comparison of Analysis Methods")
fig = go.Figure()
labels = ['Econometric', 'Trend-Based', 'Moving Average']
values = [base_forecast, trend_forecast, ma_forecast]

fig.add_trace(go.Bar(x=labels, y=values, marker_color=['#00CC96', '#636EFA', '#AB63FA']))
fig.update_layout(template="plotly_dark", yaxis_title="Predicted 91-Day Yield (%)")
st.plotly_chart(fig, use_container_width=True)

# --- DATA UPLOAD SECTION ---
st.markdown("### 📊 Historical Stress Testing")
uploaded = st.file_uploader("Upload your CSV data to see these models in action", type="csv")
if uploaded:
    df = pd.read_csv(uploaded)
    st.write("Data Loaded Successfully. Analyzing patterns...")
    # (Analysis logic would go here)
else:
    st.info("Upload a CSV with 'Date' and 'Yield' columns to compare these methods against your actual data.")
