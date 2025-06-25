# =========================
# Imports and Setup
# =========================

import streamlit as st
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import time
import re

# --- Import custom functions ---
from optimizer import (
    get_stock_data,
    generate_covariance_matrix,
    generate_expected_returns,
    sector_mapping,
    portfolio_return,
    portfolio_volatility,
    optimize_portfolio_max_sharpe,
    optimize_portfolio_min_volatility,
    optimize_portfolio_target_return,
    optimize_portfolio_target_risk
)

# --- Import Nifty50 tickers and sectors ---
from nifty50_dict import nifty50_tickers, nifty50_sectors

# =========================
# Data Preparation
# =========================

# Build ticker-to-sector mapping
ticker_sector_dict = {}
for sector, tickers in nifty50_sectors.items():
    for ticker in tickers:
        ticker_sector_dict[ticker] = sector

# Build reverse mapping for dropdown: company name -> ticker
company_names = list(nifty50_tickers.keys())

# =========================
# Streamlit Page Config and Title
# =========================

st.set_page_config(page_title="Portfolio Optimizer", layout="wide")

st.markdown("""
<h1 style='text-align: center; font-size: 3.5em;'>
    <span style='
        background: linear-gradient(90deg, #06B6D4, #10B981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        color: transparent;
        display: inline-block;
    '>
        Portfolio Optimizer
    </span>
</h1>
""", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.5em;'>Craft your ideal investment portfolio with modern optimization techniques.</p>", unsafe_allow_html=True)
# You can modify the text shown in the tabs by changing the strings in the st.tabs() call.
# For example, you can add emojis, change the wording, or use HTML (with some limitations).

tab1, tab2 = st.tabs([
    "Optimizer", 
    "Results"
])
st.markdown("---")

# =========================
# Tab 1: Optimizer UI
# =========================

with tab1:
    # --- Section: Helper for Gradient Headings ---
    def gradient_heading_tab1(text, font_size="2em"):
        st.markdown(
            f"""
            <h3 style='
                display: inline-block;
                font-size: {font_size};
            '>
                <span style='
                background: linear-gradient(90deg, #FFA500, #FFF200);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                color: transparent;
                '>
                {text}
                </span>
            </h3>
            """, unsafe_allow_html=True
        )

    # --- Section: Intro ---
    st.markdown("""
    <div style='text-align: center; font-size: 1.2em; color: #7b8184;'>
        Use the sections below to build and optimize your portfolio.
    </div>
    """, unsafe_allow_html=True)

    # --- Section: Portfolio Holdings ---
    gradient_heading_tab1("Portfolio Holdings")
    st.markdown(
        "<div style=' color:#bbb; font-size:1.1em; margin-bottom: 0.5em;'>"
        "Add stocks to your portfolio and set their allocation constraints."
        "</div>",
        unsafe_allow_html=True
    )

    # --- State Initialization ---
    if "stocks" not in st.session_state:
        st.session_state.stocks = []

    # --- Section: Add Stock Form ---
    with st.container():
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
        with col1:
            stock_name = st.selectbox("Stock", options=company_names, key="stock_select")
            stock_ticker = nifty50_tickers[stock_name]
        with col2:
            sector_display = ticker_sector_dict.get(stock_ticker, "Unknown")
            st.text_input("Sector", sector_display, disabled=True)
        with col3:
            stock_min_weight = st.number_input("Min Weight (%)", min_value=0, max_value=100, value=0)
        with col4:
            stock_max_weight = st.number_input("Max Weight (%)", min_value=0, max_value=100, value=100)
        with col5:
            st.markdown("<div style='margin-top:27px'></div>", unsafe_allow_html=True)
            if st.button("➕ Add Stock"):
                # Prevent duplicate stocks
                if any(s['ticker'] == stock_ticker for s in st.session_state.stocks):
                    warn_key = f"warn_{stock_ticker}"
                    st.session_state[warn_key] = True
                    st.warning(f"{stock_name} is already in your portfolio.")
                    time.sleep(2)
                    st.session_state[warn_key] = False
                    st.rerun()
                else:
                    st.session_state.stocks.append({
                        'name': stock_name,
                        'ticker': stock_ticker,
                        'sector': sector_display,
                        'min': stock_min_weight,
                        'max': stock_max_weight
                    })

    # --- Section: Display & Manage Added Stocks ---
    if st.session_state.stocks:
        gradient_heading_tab1("Added Stocks")

        # --- Subsection: Clear Portfolio Button ---
        col_left, col_right = st.columns([6, 1])
        with col_left:
            st.markdown(
                "<div style=' color:#bbb; font-size:1.1em; margin-bottom: 0.5em;'>"
                "Manage your portfolio by editing or removing stocks."
                "</div>",
                unsafe_allow_html=True
            )
        with col_right:
            if st.button("Clear Entire Portfolio", type="primary"):
                st.session_state.stocks = []
                st.session_state["active_tab"] = 0
                st.rerun()

        # --- Subsection: Fix legacy entries ---
        for stock in st.session_state.stocks:
            if "name" not in stock:
                ticker = stock.get("ticker")
                stock["name"] = next((k for k, v in nifty50_tickers.items() if v == ticker), ticker)

        # --- Subsection: Save message state ---
        if "save_msg" not in st.session_state:
            st.session_state.save_msg = {}

        # --- Subsection: Stock Cards ---
        for i, stock in enumerate(st.session_state.stocks):
            company_name = stock.get('name') or next((k for k, v in nifty50_tickers.items() if v == stock.get('ticker')), stock.get('ticker'))
            with st.expander(
                f"{company_name} ({stock['ticker']}) - Sector: {stock['sector']}",
                expanded=True,
            ):
                card = st.columns([3, 2, 2, 1, 1, 1])
                with card[0]:
                    st.markdown(
                        f"<span style='color:#059669; font-weight:bold;'>Company:</span> "
                        f"<span style='color:#0ea5e9;'>{company_name} ({stock['ticker']})</span><br>"
                        f"<span style='color:#059669; font-weight:bold;'>Sector:</span> "
                        f"<span style='color:#6366f1;'>{stock['sector']}</span>",
                        unsafe_allow_html=True
                    )
                with card[1]:
                    new_min = st.number_input(
                        "Min Weight (%)", 0, 100, stock["min"], key=f"min_{i}", disabled=not st.session_state.get(f"edit_{i}", False)
                    )
                with card[2]:
                    new_max = st.number_input(
                        "Max Weight (%)", 0, 100, stock["max"], key=f"max_{i}", disabled=not st.session_state.get(f"edit_{i}", False)
                    )
                with card[3]:
                    st.markdown("<div style='margin-top:35px'></div>", unsafe_allow_html=True)
                    edit_mode = st.checkbox("Edit", key=f"edit_{i}")
                with card[4]:
                    st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
                    if st.session_state.get(f"edit_{i}", False):
                        if st.button("💾 Save", key=f"save_{i}"):
                            st.session_state.stocks[i]["min"] = new_min
                            st.session_state.stocks[i]["max"] = new_max
                            st.session_state.save_msg[i] = True
                            st.rerun()
                with card[5]:
                    st.markdown("<div style='margin-top:27px'></div>", unsafe_allow_html=True)
                    if st.button("Delete Stock", key=f"delete_{i}", disabled=st.session_state.get(f"edit_{i}", False), type="primary"):
                        st.session_state.stocks.pop(i)
                        if i in st.session_state.save_msg:
                            del st.session_state.save_msg[i]
                        st.rerun()
                # --- Save confirmation message ---
                if st.session_state.save_msg.get(i, False):
                    st.markdown(
                        f"""
                        <div style='
                            text-align:center;
                            background-color:#4eb199;
                            color:#065f46;
                            font-weight:bold;
                            margin-top:10px;
                            border-radius:8px;
                            padding:8px 0;
                            border:1px solid #10b981;
                        '>
                            Saved weights for {stock['ticker']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    st.session_state.save_msg[i] = False
                    time.sleep(2)
                    st.rerun()

    # --- Section: Sector Weight Allocation ---
    if st.session_state.stocks:
        gradient_heading_tab1("Sector Weight Allocation")
        st.markdown(
            "<div style=' color:#bbb; font-size:1.1em; margin-bottom: 0.5em;'>"
            "Define minimum and maximum weight constraints for each sector."
            "</div>",
            unsafe_allow_html=True
        )

        unique_sectors = list({s['sector'] for s in st.session_state.stocks})

        if "sector_weights" not in st.session_state:
            st.session_state.sector_weights = {}

        for sector in unique_sectors:
            if sector not in st.session_state.sector_weights:
                st.session_state.sector_weights[sector] = {'min': 0, 'max': 100}

            col1, col2, col3 = st.columns([2, 2, 2])
            with col1:
                st.text_input("Sector", sector, disabled=True, key=f"{sector}_label")
            with col2:
                st.session_state.sector_weights[sector]['min'] = st.number_input(
                    f"Min Weight (%) for {sector}", min_value=0, max_value=100,
                    value=st.session_state.sector_weights[sector]['min'], key=f"{sector}_min"
                )
            with col3:
                st.session_state.sector_weights[sector]['max'] = st.number_input(
                    f"Max Weight (%) for {sector}", min_value=0, max_value=100,
                    value=st.session_state.sector_weights[sector]['max'], key=f"{sector}_max"
                )

    # --- Section: Optimization Parameters ---
    gradient_heading_tab1("Optimization Parameters")
    st.markdown(
            "<div style=' color:#bbb; font-size:1.1em; margin-bottom: 0.5em;'>"
            "Select the historical data range and optimization model for your portfolio."
            "</div>",
            unsafe_allow_html=True
        )

    with st.container():
        col1, col2 = st.columns([4, 4])

        with col1:
            range_option = st.radio(
                "Stock Data Date Range",
                options=["6 Months", "1 Year", "2 Years", "5 Years", "Custom"],
                horizontal=True,
                index=0
            )

            today = datetime.today()
            if range_option == "6 Months":
                start_date = today - timedelta(days=180)
            elif range_option == "1 Year":
                start_date = today - timedelta(days=365)
            elif range_option == "2 Years":
                start_date = today - timedelta(days=730)
            elif range_option == "5 Years":
                start_date = today - timedelta(days=1825)
            elif range_option == "Custom":
                start_date = st.date_input("Start Date", value=today - timedelta(days=180))
                end_date = st.date_input("End Date", value=today)
            else:
                start_date = today - timedelta(days=180)

            if range_option != "Custom":
                end_date = today

            st.write(f"📅 Selected Date Range: {start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}")

        with col2:
            opt_method = st.selectbox(
                "Optimization Method",
                options=["Maximum Sharpe Ratio", "Minimum Volatility", "Target Return", "Target Risk"],
                key="opt_method_select"
            )
            st.session_state["opt_method"] = opt_method  # Always keep this updated
            if opt_method in ["Target Return", "Target Risk"]:
                target_value = st.number_input(
                    "Target Return (%)" if opt_method == "Target Return" else "Target Risk (%)",
                    min_value=0.0, max_value=100.0,
                    value=st.session_state.get("target_value", 10.0), step=0.1,
                    key="target_value"
                )
            else:
                target_value = None

    # --- Section: Optimize Portfolio Button ---
    if st.button("✅ Optimize Portfolio", use_container_width=True):
        if not st.session_state.stocks:
            st.warning("Please add at least one stock to optimize.")
        else:
            st.success("Optimization initiated with selected parameters! Continue to the 'Results' tab to view your optimized portfolio.")
            st.session_state["active_tab"] = 1  # 0 for Optimizer, 1 for Results
            st.session_state["opt_method"] = opt_method  # <-- Store the selected method here

# =========================
# Tab 2: Results UI
# =========================

with tab2:
    risk_free_rate = 0.06389 # Example risk-free rate, can be adjusted or made dynamic
    if st.session_state.get("active_tab", 0) == 1:
        # --- Section: Data Fetch and Validation ---
        if "stocks" not in st.session_state or not st.session_state.stocks:
            st.info("Please optimize your portfolio first using the 'Optimizer' tab.")
        else:
            stocks_closed_prices = get_stock_data(
                [stock['ticker'] for stock in st.session_state.stocks],
                start_date=start_date,
                end_date=end_date
            )
            if stocks_closed_prices.empty:
                st.error("No stock data available for the selected date range.")
            else:
                st.session_state.cov_matrix = generate_covariance_matrix(stocks_closed_prices)
                st.session_state.expected_returns = generate_expected_returns(stocks_closed_prices)
                sector_map, sector_indices = sector_mapping(tickers=[n['ticker'] for n in st.session_state.stocks],)
                bounds = tuple(
                    (stock['min'] / 100.0, stock['max'] / 100.0)
                    for stock in st.session_state.stocks
                )
                opt_method = st.session_state.get("opt_method", "Maximum Sharpe Ratio")

                # --- Section: Portfolio Optimization ---
                portfolio_weights = None
                if opt_method == "Maximum Sharpe Ratio":
                    portfolio_weights = optimize_portfolio_max_sharpe(
                        expected_returns=st.session_state.expected_returns,
                        cov_matrix=st.session_state.cov_matrix,
                        bounds=bounds,
                        risk_free_rate=risk_free_rate,
                        sector_constraints=st.session_state.sector_weights,
                        sector_indices=sector_indices
                    )   
                elif opt_method == "Minimum Volatility":
                    portfolio_weights = optimize_portfolio_min_volatility(
                        expected_returns=st.session_state.expected_returns,
                        cov_matrix=st.session_state.cov_matrix,
                        bounds=bounds,
                        sector_constraints=st.session_state.sector_weights,
                        sector_indices=sector_indices
                    )
                elif opt_method == "Target Return":
                    if 'target_value' not in st.session_state:
                        st.session_state.target_value = 10.0
                    target_return = st.session_state.target_value / 100.0
                    portfolio_weights = optimize_portfolio_target_return(
                        expected_returns=st.session_state.expected_returns,
                        cov_matrix=st.session_state.cov_matrix,
                        target_return=target_return,
                        bounds=bounds,
                        sector_constraints=st.session_state.sector_weights,
                        sector_indices=sector_indices
                    )
                elif opt_method == "Target Risk":
                    if 'target_value' not in st.session_state:
                        st.session_state.target_value = 10.0
                    target_risk = st.session_state.target_value / 100.0
                    portfolio_weights = optimize_portfolio_target_risk(
                        expected_returns=st.session_state.expected_returns,
                        cov_matrix=st.session_state.cov_matrix,
                        target_risk=target_risk,
                        bounds=bounds,
                        sector_constraints=st.session_state.sector_weights,
                        sector_indices=sector_indices
                    )
                else:
                    st.info("No optimization method selected.")

                # --- Section: Results Display ---
                if portfolio_weights is not None:
                    # Gradient heading helper
                    def gradient_heading(text, font_size="2em"):
                        st.markdown(
                            f"""
                            <h3 style='
                                display: inline-block;
                                font-size: {font_size};
                            '>
                                <span style='
                                background: linear-gradient(90deg, #FFA500, #FFF200);
                                -webkit-background-clip: text;
                                -webkit-text-fill-color: transparent;
                                background-clip: text;
                                color: transparent;
                                '>
                                {text}
                                </span>
                            </h3>
                            """, unsafe_allow_html=True
                        )
                        
                    def section_header(title: str, subtitle: str = "", color="#00F7FF"):
                        st.markdown(f"""
                            <div style="margin-top: 20px; margin-bottom: -10px;">
                                <h3 style="color: {color}; margin-bottom: 0px;">{title}</h3>
                                <p style="color: #bbb; font-size: 0.9em; margin-top: 4px;">{subtitle}</p>
                            </div>
                        """, unsafe_allow_html=True)
       
                    #--UI FOR RESULTS DISPLAY--   
                    st.markdown(
                        """
                        <h3 style='text-align: center; font-size: 1.2em; color: #7b8184;'>
                        View and analyze your optimized portfolio results.
                        </h3>
                        """,
                        unsafe_allow_html=True
                    )

                    
                    # Map weights back to company names and tickers
                    company_names = [s['name'] for s in st.session_state.stocks]
                    tickers = [s['ticker'] for s in st.session_state.stocks]
                    weights = portfolio_weights['Weight']

                    # Calculate portfolio performance
                    port_return = portfolio_return(weights, st.session_state.expected_returns)
                    port_vol = portfolio_volatility(weights, st.session_state.cov_matrix)
                    sharpe_ratio = (port_return - risk_free_rate) / port_vol

                    # Display metrics centered using a flexbox div, full width, light gray boxes
                    gradient_heading("Portfolio Metrics")
                    # Add a visible subtitle below the heading
                    st.markdown(
                        "<div style=' color:#bbb; font-size:1.1em; margin-bottom: 0.5em;'>"
                        "These are the key performance indicators for your optimized portfolio."
                        "</div>",
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        """
                        <style>
                        .card-metrics {{
                        background: linear-gradient(145deg, #1a1a1a, #222831);
                        border-radius: 16px;
                        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.6);
                        padding: 24px;
                        color: #ffffff;
                        transition: transform 0.2s ease;
                        text-align: center;
                        min-width: 0;
                        flex: 1 1 0;
                        margin: 0;
                        }}
                        .card-metrics:hover {{
                        transform: scale(1.02);
                        }}
                        .card-metrics-title {{
                        font-size: 1.1em;
                        font-weight: bold;
                        }}
                        .card-metrics-value {{
                        font-size: 2.1em;
                        font-weight: bold;
                        }}
                        .card-metrics-title-return {{ color: #00BFA6; }}
                        .card-metrics-value-return {{ color: #00FFB3; }}
                        .card-metrics-title-vol {{ color: #00AEEF; }}
                        .card-metrics-value-vol {{ color: #1EC9FF; }}
                        .card-metrics-title-sharpe {{ color: #FFA726; }}
                        .card-metrics-value-sharpe {{ color: #FFB74D; }}
                        </style>
                        <div style="
                        display: flex;
                        justify-content: center;
                        align-items: stretch;
                        gap: 2.5rem;
                        margin-bottom: 2rem;
                        margin-top: 1.5rem;
                        flex-wrap: wrap;
                        width: 100%;
                        ">
                        <div class="card-metrics">
                            <div class="card-metrics-title card-metrics-title-return">Expected Return</div>
                            <div class="card-metrics-value card-metrics-value-return">{:.2f}%</div>
                        </div>
                        <div class="card-metrics">
                            <div class="card-metrics-title card-metrics-title-vol">Volatility</div>
                            <div class="card-metrics-value card-metrics-value-vol">{:.2f}%</div>
                        </div>
                        <div class="card-metrics">
                            <div class="card-metrics-title card-metrics-title-sharpe">Sharpe Ratio</div>
                            <div class="card-metrics-value card-metrics-value-sharpe">{:.2f}</div>
                        </div>
                        </div>
                        """.format(port_return*100, port_vol*100, sharpe_ratio),
                        unsafe_allow_html=True
                    )

                    # Two-column layout for allocation plots
                    col_left, col_right = st.columns([1, 1], gap="large")

                    # Bar Plot: Weight Allocation by Company
                    with col_left:
                        gradient_heading("Weight Allocation by Company")
                        st.markdown(
                            "<div style='color:#bbb; font-size:1.05em; margin-bottom: 0.5em;'>"
                            "The weight of each stock in the portfolio."
                            "</div>",
                            unsafe_allow_html=True
                        )
                        # Show all companies, but display 0 for small values (< 0.5%)
                        bar_weights = np.where(weights * 100 >= 0.5, weights * 100, 0)
                        bar_fig = go.Figure(
                            data=[
                                go.Bar(
                                    x=company_names,
                                    y=bar_weights,
                                    text=[f"{w:.2f}%" if w > 0 else "0.00%" for w in bar_weights],
                                    textposition="auto",
                                    marker_color="#06D4C3",
                                    width=0.5
                                )
                            ]
                        )
                        bar_fig.update_layout(
                            xaxis_title="Company",
                            yaxis_title="Weight (%)",
                            template="plotly_dark",
                            height=400,
                            margin=dict(l=30, r=10, t=40, b=40),
                            xaxis=dict(tickangle=90)
                        )
                        st.plotly_chart(bar_fig, use_container_width=True)

                    # Pie Plot: Portfolio Distribution by Sector
                    with col_right:
                        gradient_heading("Portfolio Distribution by Sector")
                        st.markdown(
                            "<div style='color:#bbb; font-size:1.05em; margin-bottom: 0.5em;'>"
                            "A breakdown of your optimized sector allocation."
                            "</div>",
                            unsafe_allow_html=True
                        )
                        sector_labels = [ticker_sector_dict[ticker] for ticker in tickers]
                        pie_data = pd.DataFrame({"Sector": sector_labels, "Weight": weights})
                        # Show all sectors, but display 0 for small values (< 0.5%)
                        pie_data["Weight"] = np.where(pie_data["Weight"] * 100 >= 0.5, pie_data["Weight"], 0)
                        pie_fig = go.Figure(data=[
                            go.Pie(labels=pie_data.Sector, values=pie_data.Weight, hole=0.4, pull=[0.02]*len(pie_data))
                        ])
                        pie_fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10, r=10, t=40, b=40))
                        st.plotly_chart(pie_fig, use_container_width=True)
                    # Display weights table
                    gradient_heading("Weight Allocation")
                    st.markdown(
                        "<div style='color:#bbb; font-size:1.05em; margin-bottom: 0.5em;'>"
                        "Optimized weights for each stock in your portfolio."
                        "</div>",
                        unsafe_allow_html=True
                    )

                    weights_df = pd.DataFrame({
                        "Stock": company_names,
                        "Weight (%)": weights * 100
                    })

                    styled_weights_df = weights_df.style.format({"Weight (%)": "{:.2f}"}).set_properties(
                        **{
                            'background-color': "#141414",
                            'color': 'white',
                            'text-align': 'left',
                            'padding': '12px 8px',
                            'font-size': '15px'
                        }
                    ).set_table_styles([
                        {
                            'selector': 'thead th',
                            'props': [
                                ('background-color', "#1c1c1c"),
                                ('color', 'white'),
                                ('font-weight', 'bold'),
                                ('text-align', 'left'),
                                ('padding', '12px 8px')
                            ]
                        },
                        {
                            'selector': 'tbody tr',
                            'props': [
                                ('border-bottom', '1px solid #333'),
                                ('margin', '6px 0')
                            ]
                        }
                    ])

                    # Extra CSS: make it feel like the reference design
                    st.markdown("""
                        <style>
                        /* Card-style container */
                        .stDataFrame div[data-testid="stHorizontalBlock"] {
                            background-color: #1a1a1a;
                            padding: 0px;
                            border-radius: 10px;
                            box-shadow: 0 0 10px rgba(0,0,0,0.3);
                            overflow: hidden;
                        }

                        /* Table structure */
                        .stDataFrame table {
                            border-collapse: separate !important;
                            border-spacing: 0 8px !important;
                        }

                        /* Rounded corners for the first and last rows */
                        .stDataFrame tbody tr:first-child td:first-child { border-top-left-radius: 10px; }
                        .stDataFrame tbody tr:first-child td:last-child { border-top-right-radius: 10px; }
                        .stDataFrame tbody tr:last-child td:first-child { border-bottom-left-radius: 10px; }
                        .stDataFrame tbody tr:last-child td:last-child { border-bottom-right-radius: 10px; }


                        /* Pop-up effect for Plotly charts on hover */
                        .stPlotlyChart {
                            transition: transform 0.18s cubic-bezier(.4,1.5,.5,1), box-shadow 0.18s cubic-bezier(.4,1.5,.5,1);
                            will-change: transform;
                        }
                        .stPlotlyChart:hover {
                            transform: scale(1.025) translateY(-6px);
                            box-shadow: 0 8px 32px 0 rgba(6,182,212,0.18), 0 1.5px 8px 0 rgba(16,185,129,0.10);
                            z-index: 10;
                        }
                        </style>
                    """, unsafe_allow_html=True)

                    # Render it
                    st.dataframe(
                        styled_weights_df,
                        use_container_width=True,
                        hide_index=True
                    )


                    # Efficient Frontier (Optimized Curve)
                    gradient_heading("Efficient Frontier (Optimized Curve)")
                    st.markdown(
                        "<div style='color:#bbb; font-size:1.05em; margin-bottom: 0.5em;'>"
                        "Visualizing risk vs. return. Hover at any point to see its allocation."
                        "</div>",
                        unsafe_allow_html=True
                    )
                    min_ret = 0
                    max_ret = 0.60
                    target_returns = np.linspace(min_ret, max_ret, 500)
                    ef_curve_vols, ef_curve_rets, ef_curve_weights = [], [], []

                    for tr in target_returns:
                        try:
                            weights_curve = optimize_portfolio_target_return(
                                expected_returns=st.session_state.expected_returns,
                                cov_matrix=st.session_state.cov_matrix,
                                bounds=bounds,
                                sector_constraints=st.session_state.sector_weights,
                                sector_indices=sector_indices,
                                target_return=tr
                            )
                            w = weights_curve['Weight']
                            r = portfolio_return(w, st.session_state.expected_returns)
                            v = portfolio_volatility(w, st.session_state.cov_matrix)
                            ef_curve_vols.append(v)
                            ef_curve_rets.append(r)
                            ef_curve_weights.append(w)
                        except Exception:
                            continue

                    # Convert to arrays
                    ef_curve_vols = np.array(ef_curve_vols)
                    ef_curve_rets = np.array(ef_curve_rets)
                    ef_curve_weights = np.array(ef_curve_weights)

                    # Build hover text showing portfolio weights
                    hover_texts = []
                    for idx, weights in enumerate(ef_curve_weights):
                        details = "<br>".join([
                            f"{company_names[i]} ({tickers[i]}): {weights[i]*100:.2f}%"
                            for i in range(len(tickers)) if weights[i] > 0.01
                        ])
                        ret = ef_curve_rets[idx]
                        vol = ef_curve_vols[idx]
                        # Only show return and volatility in the hover, not as x/y
                        hover_texts.append(
                            f"<b>Return:</b> {ret*100:.2f}%<br><b>Volatility:</b> {vol*100:.2f}%<br>{details}"
                        )

                    # Create Plot
                    ef_fig = go.Figure()

                    # Efficient Frontier Line with hover text
                    ef_fig.add_trace(go.Scatter(
                        x=ef_curve_vols,
                        y=ef_curve_rets,
                        mode='lines+markers',
                        line=dict(color="#10B981", width=3),
                        marker=dict(size=6),
                        text=hover_texts,
                        hoverinfo="text",  # Only show custom hover text, not x/y
                        name="Efficient Frontier (Optimized)"
                    ))

                    # Highlight current portfolio
                    ef_fig.add_trace(go.Scatter(
                        x=[port_vol], y=[port_return],
                        mode='markers+text', marker=dict(size=12, color='blue', symbol="star"),
                        name="Your Portfolio", text=["You"], textposition="top center",
                        hovertemplate="<b>Return:</b> %{y:.2%}<br><b>Volatility:</b> %{x:.2%}<extra></extra>"
                    ))

                    # Highlight Max Sharpe & Min Volatility
                    ef_fig.add_trace(go.Scatter(
                        x=[ef_curve_vols[np.argmax((ef_curve_rets - risk_free_rate)/ ef_curve_vols)]],
                        y=[ef_curve_rets[np.argmax((ef_curve_rets - risk_free_rate) / ef_curve_vols)]],
                        mode='markers+text', marker=dict(size=10, color='orange'),
                        name="Max Sharpe", text=["Max Sharpe"], textposition="bottom right",
                        hovertemplate="<b>Return:</b> %{y:.2%}<br><b>Volatility:</b> %{x:.2%}<extra></extra>"
                    ))
                    ef_fig.add_trace(go.Scatter(
                        x=[ef_curve_vols[np.argmin(ef_curve_vols)]],
                        y=[ef_curve_rets[np.argmin(ef_curve_vols)]],
                        mode='markers+text', marker=dict(size=10, color='red'),
                        name="Min Volatility", text=["Min Vol"], textposition="bottom right",
                        hovertemplate="<b>Return:</b> %{y:.2%}<br><b>Volatility:</b> %{x:.2%}<extra></extra>"
                    ))

                    # Final Layout
                    ef_fig.update_layout(
                        xaxis_title="Volatility (Risk)",
                        yaxis_title="Expected Return",
                        title="Efficient Frontier",
                        template="plotly_dark",
                        height=700
                    )

                    st.plotly_chart(ef_fig, use_container_width=True)
                else:
                    st.info("Portfolio optimization did not return any results.")
    else:
        st.info("Please optimize your portfolio first using the 'Optimizer' tab.")

# =========================
# Custom CSS for UI Styling
# =========================

st.markdown("""
<style>
/* Themed accent for controls */
.stSelectbox > div[data-baseweb="select"] div {
    border-color: #06B6D4 !important;
    box-shadow: 0 2px 12px 0 rgba(6,182,212,0.13) !important;
}
.stSelectbox > div[data-baseweb="select"] {
    box-shadow: 0 2px 12px 0 rgba(6,182,212,0.13) !important;
    border-radius: 8px !important;
}
/* Button base style and shadow */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 1.08em !important;
    box-shadow: 0 2px 12px 0 rgba(6,182,212,0.13) !important;
    transition: background 0.18s, box-shadow 0.18s, color 0.18s, transform 0.18s;
}
/* Add Stock & Optimize Portfolio: gradient, animated on hover */
.stButton > button[kind="secondary"], .stButton > button[data-testid="baseButton-secondary"], .stButton > button:has(svg[data-testid="stMarkdownIcon"]) {
    background: linear-gradient(90deg, #10B981 0%, #06B6D4 100%) !important;
    color: #fff !important;
    border: none !important;
    position: relative;
    overflow: hidden;
}
.stButton > button[kind="secondary"]:hover, .stButton > button[data-testid="baseButton-secondary"]:hover, .stButton > button:has(svg[data-testid="stMarkdownIcon"]):hover {
    background: linear-gradient(90deg, #06B6D4 0%, #10B981 100%) !important;
    color: #fff !important;
    box-shadow: 0 4px 18px 0 rgba(6,182,212,0.18) !important;
    transform: scale(1.03);
}

/* Expander header style */
.streamlit-expanderHeader {
    background-color: #1e1e2e;
    color: #ffffff;
    font-weight: bold;
    padding: 12px 16px;
    border-radius: 8px 8px 0 0;
    border-bottom: 2px solid #06B6D4;
}

/* Expander content style */
.streamlit-expanderContent {
    background-color: #161621;
    color: #ffffff;
    padding: 16px;
    border-radius: 0 0 8px 8px;
}

/* Range slider color */
.stSlider > div[data-baseweb="slider"] {
    color: #06B6D4;
}

/* Radio button accent color */
.stRadio > div[data-baseweb="radio"] {
    background-color: #161621;
    border-color: #06B6D4;
}

/* Checkbox accent color */
.stCheckbox > div[data-baseweb="checkbox"] {
    background-color: #161621;
    border-color: #06B6D4;
}

/* Text input and number input focus ring */
input:focus, .stTextInput input:focus, .stNumberInput input:focus {
    border-color: #06B6D4;
    box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.2);
}

/* Disabled button style */
.stButton > button[disabled] {
    background-color: #333340;
    color: #7b8184;
    box-shadow: none;
    cursor: not-allowed;
}

/* Table header style */
thead th {
    background-color: #1c1c1c;
    color: white;
    font-weight: bold;
    text-align: left;
    padding: 12px 8px;
}

/* Table row style */
tbody tr {
    background-color: #141414;
    border-bottom: 1px solid #333;
    margin: 6px 0;
}

/* Card-style container */
.stDataFrame div[data-testid="stHorizontalBlock"] {
    background-color: #1a1a1a;
    padding: 0px;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0,0,0,0.3);
    overflow: hidden;
}

/* Table structure */
.stDataFrame table {
    border-collapse: separate !important;
    border-spacing: 0 8px !important;
}

/* Rounded corners for the first and last rows */
.stDataFrame tbody tr:first-child td:first-child { border-top-left-radius: 10px; }
.stDataFrame tbody tr:first-child td:last-child { border-top-right-radius: 10px; }
.stDataFrame tbody tr:last-child td:first-child { border-bottom-left-radius: 10px; }
.stDataFrame tbody tr:last-child td:last-child { border-bottom-right-radius: 10px; }


/* Pop-up effect for Plotly charts on hover */
.stPlotlyChart {
    transition: transform 0.18s cubic-bezier(.4,1.5,.5,1), box-shadow 0.18s cubic-bezier(.4,1.5,.5,1);
    will-change: transform;
}
.stPlotlyChart:hover {
    transform: scale(1.025) translateY(-6px);
    box-shadow: 0 8px 32px 0 rgba(6,182,212,0.18), 0 1.5px 8px 0 rgba(16,185,129,0.10);
    z-index: 10;
}
</style>
""", unsafe_allow_html=True)