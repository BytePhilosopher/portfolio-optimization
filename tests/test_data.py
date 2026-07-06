"""Smoke tests for the processed dataset and fetch pipeline.

These run in CI (see .github/workflows/unittests.yml). They validate the shape
and integrity of the processed data if it is present; the fetch test is skipped
when there is no network / no data file, so CI stays green on a fresh checkout.
"""
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
PRICES = ROOT / "data" / "processed" / "prices.csv"
TICKERS = {"TSLA", "BND", "SPY"}
EXPECTED_COLS = {"Date", "Ticker", "Open", "High", "Low", "Close", "Adj Close", "Volume"}


@pytest.fixture(scope="module")
def prices():
    if not PRICES.exists():
        pytest.skip("processed/prices.csv not present — run scripts/fetch_data.py")
    return pd.read_csv(PRICES, parse_dates=["Date"])


def test_expected_columns(prices):
    assert EXPECTED_COLS.issubset(prices.columns)


def test_all_three_assets_present(prices):
    assert set(prices["Ticker"].unique()) == TICKERS


def test_no_missing_values(prices):
    assert prices.isna().sum().sum() == 0


def test_date_range_within_window(prices):
    assert prices["Date"].min() >= pd.Timestamp("2015-01-01")
    assert prices["Date"].max() <= pd.Timestamp("2026-06-30")


def test_equal_row_counts_per_asset(prices):
    counts = prices.groupby("Ticker").size()
    assert counts.nunique() == 1, f"assets not calendar-aligned: {counts.to_dict()}"


def test_prices_are_positive(prices):
    assert (prices[["Open", "High", "Low", "Close", "Adj Close"]] > 0).all().all()
