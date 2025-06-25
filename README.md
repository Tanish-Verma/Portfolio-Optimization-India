# Portfolio Optimizer

A modern, interactive Streamlit application for building and analyzing optimized stock portfolios using Modern Portfolio Theory (MPT). Designed with an intuitive interface, dynamic charts, and robust constraint handling, this tool empowers investors and students to visualize risk-return tradeoffs in a hands-on way.

---

## 🚀 Live Demo

[**Launch the App**](https://tanish-verma-portfolio-optimization-india-appapp-qt5s7u.streamlit.app/)

---

## 📌 Features

- **Nifty 50 Universe**: Add stocks from the Nifty 50, complete with sector information.
- **Flexible Constraints**: Define custom min/max weights for both individual stocks and sectors.
- **Custom Date Range**: Select historical periods (6M, 1Y, 5Y, etc.) for analysis.
- **Multiple Optimization Methods**:
  - Max Sharpe Ratio
  - Min Volatility
  - Target Return
  - Target Risk
- **Rich Visualizations**:
  - Stock Weights (Bar Chart)
  - Sector Allocation (Pie Chart)
  - Efficient Frontier (Interactive with hover/click for allocations)
- **Modern UI**: Fully dark-themed with gradient headers and card-style metrics.

---

## 📂 Project Structure

```
Portfolio-Optimizer/
│
├── App/                      # Core application code
│   ├── App.py                # Main Streamlit app
│   ├── nifty50_dict.py       # Nifty stocks & sector mapping
│   └── optimizer.py          # Portfolio optimization logic
│
├── Data/                     # Preprocessed market data
│   ├── close_prices.csv
│   ├── daily_returns.csv
│   └── raw_data.csv
│
├── Notebooks/                # Jupyter notebooks for research & prototyping
│   ├── constraints_info.ipynb
│   ├── data.ipynb
│   ├── portfolio_sin_b.ipynb
│   ├── return_analysis.ipynb
│   ├── returns.ipynb
│   └── transaction_cost_optimization.ipynb
│
├── Reports/                  # Exported reports & results
│   └── Charts/
│       ├── all_optimized_weights_comparison.csv
│       ├── cov_matrix.csv
│       ├── expected_returns.csv
│       ├── optimal_portfolios.csv
│       ├── portfolio_comparison.csv
│       ├── portfolio_simulations.csv
│       ├── Sector_constrained_portfolio.csv
│       ├── transaction_cost_tradeoff.csv
│       ├── weight_optimized_portfolio.csv
│       └── weights_for_different_alpha.csv
│
├── requirements.txt          # Dependencies
├── .gitignore
└── README.md
```

---

## 🛠️ Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Portfolio-Optimizer.git
cd Portfolio-Optimizer
```

### 2. Create & Activate a Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
streamlit run App/App.py
```
Then open your browser at [http://localhost:8501](http://localhost:8501).

---

## 🧮 Optimization Models

All strategies support:
- Stock-level min/max constraints
- Sector-level min/max constraints
- Target return or volatility (if selected)

Efficient algorithms and `scipy`/`cvxpy`-based solvers are used for optimization.

---

## 📊 Visualizations

- **Portfolio Weights**: Bar chart
- **Sector Allocation**: Donut pie chart
- **Efficient Frontier**: Interactive with allocation breakdowns
- **Metrics Cards**: Return, Volatility, Sharpe Ratio

---

## 📒 Notebooks

The `Notebooks/` folder contains Jupyter notebooks exploring MPT theory, transaction cost models, and return simulation techniques, which underpin the app's logic.

---

## 📜 License

This project is licensed under the MIT License.

---

## 🙌 Acknowledgments

- Built with ❤️ using Streamlit, Plotly, and NumPy
- Based on Markowitz’s Modern Portfolio Theory
- Data via Yahoo Finance (`yfinance`)

---

## 🔗 Connect & Contribute

Feel free to fork, submit issues, or open a pull request!
