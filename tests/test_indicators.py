"""
Unit tests for Technical Indicators:
SMA, EMA, RSI, MACD, Bollinger Bands, ATR.
"""

import pytest
import pandas as pd
import numpy as np
from src.analytics.indicators import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_atr
)


@pytest.fixture
def sample_price_series():
    """Deterministic synthetic price series of 100 observations."""
    np.random.seed(42)
    # Random walk around 100.0
    returns = np.random.normal(0.0005, 0.015, 100)
    prices = 100.0 * np.exp(np.cumsum(returns))
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    return pd.Series(prices, index=dates)


def test_sma_calculation(sample_price_series):
    """Verify Simple Moving Average formula."""
    sma_20 = calculate_sma(sample_price_series, window=20)
    
    assert len(sma_20) == len(sample_price_series)
    assert pd.isna(sma_20.iloc[18])
    assert not pd.isna(sma_20.iloc[19])
    # Compare with manual mean of first 20 bars
    expected_val = sample_price_series.iloc[0:20].mean()
    assert pytest.approx(sma_20.iloc[19], rel=1e-5) == expected_val


def test_ema_calculation(sample_price_series):
    """Verify Exponential Moving Average properties."""
    ema_20 = calculate_ema(sample_price_series, span=20)
    assert len(ema_20) == len(sample_price_series)
    assert not pd.isna(ema_20.iloc[0])
    # First point equals initial price in adjust=False
    assert pytest.approx(ema_20.iloc[0], rel=1e-5) == sample_price_series.iloc[0]


def test_rsi_bounds_and_extremes():
    """Verify RSI remains bounded in [0, 100] and handles extreme trends."""
    dates = pd.date_range("2024-01-01", periods=50, freq="D")
    
    # 1. Monotonically increasing series -> RSI should approach 100
    inc_prices = pd.Series([100.0 + i * 2.0 for i in range(50)], index=dates)
    rsi_inc = calculate_rsi(inc_prices, period=14)
    valid_inc = rsi_inc.dropna()
    assert (valid_inc >= 99.0).all()
    assert (valid_inc <= 100.0).all()

    # 2. Monotonically decreasing series -> RSI should approach 0
    dec_prices = pd.Series([200.0 - i * 2.0 for i in range(50)], index=dates)
    rsi_dec = calculate_rsi(dec_prices, period=14)
    valid_dec = rsi_dec.dropna()
    assert (valid_dec <= 1.0).all()
    assert (valid_dec >= 0.0).all()


def test_macd_structure(sample_price_series):
    """Verify MACD returns proper components and histogram relationship."""
    macd_df = calculate_macd(sample_price_series, fast=12, slow=26, signal=9)
    assert "MACD" in macd_df.columns
    assert "Signal" in macd_df.columns
    assert "Histogram" in macd_df.columns

    # Check relation: Histogram == MACD - Signal
    valid = macd_df.dropna()
    diff = valid["MACD"] - valid["Signal"]
    assert np.allclose(valid["Histogram"], diff, atol=1e-6)


def test_bollinger_bands(sample_price_series):
    """Verify Bollinger Bands ordering: Upper >= Middle >= Lower."""
    bb = calculate_bollinger_bands(sample_price_series, window=20, num_std=2.0)
    valid = bb.dropna()
    assert (valid["Upper"] >= valid["Middle"]).all()
    assert (valid["Middle"] >= valid["Lower"]).all()
