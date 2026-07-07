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
- **Task 2 — Forecasting** ✅ — ARIMA/SARIMA (`auto_arima`) vs. a stacked LSTM for TSLA, compared on
  MAE/RMSE/MAPE with a chronological split. See [`notebooks/02_task2_forecasting.ipynb`](notebooks/02_task2_forecasting.ipynb).
- **Task 3 — Forecast future trends** ✅ — 12-month TSLA forecast with confidence intervals, trend
  analysis, opportunities/risks, and a reliability-by-horizon assessment.
  See [`notebooks/03_task3_future_forecast.ipynb`](notebooks/03_task3_future_forecast.ipynb).
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

## Task 2 — headline findings

Forecasting **TSLA Adjusted Close**, train 2015–2024 / test 2025–2026-06, one-step-ahead:

| Model | MAE | RMSE | MAPE |
|-------|-----|------|------|
| **ARIMA(0,1,0) — 1-step** | **9.04** | **11.96** | **2.53%** |
| LSTM — 1-step (window=60) | 22.75 | 27.71 | 5.99% |
| ARIMA(0,1,0) — static multi-step | 54.06 | 70.11 | 17.08% |

- `auto_arima` selects **ARIMA(0,1,0)** — a random walk; its one-step forecast is the optimal
  *persistence* prediction and **beats the LSTM outright** (< half the error) with zero parameters.
- The static multi-step forecast flattens (EMH): long-horizon price direction is not reliably forecastable.
- **Takeaway:** treat forecasts as low-confidence views; rely on diversification/optimization downstream.
