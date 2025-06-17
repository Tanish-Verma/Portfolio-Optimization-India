import yfinance as yf 
import numpy as np
import pandas as pd 
from scipy.optimize import minimize

def get_stock_data(tickers, start_date, end_date):
    """
    Fetches historical stock data for the given tickers and date range.
    """
    data = yf.download(tickers, start=start_date, end=end_date)['Close']
    return data
