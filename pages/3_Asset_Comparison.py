"""
QuantifyAI — Page 3: Asset Comparison (Matching Reference Screen 3).
Features multi-asset badge selector, sub-tabs (Performance, Risk Metrics, Correlation, Drawdown, Returns Distribution),
Normalized Base=100 spline chart, Comparison Summary table, Correlation Heatmap, and Risk-Return scatter plot.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

import config
from src.data.asset_registry import get_default_registry
from src.data.market_data import MarketDataManager, slice_timeframe, data_status
from src.comparison.comparative_analytics import (
    align_multi_asset_data,
    normalize_price_series,
    compute_comparison_summary
)
from src.analytics.metrics import calculate_drawdown_series, calculate_daily_returns
from src.reporting.export import dataframe_to_csv_bytes
from src.api.featherless_client import get_featherless_client
from src.ui.theme import apply_custom_theme, get_color_palette
from src.ui.components import (
    render_sidebar_branding,
    render_brand_footer
)
from src.ui.charts import (
    create_performance_line_chart,
    create_correlation_heatmap,
    create_risk_return_scatter,
    create_daily_returns_bar_chart
)

try:
    st.set_page_config(page_title="Asset Comparison | QuantifyAI", page_icon="⚖️", layout="wide")
except Exception:
    pass
apply_custom_theme()
colors = get_color_palette()
registry = get_default_registry()
ai_client = get_featherless_client()

# Header matching Mockup Screen 3
st.markdown(
    """
    <div style="margin-bottom: 1.2rem;">
        <h1 style="margin: 0; font-size: 1.75rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
            Asset Comparison
        </h1>
        <p style="margin: 2px 0 0 0; font-size: 0.88rem; color: #7e92a2;">
            Compare multiple assets side by side.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Control Filter Bar (Matching Mockup Screen 3)
c_assets, c_date, c_btn = st.columns([5, 4, 1.5])

with c_assets:
    asset_list = registry.list_assets()
    options_map = {f"{a['name']} ({a['ticker']})": a["ticker"] for a in asset_list}
    default_tickers = ["Gold (GLD)", "Bitcoin (BTC-USD)", "NVIDIA (NVDA)"]
    default_keys = [k for k in options_map.keys() if any(d in k for d in ["Gold", "Bitcoin", "NVIDIA"])]

    selected_keys = st.multiselect(
        "Select Assets",
        options=list(options_map.keys()),
        default=default_keys
    )
    selected_tickers = [options_map[k] for k in selected_keys]

today = datetime.now().date()
with c_date:
    d1, d2 = st.columns(2)
    with d1:
        start_date = st.date_input("Start Date", today - timedelta(days=730))
    with d2:
        end_date = st.date_input("End Date", today)

with c_btn:
    st.write("")
    st.write("")
    compare_btn = st.button("Compare", type="primary", use_container_width=True)

if len(selected_tickers) < 2:
    st.warning("⚠️ Please select at least two assets to initiate multi-asset comparison.")
else:
    with st.spinner("Synchronizing multi-asset series..."):
        aligned_df, comp_meta = MarketDataManager.fetch_multiple_assets(
            tickers=selected_tickers,
            start_date=start_date,
            end_date=end_date,
            align_method="ffill"
        )

    if aligned_df.empty or len(aligned_df) < 5:
        st.error("Insufficient overlapping historical data for the chosen instruments.")
    else:
        # Simplify display names to match Mockup ("Gold", "Bitcoin", "NVIDIA")
        col_names = {
            "GLD": "Gold (GLD)",
            "GC=F": "Gold (GC=F)",
            "BTC-USD": "Bitcoin (BTC)",
            "NVDA": "NVIDIA (NVDA)",
            "SPY": "S&P 500 (SPY)"
        }
        renamed_df = aligned_df.rename(columns=lambda c: col_names.get(c, c))

        # Working timeframe selector - slices every panel below (performance, risk, correlation, drawdown, distributions)
        cmp_tf = st.segmented_control(
            "Timeframe",
            options=["1M", "3M", "6M", "1Y", "ALL"],
            default="ALL",
            key="cmp_timeframe",
            help="Trailing window applied to all comparison panels. ALL = the full date range selected above."
        )
        _windowed = slice_timeframe(renamed_df, cmp_tf)
        if len(_windowed) >= 5:
            renamed_df = _windowed
        else:
            st.info("Selected timeframe has too few trading sessions - showing the full date range instead.")

        _feed = data_status(comp_meta)
        if _feed == "snapshot":
            st.caption("⚠️ Yahoo Finance unreachable for at least one asset - using locally saved snapshot data.")
        else:
            st.caption(f"Data: Yahoo Finance · {len(renamed_df)} sessions · {renamed_df.index.min().strftime('%Y-%m-%d')} to {renamed_df.index.max().strftime('%Y-%m-%d')}")

        # Tabs matching Mockup Screen 3:
        # Performance | Risk Metrics | Correlation | Drawdown | Returns Distribution
        tab_perf, tab_risk, tab_corr, tab_dd, tab_dist = st.tabs([
            "Performance",
            "Risk Metrics",
            "Correlation",
            "Drawdown",
            "Returns Distribution"
        ])

        norm_df = normalize_price_series(renamed_df, base_value=100.0)
        summary_df = compute_comparison_summary(renamed_df, risk_free_rate=config.DEFAULT_RISK_FREE_RATE)
        returns_df = renamed_df.pct_change().dropna()
        corr_matrix = returns_df.corr()

        with tab_perf:
            st.markdown(
                "<div style='font-weight: 700; font-size: 1.05rem; color: #ffffff; margin-bottom: 0.3rem;'>"
                f"Normalized Performance (Base = 100) · {cmp_tf or 'ALL'}</div>",
                unsafe_allow_html=True
            )
            fig_norm = create_performance_line_chart(
                norm_df,
                title="",
                y_title="Rebased Value",
                is_normalized=True
            )
            st.plotly_chart(fig_norm, use_container_width=True, key="comp_fig_norm")

            # Two columns below matching Mockup Screen 3
            col_summary, col_right = st.columns([55, 45])

            with col_summary:
                st.markdown("<div style='font-weight: 700; font-size: 1rem; color: #ffffff; margin-bottom: 0.5rem;'>Comparison Summary</div>", unsafe_allow_html=True)
                styled_sum = summary_df.style.format({
                    "Start Price": "${:,.2f}",
                    "End Price": "${:,.2f}",
                    "Total Return": "{:+.1%}",
                    "Annualized Return": "{:+.1%}",
                    "Annualized Volatility": "{:.1%}",
                    "Sharpe Ratio": "{:.2f}",
                    "Max Drawdown": "{:.1%}"
                })
                st.dataframe(styled_sum, use_container_width=True)

                csv_data = dataframe_to_csv_bytes(summary_df)
                st.download_button(
                    label="⬇️ Export Comparison Summary (CSV)",
                    data=csv_data,
                    file_name="comparison_summary.csv",
                    mime="text/csv"
                )

            with col_right:
                st.markdown("<div style='font-weight: 700; font-size: 1rem; color: #ffffff; margin-bottom: 0.5rem;'>Correlation & Risk Profile</div>", unsafe_allow_html=True)
                sub_c1, sub_c2 = st.tabs(["Heatmap", "Risk vs Return"])
                with sub_c1:
                    fig_c = create_correlation_heatmap(corr_matrix)
                    st.plotly_chart(fig_c, use_container_width=True, key="comp_fig_corr_small")
                with sub_c2:
                    fig_s = create_risk_return_scatter(summary_df)
                    st.plotly_chart(fig_s, use_container_width=True, key="comp_fig_scatter_small")

        with tab_risk:
            st.markdown("""
                <div style="margin-bottom: 1.1rem;">
                    <div style="font-size: 1.25rem; font-weight: 800; color: #ffffff;">🛡️ Risk vs. Return & Statistical Profile</div>
                    <div style="font-size: 0.82rem; color: #94a3b8;">Evaluate capital efficiency, Sharpe ratio frontiers, and historical volatility tradeoffs across all selected instruments.</div>
                </div>
            """, unsafe_allow_html=True)

            # Leaderboard metrics
            if not summary_df.empty:
                best_sharpe_row = summary_df.loc[summary_df["Sharpe Ratio"].idxmax()]
                min_vol_row = summary_df.loc[summary_df["Annualized Volatility"].idxmin()]
                max_ret_row = summary_df.loc[summary_df["Annualized Return"].idxmax()]
                min_dd_row = summary_df.loc[summary_df["Max Drawdown"].idxmax()]

                r1, r2, r3, r4 = st.columns(4)
                with r1:
                    st.markdown(f"""
                        <div style="background: rgba(0, 242, 169, 0.08); border: 1px solid rgba(0, 242, 169, 0.3); border-radius: 10px; padding: 12px 14px;">
                            <div style="font-size: 0.72rem; color: #94a3b8; font-weight: 600;">🏆 HIGHEST SHARPE RATIO</div>
                            <div style="font-size: 1.05rem; font-weight: 800; color: #00f2a9; margin: 3px 0;">{best_sharpe_row['Asset']}</div>
                            <div style="font-size: 0.78rem; color: #cbd5e1; font-family: monospace;">Sharpe: <b>{best_sharpe_row['Sharpe Ratio']:.2f}</b></div>
                        </div>
                    """, unsafe_allow_html=True)
                with r2:
                    st.markdown(f"""
                        <div style="background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 10px; padding: 12px 14px;">
                            <div style="font-size: 0.72rem; color: #94a3b8; font-weight: 600;">🛡️ MINIMUM VOLATILITY (LOW RISK)</div>
                            <div style="font-size: 1.05rem; font-weight: 800; color: #38bdf8; margin: 3px 0;">{min_vol_row['Asset']}</div>
                            <div style="font-size: 0.78rem; color: #cbd5e1; font-family: monospace;">Vol: <b>{min_vol_row['Annualized Volatility']*100:.1f}%</b></div>
                        </div>
                    """, unsafe_allow_html=True)
                with r3:
                    st.markdown(f"""
                        <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 10px; padding: 12px 14px;">
                            <div style="font-size: 0.72rem; color: #94a3b8; font-weight: 600;">🚀 MAX ANNUALIZED RETURN</div>
                            <div style="font-size: 1.05rem; font-weight: 800; color: #fbbf24; margin: 3px 0;">{max_ret_row['Asset']}</div>
                            <div style="font-size: 0.78rem; color: #cbd5e1; font-family: monospace;">CAGR: <b>{max_ret_row['Annualized Return']*100:+.1f}%</b></div>
                        </div>
                    """, unsafe_allow_html=True)
                with r4:
                    st.markdown(f"""
                        <div style="background: rgba(168, 85, 247, 0.08); border: 1px solid rgba(168, 85, 247, 0.3); border-radius: 10px; padding: 12px 14px;">
                            <div style="font-size: 0.72rem; color: #94a3b8; font-weight: 600;">📉 LOWEST DRAWDOWN DROP</div>
                            <div style="font-size: 1.05rem; font-weight: 800; color: #c084fc; margin: 3px 0;">{min_dd_row['Asset']}</div>
                            <div style="font-size: 0.78rem; color: #cbd5e1; font-family: monospace;">Max DD: <b>{min_dd_row['Max Drawdown']*100:.1f}%</b></div>
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown("<div style='margin-top: 1.2rem;'></div>", unsafe_allow_html=True)

            col_r_chart, col_r_table = st.columns([6, 4])
            with col_r_chart:
                fig_risk_scatter = create_risk_return_scatter(summary_df, height=420)
                st.plotly_chart(fig_risk_scatter, use_container_width=True, key="comp_fig_scatter_tab")
            with col_r_table:
                st.markdown("<div style='font-weight: 700; font-size: 0.95rem; color: #ffffff; margin-bottom: 0.6rem;'>📊 Risk Metrics Table</div>", unsafe_allow_html=True)
                st.dataframe(summary_df[["Asset", "Annualized Volatility", "Sharpe Ratio", "Max Drawdown"]].style.format({
                    "Annualized Volatility": "{:.2%}",
                    "Sharpe Ratio": "{:.2f}",
                    "Max Drawdown": "{:.2%}"
                }), use_container_width=True)
                st.markdown("""
                    <div style="background: rgba(11, 21, 29, 0.8); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 10px 12px; font-size: 0.73rem; color: #94a3b8; line-height: 1.45; margin-top: 8px;">
                        <span style="color: #00f2a9; font-weight: 700;">💡 How to Interpret:</span><br>
                        Assets in the <b>Upper-Left</b> quadrant offer superior risk-efficiency (higher return with lower volatility). The dashed line marks the <b>Risk-Free Benchmark (4.2%)</b>.
                    </div>
                """, unsafe_allow_html=True)

        with tab_corr:
            st.markdown("### 🧬 Pairwise Asset Return Correlation")
            fig_corr_full = create_correlation_heatmap(corr_matrix)
            st.plotly_chart(fig_corr_full, use_container_width=True, key="comp_fig_corr_full")

        with tab_dd:
            st.markdown("### 📉 Comparative Underwater Drawdowns")
            dd_dict = {col: calculate_drawdown_series(renamed_df[col]) * 100.0 for col in renamed_df.columns}
            dd_df = pd.DataFrame(dd_dict)
            fig_dd = create_performance_line_chart(dd_df, title="Drawdown Trajectories (%)", y_title="Drawdown (%)")
            st.plotly_chart(fig_dd, use_container_width=True, key="comp_fig_dd")

        with tab_dist:
            st.markdown("### 📊 Daily Return Distributions")
            for idx, col in enumerate(renamed_df.columns):
                ret = calculate_daily_returns(renamed_df[col])
                fig_ret = create_daily_returns_bar_chart(ret, title=f"Daily Return Bars — {col}")
                st.plotly_chart(fig_ret, use_container_width=True, key=f"comp_fig_dist_{idx}_{col}")

        # Contextual Featherless AI Comparison Interpretation
        st.markdown("---")
        ai_col1, ai_col2 = st.columns([4, 1])
        with ai_col1:
            st.markdown(
                "**🤖 Featherless AI Multi-Asset Comparison Analysis:** "
                "Synthesize institutional risk, return, and correlation dynamics for these assets."
            )
        with ai_col2:
            if st.button("🧠 Compare Assets", type="secondary", use_container_width=True):
                with st.spinner("Featherless AI is synthesizing multi-asset comparative commentary..."):
                    prompt = f"Analyze and contrast the historical risk, return, correlation, and drawdown behavior of {', '.join(selected_tickers)} based on the summary metrics."
                    context_str = summary_df.to_string()
                    resp = ai_client.chat_completion(
                        messages=[{"role": "user", "content": prompt}],
                        system_context=context_str,
                        max_tokens=650
                    )
                    explanation = resp.get("content", "Analysis unavailable.")
                    st.markdown(
                        f"""
                        <div class="quant-card" style="border-left: 3px solid #00f2a9; margin-top: 1rem;">
                            <div style="font-size: 0.85rem; font-weight: 700; color: #00f2a9; margin-bottom: 6px;">
                                🧠 INSTITUTIONAL COMPARATIVE INTERPRETATION
                            </div>
                            {explanation}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

render_brand_footer()
