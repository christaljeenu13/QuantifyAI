"""
Comparative Analytics Module.
Aligns, normalizes (Base = 100), and computes comparative statistical profiles across multiple assets.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import config
from src.analytics.metrics import (
    calculate_total_return,
    calculate_cagr,
    calculate_annualized_volatility,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    calculate_drawdown_series
)


def normalize_price_series(prices_df: pd.DataFrame, base_value: float = 100.0) -> pd.DataFrame:
    """
    Rebase all asset price series to base_value (e.g. 100.0) at the first aligned observation.
    Indexed_t = (Price_t / Price_0) * base_value
    """
    if prices_df.empty:
        return pd.DataFrame()

    first_row = prices_df.iloc[0]
    # Guard against division by zero
    valid_cols = first_row[first_row > 0].index
    normalized = (prices_df[valid_cols] / first_row[valid_cols]) * base_value
    return normalized


def align_multi_asset_data(
    asset_dict: Dict[str, pd.DataFrame], method: str = "inner"
) -> pd.DataFrame:
    """
    Merge Close price series across multiple asset DataFrames.
    method: 'inner' (only common sessions) or 'ffill' (forward-fill weekends/holidays)
    """
    if not asset_dict:
        return pd.DataFrame()

    series_map = {}
    for name, df in asset_dict.items():
        if df is not None and not df.empty and "Close" in df.columns:
            series_map[name] = df["Close"]

    if not series_map:
        return pd.DataFrame()

    combined = pd.DataFrame(series_map)
    combined.sort_index(inplace=True)

    if method == "inner":
        combined.dropna(inplace=True)
    elif method == "ffill":
        combined.ffill(inplace=True)
        combined.dropna(inplace=True)

    return combined


def compute_comparison_summary(
    aligned_prices: pd.DataFrame, risk_free_rate: float = config.DEFAULT_RISK_FREE_RATE
) -> pd.DataFrame:
    """
    Produce side-by-side comparison summary table across all aligned assets.
    """
    if aligned_prices.empty or len(aligned_prices) < 2:
        return pd.DataFrame()

    records = []
    returns_df = aligned_prices.pct_change().dropna()

    for col in aligned_prices.columns:
        s = aligned_prices[col]
        if isinstance(s, pd.DataFrame):
            s = s.iloc[:, 0]
        r = returns_df[col] if col in returns_df.columns else pd.Series(dtype=float)
        if isinstance(r, pd.DataFrame):
            r = r.iloc[:, 0]

        start_p = float(s.iloc[0])
        end_p = float(s.iloc[-1])
        tot_ret = calculate_total_return(s)
        cagr = calculate_cagr(s)
        vol = calculate_annualized_volatility(r)
        sharpe = calculate_sharpe_ratio(r, risk_free_rate=risk_free_rate)
        mdd = calculate_max_drawdown(s)

        records.append({
            "Asset": col,
            "Start Price": start_p,
            "End Price": end_p,
            "Total Return": tot_ret,
            "Annualized Return": cagr,
            "Annualized Volatility": vol,
            "Sharpe Ratio": sharpe,
            "Max Drawdown": mdd
        })

    return pd.DataFrame(records)


def compute_rolling_correlation(
    s1: pd.Series, s2: pd.Series, window: int = 60
) -> pd.Series:
    """Compute rolling Pearson correlation between two asset return series."""
    r1 = s1.pct_change().dropna()
    r2 = s2.pct_change().dropna()
    common_idx = r1.index.intersection(r2.index)
    if len(common_idx) < window:
        return pd.Series(index=common_idx, dtype=float)

    return r1.loc[common_idx].rolling(window=window).corr(r2.loc[common_idx])
