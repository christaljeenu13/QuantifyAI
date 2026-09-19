"""
Market Data Manager.
Handles downloading, normalizing, validating, and caching historical market data from yfinance.

Data flow (every fetch reports where its data really came from):
  1. Live download from Yahoo Finance (cached in-memory by Streamlit for 30 min).
  2. If Yahoo is unreachable / returns nothing -> local CSV snapshot in ./data_cache
     (written automatically after every successful live download).
  3. If neither exists -> empty DataFrame with status="error". No fake data is ever generated.
"""

from datetime import datetime, date, timedelta, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
import yfinance as yf

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

SNAP_DIR = Path(__file__).resolve().parents[2] / "data_cache"

SOURCE_LIVE = "Yahoo Finance (yfinance)"
SOURCE_SNAPSHOT = "Local snapshot (Yahoo unreachable)"


def _clean_yf_dataframe(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Normalize yfinance raw dataframe into clean standard OHLCV format."""
    if df is None or df.empty:
        return pd.DataFrame()

    # Handle multi-level columns if returned by yfinance
    if isinstance(df.columns, pd.MultiIndex):
        # Flatten MultiIndex e.g. ('Close', 'NVDA') -> 'Close'
        df.columns = [col[0] for col in df.columns]

    # Ensure index is datetime and sorted
    df = df.copy()
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    # Strip timezone to ensure consistent date alignment across exchanges
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)

    df.sort_index(inplace=True)

    # Standardize expected columns
    expected_cols = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
    for col in expected_cols:
        if col not in df.columns:
            if col == "Adj Close" and "Close" in df.columns:
                df["Adj Close"] = df["Close"]
            elif col == "Volume":
                df["Volume"] = 0
            else:
                # If essential price columns missing
                if col in ["Open", "High", "Low", "Close"]:
                    return pd.DataFrame()

    # Cast to float
    for col in ["Open", "High", "Low", "Close", "Adj Close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce").fillna(0)

    # Drop rows where Close is NaN
    df.dropna(subset=["Close"], inplace=True)

    # Remove duplicates
    df = df[~df.index.duplicated(keep="first")]

    # Add Return column
    df["Daily_Return"] = df["Close"].pct_change().fillna(0.0)

    return df


def _fetch_from_yfinance(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Underlying yfinance download call. Tries yf.download, then Ticker.history if empty/failed."""
    try:
        data = yf.download(
            tickers=ticker,
            start=start,
            end=end,
            progress=False,
            auto_adjust=False,
            timeout=15
        )
        df = _clean_yf_dataframe(data, ticker)
        if not df.empty:
            return df
    except Exception:
        pass

    # Fallback (also runs when download silently returns an empty frame)
    try:
        t = yf.Ticker(ticker)
        data = t.history(start=start, end=end, auto_adjust=False)
        return _clean_yf_dataframe(data, ticker)
    except Exception:
        return pd.DataFrame()


# ─── Local snapshot (offline backup) ─────────────────────────────────────────
def _snapshot_path(ticker: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in ticker)
    return SNAP_DIR / f"{safe}.csv"


def _load_snapshot(ticker: str) -> pd.DataFrame:
    path = _snapshot_path(ticker)
    if not path.exists():
        return pd.DataFrame()
    try:
        raw = pd.read_csv(path, index_col=0, parse_dates=True)
        return _clean_yf_dataframe(raw, ticker)
    except Exception:
        return pd.DataFrame()


def _save_snapshot(ticker: str, df: pd.DataFrame) -> None:
    """Merge new rows into the ticker's snapshot so a short fetch never shrinks a long one."""
    try:
        SNAP_DIR.mkdir(parents=True, exist_ok=True)
        existing = _load_snapshot(ticker)
        if not existing.empty:
            df = pd.concat([existing, df])
            df = df[~df.index.duplicated(keep="last")].sort_index()
        df.to_csv(_snapshot_path(ticker))
    except Exception:
        pass  # snapshot is best-effort; never break the app because of it


def _download_or_raise(ticker: str, start: str, end: str) -> pd.DataFrame:
    """
    Live download. Raises when Yahoo returns nothing so Streamlit does NOT cache the failure.
    Successful downloads are also written to the local snapshot.
    """
    df = _fetch_from_yfinance(ticker, start, end)
    if df.empty:
        raise ValueError(f"No live data returned for {ticker}")
    _save_snapshot(ticker, df)
    return df


if HAS_STREAMLIT:
    _cached_download = st.cache_data(ttl=1800, show_spinner=False)(_download_or_raise)
else:
    _cached_download = _download_or_raise


def _to_ts(value: Any, default: pd.Timestamp) -> pd.Timestamp:
    if value is None:
        return default
    return pd.to_datetime(value if isinstance(value, (datetime, date)) else str(value))


class MarketDataManager:
    """Manages downloading, caching, and validating asset time series."""

    @staticmethod
    def fetch_data(
        ticker: str,
        start_date: Optional[Any] = None,
        end_date: Optional[Any] = None,
        lookback_years: int = 2
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Fetch OHLCV data for a ticker over the specified date window.
        Returns: (DataFrame, metadata_dict)

        metadata["status"]  : "success" | "error"
        metadata["is_live"] : True only when the rows came from a live Yahoo download
        metadata["data_source"] : where the rows came from (live / snapshot)
        """
        end_dt = _to_ts(end_date, pd.Timestamp(datetime.now()))
        start_dt = _to_ts(start_date, end_dt - timedelta(days=int(lookback_years * 365.25)))

        start_str = start_dt.strftime("%Y-%m-%d")
        # Add 1 day to end_date so yfinance includes the end date
        end_str = (end_dt + timedelta(days=1)).strftime("%Y-%m-%d")

        fetch_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        source = SOURCE_LIVE
        try:
            df = _cached_download(ticker, start_str, end_str)
        except Exception:
            df = _load_snapshot(ticker)
            source = SOURCE_SNAPSHOT

        if not df.empty:
            # Filter strictly within requested range
            df = df[(df.index >= start_dt) & (df.index <= end_dt)]

        if df.empty:
            metadata = {
                "ticker": ticker,
                "status": "error",
                "is_live": False,
                "message": f"No data found for ticker '{ticker}' between {start_str} and {end_dt.strftime('%Y-%m-%d')}.",
                "fetched_at": fetch_time,
                "data_source": "Unavailable",
                "rows": 0
            }
            return pd.DataFrame(), metadata

        metadata = {
            "ticker": ticker,
            "status": "success",
            "is_live": source == SOURCE_LIVE,
            "start_date": df.index.min().strftime("%Y-%m-%d"),
            "end_date": df.index.max().strftime("%Y-%m-%d"),
            "rows": len(df),
            "latest_close": float(df["Close"].iloc[-1]),
            "fetched_at": fetch_time,
            "data_source": source,
            "currency": "USD"
        }

        return df, metadata

    @staticmethod
    def fetch_multiple_assets(
        tickers: List[str],
        start_date: Optional[Any] = None,
        end_date: Optional[Any] = None,
        align_method: str = "inner"
    ) -> Tuple[pd.DataFrame, Dict[str, Dict[str, Any]]]:
        """
        Fetch multiple assets and align their Close prices into a single DataFrame.
        align_method: 'inner' (only common sessions) or 'ffill' (crypto+equity aligned with forward-fill)
        Returns: (Aligned_Close_DF, dict_of_metadata)
        """
        close_series = {}
        all_metadata = {}

        for ticker in tickers:
            df, meta = MarketDataManager.fetch_data(ticker, start_date, end_date)
            all_metadata[ticker] = meta
            if not df.empty:
                close_series[ticker] = df["Close"]

        if not close_series:
            return pd.DataFrame(), all_metadata

        combined = pd.DataFrame(close_series)

        if align_method == "inner":
            combined.dropna(inplace=True)
        elif align_method == "ffill":
            # Useful when comparing 7-day crypto (BTC) with 5-day equities (NVDA/GLD)
            combined.ffill(inplace=True)
            combined.dropna(inplace=True)

        return combined, all_metadata


# ─── Helpers shared by the UI pages ──────────────────────────────────────────
def data_status(metas: Any) -> str:
    """
    Summarize one metadata dict (or an iterable / dict of them) into
    'live' | 'snapshot' | 'unavailable'.
    """
    if isinstance(metas, dict) and "status" in metas:
        metas = [metas]
    elif isinstance(metas, dict):
        metas = list(metas.values())
    metas = list(metas)
    ok = [m for m in metas if m.get("status") == "success"]
    if not ok:
        return "unavailable"
    if all(m.get("is_live") for m in ok) and len(ok) == len(metas):
        return "live"
    return "snapshot"


def slice_timeframe(obj, tf: str):
    """Keep only the trailing window of a DataFrame/Series ('1M','3M','6M','1Y','5Y','ALL')."""
    if obj is None or len(obj) == 0 or tf in (None, "ALL", "All"):
        return obj
    days = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365, "5Y": 1825}.get(tf)
    if days is None:
        return obj
    return obj[obj.index >= obj.index.max() - pd.Timedelta(days=days)]


def fetch_asset_history(ticker: str, start_date: str, end_date: str):
    """Kept for backward compatibility; caching now happens inside fetch_data."""
    return MarketDataManager.fetch_data(ticker, start_date, end_date)
