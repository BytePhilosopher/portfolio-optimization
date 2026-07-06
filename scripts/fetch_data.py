"""Fetch historical price data for the portfolio assets from Yahoo Finance.

Downloads OHLCV + Adjusted Close for TSLA, BND, and SPY over the challenge
window (2015-01-01 .. 2026-06-30) and writes both a tidy long-format CSV and a
wide adjusted-close matrix into ``data/``.

Usage
-----
    python scripts/fetch_data.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd
import yfinance as yf

TICKERS = ["TSLA", "BND", "SPY"]
START = "2015-01-01"
END = "2026-06-30"  # inclusive intent; yfinance `end` is exclusive so we bump below

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

FIELDS = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]


def download(ticker: str, retries: int = 4, pause: float = 3.0) -> pd.DataFrame:
    """Download a single ticker with simple exponential back-off on failure."""
    # yfinance treats `end` as exclusive, so add a day to include 2026-06-30.
    end_exclusive = (pd.Timestamp(END) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            df = yf.download(
                ticker,
                start=START,
                end=end_exclusive,
                auto_adjust=False,   # keep raw Close *and* Adj Close
                progress=False,
                threads=False,
            )
            if df is not None and not df.empty:
                # Flatten the (field, ticker) column MultiIndex yfinance returns.
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df = df.reindex(columns=FIELDS)
                df.index.name = "Date"
                return df
            raise ValueError("empty frame returned")
        except Exception as err:  # noqa: BLE001 - report and retry
            last_err = err
            wait = pause * attempt
            print(f"  [{ticker}] attempt {attempt}/{retries} failed: {err} "
                  f"-> retrying in {wait:.0f}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"Failed to download {ticker}: {last_err}")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    long_frames: list[pd.DataFrame] = []
    for ticker in TICKERS:
        print(f"Downloading {ticker} ...")
        df = download(ticker)

        # Persist the per-asset raw file.
        df.to_csv(RAW_DIR / f"{ticker}.csv")

        tidy = df.reset_index()
        tidy.insert(1, "Ticker", ticker)
        long_frames.append(tidy)

    combined = pd.concat(long_frames, ignore_index=True)
    combined = combined.sort_values(["Ticker", "Date"]).reset_index(drop=True)
    combined.to_csv(PROCESSED_DIR / "prices.csv", index=False)

    # Wide adjusted-close matrix (rows = dates, cols = tickers) for modeling.
    wide = combined.pivot(index="Date", columns="Ticker", values="Adj Close")
    wide = wide.sort_index()
    wide.to_csv(PROCESSED_DIR / "adj_close.csv")

    print("\nSaved:")
    print(f"  {RAW_DIR}/<TICKER>.csv           (raw per-asset OHLCV)")
    print(f"  {PROCESSED_DIR}/prices.csv       (tidy long format, {len(combined):,} rows)")
    print(f"  {PROCESSED_DIR}/adj_close.csv    (wide adj-close, {wide.shape[0]:,} dates)")
    print("\nDate coverage:")
    print(f"  {combined['Date'].min().date()} -> {combined['Date'].max().date()}")


if __name__ == "__main__":
    main()
