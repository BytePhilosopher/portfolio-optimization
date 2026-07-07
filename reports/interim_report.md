# Interim Report — Portfolio Optimization (Week 9)

**Guide Me in Finance (GMF) Investments**
**Author:** Yostina Abera · [bet30539@gmail.com](mailto:bet30539@gmail.com)
**Scope:** Task 1 — Data preprocessing, exploratory analysis, stationarity testing, and foundational risk metrics
**Assets:** TSLA (high-growth equity) · SPY (broad market) · BND (investment-grade bonds)
**Period:** 2015-01-01 → 2026-06-30 · **Source:** Yahoo Finance (`yfinance`)
**Supporting notebook:** [`notebooks/01_task1_eda.ipynb`](../notebooks/01_task1_eda.ipynb)

---

## 1 · Data Extraction & Cleaning

**Extraction.** Daily OHLCV data plus dividend/split-adjusted close was pulled for TSLA, BND, and SPY
via `yfinance` (script: [`scripts/fetch_data.py`](../scripts/fetch_data.py)). The downloader keeps both
the raw **Close** and **Adjusted Close** (`auto_adjust=False`), retries with exponential back-off
against rate limits, and writes two artifacts:

- `data/processed/prices.csv` — tidy long format (Date, Ticker, OHLCV, Adj Close)
- `data/processed/adj_close.csv` — wide adjusted-close matrix (dates × tickers) for modeling

All return-based analysis uses **Adjusted Close**, the correct basis for total-return measurement.

**Data-quality assessment and handling.**

| Check | Finding | Action |
|-------|---------|--------|
| Coverage | **2,889 trading days** per asset (2015-01-02 → 2026-06-30) | None needed |
| Data types | Dates parsed to `datetime64`; prices `float64`; volume `int` | Enforced on load |
| Missing values | **Zero** nulls in any column | None needed |
| Calendar alignment | All three trade on the identical NYSE calendar — perfectly aligned | Verified |
| Robustness guard | — | Reindexed onto the full business-day calendar + forward-fill, so the pipeline stays correct if the data source changes |

**Summary:** the dataset was **clean on arrival** — no missing values, no type coercion required, and
full calendar alignment across the three assets. A defensive reindex/forward-fill step is retained for
reproducibility. Daily simple returns were engineered as the primary analysis unit (scale-free and far
closer to stationary than raw prices).

---

## 2 · Key EDA Visualizations & Insights

Three visualizations carry the core story (all reproduced in the notebook):

**① Growth of \$1 invested (normalized prices).** Placing all assets on a common base exposes relative
performance:

| Asset | \$1 in 2015 → June 2026 |
|-------|------------------------|
| **TSLA** | **\$28.77** |
| SPY | \$4.40 |
| BND | \$1.23 |

> *Insight:* Tesla delivered ~29× growth — an order of magnitude above the market — but, as the
> volatility analysis shows, at dramatically higher risk. SPY compounded steadily; BND barely moved,
> consistent with its role as a capital-preservation holding.

**② Daily returns time-series + distributions.** The return series and histograms make the risk
ordering visually unambiguous: TSLA's spread dwarfs SPY's, which dwarfs BND's. All three distributions
are **fat-tailed** (excess kurtosis) — extreme days occur far more often than a normal distribution
predicts, which is why we report *historical* VaR alongside the parametric estimate.

**③ Rolling 21-day volatility.** Rolling standard deviation reveals strong **volatility clustering** —
calm regimes punctuated by synchronized spikes across all assets, most dramatically the **COVID crash
(Feb–Mar 2020)**, which lifted volatility even in the normally-placid bond fund.

**Outliers / extreme days (|z| > 3σ):** TSLA 50 · SPY 42 · BND 35. The largest single-day moves map to
identifiable market events:

| Asset | Best day | Worst day |
|-------|----------|-----------|
| TSLA | +22.7% (2025-04-09) | −21.1% (2020-09-08) |
| SPY | +10.5% (2025-04-09) | −10.9% (2020-03-16) |
| BND | +4.2% (2020-03-13) | −5.4% (2020-03-12) |

> *Insight:* BND records the **fewest** z-score outliers and its "extremes" are sub-1% in absolute
> terms; TSLA's outliers are genuine double-digit swings driven by earnings/product news. The shared
> April-2025 and March-2020 dates confirm system-wide risk events rather than idiosyncratic noise.

---

## 3 · Stationarity Test Results & Interpretation

Augmented Dickey-Fuller (ADF) test — H₀: unit root (non-stationary); reject at p < 0.05.

| Series | ADF p-value (price **level**) | ADF p-value (**daily return**) |
|--------|------------------------------:|-------------------------------:|
| TSLA | 0.746 → **non-stationary** | ≈ 0 → **stationary** |
| SPY | 0.997 → **non-stationary** | ≈ 0 → **stationary** |
| BND | 0.710 → **non-stationary** | ≈ 0 → **stationary** |

**Interpretation.** Every raw price series fails to reject the unit-root null — prices trend and their
variance grows over time, behaving like a **random walk** (consistent with the **Efficient Market
Hypothesis**: past prices don't cleanly predict future ones). Differencing once — which is effectively
what a daily return is — removes the trend and yields a stable mean/variance, so returns are strongly
stationary.

**Modeling implication.** ARIMA requires a stationary input, so the price series needs **one order of
differencing (`d = 1`)** — or, equivalently, we model returns directly. This single result is what
justifies the "I" (integrated) term in ARIMA and directly informs Task 2.

---

## 4 · Volatility Analysis & Risk Metrics

**Annualized risk/return profile** (daily stats annualized: return ×252, volatility ×√252):

| Asset | Ann. return | Ann. volatility | Skew | Excess kurtosis | Sharpe (rf = 2%) |
|-------|------------:|----------------:|-----:|----------------:|-----------------:|
| **TSLA** | 45.6% | 57.2% | +0.29 | 4.5 | **0.76** |
| **SPY** | 14.5% | 17.7% | −0.31 | 14.0 | 0.71 |
| **BND** | 2.0% | 5.3% | −0.92 | 36.5 | ≈ 0.00 |

**Value at Risk (VaR)** — maximum expected single-day loss, reported as a positive % loss:

| Asset | Historical VaR 95% | Historical VaR 99% | Parametric VaR 99% |
|-------|-------------------:|-------------------:|-------------------:|
| TSLA | 5.17% | 8.99% | 8.20% |
| SPY | 1.66% | 3.17% | 2.53% |
| BND | 0.48% | 0.86% | 0.77% |

**Insights.**

- **Risk is cleanly ranked:** TSLA ≫ SPY ≫ BND on both volatility and VaR. On a bad 1-in-20 day, TSLA
  can lose ~5% versus BND's ~0.5% — roughly an order of magnitude apart.
- **Fat tails are real:** for every asset **historical VaR exceeds parametric (Gaussian) VaR** at the
  99% level, confirming the non-normality seen in the return histograms — the normal model *understates*
  extreme losses. High excess kurtosis (SPY 14, BND 36.5) quantifies this.
- **Risk-adjusted return:** over this 2015–2026 window **TSLA posts both the highest raw return and the
  highest Sharpe (~0.76)**, narrowly ahead of SPY (~0.71) — its outsized returns compensated for its
  volatility in this sample. SPY earns nearly the same risk-adjusted return with a fraction of the risk
  (the more robust core), while **BND's Sharpe is ≈ 0** (its return barely clears the 2% risk-free
  rate) — its job is stability, not return.
- **Volatility clustering** (rolling-std analysis) means variance is time-varying, not constant — a
  reason to treat any single volatility estimate with caution.

---

## 5 · Conclusion & Next Steps

The three assets are well-chosen complements: **TSLA** supplies return potential, **BND** supplies
ballast, and **SPY** supplies diversified core exposure. Their differing risk profiles and imperfect
correlations are exactly the raw material needed for portfolio optimization.

The data is clean and modeling-ready. The stationarity results (`d = 1`) directly configure the
forecasting models in **Task 2 (ARIMA/SARIMA vs. LSTM)**, and the risk metrics established here (VaR,
volatility, Sharpe) provide the baseline against which the optimized portfolio will be evaluated in
**Task 4 (Efficient Frontier & backtesting)**.

*Key caveat carried forward:* the random-walk / EMH evidence warns that **pure long-horizon price
prediction is unreliable** — so downstream decisions should lean on diversification and optimization
rather than point-price forecasts.
