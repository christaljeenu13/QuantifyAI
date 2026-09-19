"""
Financial Performance Metrics Module.
Implements institutional formulas for returns, CAGR, volatility, Sharpe, Sortino,
drawdowns, and calendar return matrices.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import config


def calculate_daily_returns(prices: pd.Series) -> pd.Series:
    """Calculate percentage daily return series."""
    if len(prices) < 2:
        return pd.Series(dtype=float)
    return prices.pct_change().dropna()


def calculate_cumulative_returns(returns: pd.Series) -> pd.Series:
    """Compute cumulative wealth trajectory starting at 0%."""
    if len(returns) == 0:
        return pd.Series(dtype=float)
    return (1.0 + returns).cumprod() - 1.0


def calculate_total_return(prices: pd.Series) -> float:
    """Total absolute return over the price series."""
    if len(prices) < 2:
        return 0.0
    start = float(prices.iloc[0])
    end = float(prices.iloc[-1])
    if start <= 0:
        return 0.0
    return (end - start) / start


def calculate_cagr(prices: pd.Series, periods_per_year: int = 252) -> float:
    """
    Compound Annual Growth Rate (CAGR).
    CAGR = (End_Value / Start_Value) ** (periods_per_year / N) - 1
    """
    if len(prices) < 2:
        return 0.0
    start = float(prices.iloc[0])
    end = float(prices.iloc[-1])
    if start <= 0 or end <= 0:
        return 0.0

    n_periods = len(prices) - 1
    if n_periods <= 0:
        return 0.0

    years = n_periods / periods_per_year
    if years <= 0:
        return 0.0

    try:
        cagr = (end / start) ** (1.0 / years) - 1.0
        # Guard against astronomical numbers for tiny duration spikes
        if np.isinf(cagr) or np.isnan(cagr):
            return 0.0
        return float(cagr)
    except (ZeroDivisionError, OverflowError):
        return 0.0


def calculate_annualized_volatility(
    returns: pd.Series, periods_per_year: int = 252
) -> float:
    """
    Annualized Volatility (Standard Deviation * sqrt(periods_per_year)).
    """
    if len(returns) < 2:
        return 0.0
    daily_std = float(returns.std(ddof=1))
    if np.isnan(daily_std) or daily_std <= 0:
        return 0.0
    return float(daily_std * np.sqrt(periods_per_year))


def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = config.DEFAULT_RISK_FREE_RATE,
    periods_per_year: int = 252
) -> float:
    """
    Annualized Sharpe Ratio:
    (Annualized Return - Risk Free Rate) / Annualized Volatility
    """
    if len(returns) < 2:
        return 0.0

    ann_vol = calculate_annualized_volatility(returns, periods_per_year)
    if ann_vol <= 1e-8:
        return 0.0

    # Arithmetic annualization of excess return
    mean_daily = float(returns.mean())
    ann_return = mean_daily * periods_per_year
    excess_return = ann_return - risk_free_rate

    sharpe = excess_return / ann_vol
    if np.isnan(sharpe) or np.isinf(sharpe):
        return 0.0
    return float(sharpe)


def calculate_sortino_ratio(
    returns: pd.Series,
    risk_free_rate: float = config.DEFAULT_RISK_FREE_RATE,
    periods_per_year: int = 252
) -> float:
    """
    Annualized Sortino Ratio:
    Penalizes only downside volatility below the risk-free benchmark.
    """
    if len(returns) < 2:
        return 0.0

    daily_rf = risk_free_rate / periods_per_year
    downside = returns[returns < daily_rf] - daily_rf
    if len(downside) < 2:
        return 0.0

    downside_dev = np.sqrt(np.mean(downside**2)) * np.sqrt(periods_per_year)
    if downside_dev <= 1e-8 or np.isnan(downside_dev):
        return 0.0

    mean_daily = float(returns.mean())
    ann_return = mean_daily * periods_per_year
    excess_return = ann_return - risk_free_rate

    sortino = excess_return / downside_dev
    if np.isnan(sortino) or np.isinf(sortino):
        return 0.0
    return float(sortino)


def calculate_drawdown_series(prices: pd.Series) -> pd.Series:
    """
    Calculate peak-to-trough percentage drawdown series.
    Drawdown_t = (Price_t - Peak_t) / Peak_t (bounded <= 0)
    """
    if len(prices) == 0:
        return pd.Series(dtype=float)
    peak = prices.cummax()
    drawdown = (prices - peak) / peak.replace(0, np.nan)
    return drawdown.fillna(0.0)


def calculate_max_drawdown(prices: pd.Series) -> float:
    """
    Calculate Maximum Drawdown over the price series.
    Returns negative float (e.g., -0.224 for -22.4%).
    """
    if len(prices) < 2:
        return 0.0
    dd = calculate_drawdown_series(prices)
    mdd = float(dd.min())
    if np.isnan(mdd):
        return 0.0
    return mdd


def calculate_monthly_returns(prices: pd.Series) -> pd.DataFrame:
    """
    Generate Monthly Calendar Returns Table (Year x Month).
    """
    if len(prices) < 20:
        return pd.DataFrame()

    # Resample to month-end
    monthly_prices = prices.resample("M").last().dropna()
    monthly_ret = monthly_prices.pct_change().dropna()

    if monthly_ret.empty:
        return pd.DataFrame()

    df = pd.DataFrame({
        "Year": monthly_ret.index.year,
        "Month": monthly_ret.index.strftime("%b"),
        "Return": monthly_ret.values
    })

    month_order = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    pivot = df.pivot(index="Year", columns="Month", values="Return")
    pivot = pivot.reindex(columns=[m for m in month_order if m in pivot.columns])

    # Calculate Annual Compound Return for each year
    def _comp_year(row):
        valid = row.dropna()
        if len(valid) == 0:
            return np.nan
        return float((1.0 + valid).prod() - 1.0)

    pivot["Year_Total"] = pivot.apply(_comp_year, axis=1)
    return pivot


def calculate_summary_metrics(
    prices: pd.Series, risk_free_rate: float = config.DEFAULT_RISK_FREE_RATE
) -> Dict[str, Any]:
    """
    Compute comprehensive suite of performance metrics for an asset.
    """
    if len(prices) < 2:
        return {
            "latest_price": 0.0,
            "total_return": 0.0,
            "annualized_return": 0.0,
            "annualized_volatility": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "max_drawdown": 0.0,
            "trading_days": 0
        }

    daily_ret = calculate_daily_returns(prices)
    total_ret = calculate_total_return(prices)
    cagr = calculate_cagr(prices)
    vol = calculate_annualized_volatility(daily_ret)
    sharpe = calculate_sharpe_ratio(daily_ret, risk_free_rate=risk_free_rate)
    sortino = calculate_sortino_ratio(daily_ret, risk_free_rate=risk_free_rate)
    mdd = calculate_max_drawdown(prices)

    return {
        "latest_price": float(prices.iloc[-1]),
        "start_price": float(prices.iloc[0]),
        "total_return": float(total_ret),
        "annualized_return": float(cagr),
        "annualized_volatility": float(vol),
        "sharpe_ratio": float(sharpe),
        "sortino_ratio": float(sortino),
        "max_drawdown": float(mdd),
        "trading_days": len(prices)
    }
