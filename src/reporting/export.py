"""
Reporting and Data Export Module.
Formats and serializes backtests, comparison matrices, and historical datasets to CSV.
"""

from typing import List, Dict, Any
import pandas as pd
from src.backtesting.engine import Trade


def trades_to_dataframe(trades: List[Trade]) -> pd.DataFrame:
    """Convert list of Trade objects to a clean display/export DataFrame."""
    if not trades:
        return pd.DataFrame(columns=[
            "Trade #", "Entry Date", "Exit Date", "Entry Price", "Exit Price",
            "Shares", "Entry Fee", "Exit Fee", "Net PnL", "Return %", "Duration (Days)", "Status"
        ])

    rows = []
    for t in trades:
        rows.append({
            "Trade #": t.trade_id,
            "Entry Date": t.entry_date,
            "Exit Date": t.exit_date,
            "Entry Price": round(t.entry_price, 4),
            "Exit Price": round(t.exit_price, 4),
            "Shares": round(t.shares, 4),
            "Entry Fee": round(t.entry_fee, 2),
            "Exit Fee": round(t.exit_fee, 2),
            "Net PnL": round(t.net_pnl, 2),
            "Return %": round(t.return_pct * 100.0, 2),
            "Duration (Days)": t.duration_days,
            "Status": "Open" if t.is_open else "Closed"
        })
    return pd.DataFrame(rows)


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Serialize DataFrame to UTF-8 CSV bytes for Streamlit download button."""
    return df.to_csv(index=True).encode("utf-8")
