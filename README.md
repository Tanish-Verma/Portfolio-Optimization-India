Portfolio Optimizer - README
A modern, interactive Streamlit application for building and analyzing optimized stock portfolios using Modern Portfolio Theory. Designed with an intuitive interface, dynamic charts, and sector/stock-level constraints, this tool helps investors and students visualize tradeoffs between risk and return in a hands-on way.

🚀 Live App: [Visit the App](https://tanish-verma-portfolio-optimization-india-appapp-qt5s7u.streamlit.app/)
📌 Key Features
🎯 Add stocks from Nifty 50 with sector info
⚖️ Define custom min/max weights for both stocks and sectors
🗓️ Choose historical date range (6M, 1Y, 5Y, etc.)
📈 Portfolio Optimization Methods:
  - Max Sharpe Ratio
  - Min Volatility
  - Target Return
  - Target Risk
📊 Rich Data Visualizations:
  - Stock weights (Bar Chart)
  - Sector allocation (Pie Chart)
  - Efficient Frontier (Interactive with hover allocations)
💡 Fully dark-themed UI with gradient headers and card-style metrics

📂 Project Structure
Portfolio-Optimizer/
│
├── App/                      # Core application code
│   ├── App.py                # Main Streamlit app
│   ├── nifty50_dict.py       # Mapping of Nifty stocks and sectors
│   └── optimizer.py          # Portfolio optimization functions
│
├── Data/                     # Preprocessed market data
│   ├── close_prices.csv
│   ├── daily_returns.csv
│   └── raw_data.csv
│
├── Notebooks/                # Jupyter notebooks for research and model dev
│   ├── constraints_info.ipynb
│   ├── data.ipynb
│   ├── portfolio_sin_b.ipynb
│   ├── return_analysis.ipynb
│   ├── returns.ipynb
│   └── transaction_cost_optimization.ipynb
│
├── Reports/                  # Exported reports & optimization results
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

💡 Notebooks
The Notebooks/ folder contains interactive Jupyter notebooks where the theory of Modern Portfolio Theory (MPT), transaction cost models, and return simulation techniques are explored. These were used as a foundation for the logic implemented in the main application.
🛠️ Setup Instructions
🔧 Step 1: Clone the Repository
git clone https://github.com/your-username/Portfolio-Optimizer.git
cd Portfolio-Optimizer
📦 Step 2: Create and Activate a Virtual Environment
Windows:
python -m venv venv
venv\Scripts\activate

macOS/Linux:
python3 -m venv venv
source venv/bin/activate
📄 Step 3: Install Requirements
pip install -r requirements.txt
▶️ Run the App
streamlit run App/App.py
Then open your browser and go to: http://localhost:8501
🧮 Optimization Models
All optimization strategies consider stock-level min/max constraints, sector-level min/max constraints, and target return or volatility (if selected). The app uses efficient algorithms and scipy/cvxpy-based solvers.
📊 Visuals Included
📦 Portfolio Weights (Bar Chart)
🧭 Sector Allocation (Donut Pie)
⚙️ Efficient Frontier with clickable/hoverable weight breakdowns
📈 Metrics Cards: Return, Volatility, Sharpe Ratio

📜 License
This project is licensed under the MIT License.
🙌 Acknowledgments
Built with ❤️ using Streamlit, Plotly, and NumPy
Based on Markowitz’s Modern Portfolio Theory
Data fetched via Yahoo Finance using yfinance

🔗 Connect & Contribute
Feel free to fork the project, submit issues, or open a pull request.
