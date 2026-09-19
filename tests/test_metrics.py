"""
Unit tests for Financial Performance Metrics:
Returns, CAGR, Volatility, Sharpe Ratio, Sortino Ratio, Drawdown.
"""

import pytest
import pandas as pd
import numpy as np
from src.analytics.metrics import (
    calculate_daily_returns,
    calculate_total_return,
    calculate_cagr,
    calculate_annualized_volatility,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_max_drawdown,
    calculate_drawdown_series
)


def test_total_return_and_cagr():
    """Verify total return and annualized CAGR math."""
    # 252 days with a 21% gain: 100 to 121
    dates = pd.date_range("2024-01-01", periods=253, freq="D")
    prices = pd.Series(np.linspace(100.0, 121.0, 253), index=dates)

    tot = calculate_total_return(prices)
    assert pytest.approx(tot, rel=1e-4) == 0.21

    # Over exactly 252 periods (1 year with periods_per_year=252), CAGR == total return
    cagr = calculate_cagr(prices, periods_per_year=252)
    assert pytest.approx(cagr, rel=1e-3) == 0.21


def test_annualized_volatility():
    """Verify standard deviation annualization scaling with sqrt(252)."""
    np.random.seed(123)
    daily_returns = pd.Series(np.random.normal(0.0, 0.01, 500))
    ann_vol = calculate_annualized_volatility(daily_returns, periods_per_year=252)

    sample_std = daily_returns.std(ddof=1)
    expected_vol = sample_std * np.sqrt(252)
    assert pytest.approx(ann_vol, rel=1e-5) == expected_vol


def test_sharpe_ratio_zero_volatility_safety():
    """Zero volatility series must safely return 0.0 without division by zero."""
    flat_returns = pd.Series([0.001] * 100)  # Constant return -> std == 0
    sharpe = calculate_sharpe_ratio(flat_returns, risk_free_rate=0.04)
    assert sharpe == 0.0


def test_max_drawdown_calculation():
    """Verify peak-to-trough drawdown calculation."""
    # Price rises from 100 to 200, drops to 100, then rises to 150
    # Peak = 200, Trough = 100 -> MDD = (100 - 200) / 200 = -0.50 (-50%)
    prices = pd.Series([100.0, 150.0, 200.0, 150.0, 100.0, 130.0, 150.0])
    mdd = calculate_max_drawdown(prices)
    assert pytest.approx(mdd, rel=1e-4) == -0.50

    # Monotonically increasing series -> MDD == 0.0
    up_prices = pd.Series([10.0, 12.0, 15.0, 20.0, 25.0])
    assert calculate_max_drawdown(up_prices) == 0.0


def test_sortino_ratio():
    """Sortino ratio should compute finite value when downside volatility exists."""
    np.random.seed(42)
    returns = pd.Series(np.random.normal(0.001, 0.02, 250))
    sortino = calculate_sortino_ratio(returns, risk_free_rate=0.04)
    assert isinstance(sortino, float)
    assert not np.isnan(sortino)
    assert not np.isinf(sortino)
