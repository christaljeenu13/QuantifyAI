"""
Unit tests for Backtesting Engine:
Zero look-ahead bias, trade accounting, cash conservation, fee deduction, and win rates.
"""

import pytest
import pandas as pd
import numpy as np
from src.backtesting.engine import BacktestEngine
from src.backtesting.strategies import generate_sma_crossover_signals


@pytest.fixture
def synthetic_market_data():
    """Generates 100 days of synthetic OHLCV data."""
    dates = pd.date_range("2023-01-01", periods=100, freq="D")
    np.random.seed(99)
    ret = np.random.normal(0.001, 0.02, 100)
    close = 100.0 * np.exp(np.cumsum(ret))
    open_p = close * np.random.uniform(0.995, 1.005, 100)
    high_p = np.maximum(open_p, close) * 1.01
    low_p = np.minimum(open_p, close) * 0.99

    return pd.DataFrame({
        "Open": open_p,
        "High": high_p,
        "Low": low_p,
        "Close": close,
        "Volume": 1000000
    }, index=dates)


def test_zero_lookahead_execution_timing(synthetic_market_data):
    """
    Verify that a signal generated on day T does NOT execute until day T+1.
    """
    df = synthetic_market_data
    # Signal is 0 everywhere, except Long on bar 10
    signals = pd.Series(0, index=df.index)
    signals.iloc[10] = 1  # Signal emitted at Close of bar 10

    engine = BacktestEngine(
        initial_capital=10000.0,
        commission_rate=0.001,
        slippage_rate=0.0,
        execution_timing="next_open"
    )
    res = engine.run(df, signals)

    # On bar 10, cash must still equal initial capital (no lookahead execution at bar 10 Close)
    assert pytest.approx(res.equity_curve["Cash"].iloc[10], rel=1e-5) == 10000.0

    # On bar 11, the trade executes at Open of bar 11
    assert res.equity_curve["Holdings_Value"].iloc[11] > 0
    assert len(res.trades) >= 1
    # Trade entry date must correspond to bar 11, NOT bar 10
    assert res.trades[0].entry_date == df.index[11].strftime("%Y-%m-%d")


def test_fee_deduction_and_cash_conservation(synthetic_market_data):
    """Verify that fees are deducted and cash never goes negative."""
    df = synthetic_market_data
    # Buy on bar 5, sell on bar 15
    signals = pd.Series(0, index=df.index)
    signals.iloc[5:15] = 1

    fee_rate = 0.005  # 0.5% fee
    engine = BacktestEngine(
        initial_capital=10000.0,
        commission_rate=fee_rate,
        slippage_rate=0.0,
        execution_timing="next_open"
    )
    res = engine.run(df, signals)

    # Cash must never be negative
    assert (res.equity_curve["Cash"] >= -1e-6).all()
    # Fees must be recorded
    assert res.metrics["total_fees_paid"] > 0
    assert len(res.trades) == 1
    t = res.trades[0]
    assert t.entry_fee > 0
    assert t.exit_fee > 0


def test_benchmark_initial_capital_parity(synthetic_market_data):
    """Benchmark and strategy must start with the exact same initial capital."""
    df = synthetic_market_data
    signals = pd.Series(0, index=df.index)  # 100% Cash strategy
    engine = BacktestEngine(initial_capital=50000.0)
    res = engine.run(df, signals)

    assert res.equity_curve["Strategy_Equity"].iloc[0] == 50000.0
    assert res.equity_curve["Benchmark_Equity"].iloc[0] == 50000.0
