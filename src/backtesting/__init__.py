"""Backtesting engine and quantitative strategies package initialization."""
from .strategies import (
    generate_sma_crossover_signals,
    generate_ema_crossover_signals,
    generate_price_sma_signals,
    generate_rsi_strategy_signals,
    generate_buy_and_hold_signals
)
from .engine import BacktestEngine, BacktestResult
from .sensitivity import run_parameter_sensitivity
