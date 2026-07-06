# Notebooks

| Notebook | Task | Description |
|----------|------|-------------|
| `01_task1_eda.ipynb` | Task 1 | Data extraction, cleaning, EDA, stationarity testing, and foundational risk metrics for TSLA, BND, and SPY. |

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
