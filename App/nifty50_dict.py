# -----------------------------------------------
# Nifty 50 Tickers and Sector Classification
# -----------------------------------------------

# Mapping of company names to their NSE ticker symbols
nifty50_tickers = {
    "Adani Enterprises": "ADANIENT.NS",
    "Adani Ports": "ADANIPORTS.NS",
    "Apollo Hospitals": "APOLLOHOSP.NS",
    "Asian Paints": "ASIANPAINT.NS",
    "Axis Bank": "AXISBANK.NS",
    "Bajaj Auto": "BAJAJ-AUTO.NS",
    "Bajaj Finance": "BAJFINANCE.NS",
    "Bajaj Finserv": "BAJAJFINSV.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "BPCL": "BPCL.NS",
    "Britannia": "BRITANNIA.NS",
    "Cipla": "CIPLA.NS",
    "Coal India": "COALINDIA.NS",
    "Divi's Labs": "DIVISLAB.NS",
    "Dr Reddy's Labs": "DRREDDY.NS",
    "Eicher Motors": "EICHERMOT.NS",
    "Grasim": "GRASIM.NS",
    "HCL Tech": "HCLTECH.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "HDFC Life": "HDFCLIFE.NS",
    "Hero MotoCorp": "HEROMOTOCO.NS",
    "Hindalco": "HINDALCO.NS",
    "HUL": "HINDUNILVR.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "IndusInd Bank": "INDUSINDBK.NS",
    "Infosys": "INFY.NS",
    "ITC": "ITC.NS",
    "JSW Steel": "JSWSTEEL.NS",
    "Kotak Mahindra Bank": "KOTAKBANK.NS",
    "Larsen & Toubro": "LT.NS",
    "LTIMindtree": "LTIM.NS",
    "Mahindra & Mahindra": "M&M.NS",
    "Maruti Suzuki": "MARUTI.NS",
    "Nestle India": "NESTLEIND.NS",
    "NTPC": "NTPC.NS",
    "ONGC": "ONGC.NS",
    "Power Grid": "POWERGRID.NS",
    "Reliance Industries": "RELIANCE.NS",
    "SBI": "SBIN.NS",
    "SBI Life": "SBILIFE.NS",
    "Sun Pharma": "SUNPHARMA.NS",
    "Tata Consumer": "TATACONSUM.NS",
    "Tata Motors": "TATAMOTORS.NS",
    "Tata Steel": "TATASTEEL.NS",
    "TCS": "TCS.NS",
    "Tech Mahindra": "TECHM.NS",
    "Titan": "TITAN.NS",
    "UltraTech Cement": "ULTRACEMCO.NS",
    "UPL": "UPL.NS",
    "Wipro": "WIPRO.NS"
}

# Mapping of sectors to lists of ticker symbols
nifty50_sectors = {
    'Energy': [
        'ADANIENT.NS', 'BPCL.NS', 'COALINDIA.NS', 'ONGC.NS', 'RELIANCE.NS'
    ],
    'Industrials': [
        'ADANIPORTS.NS', 'LT.NS'
    ],
    'Healthcare': [
        'APOLLOHOSP.NS', 'CIPLA.NS', 'DIVISLAB.NS', 'DRREDDY.NS', 'SUNPHARMA.NS'
    ],
    'Basic Materials': [
        'ASIANPAINT.NS', 'GRASIM.NS', 'HINDALCO.NS', 'JSWSTEEL.NS', 'TATASTEEL.NS', 'ULTRACEMCO.NS', 'UPL.NS'
    ],
    'Financial Services': [
        'AXISBANK.NS', 'BAJFINANCE.NS', 'BAJAJFINSV.NS', 'HDFCBANK.NS', 'HDFCLIFE.NS',
        'ICICIBANK.NS', 'INDUSINDBK.NS', 'KOTAKBANK.NS', 'SBIN.NS', 'SBILIFE.NS'
    ],
    'Consumer Cyclical': [
        'BAJAJ-AUTO.NS', 'EICHERMOT.NS', 'HEROMOTOCO.NS', 'M&M.NS', 'MARUTI.NS', 'TATAMOTORS.NS', 'TITAN.NS'
    ],
    'Communication Services': [
        'BHARTIARTL.NS'
    ],
    'Consumer Defensive': [
        'BRITANNIA.NS', 'HINDUNILVR.NS', 'ITC.NS', 'NESTLEIND.NS', 'TATACONSUM.NS'
    ],
    'Technology': [
        'HCLTECH.NS', 'INFY.NS', 'LTIM.NS', 'TCS.NS', 'TECHM.NS', 'WIPRO.NS'
    ],
    'Utilities': [
        'NTPC.NS', 'POWERGRID.NS'
    ]
}