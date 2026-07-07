# Notebooks

| Notebook | Task | Description |
|----------|------|-------------|
| `01_task1_eda.ipynb` | Task 1 | Data extraction, cleaning, EDA, stationarity testing, and foundational risk metrics for TSLA, BND, and SPY. |
| `02_task2_forecasting.ipynb` | Task 2 | Forecasting TSLA: chronological split, ARIMA/SARIMA (`auto_arima`) and a stacked LSTM, compared on MAE/RMSE/MAPE. |
| `03_task3_future_forecast.ipynb` | Task 3 | 12-month TSLA forecast with confidence intervals (ARIMA best model + iterative LSTM), trend analysis, opportunities/risks, and reliability-by-horizon. |

## Running

From the repository root:

```bash
pip install -r requirements.txt
python scripts/fetch_data.py           # downloads raw + processed data
jupyter lab notebooks/01_task1_eda.ipynb
```

The notebook expects the processed dataset produced by `scripts/fetch_data.py`
(`data/processed/prices.csv`). If it is missing, the notebook will fetch the
data directly via `yfinance` as a fallback.
