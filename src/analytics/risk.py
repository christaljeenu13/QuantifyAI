"""
Portfolio Risk Lab Module.
Implements multi-asset portfolio mathematics:
- Covariance & Correlation matrices
- Portfolio variance & annualized volatility (w^T * Sigma * w)
- Marginal & Percentage Risk Contributions (Euler decomposition)
- Value at Risk (VaR 95%) and Conditional VaR (Expected Shortfall)
- Portfolio wealth trajectory
"""

from typing import Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np
import config
from .metrics import (
    calculate_annualized_volatility,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    calculate_cagr
)


def calculate_covariance_matrix(
    returns_df: pd.DataFrame, periods_per_year: int = 252
) -> pd.DataFrame:
    """Annualized covariance matrix (Sigma * 252)."""
    if returns_df.empty or len(returns_df) < 2:
        return pd.DataFrame()
    return returns_df.cov() * periods_per_year


def calculate_correlation_matrix(returns_df: pd.DataFrame) -> pd.DataFrame:
    """Pairwise Pearson correlation matrix."""
    if returns_df.empty or len(returns_df) < 2:
        return pd.DataFrame()
    return returns_df.corr()


def calculate_portfolio_returns(
    returns_df: pd.DataFrame, weights: Dict[str, float]
) -> pd.Series:
    """
    Compute daily portfolio return series given asset returns and fixed rebalancing weights.
    Portfolio_Return_t = sum(w_i * r_i,t)
    """
    if returns_df.empty:
        return pd.Series(dtype=float)

    # Ensure weights match columns
    clean_weights = np.array([weights.get(col, 0.0) for col in returns_df.columns])
    
    # Dot product of returns matrix and weights vector
    port_ret = returns_df.dot(clean_weights)
    return port_ret


def calculate_portfolio_volatility(
    weights: Dict[str, float], cov_matrix: pd.DataFrame
) -> float:
    """
    Portfolio annualized volatility: sqrt(w^T * Sigma * w).
    """
    if cov_matrix.empty:
        return 0.0

    tickers = list(cov_matrix.columns)
    w = np.array([weights.get(t, 0.0) for t in tickers], dtype=float)
    
    # Matrix multiplication: w.T @ Sigma @ w
    variance = float(w.T @ cov_matrix.values @ w)
    if variance <= 0 or np.isnan(variance):
        return 0.0
    return float(np.sqrt(variance))


def calculate_risk_contributions(
    weights: Dict[str, float], cov_matrix: pd.DataFrame
) -> Dict[str, Dict[str, float]]:
    """
    Euler Risk Decomposition:
    - Marginal Contribution to Risk (MCR): (Sigma @ w) / sigma_p
    - Absolute Risk Contribution (ARC): w_i * MCR_i
    - Percentage Risk Contribution (PRC): ARC_i / sigma_p (sums to 100%)
    """
    tickers = list(cov_matrix.columns)
    w = np.array([weights.get(t, 0.0) for t in tickers], dtype=float)
    sigma_p = calculate_portfolio_volatility(weights, cov_matrix)

    if sigma_p <= 1e-8:
        return {
            t: {"weight": weights.get(t, 0.0), "mcr": 0.0, "arc": 0.0, "prc": 0.0}
            for t in tickers
        }

    # Marginal Risk Contribution vector
    mcr = (cov_matrix.values @ w) / sigma_p
    arc = w * mcr
    prc = arc / sigma_p

    contributions = {}
    for i, t in enumerate(tickers):
        contributions[t] = {
            "weight": float(w[i]),
            "mcr": float(mcr[i]),
            "arc": float(arc[i]),
            "prc": float(prc[i] * 100.0)  # Convert to percentage
        }

    return contributions


def calculate_var_cvar(
    returns: pd.Series, confidence_level: float = 0.95
) -> Tuple[float, float]:
    """
    Calculate Historical Value at Risk (VaR) and Conditional VaR (Expected Shortfall).
    Returned as positive loss percentages (e.g. 0.024 for 2.4% daily VaR).
    """
    if len(returns) < 5:
        return 0.0, 0.0

    # Alpha quantile of returns (left tail)
    alpha = 1.0 - confidence_level
    var_cutoff = float(np.percentile(returns, alpha * 100))
    # VaR as positive loss
    var_95 = -var_cutoff if var_cutoff < 0 else 0.0

    # CVaR is the mean of losses strictly exceeding the VaR cutoff
    tail_losses = returns[returns <= var_cutoff]
    if len(tail_losses) > 0:
        cvar_95 = float(-tail_losses.mean())
    else:
        cvar_95 = var_95

    return var_95, cvar_95


def calculate_portfolio_metrics(
    aligned_prices: pd.DataFrame,
    weights: Dict[str, float],
    risk_free_rate: float = config.DEFAULT_RISK_FREE_RATE
) -> Dict[str, Any]:
    """
    Calculate comprehensive portfolio stats from aligned prices and asset weights.
    """
    if aligned_prices.empty or len(aligned_prices) < 2:
        return {
            "total_return": 0.0,
            "annualized_return": 0.0,
            "annualized_volatility": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "var_95_daily": 0.0,
            "cvar_95_daily": 0.0,
            "wealth_series": pd.Series(dtype=float),
            "drawdown_series": pd.Series(dtype=float)
        }

    returns_df = aligned_prices.pct_change().dropna()
    port_ret = calculate_portfolio_returns(returns_df, weights)

    # Reconstruct portfolio wealth index starting at 100.0
    wealth_index = (1.0 + port_ret).cumprod() * 100.0
    # Prepend starting 100 on day 0
    first_date = aligned_prices.index[0]
    wealth_series = pd.Series([100.0], index=[first_date])._append(wealth_index)
    wealth_series = wealth_series[~wealth_series.index.duplicated(keep="last")]

    cov_matrix = calculate_covariance_matrix(returns_df)
    ann_vol = calculate_portfolio_volatility(weights, cov_matrix)
    cagr = calculate_cagr(wealth_series)
    sharpe = calculate_sharpe_ratio(port_ret, risk_free_rate=risk_free_rate)
    mdd = calculate_max_drawdown(wealth_series)
    var_95, cvar_95 = calculate_var_cvar(port_ret, 0.95)

    risk_contribs = calculate_risk_contributions(weights, cov_matrix)

    return {
        "total_return": float((wealth_series.iloc[-1] / wealth_series.iloc[0]) - 1.0),
        "annualized_return": float(cagr),
        "annualized_volatility": float(ann_vol),
        "sharpe_ratio": float(sharpe),
        "max_drawdown": float(mdd),
        "var_95_daily": float(var_95),
        "cvar_95_daily": float(cvar_95),
        "wealth_series": wealth_series,
        "returns_series": port_ret,
        "cov_matrix": cov_matrix,
        "corr_matrix": calculate_correlation_matrix(returns_df),
        "risk_contributions": risk_contribs
    }
