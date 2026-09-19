"""
Unit tests for Multi-Asset Data Alignment and Normalization:
Calendar alignment, missing dates, and base=100 rebasing.
"""

import pytest
import pandas as pd
import numpy as np
from src.comparison.comparative_analytics import normalize_price_series, align_multi_asset_data


def test_base_100_normalization():
    """Verify that normalized series starts at exactly base_value (100.0)."""
    df = pd.DataFrame({
        "Asset1": [50.0, 55.0, 60.0],
        "Asset2": [200.0, 180.0, 220.0]
    })
    norm = normalize_price_series(df, base_value=100.0)

    assert pytest.approx(norm["Asset1"].iloc[0], rel=1e-5) == 100.0
    assert pytest.approx(norm["Asset2"].iloc[0], rel=1e-5) == 100.0
    assert pytest.approx(norm["Asset1"].iloc[-1], rel=1e-5) == 120.0  # +20%
    assert pytest.approx(norm["Asset2"].iloc[-1], rel=1e-5) == 110.0  # +10%


def test_align_multi_asset_inner_and_ffill():
    """Verify inner join drops disjoint dates while ffill retains continuous dates."""
    dates_5d = pd.date_range("2024-01-01", periods=5, freq="B")  # Business days
    dates_7d = pd.date_range("2024-01-01", periods=7, freq="D")  # All calendar days

    df_stock = pd.DataFrame({"Close": [100.0] * len(dates_5d)}, index=dates_5d)
    df_crypto = pd.DataFrame({"Close": [200.0] * len(dates_7d)}, index=dates_7d)

    asset_map = {"Stock": df_stock, "Crypto": df_crypto}

    # Inner alignment
    aligned_inner = align_multi_asset_data(asset_map, method="inner")
    assert len(aligned_inner) == len(dates_5d)

    # Forward fill alignment
    aligned_ffill = align_multi_asset_data(asset_map, method="ffill")
    assert len(aligned_ffill) >= len(dates_5d)
    assert not aligned_ffill.isnull().any().any()
