import yfinance as yf 
import numpy as np
import pandas as pd 
from scipy.optimize import minimize
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sb
import plotly.graph_objs as go
import plotly.io as pio
from nifty50_dict import nifty50_sectors  # add this import

# Stock Data Fetching and Processing Functions
def get_stock_data(tickers, start_date, end_date):
    """
    Fetch historical closing price data for the given tickers and date range.

    Args:
        tickers (list): List of ticker symbols.
        start_date (str or datetime): Start date for data.
        end_date (str or datetime): End date for data.

    Returns:
        pd.DataFrame: DataFrame of closing prices (columns: tickers, index: dates).
    """
    data = yf.download(tickers, start=start_date, end=end_date)['Close']
    return data

def sector_mapping(tickers):
    """
    Map stock tickers to their respective sectors using yfinance info.

    Args:
        tickers (list): List of ticker symbols.

    Returns:
        tuple: (sector_map, sector_indices)
            sector_map (dict): ticker -> sector
            sector_indices (dict): sector -> list of indices in tickers
    """
    sector_map = {
        ticker: yf.Ticker(ticker).info.get('sector') for ticker in tickers
    }
    
    sector_indices = defaultdict(list)

    for i, stock in enumerate(sector_map):
        sector = sector_map[stock]
        sector_indices[sector].append(i)

    return sector_map, sector_indices

def get_sector_to_tickers(tickers):
    """
    Returns a dictionary mapping sector names to lists of tickers in that sector.
    Uses static mapping from nifty50_dict.py for speed.

    Args:
        tickers (list): List of ticker symbols.

    Returns:
        dict: sector -> list of tickers in that sector
    """
    sector_to_tickers = {}
    for sector, sector_tickers in nifty50_sectors.items():
        filtered = [t for t in sector_tickers if t in tickers]
        if filtered:
            sector_to_tickers[sector] = filtered
    # Add tickers not found in any sector as 'Unknown'
    all_sector_tickers = set()
    for sector_tickers in nifty50_sectors.values():
        all_sector_tickers.update(sector_tickers)
    unknowns = [t for t in tickers if t not in all_sector_tickers]
    if unknowns:
        sector_to_tickers['Unknown'] = unknowns
    return sector_to_tickers

def generate_expected_returns(closed_prices):
    """
    Calculate annualized expected returns from daily closing prices.

    Args:
        closed_prices (pd.DataFrame): DataFrame of closing prices.

    Returns:
        pd.Series: Expected annualized returns for each ticker.
    """
    returns = closed_prices.pct_change().dropna()
    expected_returns = returns.mean()
    expected_returns = expected_returns * 252 
    return expected_returns

def generate_covariance_matrix(closed_prices):
    """
    Calculate annualized covariance matrix from daily closing prices.

    Args:
        closed_prices (pd.DataFrame): DataFrame of closing prices.

    Returns:
        pd.DataFrame: Annualized covariance matrix.
    """
    returns = closed_prices.pct_change().dropna()
    covariance_matrix = returns.cov() * 252 
    return covariance_matrix

def portfolio_return(weights, expected_returns):
    """
    Calculate portfolio expected return.

    Args:
        weights (np.ndarray): Portfolio weights.
        expected_returns (pd.Series or np.ndarray): Expected returns.

    Returns:
        float: Portfolio expected return.
    """
    return np.dot(weights, expected_returns)

def portfolio_volatility(weights, cov_matrix):
    """
    Calculate portfolio volatility (standard deviation).

    Args:
        weights (np.ndarray): Portfolio weights.
        cov_matrix (pd.DataFrame or np.ndarray): Covariance matrix.

    Returns:
        float: Portfolio volatility.
    """
    return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

def neg_sharpe_ratio(weights, expected_returns, cov_matrix, risk_free_rate):
    """
    Negative Sharpe ratio (for minimization).

    Args:
        weights (np.ndarray): Portfolio weights.
        expected_returns (pd.Series or np.ndarray): Expected returns.
        cov_matrix (pd.DataFrame or np.ndarray): Covariance matrix.
        risk_free_rate (float): Risk-free rate.

    Returns:
        float: Negative Sharpe ratio.
    """
    port_return = portfolio_return(weights, expected_returns)
    port_vol = portfolio_volatility(weights, cov_matrix)
    return -(port_return - risk_free_rate) / port_vol

def generate_Sector_constraints(sector_constraints, sector_indices):
    """
    Generate sector weight constraints for optimizer.

    Args:
        sector_constraints (dict): sector -> {'min': float, 'max': float}
        sector_indices (dict): sector -> list of indices

    Returns:
        list: List of constraint dicts for optimizer.
    """
    sector_cons = []
    if sector_constraints and sector_indices:
        for sector, indices in sector_indices.items():
            if sector in sector_constraints:
                min_inv = sector_constraints[sector].get("min", 0) / 100.0
                max_inv = sector_constraints[sector].get("max", 100) / 100.0
                sector_cons.append({
                    'type': 'ineq',
                    'fun': lambda x, idx=indices, min_inv=min_inv: np.sum(x[idx]) - min_inv
                })
                sector_cons.append({
                    'type': 'ineq',
                    'fun': lambda x, idx=indices, max_inv=max_inv: max_inv - np.sum(x[idx])
                })
    return sector_cons

def transaction_penalty(weights, previous_weights, penalty_rate, alpha):
    """
    Calculates the transaction penalty based on the change in weights.

    Args:
        weights (np.ndarray): New portfolio weights.
        previous_weights (np.ndarray): Previous portfolio weights.
        penalty_rate (float): Penalty rate per unit change.
        alpha (float): Scaling factor for penalty.

    Returns:
        float: Transaction penalty value.
    """
    transaction_penalty = np.sum(penalty_rate * np.abs(weights - previous_weights))
    return transaction_penalty * alpha

def transform_weights_to_df(weights, tickers):
    """
    Transforms the optimized weights into a DataFrame with tickers as index and weights as a column.

    Args:
        weights (np.ndarray): Optimized weights.
        tickers (list): List of ticker symbols.

    Returns:
        pd.DataFrame: DataFrame with 'Weight' column and tickers as index.
    """
    return pd.DataFrame({'Weight': weights}, index=tickers)

# Portfolio Optimization Functions
def optimize_portfolio_max_sharpe(expected_returns, cov_matrix, bounds, risk_free_rate=0.0, sector_constraints=None, sector_indices=None):
    """
    Optimize portfolio for maximum Sharpe ratio.

    Args:
        expected_returns (pd.Series): Expected returns.
        cov_matrix (pd.DataFrame): Covariance matrix.
        bounds (tuple): Bounds for weights.
        risk_free_rate (float): Risk-free rate.
        sector_constraints (dict): Sector constraints.
        sector_indices (dict): Sector indices.

    Returns:
        pd.DataFrame: Optimized weights DataFrame.
    """
    constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
    sector_cons = generate_Sector_constraints(sector_constraints, sector_indices)
    all_constraints = [constraints] + sector_cons
    initial_weights = np.ones(len(expected_returns)) / len(expected_returns)
    result = minimize(
        neg_sharpe_ratio,
        initial_weights,
        args=(expected_returns, cov_matrix, risk_free_rate),
        method='SLSQP',
        bounds=bounds,
        constraints=all_constraints
    )
    return transform_weights_to_df(result.x, expected_returns.index.tolist())


def optimize_portfolio_min_volatility(expected_returns, cov_matrix, bounds, sector_constraints=None, sector_indices=None):
    """
    Optimize portfolio for minimum volatility.

    Args:
        expected_returns (pd.Series): Expected returns.
        cov_matrix (pd.DataFrame): Covariance matrix.
        bounds (tuple): Bounds for weights.
        sector_constraints (dict): Sector constraints.
        sector_indices (dict): Sector indices.

    Returns:
        pd.DataFrame: Optimized weights DataFrame.
    """
    constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
    sector_cons = generate_Sector_constraints(sector_constraints, sector_indices)
    all_constraints = [constraints] + sector_cons
    initial_weights = np.ones(len(expected_returns)) / len(expected_returns)
    result = minimize(
        portfolio_volatility,
        initial_weights,
        args=(cov_matrix,),
        method='SLSQP',
        bounds=bounds,
        constraints=all_constraints
    )
    return transform_weights_to_df(result.x, expected_returns.index.tolist())


def optimize_portfolio_target_return(expected_returns, cov_matrix, target_return, bounds, sector_constraints=None, sector_indices=None):
    """
    Optimize portfolio for minimum volatility given a target return.

    Args:
        expected_returns (pd.Series): Expected returns.
        cov_matrix (pd.DataFrame): Covariance matrix.
        target_return (float): Target portfolio return.
        bounds (tuple): Bounds for weights.
        sector_constraints (dict): Sector constraints.
        sector_indices (dict): Sector indices.

    Returns:
        pd.DataFrame: Optimized weights DataFrame.
    """
    constraints = [
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}, 
        {'type': 'eq', 'fun': lambda x: portfolio_return(x, expected_returns) - target_return}
    ]
    sector_cons = generate_Sector_constraints(sector_constraints, sector_indices)
    all_constraints = constraints + sector_cons
    initial_weights= np.ones(len(expected_returns)) / len(expected_returns)
    result = minimize(
        portfolio_volatility,
        initial_weights,
        args=(cov_matrix,),
        method='SLSQP',
        bounds=bounds,
        constraints=all_constraints
    )
    return transform_weights_to_df(result.x, expected_returns.index.tolist())


def optimize_portfolio_target_risk(expected_returns, cov_matrix, target_risk, bounds, sector_constraints=None, sector_indices=None):
    """
    Optimize portfolio for maximum return given a target risk (volatility).

    Args:
        expected_returns (pd.Series): Expected returns.
        cov_matrix (pd.DataFrame): Covariance matrix.
        target_risk (float): Target portfolio volatility.
        bounds (tuple): Bounds for weights.
        sector_constraints (dict): Sector constraints.
        sector_indices (dict): Sector indices.

    Returns:
        pd.DataFrame: Optimized weights DataFrame.
    """
    constraints = [
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}, 
        {'type': 'eq', 'fun': lambda x: portfolio_volatility(x, cov_matrix) - target_risk}
    ]
    sector_cons = generate_Sector_constraints(sector_constraints, sector_indices)
    all_constraints = constraints + sector_cons
    initial_weights = np.ones(len(expected_returns)) / len(expected_returns)
    result = minimize(
        lambda w, mu: -portfolio_return(w, mu),
        initial_weights,
        args=(expected_returns,),
        method='SLSQP',
        bounds=bounds,
        constraints=all_constraints
    )
    return transform_weights_to_df(result.x, expected_returns.index.tolist())

# #Transaction Penalty Optimizers

# def optimize_portfolio_max_sharpe_transaction_penalty(expected_returns, cov_matrix, previous_weights, risk_free_rate=0.0, lower_bound=0.0, upper_bound=1.0, sector_constraints=None, sector_indices=None, penalty_rate=0.01, alpha=1.0, custom_bounds=None):
#     initial_weights, bounds, constraints = create_optimization_parameters(expected_returns, lower_bound, upper_bound, custom_bounds)
#     sector_cons = generate_Sector_constraints(sector_constraints, sector_indices)
#     all_constraints = [constraints] + sector_cons
#     result = minimize(
#         lambda x: neg_sharpe_ratio(x, expected_returns, cov_matrix, risk_free_rate) + transaction_penalty(x, previous_weights, penalty_rate, alpha),
#         initial_weights,
#         method='SLSQP',
#         bounds=bounds,
#         constraints=all_constraints
#     )
#     return transform_weights_to_dict(result.x, expected_returns.index.tolist())


# def optimize_portfolio_min_volatility_transaction_penalty(expected_returns, cov_matrix, previous_weights, lower_bound=0.0, upper_bound=1.0, sector_constraints=None, sector_indices=None, penalty_rate=0.01, alpha=1.0, custom_bounds=None):
#     initial_weights, bounds, constraints = create_optimization_parameters(expected_returns, lower_bound, upper_bound, custom_bounds)
#     sector_cons = generate_Sector_constraints(sector_constraints, sector_indices)
#     all_constraints = [constraints] + sector_cons
#     result = minimize(
#         lambda x: portfolio_volatility(x, cov_matrix) + transaction_penalty(x, previous_weights, penalty_rate, alpha),
#         initial_weights,
#         method='SLSQP',
#         bounds=bounds,
#         constraints=all_constraints
#     )
#     return transform_weights_to_dict(result.x, expected_returns.index.tolist())


# def optimize_portfolio_target_return_transaction_penalty(expected_returns, cov_matrix, target_return, previous_weights, lower_bound=0.0, upper_bound=1.0, sector_constraints=None, sector_indices=None, penalty_rate=0.01, alpha=1.0, custom_bounds=None):
#     initial_weights, bounds, constraints = initialize_target_return_parameters(expected_returns, target_return, lower_bound, upper_bound, custom_bounds)
#     sector_cons = generate_Sector_constraints(sector_constraints, sector_indices)
#     all_constraints = constraints + sector_cons
#     result = minimize(
#         lambda x: portfolio_volatility(x, cov_matrix) + transaction_penalty(x, previous_weights, penalty_rate, alpha),
#         initial_weights,
#         method='SLSQP',
#         bounds=bounds,
#         constraints=all_constraints
#     )
#     return transform_weights_to_dict(result.x, expected_returns.index.tolist())


# def optimize_portfolio_target_risk_transaction_penalty(expected_returns, cov_matrix, target_risk, previous_weights, lower_bound=0.0, upper_bound=1.0, sector_constraints=None, sector_indices=None, penalty_rate=0.01, alpha=1.0, custom_bounds=None):    
#     initial_weights, bounds, constraints = initialize_target_risk_parameters(expected_returns, cov_matrix, target_risk, lower_bound, upper_bound, custom_bounds)
#     sector_cons = generate_Sector_constraints(sector_constraints, sector_indices)
#     all_constraints = constraints + sector_cons
#     result = minimize(
#         lambda x: -portfolio_return(x, expected_returns) + transaction_penalty(x, previous_weights, penalty_rate, alpha),
#         initial_weights,
#         method='SLSQP',
#         bounds=bounds,
#         constraints=all_constraints
#     )
#     return transform_weights_to_dict(result.x, expected_returns.index.tolist())

# #plotting functions

# def optimize_portfolio_min_volatility_transaction_penalty(expected_returns, cov_matrix, previous_weights, lower_bound=0.0, upper_bound=1.0, sector_constraints=None, sector_indices=None, penalty_rate=0.01, alpha=1.0, custom_bounds=None):
#     initial_weights, bounds, constraints = create_optimization_parameters(expected_returns, lower_bound, upper_bound, custom_bounds)
#     sector_cons = generate_Sector_constraints(sector_constraints, sector_indices)
#     all_constraints = [constraints] + sector_cons
#     result = minimize(
#         lambda x: portfolio_volatility(x, cov_matrix) + transaction_penalty(x, previous_weights, penalty_rate, alpha),
#         initial_weights,
#         method='SLSQP',
#         bounds=bounds,
#         constraints=all_constraints
#     )
#     return transform_weights_to_dict(result.x, expected_returns.index.tolist())


# def optimize_portfolio_target_return_transaction_penalty(expected_returns, cov_matrix, target_return, previous_weights, lower_bound=0.0, upper_bound=1.0, sector_constraints=None, sector_indices=None, penalty_rate=0.01, alpha=1.0, custom_bounds=None):
#     initial_weights, bounds, constraints = initialize_target_return_parameters(expected_returns, target_return, lower_bound, upper_bound, custom_bounds)
#     sector_cons = generate_Sector_constraints(sector_constraints, sector_indices)
#     all_constraints = constraints + sector_cons
#     result = minimize(
#         lambda x: portfolio_volatility(x, cov_matrix) + transaction_penalty(x, previous_weights, penalty_rate, alpha),
#         initial_weights,
#         method='SLSQP',
#         bounds=bounds,
#         constraints=all_constraints
#     )
#     return transform_weights_to_dict(result.x, expected_returns.index.tolist())


# def optimize_portfolio_target_risk_transaction_penalty(expected_returns, cov_matrix, target_risk, previous_weights, lower_bound=0.0, upper_bound=1.0, sector_constraints=None, sector_indices=None, penalty_rate=0.01, alpha=1.0, custom_bounds=None):    
#     initial_weights, bounds, constraints = initialize_target_risk_parameters(expected_returns, cov_matrix, target_risk, lower_bound, upper_bound, custom_bounds)
#     sector_cons = generate_Sector_constraints(sector_constraints, sector_indices)
#     all_constraints = constraints + sector_cons
#     result = minimize(
#         lambda x: -portfolio_return(x, expected_returns) + transaction_penalty(x, previous_weights, penalty_rate, alpha),
#         initial_weights,
#         method='SLSQP',
#         bounds=bounds,
#         constraints=all_constraints
#     )
#     return transform_weights_to_dict(result.x, expected_returns.index.tolist())

# #plotting functions


