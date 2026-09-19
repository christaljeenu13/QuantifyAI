"""
Strategy Parameter Sensitivity Grid Module.
Evaluates strategy robustness across a matrix of parameter permutations.
"""

from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np
from .strategies import generate_sma_crossover_signals, generate_ema_crossover_signals
from .engine import BacktestEngine


def run_parameter_sensitivity(
    df: pd.DataFrame,
    strategy_type: str = "SMA Crossover",
    fast_range: List[int] = [10, 15, 20, 25, 30],
    slow_range: List[int] = [40, 50, 60, 70, 80],
    metric_target: str = "sharpe_ratio",
    initial_capital: float = 10000.0,
    commission_rate: float = 0.001
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Run 2D sensitivity matrix.
    Rows: Fast Window
    Columns: Slow Window
    Values: metric_target (e.g., 'sharpe_ratio' or 'total_return')
    """
    matrix_data = []
    engine = BacktestEngine(
        initial_capital=initial_capital,
        commission_rate=commission_rate,
        execution_timing="next_open"
    )

    best_val = -999.0
    best_params = {"fast": None, "slow": None, "value": None}

    for fast in fast_range:
        row_vals = []
        for slow in slow_range:
            if fast >= slow:
                row_vals.append(np.nan)
                continue

            if strategy_type == "EMA Crossover":
                signals = generate_ema_crossover_signals(df, fast_period=fast, slow_period=slow)
            else:
                signals = generate_sma_crossover_signals(df, fast_period=fast, slow_period=slow)

            res = engine.run(df, signals)
            val = res.metrics.get(metric_target, 0.0)

            # Check if best
            if not np.isnan(val) and val > best_val:
                best_val = val
                best_params = {"fast": fast, "slow": slow, "value": val}

            row_vals.append(val)
        matrix_data.append(row_vals)

    grid_df = pd.DataFrame(matrix_data, index=fast_range, columns=slow_range)
    grid_df.index.name = "Fast Period"
    grid_df.columns.name = "Slow Period"

    summary = {
        "strategy": strategy_type,
        "metric": metric_target,
        "best_fast": best_params["fast"],
        "best_slow": best_params["slow"],
        "best_score": best_params["value"]
    }

    return grid_df, summary
