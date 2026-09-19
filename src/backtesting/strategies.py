"""
Quantitative Strategy Signal Generators.
Generates desired target position signals (1 = Long, 0 = Flat/Cash)
using past and present session data without lookahead.
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from src.analytics.indicators import calculate_sma, calculate_ema, calculate_rsi


def generate_sma_crossover_signals(
    df: pd.DataFrame, fast_period: int = 20, slow_period: int = 50
) -> pd.Series:
    """
    Dual Simple Moving Average Crossover.
    Signal = 1 when Fast SMA > Slow SMA, else 0.
    """
    if len(df) < slow_period:
        return pd.Series(0, index=df.index)

    fast_sma = calculate_sma(df["Close"], window=fast_period)
    slow_sma = calculate_sma(df["Close"], window=slow_period)

    signals = pd.Series(0, index=df.index)
    signals[fast_sma > slow_sma] = 1
    # Warmup period is Flat
    signals.iloc[:slow_period] = 0
    return signals


def generate_ema_crossover_signals(
    df: pd.DataFrame, fast_period: int = 12, slow_period: int = 26
) -> pd.Series:
    """
    Dual Exponential Moving Average Crossover.
    Signal = 1 when Fast EMA > Slow EMA, else 0.
    """
    if len(df) < slow_period:
        return pd.Series(0, index=df.index)

    fast_ema = calculate_ema(df["Close"], span=fast_period)
    slow_ema = calculate_ema(df["Close"], span=slow_period)

    signals = pd.Series(0, index=df.index)
    signals[fast_ema > slow_ema] = 1
    signals.iloc[:slow_period] = 0
    return signals


def generate_price_sma_signals(df: pd.DataFrame, window: int = 50) -> pd.Series:
    """
    Trend Following: Price vs SMA.
    Signal = 1 when Close > SMA, else 0.
    """
    if len(df) < window:
        return pd.Series(0, index=df.index)

    sma = calculate_sma(df["Close"], window=window)
    signals = pd.Series(0, index=df.index)
    signals[df["Close"] > sma] = 1
    signals.iloc[:window] = 0
    return signals


def generate_rsi_strategy_signals(
    df: pd.DataFrame, period: int = 14, oversold: float = 30.0, overbought: float = 70.0
) -> pd.Series:
    """
    RSI Mean Reversion:
    Enter Long when RSI crosses below oversold; exit when crosses above overbought.
    """
    if len(df) < period + 5:
        return pd.Series(0, index=df.index)

    rsi = calculate_rsi(df["Close"], period=period)
    signals = pd.Series(0, index=df.index)

    position = 0
    for i in range(period, len(df)):
        val = rsi.iloc[i]
        if np.isnan(val):
            continue
        if position == 0 and val < oversold:
            position = 1
        elif position == 1 and val > overbought:
            position = 0
        signals.iloc[i] = position

    return signals


def generate_buy_and_hold_signals(df: pd.DataFrame) -> pd.Series:
    """Buy & Hold Benchmark: 100% long at all eligible sessions."""
    return pd.Series(1, index=df.index)
