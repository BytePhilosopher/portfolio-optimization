# Portfolio Optimization — Time Series Forecasting for Portfolio Management

Guide Me in Finance (GMF) Investments · **Week 9 Challenge**

Applying time-series forecasting and Modern Portfolio Theory (MPT) to build and evaluate a
data-driven portfolio across three assets with distinct risk profiles.

## Assets

| Asset | Ticker | Role | Risk profile |
|-------|--------|------|--------------|
| Tesla | `TSLA` | High-growth consumer-discretionary equity | High risk / high potential return |
| Vanguard Total Bond Market ETF | `BND` | U.S. investment-grade bonds | Low risk — stability & income |
| S&P 500 ETF | `SPY` | Broad U.S. large-cap market | Moderate risk — diversified exposure |

**Data window:** 2015-01-01 → 2026-06-30, sourced via [`yfinance`](https://pypi.org/project/yfinance/).

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. Download & cache the data
python scripts/fetch_data.py

# 2. Open the Task 1 analysis
jupyter lab notebooks/01_task1_eda.ipynb

# 3. Run the tests
pytest tests/ -v
```

## Project structure

```
portfolio-optimization/
├── .github/workflows/unittests.yml   # CI: install deps + run pytest
├── .vscode/settings.json
├── requirements.txt
├── data/
│   ├── raw/                          # per-asset OHLCV (git-ignored, regenerable)
│   └── processed/                    # prices.csv (tidy) + adj_close.csv (wide)
├── notebooks/
│   └── 01_task1_eda.ipynb            # Task 1 — preprocessing & EDA
├── scripts/
│   └── fetch_data.py                 # yfinance downloader
├── src/                              # reusable modules (later tasks)
└── tests/
    └── test_data.py                  # dataset integrity smoke tests
```

## Tasks

- **Task 1 — Preprocess & Explore** ✅ — data extraction, cleaning, EDA, stationarity (ADF),
  and foundational risk metrics (VaR, Sharpe). See [`notebooks/01_task1_eda.ipynb`](notebooks/01_task1_eda.ipynb).
- **Task 2 — Forecasting** — ARIMA/SARIMA (statsmodels/pmdarima) vs. LSTM, compared on MAE/RMSE/MAPE.
- **Task 3 — Forecast-driven analysis** — translate forecasts into forward-looking market views.
- **Task 4 — Optimization & Backtesting** — Efficient Frontier via PyPortfolioOpt, then backtest vs. benchmark.

## Task 1 — headline findings

- **Clean data:** 2,889 trading days per asset, fully calendar-aligned, zero missing values.
- **Stationarity:** price *levels* are non-stationary (ADF p ≫ 0.05); *daily returns* are stationary
  (p ≈ 0) ⇒ ARIMA needs `d = 1`.
- **Risk/return (2015–2026 sample):** TSLA has the highest return, volatility, and VaR; SPY offers a
  strong risk-adjusted return with far less risk; BND is the low-volatility stabilizer.
- Returns are **fat-tailed** (historical VaR > parametric VaR in the tails) with clear **volatility
  clustering** around the COVID crash.

> **Note on the risk-free rate:** the Sharpe Ratio assumes a 2% annual risk-free rate (`RF_ANNUAL` in
> the notebook); adjust as needed.
