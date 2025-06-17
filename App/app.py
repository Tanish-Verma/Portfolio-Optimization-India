import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import seaborn as sb
from scipy.optimize import minimize
from nifty50_dict import nifty50_tickers
from optimizer import get_stock_data
from datetime import datetime, timedelta
st.set_page_config(page_title="Indian Portfolio Optimizer", layout="wide")
st.markdown("<h1 style='text-align: center;'>Indian Stock Portfolio Optimization Tool</h1>", unsafe_allow_html=True)


selected_names = st.sidebar.multiselect(
    "📈 Choose Nifty 50 Stocks for Portfolio Optimization",
    options=list(nifty50_tickers.keys()),
    default=[],
    help="Select the stocks you want to include in your portfolio. You can choose multiple stocks."
)
# if not selected_names:
#     st.sidebar.warning("Please select at least one stock to proceed with the optimization.")
#     st.stop()
selected_tickers = [nifty50_tickers[name] for name in selected_names]


st.sidebar.header("🕒 Select Timeframe for Historical Data")

# Quick timeframe options
quick_options = {
    "6 Months": timedelta(days=182),
    "1 Year": timedelta(days=365),
    "2 Years": timedelta(days=730),
    "5 Years": timedelta(days=1825)
}

# Quick select
quick_choice = st.sidebar.selectbox(
    "Quick Timeframe",
    options=["Custom"] + list(quick_options.keys()),
    index=1,
    help="Select a predefined timeframe for historical data. You can also choose 'Custom' to specify your own dates."
)

if quick_choice != "Custom":
    end_date = datetime.today()
    start_date = end_date - quick_options[quick_choice]
else:
    end_date = st.sidebar.date_input("End Date", datetime.today())
    start_date = st.sidebar.date_input("Start Date", end_date - timedelta(days=365))

    if start_date > end_date:
        st.sidebar.error("Start date must be before end date.")

