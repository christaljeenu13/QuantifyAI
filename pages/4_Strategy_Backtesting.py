"""
QuantifyAI — Page 4: Strategy Backtesting (Matching Reference Screen 4).
Features dual-column layout: Strategy vs Benchmark chart on left (65%),
Performance Metrics card on right (35%), Drawdown chart and Trade History table below.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

import config
from src.data.asset_registry import get_default_registry
from src.data.market_data import MarketDataManager, slice_timeframe, data_status
from src.backtesting.engine import BacktestEngine
from src.backtesting.strategies import (
    generate_sma_crossover_signals,
    generate_ema_crossover_signals,
    generate_price_sma_signals,
    generate_buy_and_hold_signals
)
from src.backtesting.sensitivity import run_parameter_sensitivity
from src.reporting.export import trades_to_dataframe, dataframe_to_csv_bytes
from src.api.featherless_client import get_featherless_client
from src.ui.theme import apply_custom_theme, get_color_palette
from src.ui.components import (
    render_html,
    render_sidebar_branding,
    render_brand_footer
)
from src.ui.charts import (
    create_performance_line_chart,
    create_drawdown_chart,
    create_sensitivity_heatmap
)
from src.analytics.metrics import calculate_drawdown_series

try:
    st.set_page_config(page_title="Strategy Backtesting | QuantifyAI", page_icon="⏱️", layout="wide")
except Exception:
    pass
apply_custom_theme()
colors = get_color_palette()
registry = get_default_registry()
ai_client = get_featherless_client()

# Header matching Mockup Screen 4
render_html("""
<div style="margin-bottom: 1.2rem;">
    <h1 style="margin: 0; font-size: 1.75rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
        Strategy Backtesting
    </h1>
    <p style="margin: 2px 0 0 0; font-size: 0.88rem; color: #7e92a2;">
        Test and evaluate trading strategies on historical data.
    </p>
</div>
""")

# Control Filter Bar matching Mockup Screen 4
c1, c2, c3, c4, c5, c6, c7, c8, c_btn = st.columns([2.5, 2.5, 1.3, 1.3, 1.8, 1.8, 1.8, 1.4, 1.8])

with c1:
    asset_list = registry.list_assets()
    options_map = {f"{a['name']} ({a['ticker']})": a["ticker"] for a in asset_list}
    default_asset = [k for k in options_map.keys() if "BTC" in k]
    selected_asset = st.selectbox(
        "Asset",
        options=list(options_map.keys()),
        index=list(options_map.keys()).index(default_asset[0]) if default_asset else 0
    )
    ticker = options_map[selected_asset]

with c2:
    strategy_type = st.selectbox(
        "Strategy",
        ["SMA Crossover", "EMA Crossover", "Price vs SMA", "Buy & Hold"]
    )

with c3:
    short_ma = st.number_input("Short MA", min_value=3, max_value=100, value=20)

with c4:
    long_ma = st.number_input("Long MA", min_value=10, max_value=300, value=50)

today = datetime.now().date()
with c5:
    start_date = st.date_input("Start Date", today - timedelta(days=1095))
with c6:
    end_date = st.date_input("End Date", today)

with c7:
    capital = st.number_input("Initial Capital ($)", value=10000.0, step=1000.0)

with c8:
    fee_pct = st.number_input("Fee (%)", value=0.10, step=0.05)

with c_btn:
    st.write("")
    st.write("")
    run_btn = st.button("Run Backtest", type="primary", use_container_width=True)

# Fetch Market Data & Run Simulation
with st.spinner(f"Simulating strategy on {ticker}..."):
    df, meta = MarketDataManager.fetch_data(ticker, start_date=start_date, end_date=end_date)

if df.empty:
    st.error("No historical data available for backtesting.")
else:
    if strategy_type == "SMA Crossover":
        signals = generate_sma_crossover_signals(df, fast_period=short_ma, slow_period=long_ma)
    elif strategy_type == "EMA Crossover":
        signals = generate_ema_crossover_signals(df, fast_period=short_ma, slow_period=long_ma)
    elif strategy_type == "Price vs SMA":
        signals = generate_price_sma_signals(df, window=short_ma)
    else:
        signals = generate_buy_and_hold_signals(df)

    engine = BacktestEngine(
        initial_capital=capital,
        commission_rate=fee_pct / 100.0,
        slippage_rate=0.0005,
        execution_timing="next_open"
    )
    res = engine.run(df, signals)

    # Share the latest real backtest result with the AI Assistant page
    st.session_state["last_backtest"] = {
        "asset": ticker,
        "strategy": strategy_type,
        "period": f"{start_date} to {end_date}",
        "initial_capital": capital,
        "fee_pct": fee_pct,
        "strategy_metrics": {k: v for k, v in res.metrics.items() if isinstance(v, (int, float))},
        "benchmark_metrics": {k: v for k, v in res.benchmark_metrics.items() if isinstance(v, (int, float))},
    }

    if data_status(meta) == "snapshot":
        st.caption("⚠️ Yahoo Finance unreachable - backtest is running on locally saved snapshot data.")
    else:
        st.caption(f"Data: Yahoo Finance · {meta.get('rows', len(df))} sessions · {meta.get('start_date', '')} to {meta.get('end_date', '')}")

    # Main Split Row matching Mockup Screen 4 (65% Chart, 35% Metrics Card)
    col_strat_chart, col_strat_metrics = st.columns([65, 35])

    with col_strat_chart:
        render_html("<div style='font-weight: 700; font-size: 1.05rem; color: #ffffff; margin-bottom: 0.3rem;'>Strategy Performance</div>")
        bt_tf = st.segmented_control(
            "Chart window",
            options=["1M", "3M", "6M", "1Y", "ALL"],
            default="ALL",
            key="bt_timeframe",
            label_visibility="collapsed",
            help="Zooms the equity chart only. Metrics on the right always cover the full backtest."
        )

        chart_df = pd.DataFrame({
            "Strategy": res.equity_curve["Strategy_Equity"],
            "Buy & Hold": res.equity_curve["Benchmark_Equity"]
        })
        chart_df = slice_timeframe(chart_df, bt_tf)
        fig_strat = create_performance_line_chart(
            chart_df,
            title="",
            y_title="Portfolio Value ($)"
        )
        st.plotly_chart(fig_strat, use_container_width=True)

    with col_strat_metrics:
        sm = res.metrics
        render_html(f"""
<div class="quant-card" style="padding: 1.1rem 1.3rem;">
    <div class="quant-label" style="font-size: 0.8rem; margin-bottom: 0.6rem;">Performance Metrics</div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid {colors['border_teal']}; padding-bottom: 6px;">
        <span style="font-size: 0.82rem; color: #7e92a2;">Final Portfolio Value</span>
        <span class="quant-val-small" style="font-size: 1.05rem;">${sm['final_value']:,.2f}</span>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid {colors['border_teal']}; padding-bottom: 6px;">
        <span style="font-size: 0.82rem; color: #7e92a2;">Total Return</span>
        <span class="quant-delta-pos" style="font-size: 1rem;">{'+' if sm['total_return'] >= 0 else ''}{sm['total_return']*100:.1f}%</span>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid {colors['border_teal']}; padding-bottom: 6px;">
        <span style="font-size: 0.82rem; color: #7e92a2;">Annualized Return</span>
        <span style="font-family: 'JetBrains Mono'; font-weight: 600; color: #ffffff;">{sm['annualized_return']*100:.1f}%</span>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid {colors['border_teal']}; padding-bottom: 6px;">
        <span style="font-size: 0.82rem; color: #7e92a2;">Volatility</span>
        <span style="font-family: 'JetBrains Mono'; font-weight: 600; color: #ffffff;">{sm['annualized_volatility']*100:.1f}%</span>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid {colors['border_teal']}; padding-bottom: 6px;">
        <span style="font-size: 0.82rem; color: #7e92a2;">Sharpe Ratio</span>
        <span style="font-family: 'JetBrains Mono'; font-weight: 700; color: #00f2a9;">{sm['sharpe_ratio']:.2f}</span>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid {colors['border_teal']}; padding-bottom: 6px;">
        <span style="font-size: 0.82rem; color: #7e92a2;">Max Drawdown</span>
        <span class="quant-delta-neg" style="font-size: 1rem;">{sm['max_drawdown']*100:.1f}%</span>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid {colors['border_teal']}; padding-bottom: 6px;">
        <span style="font-size: 0.82rem; color: #7e92a2;">Total Trades</span>
        <span style="font-family: 'JetBrains Mono'; font-weight: 600; color: #ffffff;">{sm['total_trades']}</span>
    </div>
    <div style="display: flex; justify-content: space-between;">
        <span style="font-size: 0.82rem; color: #7e92a2;">Win Rate</span>
        <span style="font-family: 'JetBrains Mono'; font-weight: 600; color: #ffffff;">{sm['win_rate']:.1f}%</span>
    </div>
</div>
""")

    # Bottom Split Row matching Mockup Screen 4 (Drawdown Chart left, Trade History right)
    col_bt_dd, col_bt_trades = st.columns([45, 55])

    with col_bt_dd:
        render_html("<div style='font-weight: 700; font-size: 1rem; color: #ffffff; margin-bottom: 0.5rem;'>Drawdown</div>")
        strat_dd = calculate_drawdown_series(res.equity_curve["Strategy_Equity"])
        fig_dd_area = create_drawdown_chart(strat_dd, title="")
        st.plotly_chart(fig_dd_area, use_container_width=True)

    with col_bt_trades:
        render_html("<div style='font-weight: 700; font-size: 1rem; color: #ffffff; margin-bottom: 0.5rem;'>Trade History (Last 10 Trades)</div>")
        trades_df = trades_to_dataframe(res.trades)
        if not trades_df.empty:
            display_trades = trades_df.tail(10)[["Entry Date", "Status", "Entry Price", "Shares", "Net PnL", "Exit Fee"]]
            display_trades = display_trades.rename(columns={
                "Entry Date": "Date",
                "Status": "Signal",
                "Entry Price": "Price",
                "Shares": "Quantity",
                "Net PnL": "Value",
                "Exit Fee": "Fee"
            })
            st.dataframe(display_trades, use_container_width=True)
        else:
            st.info("No round-trip trades executed in this period.")

    # Parameter Sensitivity Expander
    with st.expander("🔥 Parameter Sensitivity Heatmap"):
        if st.button("Compute Sensitivity Grid"):
            with st.spinner("Computing 2D parameter grid..."):
                sens_df, _ = run_parameter_sensitivity(
                    df=df,
                    strategy_type=strategy_type if "Crossover" in strategy_type else "SMA Crossover",
                    fast_range=[10, 15, 20, 25, 30],
                    slow_range=[40, 50, 60, 70, 80],
                    metric_target="sharpe_ratio",
                    initial_capital=capital,
                    commission_rate=fee_pct / 100.0
                )
                fig_sens = create_sensitivity_heatmap(sens_df)
                st.plotly_chart(fig_sens, use_container_width=True)

    # Featherless AI Backtest Performance Critique
    st.markdown("---")
    ai_col1, ai_col2 = st.columns([4, 1])
    with ai_col1:
        st.markdown(
            "**🤖 Featherless AI Strategy Critique:** "
            "Generate institutional quantitative critique evaluating strategy efficiency, trading friction, and drawdowns."
        )
    with ai_col2:
        if st.button("🧠 Critique Strategy", type="secondary", use_container_width=True):
            with st.spinner("Featherless AI is analyzing trade log and execution telemetry..."):
                critique = ai_client.explain_backtest_performance(
                    strategy_name=strategy_type,
                    asset_name=selected_asset,
                    strat_metrics=res.metrics,
                    bench_metrics=res.benchmark_metrics
                )
                st.markdown(
                    f"""
                    <div class="quant-card" style="border-left: 3px solid #00f2a9; margin-top: 1rem;">
                        <div style="font-size: 0.85rem; font-weight: 700; color: #00f2a9; margin-bottom: 6px;">
                            🧠 INSTITUTIONAL STRATEGY CRITIQUE & DECOMPOSITION
                        </div>
                        {critique}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

render_brand_footer()
