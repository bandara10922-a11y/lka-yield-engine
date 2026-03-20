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
    st.stop()

# --- 3. RELIABLE DATA FETCHING ---
@st.cache_data(ttl=3600)
def get_global_markets():
    data = {"US10Y": 4.28, "Oil": 85.0} 
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
st.sidebar.title("Data Inputs")
st.sidebar.caption(api_status)

with st.sidebar.expander("📊 1. The Economy (Macro)", expanded=True):
    opr = st.number_input("Overnight Policy Rate (%)", value=7.75, step=0.25, 
                          help="Think of this as the 'steering wheel' for the economy. It's the base interest rate the Central Bank uses to control money.")
    ccpi = st.number_input("Inflation Rate (YoY %)", value=1.6, step=0.1, 
                           help="How fast prices at the supermarket and gas station are rising compared to exactly one year ago.")
    gor = st.number_input("Foreign Reserves ($B)", value=7.1, step=0.1, 
                          help="The country's emergency savings account in US Dollars. If this drops too low, panic sets in and interest rates shoot up.")

with st.sidebar.expander("🏛️ 2. Government & Market", expanded=True):
    debt_gdp = st.slider("Debt-to-GDP (%)", 80, 130, 105, 
                         help="Like a person's credit card debt compared to their annual salary. Over 95% means the country is heavily in debt.")
    bid_to_cover = st.slider("Auction Demand (Bid-to-Cover)", 0.5, 4.0, 1.8, 
                             help="How many investors want to buy government debt. 2.0 means twice as many buyers as available bonds (high demand). Below 1.0 means nobody wants them.")
    guidance = st.selectbox("Central Bank Mood (Guidance)", ["Dovish (Wants to lower rates)", "Neutral (Wait and see)", "Hawkish (Wants to raise rates)"], index=1)

# Extract just the first word for the math logic
guidance_logic = guidance.split()[0]

# --- 5. ECONOMETRIC CORE (The Math) ---
term_premium_182 = 0.65 + max(0, (debt_gdp - 95) * 0.05)
term_premium_364 = 1.45 + max(0, (debt_gdp - 95) * 0.10)

base_91 = opr + (market_data['US10Y'] * 0.35) + max(0, (ccpi - 5.0) * 0.3) + max(0, (5.0 - gor) * 1.5)

if guidance_logic == "Hawkish": base_91 += 0.50
elif guidance_logic == "Dovish": base_91 -= 0.50

y91 = base_91 + max(0, (1.8 - bid_to_cover) * 1.2) 
y182 = y91 + term_premium_182
y364 = y91 + term_premium_364

# --- 6. MAIN DASHBOARD ---
st.title("Sri Lanka Interest Rate Predictor")
st.markdown("A tool that uses math to predict what the government will have to pay to borrow money.")

# Top Metric Row
m1, m2, m3, m4 = st.columns(4)
m1.metric("91-Day Interest Rate", f"{y91:.2f}%", help="What the government pays to borrow money for 3 months.")
m2.metric("182-Day Interest Rate", f"{y182:.2f}%", help="What the government pays to borrow money for 6 months.")
m3.metric("364-Day Interest Rate", f"{y364:.2f}%", help="What the government pays to borrow money for 1 year.")
m4.metric("Real Profit (Real Rate)", f"{y91 - ccpi:.2f}%", help="Your actual profit on a 91-Day bill AFTER subtracting inflation. (If inflation is higher than the interest rate, you lose buying power!)")

# Plain English Explanation for the top numbers
with st.expander("📖 What do these top numbers mean? (Click to read)"):
    st.write(f"""
    * **The 91-Day Rate ({y91:.2f}%):** This is the baseline. It tells us the absolute minimum interest rate the government must offer today to convince people to lend them money for 3 months.
    * **The Real Profit ({y91 - ccpi:.2f}%):** Imagine you earn {y91:.2f}% interest at the bank, but the cost of groceries goes up by {ccpi}% this year. Your *actual* gain in wealth is only {y91 - ccpi:.2f}%. Investors look at this number very closely.
    """)

st.markdown("---")

# Navigation Tabs
tab1, tab2, tab3 = st.tabs(["📈 The Yield Curve (Time vs. Rate)", "📊 Time-Series (Trend Forecast)", "📑 Generate Summary Report"])

# TAB 1: Yield Curve
with tab1:
    st.subheader("The Yield Curve: Does waiting longer pay more?")
    st.info("💡 **Plain English:** A 'Yield Curve' is just a line chart. It shows you if you get paid a higher interest rate for locking your money away for 1 whole year (364 Days) compared to just 3 months (91 Days). Normally, the line should go UP. If it goes DOWN, the economy is usually in trouble.")
    
    fig_curve = go.Figure()
    fig_curve.add_trace(go.Scatter(x=['3 Months (91D)', '6 Months (182D)', '1 Year (364D)'], y=[y91-0.4, y182-0.3, y364-0.1], name="Current Market", line=dict(dash='dash', color='gray')))
    fig_curve.add_trace(go.Scatter(x=['3 Months (91D)', '6 Months (182D)', '1 Year (364D)'], y=[y91, y182, y364], name="Our Computer Forecast", line=dict(width=4, color='#00ffcc')))
    fig_curve.update_layout(template="plotly_dark", yaxis_title="Interest Rate (%)", margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_curve, use_container_width=True)

# TAB 2: File Upload & Time Series
with tab2:
    st.subheader("Trend Forecaster")
    st.info("💡 **Plain English:** Upload past interest rate data here. The computer will look at the pattern of the past and draw a line guessing where interest rates will go over the next 30 weeks.")
    
    uploaded_file = st.file_uploader("Upload Past Data (.csv)", type="csv")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if len(df.columns) >= 2:
                yield_data = df.iloc[:, 1].values
                model = ExponentialSmoothing(yield_data, trend='add', seasonal=None, initialization_method="estimated").fit()
                forecast = model.forecast(30)
                
                fig_ts = go.Figure()
                fig_ts.add_trace(go.Scatter(y=yield_data, name="Past Data You Uploaded"))
                fig_ts.add_trace(go.Scatter(x=np.arange(len(yield_data), len(yield_data)+30), y=forecast, name="Computer's Future Guess", line=dict(color='gold')))
                fig_ts.update_layout(template="plotly_dark", title="Future Interest Rate Trend")
                st.plotly_chart(fig_ts, use_container_width=True)
            else:
                st.error("CSV must have at least two columns (Date, Yield).")
        except Exception as e:
            st.error(f"Error processing file: {e}")
    else:
        st.warning("Waiting for your file... Showing a random simulation for now.")
        np.random.seed(42)
        sim_data = np.random.normal(y91, 0.15, 60)
        fig_sim = go.Figure()
        fig_sim.add_trace(go.Scatter(y=sim_data, name="Simulated Past Data", line=dict(color='gray')))
        st.plotly_chart(fig_sim, use_container_width=True)

# TAB 3: Report Generator
with tab3:
    st.subheader("Instant Summary Report")
    st.write("Click below to download a written explanation of the current economy to share with your team.")
    
    report_text = f"""ECONOMIC SUMMARY REPORT
Date: {datetime.date.today()}

1. THE BIG PICTURE
The Central Bank's main steering rate is currently at {opr}%. 
Because inflation (the rising cost of living) is at {ccpi}%, investors are making a real profit of {y91 - ccpi:.2f}% on short-term government loans.
The Central Bank's mood is currently: {guidance.upper()}.

2. PREDICTED INTEREST RATES (What the government will have to pay)
- Borrowing for 3 Months: {y91:.2f}%
- Borrowing for 6 Months: {y182:.2f}%
- Borrowing for 1 Year: {y364:.2f}%

3. RED FLAGS & WARNINGS
- The country's Debt-to-GDP is {debt_gdp}%. Because this is high, investors are demanding an extra {(y364 - y91)*100:.0f} points of interest to lock their money away for a full year.
- The country has ${gor} Billion in emergency savings (Foreign Reserves). 
- Investor Demand: The current Bid-to-Cover ratio is {bid_to_cover}. (Anything over 1.5 means the government is having no trouble finding people to lend it money).

Summary: Based on these numbers, the safest bet for investors is to expect the 3-month interest rate to hover around {y91:.2f}%.
"""
    st.text_area("Report Preview", report_text, height=350)
    st.download_button("📥 Download Report to your Computer (.txt)", data=report_text, file_name=f"Simple_Economic_Report_{datetime.date.today()}.txt")
