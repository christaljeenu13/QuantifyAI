"""
Unit tests for Portfolio Risk Lab mathematics:
Covariance matrix, Portfolio Volatility, Euler Risk Contributions, VaR and CVaR.
"""

import pytest
import pandas as pd
import numpy as np
from src.analytics.risk import (
    calculate_covariance_matrix,
    calculate_correlation_matrix,
    calculate_portfolio_volatility,
    calculate_risk_contributions,
    calculate_var_cvar
)


@pytest.fixture
def multi_asset_returns():
    """Generates synthetic returns for 3 assets."""
    np.random.seed(77)
    dates = pd.date_range("2023-01-01", periods=250, freq="D")
    r1 = np.random.normal(0.0005, 0.01, 250)  # Low vol (e.g. Gold)
    r2 = np.random.normal(0.0015, 0.03, 250)  # High vol (e.g. BTC)
    r3 = np.random.normal(0.0010, 0.02, 250)  # Med vol (e.g. NVDA)

    return pd.DataFrame({"AssetA": r1, "AssetB": r2, "AssetC": r3}, index=dates)


def test_portfolio_volatility_single_asset_parity(multi_asset_returns):
    """If weight is 1.0 on AssetA and 0 elsewhere, portfolio vol must match AssetA ann vol."""
    cov = calculate_covariance_matrix(multi_asset_returns)
    weights = {"AssetA": 1.0, "AssetB": 0.0, "AssetC": 0.0}

    port_vol = calculate_portfolio_volatility(weights, cov)
    asset_a_vol = multi_asset_returns["AssetA"].std(ddof=1) * np.sqrt(252)

    assert pytest.approx(port_vol, rel=1e-4) == asset_a_vol


def test_euler_risk_contribution_sum_to_100(multi_asset_returns):
    """The sum of percentage risk contributions (PRC) across all assets must equal 100%."""
    cov = calculate_covariance_matrix(multi_asset_returns)
    weights = {"AssetA": 0.3, "AssetB": 0.4, "AssetC": 0.3}

    risk_decomp = calculate_risk_contributions(weights, cov)
    total_prc = sum(d["prc"] for d in risk_decomp.values())

    assert pytest.approx(total_prc, abs=1e-3) == 100.0


def test_var_and_cvar():
    """Verify VaR 95% and CVaR 95% properties (CVaR >= VaR)."""
    np.random.seed(42)
    returns = pd.Series(np.random.normal(0.0, 0.02, 1000))
    var_95, cvar_95 = calculate_var_cvar(returns, 0.95)

    assert var_95 > 0
    assert cvar_95 >= var_95
