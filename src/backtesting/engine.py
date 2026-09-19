"""
Event-Driven Strategy Backtesting Engine.
Executes trading signals with strict lookahead prevention, trade cost accounting,
cash and position conservation, and benchmarking.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import config
from src.analytics.metrics import (
    calculate_annualized_volatility,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    calculate_cagr
)


@dataclass
class Trade:
    trade_id: int
    entry_date: str
    exit_date: str
    entry_price: float
    exit_price: float
    shares: float
    entry_fee: float
    exit_fee: float
    gross_pnl: float
    net_pnl: float
    return_pct: float
    duration_days: int
    is_open: bool = False


@dataclass
class BacktestResult:
    equity_curve: pd.DataFrame
    trades: List[Trade]
    metrics: Dict[str, Any]
    benchmark_metrics: Dict[str, Any]
    execution_notes: str


class BacktestEngine:
    """Institutional-grade backtesting engine."""

    def __init__(
        self,
        initial_capital: float = config.DEFAULT_INITIAL_CAPITAL,
        commission_rate: float = config.DEFAULT_TRANSACTION_FEE,
        slippage_rate: float = 0.0005,
        execution_timing: str = "next_open",
        risk_free_rate: float = config.DEFAULT_RISK_FREE_RATE
    ):
        self.initial_capital = float(initial_capital)
        self.commission_rate = float(commission_rate)
        self.slippage_rate = float(slippage_rate)
        self.execution_timing = execution_timing.lower()
        self.risk_free_rate = float(risk_free_rate)

    def run(self, df: pd.DataFrame, target_signals: pd.Series) -> BacktestResult:
        """
        Execute backtest simulation.
        df: DataFrame containing at least 'Close', and 'Open' if execution_timing='next_open'.
        target_signals: pd.Series with target position {0, 1} generated at session Close.
        """
        if df.empty or len(df) < 2:
            return self._empty_result("Insufficient historical data for backtesting.")

        # Ensure index aligned
        common_idx = df.index.intersection(target_signals.index)
        df_aligned = df.loc[common_idx].sort_index()
        signals_aligned = target_signals.loc[common_idx].sort_index()

        n = len(df_aligned)
        if n < 2:
            return self._empty_result("Aligned data has fewer than 2 periods.")

        # State tracking
        cash = self.initial_capital
        shares = 0.0
        current_pos = 0  # 0 = Flat, 1 = Long
        trades: List[Trade] = []
        trade_counter = 0
        total_fees_paid = 0.0

        # Open trade tracker
        active_trade_entry = None

        # Tracking series
        portfolio_equity = np.zeros(n)
        cash_history = np.zeros(n)
        holdings_history = np.zeros(n)
        benchmark_equity = np.zeros(n)

        # Benchmark setup (Buy & Hold from bar 1 execution)
        b_first_exec_price = (
            df_aligned["Open"].iloc[1]
            if self.execution_timing == "next_open" and "Open" in df_aligned.columns
            else df_aligned["Close"].iloc[1]
        )
        b_fee = self.initial_capital * self.commission_rate
        b_capital_after_fee = self.initial_capital - b_fee
        b_shares = b_capital_after_fee / b_first_exec_price if b_first_exec_price > 0 else 0.0
        b_cash = self.initial_capital - (b_shares * b_first_exec_price + b_fee)

        # Day 0: Initial state before any signal can execute
        portfolio_equity[0] = self.initial_capital
        cash_history[0] = self.initial_capital
        holdings_history[0] = 0.0
        benchmark_equity[0] = self.initial_capital

        # Simulation loop:
        # At day i-1 Close, signal is generated: signals_aligned.iloc[i-1]
        # At day i, signal executes at Open (or Close): df_aligned.iloc[i]
        for i in range(1, n):
            current_date = df_aligned.index[i]
            prev_signal = int(signals_aligned.iloc[i - 1])

            # Determine execution price for today
            if self.execution_timing == "next_open" and "Open" in df_aligned.columns:
                base_exec_price = float(df_aligned["Open"].iloc[i])
            else:
                base_exec_price = float(df_aligned["Close"].iloc[i])

            close_today = float(df_aligned["Close"].iloc[i])

            # Check if position rebalancing needed
            if prev_signal != current_pos:
                if prev_signal == 1 and current_pos == 0:
                    # BUY SIGNAL
                    exec_price = base_exec_price * (1.0 + self.slippage_rate)
                    if exec_price > 0 and cash > 0:
                        # Allocate entire cash minus estimated commission
                        eff_capital = cash / (1.0 + self.commission_rate)
                        shares_to_buy = eff_capital / exec_price
                        gross_cost = shares_to_buy * exec_price
                        fee = gross_cost * self.commission_rate
                        total_cost = gross_cost + fee

                        if total_cost <= cash + 1e-6:
                            cash -= total_cost
                            shares += shares_to_buy
                            current_pos = 1
                            total_fees_paid += fee
                            trade_counter += 1
                            active_trade_entry = {
                                "id": trade_counter,
                                "date": current_date.strftime("%Y-%m-%d"),
                                "price": exec_price,
                                "shares": shares_to_buy,
                                "fee": fee,
                                "bar_idx": i
                            }

                elif prev_signal == 0 and current_pos == 1:
                    # SELL SIGNAL
                    exec_price = base_exec_price * (1.0 - self.slippage_rate)
                    if exec_price > 0 and shares > 0:
                        gross_proceeds = shares * exec_price
                        fee = gross_proceeds * self.commission_rate
                        net_proceeds = gross_proceeds - fee

                        cash += net_proceeds
                        total_fees_paid += fee

                        if active_trade_entry:
                            entry_p = active_trade_entry["price"]
                            entry_fee = active_trade_entry["fee"]
                            gross_pnl = gross_proceeds - (shares * entry_p)
                            net_pnl = gross_pnl - entry_fee - fee
                            cost_basis = shares * entry_p + entry_fee
                            ret_pct = (net_pnl / cost_basis) if cost_basis > 0 else 0.0

                            trades.append(Trade(
                                trade_id=active_trade_entry["id"],
                                entry_date=active_trade_entry["date"],
                                exit_date=current_date.strftime("%Y-%m-%d"),
                                entry_price=entry_p,
                                exit_price=exec_price,
                                shares=shares,
                                entry_fee=entry_fee,
                                exit_fee=fee,
                                gross_pnl=gross_pnl,
                                net_pnl=net_pnl,
                                return_pct=ret_pct,
                                duration_days=(i - active_trade_entry["bar_idx"]),
                                is_open=False
                            ))
                            active_trade_entry = None

                        shares = 0.0
                        current_pos = 0

            # Record end-of-day equity
            position_val = shares * close_today
            total_val = cash + position_val
            portfolio_equity[i] = total_val
            cash_history[i] = cash
            holdings_history[i] = position_val

            # Benchmark mark to market
            benchmark_equity[i] = b_cash + (b_shares * close_today)

        # Handle terminal open position
        if current_pos == 1 and active_trade_entry and shares > 0:
            final_price = float(df_aligned["Close"].iloc[-1])
            gross_val = shares * final_price
            est_fee = gross_val * self.commission_rate
            net_val = gross_val - est_fee
            entry_p = active_trade_entry["price"]
            entry_fee = active_trade_entry["fee"]
            gross_pnl = gross_val - (shares * entry_p)
            net_pnl = gross_pnl - entry_fee - est_fee
            cost_basis = shares * entry_p + entry_fee
            ret_pct = (net_pnl / cost_basis) if cost_basis > 0 else 0.0

            trades.append(Trade(
                trade_id=active_trade_entry["id"],
                entry_date=active_trade_entry["date"],
                exit_date=df_aligned.index[-1].strftime("%Y-%m-%d") + " (Open)",
                entry_price=entry_p,
                exit_price=final_price,
                shares=shares,
                entry_fee=entry_fee,
                exit_fee=est_fee,
                gross_pnl=gross_pnl,
                net_pnl=net_pnl,
                return_pct=ret_pct,
                duration_days=(n - 1 - active_trade_entry["bar_idx"]),
                is_open=True
            ))

        # Assemble Equity Curve DataFrame
        equity_df = pd.DataFrame(
            {
                "Strategy_Equity": portfolio_equity,
                "Benchmark_Equity": benchmark_equity,
                "Cash": cash_history,
                "Holdings_Value": holdings_history
            },
            index=df_aligned.index
        )
        equity_df["Strategy_Return"] = equity_df["Strategy_Equity"].pct_change().fillna(0.0)
        equity_df["Benchmark_Return"] = equity_df["Benchmark_Equity"].pct_change().fillna(0.0)

        # Calculate Performance Metrics
        strat_metrics = self._compute_performance_metrics(
            equity_df["Strategy_Equity"], equity_df["Strategy_Return"], trades, total_fees_paid
        )
        bench_metrics = self._compute_performance_metrics(
            equity_df["Benchmark_Equity"], equity_df["Benchmark_Return"], [], b_fee
        )

        exec_notes = (
            f"Executed using zero-lookahead assumption ({self.execution_timing}). "
            f"Trading fees: {self.commission_rate * 100:.2f}%, Slippage: {self.slippage_rate * 100:.2f}%. "
            f"Starting capital: ${self.initial_capital:,.2f}."
        )

        return BacktestResult(
            equity_curve=equity_df,
            trades=trades,
            metrics=strat_metrics,
            benchmark_metrics=bench_metrics,
            execution_notes=exec_notes
        )

    def _compute_performance_metrics(
        self, equity_series: pd.Series, return_series: pd.Series, trades: List[Trade], total_fees: float
    ) -> Dict[str, Any]:
        """Compile statistical metrics from equity curve and trades."""
        start_val = float(equity_series.iloc[0])
        end_val = float(equity_series.iloc[-1])
        total_return = (end_val - start_val) / start_val if start_val > 0 else 0.0

        cagr = calculate_cagr(equity_series)
        vol = calculate_annualized_volatility(return_series)
        sharpe = calculate_sharpe_ratio(return_series, risk_free_rate=self.risk_free_rate)
        mdd = calculate_max_drawdown(equity_series)

        # Trade statistics
        closed_trades = [t for t in trades if not t.is_open]
        total_trades = len(trades)
        winning_trades = [t for t in closed_trades if t.net_pnl > 0]
        losing_trades = [t for t in closed_trades if t.net_pnl <= 0]
        win_rate = (len(winning_trades) / len(closed_trades) * 100.0) if closed_trades else 0.0

        gross_profits = sum(t.net_pnl for t in winning_trades)
        gross_losses = abs(sum(t.net_pnl for t in losing_trades))
        profit_factor = (gross_profits / gross_losses) if gross_losses > 0 else (999.0 if gross_profits > 0 else 0.0)

        return {
            "initial_capital": start_val,
            "final_value": end_val,
            "total_return": float(total_return),
            "annualized_return": float(cagr),
            "annualized_volatility": float(vol),
            "sharpe_ratio": float(sharpe),
            "max_drawdown": float(mdd),
            "total_trades": total_trades,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": float(win_rate),
            "profit_factor": float(profit_factor),
            "total_fees_paid": float(total_fees)
        }

    def _empty_result(self, msg: str) -> BacktestResult:
        empty_df = pd.DataFrame(columns=["Strategy_Equity", "Benchmark_Equity"])
        return BacktestResult(
            equity_curve=empty_df,
            trades=[],
            metrics={
                "initial_capital": self.initial_capital,
                "final_value": self.initial_capital,
                "total_return": 0.0,
                "annualized_return": 0.0,
                "annualized_volatility": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "total_trades": 0,
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "total_fees_paid": 0.0
            },
            benchmark_metrics={},
            execution_notes=msg
        )
