"""
Technical Indicators Module.
Pure Pandas/NumPy implementations of core technical indicators:
SMA, EMA, RSI (Wilder's smoothing), MACD, Bollinger Bands, and ATR.
"""

from typing import Tuple
import pandas as pd
import numpy as np


def calculate_sma(series: pd.Series, window: int = 20) -> pd.Series:
    """Calculate Simple Moving Average."""
    if len(series) < window or window <= 0:
        return pd.Series(index=series.index, dtype=float)
    return series.rolling(window=window).mean()


def calculate_ema(series: pd.Series, span: int = 20) -> pd.Series:
    """Calculate Exponential Moving Average using standard recursive multiplier."""
    if len(series) == 0 or span <= 0:
        return pd.Series(index=series.index, dtype=float)
    return series.ewm(span=span, adjust=False).mean()


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI) using Wilder's Exponential Smoothing.
    Values bounded between [0, 100].
    """
    if len(series) < period + 1 or period <= 0:
        return pd.Series(index=series.index, dtype=float)

    delta = series.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)

    # Wilder's smoothing uses alpha = 1 / period
    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))

    # Clean extreme boundaries
    rsi = rsi.where(avg_loss != 0, 100.0)
    rsi = rsi.where(avg_gain != 0, 0.0)

    # First `period` values are NaN
    rsi.iloc[:period] = np.nan
    return rsi


def calculate_macd(
    series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> pd.DataFrame:
    """
    Calculate Moving Average Convergence Divergence (MACD).
    Returns DataFrame with columns: ['MACD', 'Signal', 'Histogram']
    """
    df = pd.DataFrame(index=series.index)
    if len(series) < slow:
        df["MACD"] = np.nan
        df["Signal"] = np.nan
        df["Histogram"] = np.nan
        return df

    fast_ema = calculate_ema(series, span=fast)
    slow_ema = calculate_ema(series, span=slow)
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line

    df["MACD"] = macd_line
    df["Signal"] = signal_line
    df["Histogram"] = histogram
    return df


def calculate_bollinger_bands(
    series: pd.Series, window: int = 20, num_std: float = 2.0
) -> pd.DataFrame:
    """
    Calculate Bollinger Bands.
    Returns DataFrame with columns: ['Middle', 'Upper', 'Lower']
    """
    df = pd.DataFrame(index=series.index)
    if len(series) < window:
        df["Middle"] = np.nan
        df["Upper"] = np.nan
        df["Lower"] = np.nan
        return df

    middle = series.rolling(window=window).mean()
    std = series.rolling(window=window).std()
    df["Middle"] = middle
    df["Upper"] = middle + (num_std * std)
    df["Lower"] = middle - (num_std * std)
    return df


def calculate_atr(
    high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
) -> pd.Series:
    """
    Calculate Average True Range (ATR).
    """
    if len(close) < period + 1:
        return pd.Series(index=close.index, dtype=float)

    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    return atr
