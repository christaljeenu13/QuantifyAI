"""
Storage Manager.
Handles persistent storage of user portfolios, saved backtests, and analysis logs via SQLite.
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import config

DB_PATH = config.BASE_DIR / "quantifyai.db"


class StorageManager:
    """SQLite-backed persistent repository for saved portfolios and backtest runs."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_tables()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        """Create tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Saved Portfolios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS saved_portfolios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    weights_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            """)
            # Saved Backtests
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS saved_backtests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    ticker TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    params_json TEXT NOT NULL,
                    metrics_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_portfolio(self, name: str, weights: Dict[str, float], notes: str = "") -> int:
        """Save a portfolio allocation configuration."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO saved_portfolios (name, weights_json, notes) VALUES (?, ?, ?)",
                (name, json.dumps(weights), notes)
            )
            conn.commit()
            return cursor.lastrowid

    def list_portfolios(self) -> List[Dict[str, Any]]:
        """List all saved portfolios."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM saved_portfolios ORDER BY created_at DESC")
            rows = cursor.fetchall()
            results = []
            for r in rows:
                results.append({
                    "id": r["id"],
                    "name": r["name"],
                    "weights": json.loads(r["weights_json"]),
                    "created_at": r["created_at"],
                    "notes": r["notes"]
                })
            return results

    def save_backtest_run(
        self,
        name: str,
        ticker: str,
        strategy: str,
        params: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> int:
        """Save a backtest execution summary."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO saved_backtests 
                   (name, ticker, strategy, params_json, metrics_json) 
                   VALUES (?, ?, ?, ?, ?)""",
                (name, ticker, strategy, json.dumps(params), json.dumps(metrics))
            )
            conn.commit()
            return cursor.lastrowid

    def list_backtests(self, limit: int = 15) -> List[Dict[str, Any]]:
        """List recently saved backtest executions."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM saved_backtests ORDER BY created_at DESC LIMIT ?", (limit,)
            )
            rows = cursor.fetchall()
            results = []
            for r in rows:
                results.append({
                    "id": r["id"],
                    "name": r["name"],
                    "ticker": r["ticker"],
                    "strategy": r["strategy"],
                    "params": json.loads(r["params_json"]),
                    "metrics": json.loads(r["metrics_json"]),
                    "created_at": r["created_at"]
                })
            return results
