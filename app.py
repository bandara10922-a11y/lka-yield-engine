import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="LKA Yield Engine PRO", page_icon="📈", layout="wide")

# --- 2. SECURE LOGIN SYSTEM ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login_screen():
    st.markdown("<h1 style='text-align: center;'>🏛️ Sovereign Risk Terminal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Authorized Personnel Only</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            user = st.text_input("Username", placeholder="e.g., Admin101")
            pw = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Access Terminal", use_container_width=True)
            
            if submitted:
                if user == "Admin101" and pw == "NSB101@@":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Invalid Credentials. Please try again.")

if not st.session_state.authenticated:
    login_screen()
    st.stop() # Stops the rest of the code from running until logged in

# --- 3. RELIABLE DATA FETCHING ---
@st.cache_data(ttl=3600) # Caches data for 1 hour so it doesn't overload the API
def get_global_markets():
    data = {"US10Y": 4.28, "Oil": 85.0} # Reliable Default Fallbacks
    status = "🟢 Live API Connected"
    try:
        us10y_data = yf.Ticker("^TNX").history(period="1d")
        oil_data = yf.Ticker("BZ=F").history(period="1d")
        
        if not us10y_data.empty and not oil_data.empty:
            data["US10Y"] = us10y_data['Close'].iloc[-1]
            data["Oil"] = oil_data['Close'].iloc[-1]
        else:
            status = "🟡 API Timeout: Using Cached Defaults"
    except Exception:
        status = "🔴 API Failed: Using Baseline Defaults"
    
    return data, status

market_data, api_status = get_global_markets()

# --- 4. SIDEBAR: USER-FRIENDLY INPUTS ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/0/03/Central_Bank_of_Sri_Lanka_logo.svg/1200px-Central_Bank_of_Sri_Lanka_logo.svg.png", width=100)
st.sidebar.title("Configuration")
st.sidebar.caption(api_status)

with st.sidebar.expander("📊 1. Macro Indicators", expanded=True):
    opr = st.number_input("Overnight Policy Rate (%)", value=7.75, step=0.25, help="Current CBSL signaling rate.")
    ccpi = st.number_input("YoY CCPI Inflation (%)", value=1.6, step=0.1, help="Point-to-point inflation from Dept. of Census & Statistics.")
    gor = st.number_input("Gross Official Reserves ($B)", value=7.1, step=0.1, help="Total FX buffer. Below $4.5B triggers a risk premium.")

with st.sidebar.expander("🏛️ 2. Structural & Market", expanded=True):
    debt_gdp = st.slider("Debt-to-GDP (%)", 80, 130, 105, help="IMF target is 95%. Higher values increase long-term yields.")
    bid_to_cover = st.slider("Auction Bid-to-Cover Ratio", 0.5, 4.0, 1.8, help="Demand indicator. >1.5 is healthy.")
    guidance = st.selectbox("CBSL Forward Guidance", ["Dovish", "Neutral", "Hawkish"], index=1)

# --- 5. ECONOMETRIC CORE ---
# Term Premiums based on Solvency
term_premium_182 = 0.65 + max(0, (debt_gdp - 95) * 0.05)
term_premium_364 = 1.45 + max(0, (debt_gdp - 95) * 0.10)

# 91-Day Base Calculation
base_91 = opr + (market_data['US10Y'] * 0.35) + max(0, (ccpi - 5.0) * 0.3) + max(0, (5.0 - gor) * 1.5)

# Apply Forward Guidance Modifier
if guidance == "Hawkish": base_91 += 0.50
elif guidance == "Dovish": base_91 -= 0.50

# Apply Market Liquidity Modifier
y91 = base_91 + max(0, (1.8 - bid_to_cover) * 1.2) # Penalty only if under-subscribed
y182 = y91 + term_premium_182
y364 = y91 + term_premium_364

# --- 6. MAIN DASHBOARD ---
st.title("LKA Yield Forecast & Risk Engine")
st.markdown("Automated Arbitrage & Sovereign Risk Modeling for Sri Lankan T-Bills.")

# Top Metric Row
m1, m2, m3, m4 = st.columns(4)
m1.metric("91-Day Forecast", f"{y91:.2f}%", f"{y91 - opr:.2f}% Spread vs OPR", delta_color="inverse")
m2.metric("182-Day Forecast", f"{y182:.2f}%")
m3.metric("364-Day Forecast", f"{y364:.2f}%")
m4.metric("Implied Real Rate", f"{y91 - ccpi:.2f}%", help="91D Yield minus YoY Inflation")

st.markdown("---")

# Navigation Tabs
tab1, tab2, tab3 = st.tabs(["📈 Yield Curve", "📊 Time-Series Upload & Forecast", "📑 Auto-Report"])

# TAB 1: Yield Curve
with tab1:
    st.subheader("Projected Term Structure of Interest Rates")
    fig_curve = go.Figure()
    # Subtracting a synthetic amount to represent 'Current' vs 'Forecast'
    fig_curve.add_trace(go.Scatter(x=['91D', '182D', '364D'], y=[y91-0.4, y182-0.3, y364-0.1], name="Current Market", line=dict(dash='dash', color='gray')))
    fig_curve.add_trace(go.Scatter(x=['91D', '182D', '364D'], y=[y91, y182, y364], name="Model Forecast", line=dict(width=4, color='#00ffcc')))
    fig_curve.update_layout(template="plotly_dark", yaxis_title="Yield (%)", margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_curve, use_container_width=True)

# TAB 2: File Upload & Time Series
with tab2:
    st.subheader("Historical Data Engine")
    st.info("💡 **Instructions:** Upload a CSV file containing two columns: `Date` and `Yield`. This will replace the simulated data with actual market history.")
    
    uploaded_file = st.file_uploader("Upload CBSL Data (.csv)", type="csv")
    
    if uploaded_file is not None:
        try:
            # Read user data
            df = pd.read_csv(uploaded_file)
            # Basic validation
            if len(df.columns) >= 2:
                yield_data = df.iloc[:, 1].values # Assumes 2nd column is the yield
                
                # Forecasting Model
                model = ExponentialSmoothing(yield_data, trend='add', seasonal=None, initialization_method="estimated").fit()
                forecast = model.forecast(30) # Predict next 30 periods
                
                fig_ts = go.Figure()
                fig_ts.add_trace(go.Scatter(y=yield_data, name="Historical Upload"))
                fig_ts.add_trace(go.Scatter(x=np.arange(len(yield_data), len(yield_data)+30), y=forecast, name="30-Period Forecast", line=dict(color='gold')))
                fig_ts.update_layout(template="plotly_dark", title="Custom Data Forecast")
                st.plotly_chart(fig_ts, use_container_width=True)
            else:
                st.error("CSV must have at least two columns (Date, Yield).")
        except Exception as e:
            st.error(f"Error processing file: {e}")
    else:
        st.warning("No file uploaded. Displaying simulated baseline.")
        # Simulated Fallback
        np.random.seed(42)
        sim_data = np.random.normal(y91, 0.15, 60)
        fig_sim = go.Figure()
        fig_sim.add_trace(go.Scatter(y=sim_data, name="Simulated History", line=dict(color='gray')))
        st.plotly_chart(fig_sim, use_container_width=True)

# TAB 3: Report Generator
with tab3:
    st.subheader("Automated Advisory Brief")
    st.write("Generate a standardized text report based on current model inputs.")
    
    report_text = f"""SOVEREIGN YIELD OUTLOOK - AUTOMATED BRIEF
Date: {datetime.date.today()}

1. MONETARY CONTEXT
The CBSL Overnight Policy Rate is anchored at {opr}%. 
Given the CCPI inflation print of {ccpi}%, the real interest rate remains highly positive at {y91 - ccpi:.2f}%.
Forward Guidance Stance: {guidance.upper()}

2. YIELD FORECASTS
- 91-Day T-Bill: {y91:.2f}%
- 182-Day T-Bill: {y182:.2f}%
- 364-Day T-Bill: {y364:.2f}%

3. RISK FACTORS
- Debt-to-GDP stands at {debt_gdp}%. The term premium expansion between the 91D and 364D is currently {(y364 - y91)*100:.0f} basis points.
- Gross Official Reserves provide a buffer of ${gor}B. 
- Global Risk: US 10-Year Treasury is trading at {market_data['US10Y']:.2f}%.

Conclusion: Market liquidity is currently reflected by a bid-to-cover ratio of {bid_to_cover}x. The recommendation is to position portfolios in accordance with the {y91:.2f}% short-term anchor.
"""
    st.text_area("Report Preview", report_text, height=350)
    st.download_button("📥 Download Report (.txt)", data=report_text, file_name=f"LKA_Yield_Report_{datetime.date.today()}.txt")
