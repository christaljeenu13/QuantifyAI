"""
QuantifyAI — Page 5: Portfolio Risk Lab (Matching Reference Screen 5).
Features left weight allocation panel (35%), right performance chart (65%),
horizontal Portfolio Metrics bar, and three-column bottom grid:
Asset Allocation Donut, Correlation Matrix, and Risk Contribution bar chart.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

import config
from src.data.asset_registry import get_default_registry
from src.data.market_data import MarketDataManager, slice_timeframe, data_status
from src.analytics.risk import calculate_portfolio_metrics
from src.api.featherless_client import get_featherless_client
from src.ui.theme import apply_custom_theme, get_color_palette
from src.ui.components import (
    render_html,
    render_sidebar_branding,
    render_brand_footer
)
from src.ui.charts import (
    create_performance_line_chart,
    create_allocation_donut,
    create_correlation_heatmap,
    create_risk_contribution_bar_chart
)

try:
    st.set_page_config(page_title="Portfolio Risk Lab | QuantifyAI", page_icon="🛡️", layout="wide")
except Exception:
    pass
apply_custom_theme()
colors = get_color_palette()
registry = get_default_registry()
ai_client = get_featherless_client()

# Header matching Mockup Screen 5
render_html("""
<div style="margin-bottom: 1.2rem;">
    <h1 style="margin: 0; font-size: 1.75rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
        Portfolio Risk Lab
    </h1>
    <p style="margin: 2px 0 0 0; font-size: 0.88rem; color: #7e92a2;">
        Build and analyze multi-asset portfolios.
    </p>
</div>
""")

# Top Split Row matching Mockup Screen 5 (35% Left Allocation Panel, 65% Right Performance Chart)
col_alloc, col_port_chart = st.columns([35, 65])

with col_alloc:
    render_html("<div style='font-weight: 700; font-size: 1rem; color: #ffffff; margin-bottom: 0.6rem;'>Select Assets & Weights</div>")
    
    w_gold = st.slider("Gold (XAU/USD)", min_value=0, max_value=100, value=30, step=5, format="%d%%")
    w_btc = st.slider("Bitcoin (BTC)", min_value=0, max_value=100, value=40, step=5, format="%d%%")
    w_nvda = st.slider("NVIDIA (NVDA)", min_value=0, max_value=100, value=30, step=5, format="%d%%")

    total_w = w_gold + w_btc + w_nvda
    is_100 = (total_w == 100)

    color_tot = "#00f2a9" if is_100 else "#f87171"
    alloc_html = f"""
<div style="display: flex; justify-content: space-between; align-items: center; margin: 0.8rem 0; padding: 6px 12px; background: #0b151d; border-radius: 6px; border: 1px solid {colors['border_teal']};">
    <span style="font-size: 0.84rem; color: #94a3b8; font-weight: 600;">Total Allocation</span>
    <span style="font-family: 'JetBrains Mono'; font-weight: 700; color: {color_tot}; font-size: 1.1rem;">{total_w}%</span>
</div>
"""
    render_html(alloc_html)

    gen_btn = st.button("Generate Portfolio", type="primary", use_container_width=True)

    rl_tf = st.segmented_control(
        "Analysis window",
        options=["1M", "3M", "6M", "1Y", "ALL"],
        default="ALL",
        key="rl_timeframe",
        help="Trailing window for every portfolio metric and chart. ALL = last 2 years."
    )

# Fetch aligned market data for the 3 assets
end_d = datetime.now()
start_d = end_d - timedelta(days=730)

with st.spinner("Calculating portfolio telemetry..."):
    aligned_df, port_meta = MarketDataManager.fetch_multiple_assets(
        ["GLD", "BTC-USD", "NVDA"],
        start_date=start_d,
        end_date=end_d,
        align_method="ffill"
    )

# Apply the selected window BEFORE computing metrics so every number and chart matches it
_windowed = slice_timeframe(aligned_df, rl_tf)
if len(_windowed) >= 20:
    aligned_df = _windowed
elif not aligned_df.empty:
    st.info("Selected window has too few sessions for reliable risk metrics - using the full 2-year range.")

_feed = data_status(port_meta)
if _feed == "snapshot":
    st.caption("⚠️ Yahoo Finance unreachable for at least one asset - using locally saved snapshot data.")
elif _feed == "unavailable":
    st.caption("❌ No market data available.")

if aligned_df.empty or not is_100:
    with col_port_chart:
        if not is_100:
            st.error(f"Weights currently sum to {total_w}%. Please adjust sliders to equal exactly 100%.")
        else:
            st.info("Loading asset data...")
else:
    weights_dict = {
        "GLD": w_gold / 100.0,
        "BTC-USD": w_btc / 100.0,
        "NVDA": w_nvda / 100.0
    }
    display_weights = {
        "Gold": w_gold / 100.0,
        "Bitcoin": w_btc / 100.0,
        "NVIDIA": w_nvda / 100.0
    }

    p_metrics = calculate_portfolio_metrics(
        aligned_prices=aligned_df,
        weights=weights_dict,
        risk_free_rate=config.DEFAULT_RISK_FREE_RATE
    )

    # Share the latest real portfolio result with the AI Assistant page
    st.session_state["last_portfolio"] = {
        "weights": display_weights,
        "window": rl_tf or "ALL",
        "period": f"{aligned_df.index.min().strftime('%Y-%m-%d')} to {aligned_df.index.max().strftime('%Y-%m-%d')}",
        "metrics": {
            k: v for k, v in p_metrics.items()
            if isinstance(v, (int, float))
        },
    }

    with col_port_chart:
        render_html(f"<div style='font-weight: 700; font-size: 1.05rem; color: #ffffff; margin-bottom: 0.3rem;'>Portfolio Performance · {rl_tf or 'ALL'}</div>")
        port_series_df = pd.DataFrame({"Portfolio": p_metrics["wealth_series"]})
        fig_port_line = create_performance_line_chart(port_series_df, title="", y_title="Rebased Value", is_normalized=True)
        st.plotly_chart(fig_port_line, use_container_width=True)

    # Middle Horizontal Row: Portfolio Metrics Card matching Mockup Screen 5
    port_metrics_card = f"""
<div class="quant-card" style="margin-top: 0.8rem; margin-bottom: 1.2rem; padding: 1.1rem 1.4rem;">
    <div class="quant-label" style="margin-bottom: 0.6rem;">Portfolio Metrics</div>
    <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; text-align: left;">
        <div>
            <div style="font-size: 0.76rem; color: #7e92a2;">Total Return</div>
            <div class="quant-delta-pos" style="font-size: 1.4rem; font-weight: 700;">{'+' if p_metrics['total_return']>=0 else ''}{p_metrics['total_return']*100:.1f}%</div>
        </div>
        <div>
            <div style="font-size: 0.76rem; color: #7e92a2;">Annualized Return</div>
            <div class="quant-val" style="font-size: 1.4rem;">{p_metrics['annualized_return']*100:.1f}%</div>
        </div>
        <div>
            <div style="font-size: 0.76rem; color: #7e92a2;">Volatility</div>
            <div class="quant-val" style="font-size: 1.4rem;">{p_metrics['annualized_volatility']*100:.1f}%</div>
        </div>
        <div>
            <div style="font-size: 0.76rem; color: #7e92a2;">Sharpe Ratio</div>
            <div class="quant-val" style="font-size: 1.4rem; color: #00f2a9;">{p_metrics['sharpe_ratio']:.2f}</div>
        </div>
        <div>
            <div style="font-size: 0.76rem; color: #7e92a2;">Max Drawdown</div>
            <div class="quant-delta-neg" style="font-size: 1.4rem; font-weight: 700;">{p_metrics['max_drawdown']*100:.1f}%</div>
        </div>
    </div>
</div>
"""
    render_html(port_metrics_card)

    # Bottom Row: 3 Columns matching Mockup Screen 5
    c_donut, c_matrix, c_contrib = st.columns(3)

    with c_donut:
        fig_donut = create_allocation_donut(display_weights)
        st.plotly_chart(fig_donut, use_container_width=True)

    with c_matrix:
        renamed_corr = p_metrics["corr_matrix"].rename(
            index={"GLD": "Gold", "BTC-USD": "Bitcoin", "NVDA": "NVIDIA"},
            columns={"GLD": "Gold", "BTC-USD": "Bitcoin", "NVDA": "NVIDIA"}
        )
        fig_m = create_correlation_heatmap(renamed_corr)
        st.plotly_chart(fig_m, use_container_width=True)

    with c_contrib:
        risk_raw = p_metrics["risk_contributions"]
        label_map = {"GLD": "Gold", "BTC-USD": "Bitcoin", "NVDA": "NVIDIA"}
        risk_df = pd.DataFrame([
            {"Asset": label_map.get(t, t), "Risk Contribution (%)": d["prc"]}
            for t, d in risk_raw.items()
        ])
        fig_rc = create_risk_contribution_bar_chart(risk_df)
        st.plotly_chart(fig_rc, use_container_width=True)

    # Featherless AI Portfolio Risk Explanation
    st.markdown("---")
    ai_col1, ai_col2 = st.columns([4, 1])
    with ai_col1:
        st.markdown(
            "**🤖 Featherless AI Portfolio Risk Interpretation:** "
            "Analyze diversification benefits, covariance cancellation, and tail-risk exposure (VaR/CVaR)."
        )
    with ai_col2:
        if st.button("🧠 Explain Portfolio Risk", type="secondary", use_container_width=True):
            with st.spinner("Featherless AI is synthesizing multi-asset covariance analysis..."):
                analysis = ai_client.explain_portfolio_risk(
                    weights=display_weights,
                    port_metrics=p_metrics
                )
                st.markdown(
                    f"""
                    <div class="quant-card" style="border-left: 3px solid #00f2a9; margin-top: 1rem;">
                        <div style="font-size: 0.85rem; font-weight: 700; color: #00f2a9; margin-bottom: 6px;">
                            🧠 INSTITUTIONAL PORTFOLIO DIVERSIFICATION INTERPRETATION
                        </div>
                        {analysis}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

render_brand_footer()
