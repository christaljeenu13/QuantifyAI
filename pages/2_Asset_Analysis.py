"""
QuantifyAI — Page 2: Asset Analysis Suite.
Comprehensive institutional quantitative analysis engine implementing all 16 user-specified topics:
1. Asset Overview (with Initial Investment Growth Simulator)
2. Historical Price Analysis
3. SMA Analysis
4. EMA Analysis
5. Returns Analysis
6. Volatility Analysis
7. Sharpe Ratio
8. Maximum Drawdown
9. Rolling Performance Analysis
10. Drawdown Analysis
11. Statistical Analysis
12. Volume Analysis
13. Correlation Analysis
14. Benchmark Comparison
15. Market Regime Analysis
16. AI Research Summary
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, date
from scipy.stats import skew, kurtosis, norm, linregress

import config
from src.data.asset_registry import get_default_registry
from src.data.market_data import MarketDataManager
from src.analytics.metrics import (
    calculate_summary_metrics,
    calculate_drawdown_series,
    calculate_daily_returns,
    calculate_cumulative_returns,
    calculate_monthly_returns,
    calculate_annualized_volatility,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_max_drawdown,
    calculate_cagr
)
from src.analytics.indicators import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands
)
from src.api.featherless_client import get_featherless_client
from src.reporting.export import dataframe_to_csv_bytes
from src.ui.theme import apply_custom_theme, get_color_palette
from src.ui.components import render_html, render_brand_footer

# ─── Custom CSS for Asset Analysis ───────────────────────────────────────────
st.markdown("""
<style>
.metric-box {
    background: rgba(11, 20, 28, 0.75);
    border: 1px solid rgba(20, 40, 52, 0.9);
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 10px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.35);
}
.metric-box-title {
    font-size: 0.72rem;
    font-family: 'JetBrains Mono', monospace;
    color: #7e92a2;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 4px;
}
.metric-box-value {
    font-size: 1.55rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.02em;
    line-height: 1.1;
}
.metric-box-sub {
    font-size: 0.74rem;
    color: #94a3b8;
    margin-top: 4px;
    font-family: 'JetBrains Mono', monospace;
}
.positive-txt { color: #00f2a9 !important; font-weight: 700; }
.negative-txt { color: #f87171 !important; font-weight: 700; }
.neutral-txt  { color: #38bdf8 !important; font-weight: 700; }

.sim-banner {
    background: linear-gradient(135deg, rgba(0, 242, 169, 0.08) 0%, rgba(56, 189, 248, 0.06) 50%, rgba(168, 85, 247, 0.05) 100%);
    border: 1px solid rgba(0, 242, 169, 0.28);
    border-radius: 14px;
    padding: 18px 22px;
    margin: 1.2rem 0 1.6rem 0;
    box-shadow: 0 6px 24px rgba(0, 242, 169, 0.08);
}
.sim-title {
    font-size: 0.88rem;
    font-weight: 800;
    color: #00f2a9;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
}
.sim-val-hero {
    font-size: 2.1rem;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: -0.03em;
}
.topic-header {
    font-size: 1.25rem;
    font-weight: 800;
    color: #ffffff;
    margin: 1.2rem 0 0.8rem 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.topic-desc {
    font-size: 0.82rem;
    color: #94a3b8;
    margin-bottom: 1rem;
    line-height: 1.5;
}
.badge-bullish {
    background: rgba(0, 242, 169, 0.15);
    border: 1px solid #00f2a9;
    color: #00f2a9;
    padding: 3px 9px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}
.badge-bearish {
    background: rgba(248, 113, 113, 0.15);
    border: 1px solid #f87171;
    color: #f87171;
    padding: 3px 9px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}
.badge-neutral {
    background: rgba(56, 189, 248, 0.15);
    border: 1px solid #38bdf8;
    color: #38bdf8;
    padding: 3px 9px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}
</style>
""", unsafe_allow_html=True)

# ─── Chart Standardizer ───────────────────────────────────────────────────────
def format_chart(fig: go.Figure, title: str = "", height: int = 420) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(6, 10, 14, 0.0)",
        plot_bgcolor="rgba(8, 13, 18, 1.0)",
        font=dict(family="Inter, sans-serif", color="#cbd5e1", size=11),
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(size=13, color="#ffffff"),
            x=0.01,
            y=0.98
        ),
        margin=dict(l=45, r=20, t=40 if title else 25, b=35),
        height=height,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color="#94a3b8"),
            bgcolor="rgba(0,0,0,0)"
        ),
        shapes=[
            dict(
                type="rect",
                xref="paper", yref="paper",
                x0=0, y0=0, x1=1, y1=1,
                fillcolor="rgba(0, 242, 169, 0.025)",
                line_width=0,
                layer="below"
            )
        ]
    )
    fig.update_xaxes(gridcolor="rgba(20, 40, 52, 0.8)", zerolinecolor="#142834")
    fig.update_yaxes(gridcolor="rgba(20, 40, 52, 0.8)", zerolinecolor="#142834")
    return fig

# ─── Initialize Registry & AI Client ──────────────────────────────────────────
registry = get_default_registry()
ai_client = get_featherless_client()

# ─── Page Title Header ────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom: 1.2rem;">
    <h1 style="margin: 0; font-size: 1.8rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
        Asset Analysis
    </h1>
    <p style="margin: 3px 0 0 0; font-size: 0.86rem; color: #7e92a2;">
        Comprehensive institutional analytics suite: historical pricing, technical momentum, quantitative risk, and investment simulation.
    </p>
</div>
""", unsafe_allow_html=True)

# ─── 1. Control Filter Bar (Instruments, Date Range & Investment Amount) ───────
c1, c2, c3, c4 = st.columns([30, 28, 24, 18], vertical_alignment="bottom")

with c1:
    asset_list = registry.list_assets()
    options_map = {f"{a['name']} ({a['ticker']})": a["ticker"] for a in asset_list}

    # Handle search from Dashboard
    search_target = st.session_state.pop("search_ticker", None) or st.session_state.get("selected_asset", None)
    if search_target:
        matched = [k for k, v in options_map.items() if v.upper() == str(search_target).upper() or str(search_target).upper() in k.upper()]
        if matched:
            default_key = matched
        else:
            registry.add_custom_asset(str(search_target).upper(), name=str(search_target).upper())
            asset_list = registry.list_assets()
            options_map = {f"{a['name']} ({a['ticker']})": a["ticker"] for a in asset_list}
            matched = [k for k, v in options_map.items() if v.upper() == str(search_target).upper()]
            default_key = matched if matched else [list(options_map.keys())[0]]
    else:
        default_key = [k for k in options_map.keys() if "NVDA" in k]

    selected_label = st.selectbox(
        "SELECT INSTRUMENT",
        options=list(options_map.keys()),
        index=list(options_map.keys()).index(default_key[0]) if default_key else 0,
        key="asset_analysis_inst_select"
    )
    ticker = options_map[selected_label]

today = datetime.now().date()
# Initialize date value keys and version counter if not set (used by preset buttons & custom days)
if "aa_start_date_val" not in st.session_state:
    st.session_state["aa_start_date_val"] = today - timedelta(days=730)
if "aa_end_date_val" not in st.session_state:
    st.session_state["aa_end_date_val"] = today
if "aa_date_ver" not in st.session_state:
    st.session_state["aa_date_ver"] = 0

ver = st.session_state["aa_date_ver"]

with c2:
    d_sub1, d_sub2 = st.columns(2)
    with d_sub1:
        start_date = st.date_input(
            "START DATE",
            value=st.session_state["aa_start_date_val"],
            key=f"aa_start_date_{ver}"
        )
    with d_sub2:
        end_date = st.date_input(
            "END DATE",
            value=st.session_state["aa_end_date_val"],
            key=f"aa_end_date_{ver}"
        )

# Keep value keys in sync with user manual date selections
st.session_state["aa_start_date_val"] = start_date
st.session_state["aa_end_date_val"] = end_date

with c3:
    initial_amount = st.number_input(
        "INITIAL INVESTMENT ($)",
        min_value=10.0,
        max_value=10000000.0,
        value=1000.0,
        step=100.0,
        format="%.2f",
        key="aa_initial_inv_input",
        help="Simulate the historical growth of this initial capital investment over the selected timeframe."
    )

with c4:
    fetch_btn = st.button("⚡ Run Analysis", type="primary", use_container_width=True, key="aa_fetch_btn")

# ─── Timeframe Presets & Custom Days Selection ─────────────────────────────────
p_col1, p_col2 = st.columns([7, 3])

presets = [
    ("1M", 30),
    ("2M", 60),
    ("3M", 90),
    ("6M", 180),
    ("YTD", None),
    ("1Y", 365),
    ("2Y", 730),
    ("3Y", 1095),
    ("5Y", 1825)
]

with p_col1:
    btn_cols = st.columns(len(presets))
    for idx, (label, days) in enumerate(presets):
        with btn_cols[idx]:
            if st.button(label, use_container_width=True, key=f"btn_preset_{label}"):
                if days is not None:
                    st.session_state["aa_start_date_val"] = today - timedelta(days=days)
                    st.session_state["aa_end_date_val"] = today
                else:
                    st.session_state["aa_start_date_val"] = date(today.year, 1, 1)
                    st.session_state["aa_end_date_val"] = today
                st.session_state["aa_date_ver"] = st.session_state.get("aa_date_ver", 0) + 1
                st.rerun()

with p_col2:
    c_days_col1, c_days_col2 = st.columns([3, 2])
    with c_days_col1:
        custom_days = st.number_input(
            "Custom Days",
            min_value=1,
            max_value=3650,
            value=st.session_state.get("aa_custom_days_input", 45),
            step=1,
            label_visibility="collapsed",
            key="aa_custom_days_field",
            help="Enter any number of calendar days (e.g., 45, 120, 500) and click Apply."
        )
    with c_days_col2:
        if st.button("Apply Days", use_container_width=True, type="secondary", key="btn_apply_custom_days"):
            st.session_state["aa_custom_days_input"] = int(custom_days)
            st.session_state["aa_start_date_val"] = today - timedelta(days=int(custom_days))
            st.session_state["aa_end_date_val"] = today
            st.session_state["aa_date_ver"] = st.session_state.get("aa_date_ver", 0) + 1
            st.rerun()

# ─── Fetch Historical Data ───────────────────────────────────────────────────
with st.spinner(f"Retrieving quantitative telemetry for {ticker}..."):
    df, meta = MarketDataManager.fetch_data(ticker, start_date=start_date, end_date=end_date)
    # Also fetch SPY as universal benchmark
    spy_df, _ = MarketDataManager.fetch_data("SPY", start_date=start_date, end_date=end_date)

if meta.get("status") == "success" and not meta.get("is_live"):
    st.warning("⚠️ Yahoo Finance is unreachable - showing locally saved snapshot data (may not include the latest sessions).")

if df.empty or len(df) < 5:
    st.error(f"❌ Insufficient market data available for '{ticker}' between {start_date} and {end_date}. Please expand the date range.")
    st.stop()

# Core calculated series
close_series = df["Close"]
daily_returns = calculate_daily_returns(close_series)
drawdown_series = calculate_drawdown_series(close_series)
metrics = calculate_summary_metrics(close_series, risk_free_rate=config.DEFAULT_RISK_FREE_RATE)

# ─── FEATURE 2: INITIAL INVESTMENT SIMULATION CALCULATION ────────────────────
start_price = float(close_series.iloc[0])
end_price = float(close_series.iloc[-1])
shares_bought = initial_amount / start_price if start_price > 0 else 0
ending_portfolio_value = shares_bought * end_price
net_profit_loss = ending_portfolio_value - initial_amount
percentage_gain = (net_profit_loss / initial_amount) * 100.0 if initial_amount > 0 else 0
wealth_multiplier = ending_portfolio_value / initial_amount if initial_amount > 0 else 1.0

# Portfolio growth curve ($ value across time)
portfolio_wealth_series = (close_series / start_price) * initial_amount

# Benchmark (SPY) investment comparison
if not spy_df.empty and len(spy_df) > 5:
    # Align dates
    spy_aligned = spy_df["Close"].reindex(close_series.index).ffill().bfill()
    spy_start_price = float(spy_aligned.iloc[0])
    spy_end_price = float(spy_aligned.iloc[-1])
    spy_shares = initial_amount / spy_start_price if spy_start_price > 0 else 0
    spy_ending_val = spy_shares * spy_end_price
    spy_pnl = spy_ending_val - initial_amount
    spy_pct = (spy_pnl / initial_amount) * 100.0
    outperformance = net_profit_loss - spy_pnl
    spy_portfolio_series = (spy_aligned / spy_start_price) * initial_amount
else:
    spy_ending_val = initial_amount
    spy_pct = 0.0
    outperformance = 0.0
    spy_portfolio_series = pd.Series(dtype=float)

# ─── INVESTMENT SIMULATION: RISK & BENEFITS ANALYSIS ─────────────────────────
sign_sym = "+" if net_profit_loss >= 0 else "-"
pnl_color = "#00f2a9" if net_profit_loss >= 0 else "#f87171"

# ── Risk Scoring Calculations ─────────────────────────────────────────────────
ann_vol = metrics.get("annualized_volatility", 0.0) * 100.0 # % annualised volatility
sharpe  = metrics.get("sharpe_ratio", 0.0)
max_dd  = abs(metrics.get("max_drawdown", 0.0)) * 100.0   # % max drawdown
cagr    = metrics.get("annualized_return", 0.0) * 100.0
spy_cagr = (((spy_ending_val / initial_amount) ** (1 / max((len(df) / 252), 0.1))) - 1) * 100 if initial_amount > 0 else 0.0

# Volatility Risk: Low < 15%, Medium 15-30%, High > 30%
if ann_vol < 15:
    vol_label, vol_color, vol_badge = "LOW", "#00f2a9", "🟢"
elif ann_vol < 30:
    vol_label, vol_color, vol_badge = "MEDIUM", "#f59e0b", "🟡"
else:
    vol_label, vol_color, vol_badge = "HIGH", "#f87171", "🔴"

# Sharpe Rating: Excellent ≥ 2, Good 1-2, Fair 0.5-1, Poor < 0.5
if sharpe >= 2.0:
    sharpe_label, sharpe_color, sharpe_badge = "EXCELLENT", "#00f2a9", "🟢"
elif sharpe >= 1.0:
    sharpe_label, sharpe_color, sharpe_badge = "GOOD", "#4ade80", "🟢"
elif sharpe >= 0.5:
    sharpe_label, sharpe_color, sharpe_badge = "FAIR", "#f59e0b", "🟡"
else:
    sharpe_label, sharpe_color, sharpe_badge = "POOR", "#f87171", "🔴"

# Drawdown Risk: Low < 10%, Medium 10-25%, High > 25%
if max_dd < 10:
    dd_label, dd_color, dd_badge = "LOW", "#00f2a9", "🟢"
elif max_dd < 25:
    dd_label, dd_color, dd_badge = "MODERATE", "#f59e0b", "🟡"
else:
    dd_label, dd_color, dd_badge = "HIGH", "#f87171", "🔴"

# CAGR Benefit: Strong > 15%, Good 8-15%, Average 3-8%, Weak < 3%
if cagr > 15:
    cagr_label, cagr_color = "STRONG GROWTH", "#00f2a9"
elif cagr > 8:
    cagr_label, cagr_color = "GOOD GROWTH", "#4ade80"
elif cagr > 3:
    cagr_label, cagr_color = "AVERAGE GROWTH", "#f59e0b"
elif cagr >= 0:
    cagr_label, cagr_color = "WEAK GROWTH", "#94a3b8"
else:
    cagr_label, cagr_color = "LOSS", "#f87171"

# Outperformance benefit
outperf_pct = percentage_gain - spy_pct
op_label = f"+{outperf_pct:.1f}% vs Market" if outperf_pct >= 0 else f"{outperf_pct:.1f}% vs Market"
op_color = "#00f2a9" if outperf_pct >= 0 else "#f87171"

# Overall Risk Verdict (weighted score: 0=best risk, 3=worst)
risk_score = 0
if ann_vol >= 30: risk_score += 2
elif ann_vol >= 15: risk_score += 1
if max_dd >= 25: risk_score += 2
elif max_dd >= 10: risk_score += 1
if sharpe < 0.5: risk_score += 2
elif sharpe < 1.0: risk_score += 1

if risk_score <= 1:
    verdict_label, verdict_color, verdict_icon, verdict_desc = "LOW RISK", "#00f2a9", "🛡️", "Asset shows stable, low-risk behaviour suitable for conservative portfolios."
elif risk_score <= 3:
    verdict_label, verdict_color, verdict_icon, verdict_desc = "MODERATE RISK", "#f59e0b", "⚖️", "Balanced risk-return profile. Suitable for growth-oriented investors."
else:
    verdict_label, verdict_color, verdict_icon, verdict_desc = "HIGH RISK", "#f87171", "⚠️", "Elevated volatility and drawdown. Best for aggressive, high-conviction traders."

# Inject CSS separately to avoid markdown parser issues
st.markdown("""
<style>
.sim-card {
    background: linear-gradient(135deg, rgba(11,25,34,0.9) 0%, rgba(4,18,28,0.95) 100%);
    border: 1px solid rgba(0,242,169,0.22);
    border-radius: 16px;
    padding: 22px 26px;
    margin: 1.2rem 0 1.8rem 0;
    box-shadow: 0 8px 32px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.04);
}
.sim-top-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 14px;
    margin-bottom: 18px;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.sim-left-block { flex: 1; min-width: 260px; }
.sim-right-block { text-align: right; }
.sim-ticker-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #00f2a9;
    letter-spacing: 0.12em;
    font-weight: 700;
    margin-bottom: 4px;
}
.sim-hero-val {
    font-size: 2.6rem;
    font-weight: 900;
    letter-spacing: -0.03em;
    line-height: 1.05;
}
.sim-pnl-line {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    font-weight: 700;
    margin-top: 2px;
}
.sim-desc {
    font-size: 0.9rem;
    color: #cbd5e1;
    line-height: 1.55;
    margin-top: 6px;
}
.risk-benefit-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin-bottom: 16px;
}
.rb-section-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    font-weight: 800;
    text-transform: uppercase;
    margin-bottom: 10px;
    padding-bottom: 6px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}
.rb-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 7px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 0.8rem;
}
.rb-item:last-child { border-bottom: none; }
.rb-item-label { color: #7e92a2; font-family: 'JetBrains Mono', monospace; font-size: 0.74rem; }
.rb-item-val { font-weight: 700; font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; }
.risk-panel {
    background: rgba(0,0,0,0.25);
    border: 1px solid rgba(248,113,113,0.18);
    border-radius: 12px;
    padding: 14px 18px;
}
.benefit-panel {
    background: rgba(0,0,0,0.25);
    border: 1px solid rgba(0,242,169,0.18);
    border-radius: 12px;
    padding: 14px 18px;
}
.verdict-bar {
    display: flex;
    align-items: center;
    gap: 14px;
    border-radius: 10px;
    padding: 12px 18px;
    margin-top: 14px;
    flex-wrap: wrap;
}
.verdict-icon { font-size: 1.5rem; }
.sim-footer-bar {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
    font-size: 0.73rem;
    color: #64748b;
    font-family: 'JetBrains Mono', monospace;
    padding-top: 12px;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin-top: 14px;
}
</style>
""", unsafe_allow_html=True)

# Build the verdict background color inline
_vbg_r = 248 if verdict_label == 'HIGH RISK' else (245 if verdict_label == 'MODERATE RISK' else 0)
_vbg_g = 113 if verdict_label == 'HIGH RISK' else (158 if verdict_label == 'MODERATE RISK' else 242)
_vbg_b = 113 if verdict_label == 'HIGH RISK' else (11  if verdict_label == 'MODERATE RISK' else 169)

_sim_html = (
    f'<div class="sim-card">'
    f'<div class="sim-top-row">'
    f'<div class="sim-left-block">'
    f'<div class="sim-ticker-label">&#x1F4B0; INVESTMENT VALUE SIMULATION &middot; {ticker}</div>'
    f'<div class="sim-desc">If you invested <b style="color:#fff;">${initial_amount:,.2f}</b> on '
    f'<span style="color:#38bdf8;">{close_series.index[0].strftime("%b %d, %Y")}</span> '
    f'at <b style="color:#fff;">${start_price:,.2f}/share</b>, your portfolio today would be worth:</div>'
    f'</div>'
    f'<div class="sim-right-block">'
    f'<div class="sim-hero-val" style="color:{pnl_color};">${ending_portfolio_value:,.2f}</div>'
    f'<div class="sim-pnl-line" style="color:{pnl_color};">{sign_sym}${abs(net_profit_loss):,.2f} ({sign_sym}{abs(percentage_gain):.2f}%) &nbsp;&middot;&nbsp; {wealth_multiplier:.2f}x Multiple</div>'
    f'</div>'
    f'</div>'
    f'<div class="risk-benefit-grid">'
    f'<div class="risk-panel">'
    f'<div class="rb-section-title" style="color:#f87171;">&#x26A0;&#xFE0F; Risk Indicators</div>'
    f'<div class="rb-item"><span class="rb-item-label">Volatility (Ann.)</span>'
    f'<span class="rb-item-val" style="color:{vol_color};">{vol_badge} {ann_vol:.1f}% &middot; {vol_label}</span></div>'
    f'<div class="rb-item"><span class="rb-item-label">Sharpe Ratio</span>'
    f'<span class="rb-item-val" style="color:{sharpe_color};">{sharpe_badge} {sharpe:.2f} &middot; {sharpe_label}</span></div>'
    f'<div class="rb-item"><span class="rb-item-label">Max Drawdown</span>'
    f'<span class="rb-item-val" style="color:{dd_color};">{dd_badge} -{max_dd:.1f}% &middot; {dd_label}</span></div>'
    f'<div class="rb-item"><span class="rb-item-label">Worst Case Loss (on ${initial_amount:,.0f})</span>'
    f'<span class="rb-item-val" style="color:#f87171;">-${initial_amount * max_dd / 100:,.2f}</span></div>'
    f'<div class="rb-item"><span class="rb-item-label">Value at Risk (95% conf.)</span>'
    f'<span class="rb-item-val" style="color:#fb923c;">-${initial_amount * ann_vol / 100 * 1.65:,.2f}</span></div>'
    f'</div>'
    f'<div class="benefit-panel">'
    f'<div class="rb-section-title" style="color:#00f2a9;">&#x2705; Benefit Indicators</div>'
    f'<div class="rb-item"><span class="rb-item-label">Annualised Return (CAGR)</span>'
    f'<span class="rb-item-val" style="color:{cagr_color};">{"+" if cagr>=0 else ""}{cagr:.2f}% &middot; {cagr_label}</span></div>'
    f'<div class="rb-item"><span class="rb-item-label">Total Gain on Investment</span>'
    f'<span class="rb-item-val" style="color:{pnl_color};">{sign_sym}${abs(net_profit_loss):,.2f} ({sign_sym}{abs(percentage_gain):.1f}%)</span></div>'
    f'<div class="rb-item"><span class="rb-item-label">vs S&amp;P 500 (same period)</span>'
    f'<span class="rb-item-val" style="color:{op_color};">{op_label}</span></div>'
    f'<div class="rb-item"><span class="rb-item-label">Wealth Multiplier</span>'
    f'<span class="rb-item-val" style="color:#a78bfa;">{wealth_multiplier:.2f}x your capital</span></div>'
    f'<div class="rb-item"><span class="rb-item-label">Shares Acquired</span>'
    f'<span class="rb-item-val" style="color:#38bdf8;">{shares_bought:,.4f} units @ ${start_price:,.2f}</span></div>'
    f'</div>'
    f'</div>'
    f'<div class="verdict-bar" style="background:rgba({_vbg_r},{_vbg_g},{_vbg_b},0.09);'
    f'border:1px solid {verdict_color}33;border-left:4px solid {verdict_color};">'
    f'<div class="verdict-icon">{verdict_icon}</div>'
    f'<div><div style="font-family:\'JetBrains Mono\',monospace;font-size:0.82rem;font-weight:900;letter-spacing:0.08em;color:{verdict_color};">'
    f'OVERALL RISK: {verdict_label}</div>'
    f'<div style="font-size:0.8rem;color:#94a3b8;margin-top:2px;">{verdict_desc}</div></div>'
    f'<div style="margin-left:auto;text-align:right;font-family:\'JetBrains Mono\';font-size:0.72rem;color:#64748b;">'
    f'Risk Score: <b style="color:{verdict_color};">{risk_score}/6</b></div>'
    f'</div>'
    f'<div class="sim-footer-bar">'
    f'<span>Benchmark S&amp;P 500: <b style="color:#94a3b8;">${spy_ending_val:,.2f} ({"+" if spy_pct>=0 else ""}{spy_pct:.1f}%)</b></span>'
    f'<span>Outperformance: <b style="color:{"#00f2a9" if outperformance>=0 else "#f87171"};">{"+" if outperformance>=0 else ""}${outperformance:,.2f}</b></span>'
    f'<span>CAGR: <b style="color:#94a3b8;">{"+" if cagr>=0 else ""}{cagr:.2f}%/yr</b></span>'
    f'<span>Period: <b style="color:#94a3b8;">{close_series.index[0].strftime("%d %b %Y")} &rarr; {close_series.index[-1].strftime("%d %b %Y")}</b></span>'
    f'</div>'
    f'</div>'
)
st.markdown(_sim_html, unsafe_allow_html=True)

# ─── INVESTMENT SIMULATION: INTERACTIVE GRAPH ─────────────────────────────────
sim_chart_tab1, sim_chart_tab2 = st.tabs([
    f"📈 {ticker} Investment Growth Curve ($ Value)",
    f"📉 {ticker} Historical Drawdown & Risk Path (%)"
])

with sim_chart_tab1:
    fig_sim_growth = go.Figure()
    # Baseline: initial capital
    fig_sim_growth.add_hline(
        y=initial_amount,
        line_dash="dot",
        line_color="rgba(255, 255, 255, 0.3)",
        line_width=1.5,
        annotation_text=f"Initial Capital (${initial_amount:,.0f})",
        annotation_position="bottom right",
        annotation_font=dict(size=10, color="#94a3b8")
    )
    # Asset portfolio growth curve
    fig_sim_growth.add_trace(go.Scatter(
        x=portfolio_wealth_series.index,
        y=portfolio_wealth_series.values,
        mode="lines",
        name=f"Your ${initial_amount:,.0f} in {ticker}",
        line=dict(color="#00f2a9", width=2.8),
        fill="tozeroy",
        fillcolor="rgba(0, 242, 169, 0.08)",
        hovertemplate=f"<b>{ticker} Portfolio</b>: $%{{y:,.2f}}<br>Date: %{{x|%b %d, %Y}}<extra></extra>"
    ))
    # Benchmark SPY portfolio
    if not spy_portfolio_series.empty:
        fig_sim_growth.add_trace(go.Scatter(
            x=spy_portfolio_series.index,
            y=spy_portfolio_series.values,
            mode="lines",
            name=f"Benchmark (S&P 500) from ${initial_amount:,.0f}",
            line=dict(color="#38bdf8", width=1.8, dash="dash"),
            hovertemplate="<b>S&P 500 Benchmark</b>: $%{y:,.2f}<br>Date: %{x|%b %d, %Y}<extra></extra>"
        ))
    format_chart(fig_sim_growth, title=f"Simulation Growth Trajectory: ${initial_amount:,.0f} Invested in {ticker} vs S&P 500", height=360)
    fig_sim_growth.update_yaxes(tickprefix="$", tickformat=",.0f")
    st.plotly_chart(fig_sim_growth, use_container_width=True, key="sim_growth_fig_banner")

with sim_chart_tab2:
    fig_sim_dd = go.Figure()
    dd_pct = drawdown_series * 100.0
    fig_sim_dd.add_trace(go.Scatter(
        x=dd_pct.index,
        y=dd_pct.values,
        mode="lines",
        name=f"{ticker} Drawdown (%)",
        line=dict(color="#f87171", width=2.0),
        fill="tozeroy",
        fillcolor="rgba(248, 113, 113, 0.12)",
        hovertemplate=f"<b>{ticker} Drawdown</b>: %{{y:.2f}}%<br>Date: %{{x|%b %d, %Y}}<extra></extra>"
    ))
    format_chart(fig_sim_dd, title=f"{ticker} Drawdown History (% Drop from Peak)", height=320)
    fig_sim_dd.update_yaxes(ticksuffix="%", zeroline=True, zerolinecolor="rgba(255,255,255,0.2)")
    st.plotly_chart(fig_sim_dd, use_container_width=True, key="sim_dd_fig_banner")

st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

# ─── EXACT USER TOPICS (16 TABS) ──────────────────────────────────────────────
tabs = st.tabs([
    "Asset Overview",
    "Historical Price Analysis",
    "SMA Analysis",
    "EMA Analysis",
    "Returns Analysis",
    "Volatility Analysis",
    "Sharpe Ratio",
    "Maximum Drawdown",
    "Rolling Performance Analysis",
    "Drawdown Analysis",
    "Statistical Analysis",
    "Volume Analysis",
    "Correlation Analysis",
    "Benchmark Comparison",
    "Market Regime Analysis",
    "AI Research Summary"
])

(
    tab_overview,
    tab_historical,
    tab_sma,
    tab_ema,
    tab_returns,
    tab_volatility,
    tab_sharpe,
    tab_max_dd,
    tab_rolling,
    tab_dd_analysis,
    tab_stats,
    tab_volume,
    tab_correlation,
    tab_benchmark,
    tab_regime,
    tab_ai
) = tabs

# ═══════════════════════════════════════════════════════════════════════════════
# 1. ASSET OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with tab_overview:
    st.markdown('<div class="topic-header">📊 Asset Overview & Key Performance Indicators</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="topic-desc">Executive snapshot of {selected_label} over {len(df)} trading sessions ({start_date} to {end_date}).</div>', unsafe_allow_html=True)

    o1, o2, o3, o4 = st.columns(4)
    with o1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-box-title">CURRENT / LATEST PRICE</div>
            <div class="metric-box-value">${metrics['latest_price']:,.2f}</div>
            <div class="metric-box-sub">Open: ${df['Open'].iloc[-1]:,.2f} · High: ${df['High'].iloc[-1]:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with o2:
        tot_ret = metrics['total_return'] * 100.0
        cls = "positive-txt" if tot_ret >= 0 else "negative-txt"
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-box-title">TOTAL RETURN (PERIOD)</div>
            <div class="metric-box-value {cls}">{'+' if tot_ret>=0 else ''}{tot_ret:.2f}%</div>
            <div class="metric-box-sub">CAGR: {metrics['annualized_return']*100:.2f}% / year</div>
        </div>
        """, unsafe_allow_html=True)
    with o3:
        high_period = float(df["High"].max())
        low_period = float(df["Low"].min())
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-box-title">PERIOD RANGE (LOW - HIGH)</div>
            <div class="metric-box-value">${low_period:,.2f} – ${high_period:,.2f}</div>
            <div class="metric-box-sub">Spread: ${high_period - low_period:,.2f} ({((high_period-low_period)/low_period)*100:.1f}%)</div>
        </div>
        """, unsafe_allow_html=True)
    with o4:
        vol_latest = float(df["Volume"].iloc[-1])
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-box-title">LATEST TRADING VOLUME</div>
            <div class="metric-box-value">{vol_latest:,.0f}</div>
            <div class="metric-box-sub">20-Day Avg: {df['Volume'].rolling(20).mean().iloc[-1]:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    # Portfolio Growth Trajectory Chart
    st.markdown(f"#### 📈 Growth Trajectory of ${initial_amount:,.0f} Initial Investment")
    fig_wealth = go.Figure()
    fig_wealth.add_trace(go.Scatter(
        x=portfolio_wealth_series.index,
        y=portfolio_wealth_series.values,
        mode="lines",
        name=f"Your ${initial_amount:,.0f} in {ticker}",
        line=dict(color="#00f2a9", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(0, 242, 169, 0.08)"
    ))
    if not spy_portfolio_series.empty:
        fig_wealth.add_trace(go.Scatter(
            x=spy_portfolio_series.index,
            y=spy_portfolio_series.values,
            mode="lines",
            name=f"Benchmark (S&P 500) from ${initial_amount:,.0f}",
            line=dict(color="#38bdf8", width=1.5, dash="dot")
        ))
    format_chart(fig_wealth, title=f"Portfolio Equity Curve: ${initial_amount:,.0f} Investment in {ticker}", height=380)
    fig_wealth.update_yaxes(tickprefix="$", tickformat=",.0f")
    st.plotly_chart(fig_wealth, use_container_width=True)

    # Asset Metadata
    st.markdown("#### ℹ️ Asset Profile & Specifications")
    asset_meta = registry.get_asset_by_ticker(ticker) if hasattr(registry, "get_asset_by_ticker") else None
    asset_cat = asset_meta.get("category", "Equity") if isinstance(asset_meta, dict) else "Equity"
    meta_df = pd.DataFrame([
        {"Field": "Instrument Name", "Value": str(selected_label)},
        {"Field": "Ticker Symbol", "Value": str(ticker)},
        {"Field": "Asset Class", "Value": str(asset_cat)},
        {"Field": "Exchange Currency", "Value": "USD ($)"},
        {"Field": "Earliest Date in Sample", "Value": df.index[0].strftime("%Y-%m-%d")},
        {"Field": "Latest Date in Sample", "Value": df.index[-1].strftime("%Y-%m-%d")},
        {"Field": "Total Trading Days", "Value": str(len(df))}
    ])
    st.dataframe(meta_df, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 2. HISTORICAL PRICE ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_historical:
    st.markdown('<div class="topic-header">🕯️ Historical Price Analysis</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="topic-desc">Full open, high, low, close candlestick dynamics and trading range for {ticker}.</div>', unsafe_allow_html=True)

    fig_candle = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.75, 0.25]
    )
    fig_candle.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name="OHLC Price",
            increasing=dict(line=dict(color="#00f2a9"), fillcolor="#00f2a9"),
            decreasing=dict(line=dict(color="#f87171"), fillcolor="#f87171")
        ),
        row=1, col=1
    )
    colors_vol = ["#00f2a9" if c >= o else "#f87171" for c, o in zip(df["Close"], df["Open"])]
    fig_candle.add_trace(
        go.Bar(x=df.index, y=df['Volume'], name="Volume", marker_color=colors_vol, opacity=0.65),
        row=2, col=1
    )
    format_chart(fig_candle, title=f"{ticker} — Daily Candlestick & Volume", height=500)
    fig_candle.update_xaxes(rangeslider_visible=False)
    st.plotly_chart(fig_candle, use_container_width=True)

    # Price Extreme Stats
    h_col1, h_col2, h_col3, h_col4 = st.columns(4)
    with h_col1:
        st.metric("Period Opening Price", f"${start_price:,.2f}", df.index[0].strftime("%b %d, %Y"))
    with h_col2:
        st.metric("Period Closing Price", f"${end_price:,.2f}", df.index[-1].strftime("%b %d, %Y"))
    with h_col3:
        p_high = df["High"].max()
        p_high_date = df["High"].idxmax().strftime("%b %d, %Y")
        st.metric("All-Time High (Period)", f"${p_high:,.2f}", p_high_date)
    with h_col4:
        p_low = df["Low"].min()
        p_low_date = df["Low"].idxmin().strftime("%b %d, %Y")
        st.metric("All-Time Low (Period)", f"${p_low:,.2f}", p_low_date)

    st.markdown("#### 📋 Historical OHLCV Data Export")
    st.dataframe(df.tail(100), use_container_width=True)
    st.download_button(
        label=f"⬇️ Download {ticker} Historical Data (CSV)",
        data=dataframe_to_csv_bytes(df),
        file_name=f"{ticker}_historical_{start_date}_{end_date}.csv",
        mime="text/csv"
    )

# ═══════════════════════════════════════════════════════════════════════════════
# 3. SMA ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_sma:
    st.markdown('<div class="topic-header">📏 SMA Analysis (Simple Moving Averages)</div>', unsafe_allow_html=True)
    st.markdown('<div class="topic-desc">Simple Moving Averages smooth price noise to expose primary, intermediate, and short-term trends.</div>', unsafe_allow_html=True)

    sma20 = calculate_sma(close_series, 20)
    sma50 = calculate_sma(close_series, 50)
    sma200 = calculate_sma(close_series, 200)

    # Golden / Death Cross evaluation
    has_cross = False
    cross_text = "Insufficient historical depth for 200-day SMA cross evaluation"
    badge_cls = "badge-neutral"
    if len(sma50.dropna()) > 1 and len(sma200.dropna()) > 1:
        curr_50 = sma50.iloc[-1]
        curr_200 = sma200.iloc[-1]
        if curr_50 > curr_200:
            cross_text = "🟢 Golden Cross Active (50 SMA > 200 SMA) — Bullish Macro Trend"
            badge_cls = "badge-bullish"
        else:
            cross_text = "🔴 Death Cross Active (50 SMA < 200 SMA) — Bearish Macro Trend"
            badge_cls = "badge-bearish"

    st.markdown(f'<div style="margin-bottom:12px;"><span class="{badge_cls}">{cross_text}</span></div>', unsafe_allow_html=True)

    fig_sma = go.Figure()
    fig_sma.add_trace(go.Scatter(x=close_series.index, y=close_series.values, name="Close Price", line=dict(color="#ffffff", width=1.5)))
    fig_sma.add_trace(go.Scatter(x=sma20.index, y=sma20.values, name="20 SMA (Short-term)", line=dict(color="#f59e0b", width=1.8)))
    fig_sma.add_trace(go.Scatter(x=sma50.index, y=sma50.values, name="50 SMA (Medium-term)", line=dict(color="#38bdf8", width=1.8)))
    if len(sma200.dropna()) > 0:
        fig_sma.add_trace(go.Scatter(x=sma200.index, y=sma200.values, name="200 SMA (Institutional)", line=dict(color="#e040fb", width=2.0)))
    format_chart(fig_sma, title=f"{ticker} — Price vs 20, 50 & 200 Simple Moving Averages", height=430)
    st.plotly_chart(fig_sma, use_container_width=True)

    # Distance metrics
    c_sma1, c_sma2, c_sma3 = st.columns(3)
    curr_price = close_series.iloc[-1]
    with c_sma1:
        d20 = ((curr_price - sma20.iloc[-1]) / sma20.iloc[-1]) * 100.0 if not pd.isna(sma20.iloc[-1]) else 0
        st.metric("Price vs 20-Day SMA", f"${sma20.iloc[-1]:,.2f}", f"{'+' if d20>=0 else ''}{d20:.2f}%")
    with c_sma2:
        d50 = ((curr_price - sma50.iloc[-1]) / sma50.iloc[-1]) * 100.0 if not pd.isna(sma50.iloc[-1]) else 0
        st.metric("Price vs 50-Day SMA", f"${sma50.iloc[-1]:,.2f}", f"{'+' if d50>=0 else ''}{d50:.2f}%")
    with c_sma3:
        if len(sma200.dropna()) > 0:
            d200 = ((curr_price - sma200.iloc[-1]) / sma200.iloc[-1]) * 100.0 if not pd.isna(sma200.iloc[-1]) else 0
            st.metric("Price vs 200-Day SMA", f"${sma200.iloc[-1]:,.2f}", f"{'+' if d200>=0 else ''}{d200:.2f}%")
        else:
            st.metric("Price vs 200-Day SMA", "N/A", "Needs 200+ days")

# ═══════════════════════════════════════════════════════════════════════════════
# 4. EMA ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_ema:
    st.markdown('<div class="topic-header">⚡ EMA Analysis (Exponential Moving Averages)</div>', unsafe_allow_html=True)
    st.markdown('<div class="topic-desc">Exponential Moving Averages apply higher weighting to recent price bars, reacting swiftly to institutional trend shifts.</div>', unsafe_allow_html=True)

    ema9 = calculate_ema(close_series, 9)
    ema21 = calculate_ema(close_series, 21)
    ema50 = calculate_ema(close_series, 50)

    # Ribbon condition
    if ema9.iloc[-1] > ema21.iloc[-1] > ema50.iloc[-1]:
        ribbon_status = "🟢 Bullish EMA Ribbon Expansion (9 > 21 > 50) — Strong Upward Momentum"
        r_badge = "badge-bullish"
    elif ema9.iloc[-1] < ema21.iloc[-1] < ema50.iloc[-1]:
        ribbon_status = "🔴 Bearish EMA Ribbon Breakdown (9 < 21 < 50) — Downward Compression"
        r_badge = "badge-bearish"
    else:
        ribbon_status = "🟡 Neutral / Transitional EMA Ribbon Crossing"
        r_badge = "badge-neutral"

    st.markdown(f'<div style="margin-bottom:12px;"><span class="{r_badge}">{ribbon_status}</span></div>', unsafe_allow_html=True)

    fig_ema = go.Figure()
    fig_ema.add_trace(go.Scatter(x=close_series.index, y=close_series.values, name="Close Price", line=dict(color="#ffffff", width=1.5)))
    fig_ema.add_trace(go.Scatter(x=ema9.index, y=ema9.values, name="9 EMA (Fast)", line=dict(color="#00f2a9", width=1.8)))
    fig_ema.add_trace(go.Scatter(x=ema21.index, y=ema21.values, name="21 EMA (Pullback)", line=dict(color="#38bdf8", width=1.8)))
    fig_ema.add_trace(go.Scatter(x=ema50.index, y=ema50.values, name="50 EMA (Baseline)", line=dict(color="#f43f5e", width=1.8)))
    format_chart(fig_ema, title=f"{ticker} — 9, 21 & 50 Exponential Moving Average Ribbon", height=430)
    st.plotly_chart(fig_ema, use_container_width=True)

    e1, e2, e3 = st.columns(3)
    with e1:
        de9 = ((curr_price - ema9.iloc[-1]) / ema9.iloc[-1]) * 100.0
        st.metric("9-Day EMA", f"${ema9.iloc[-1]:,.2f}", f"{'+' if de9>=0 else ''}{de9:.2f}%")
    with e2:
        de21 = ((curr_price - ema21.iloc[-1]) / ema21.iloc[-1]) * 100.0
        st.metric("21-Day EMA", f"${ema21.iloc[-1]:,.2f}", f"{'+' if de21>=0 else ''}{de21:.2f}%")
    with e3:
        de50 = ((curr_price - ema50.iloc[-1]) / ema50.iloc[-1]) * 100.0
        st.metric("50-Day EMA", f"${ema50.iloc[-1]:,.2f}", f"{'+' if de50>=0 else ''}{de50:.2f}%")

# ═══════════════════════════════════════════════════════════════════════════════
# 5. RETURNS ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_returns:
    st.markdown('<div class="topic-header">📈 Returns Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="topic-desc">Comprehensive return distribution, cumulative wealth evolution, and calendar return matrices.</div>', unsafe_allow_html=True)

    # Daily Returns Bar Chart
    fig_ret = go.Figure()
    bar_colors = ["#00f2a9" if r >= 0 else "#f87171" for r in daily_returns]
    fig_ret.add_trace(go.Bar(
        x=daily_returns.index,
        y=daily_returns.values * 100.0,
        name="Daily Return %",
        marker_color=bar_colors
    ))
    format_chart(fig_ret, title=f"{ticker} — Daily Percentage Returns", height=350)
    fig_ret.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig_ret, use_container_width=True)

    # Key Return Statistics
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        best_day = daily_returns.max() * 100.0
        best_date = daily_returns.idxmax().strftime("%b %d, %Y")
        st.metric("Best Trading Day", f"+{best_day:.2f}%", best_date)
    with r2:
        worst_day = daily_returns.min() * 100.0
        worst_date = daily_returns.idxmin().strftime("%b %d, %Y")
        st.metric("Worst Trading Day", f"{worst_day:.2f}%", worst_date)
    with r3:
        win_days = (daily_returns > 0).sum()
        win_rate = (win_days / len(daily_returns)) * 100.0 if len(daily_returns) > 0 else 0
        st.metric("Win Rate (% Up Days)", f"{win_rate:.1f}%", f"{win_days} / {len(daily_returns)} days")
    with r4:
        median_daily = daily_returns.median() * 100.0
        st.metric("Median Daily Return", f"{'+' if median_daily>=0 else ''}{median_daily:.2f}%", "Middle outcome")

    # Monthly Calendar Matrix
    st.markdown("#### 📅 Monthly Returns Heatmap Matrix")
    monthly_df = calculate_monthly_returns(close_series)
    if not monthly_df.empty:
        st.dataframe(
            monthly_df.style.format("{:+.2%}", na_rep="-").background_gradient(
                cmap="RdYlGn", vmin=-0.15, vmax=0.15
            ),
            use_container_width=True
        )

# ═══════════════════════════════════════════════════════════════════════════════
# 6. VOLATILITY ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_volatility:
    st.markdown('<div class="topic-header">🌊 Volatility Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="topic-desc">Measure risk dispersion, price fluctuation intensity, and shifting volatility regimes.</div>', unsafe_allow_html=True)

    ann_vol = metrics['annualized_volatility'] * 100.0
    rolling_vol30 = daily_returns.rolling(30).std() * np.sqrt(252) * 100.0

    # Risk Tier classification
    if ann_vol < 15.0:
        vol_tier = "🟢 Low Volatility (Defensive Asset, <15%)"
    elif ann_vol < 30.0:
        vol_tier = "🟡 Moderate Volatility (Market Equities, 15-30%)"
    elif ann_vol < 50.0:
        vol_tier = "🟠 High Volatility (Growth Tech / Leveraged, 30-50%)"
    else:
        vol_tier = "🔴 Extreme Volatility (Speculative / Crypto, >50%)"

    st.markdown(f"""
    <div style="background:rgba(20,40,52,0.6); border:1px solid rgba(0,242,169,0.25); border-radius:10px; padding:12px 16px; margin-bottom:14px;">
        <span style="font-size:0.8rem; color:#7e92a2; font-family:'JetBrains Mono';">VOLATILITY RISK CLASSIFICATION:</span> &nbsp;
        <b style="color:#ffffff;">{vol_tier}</b>
    </div>
    """, unsafe_allow_html=True)

    fig_vol = go.Figure()
    fig_vol.add_trace(go.Scatter(
        x=rolling_vol30.index,
        y=rolling_vol30.values,
        mode="lines",
        name="30-Day Rolling Annualized Vol",
        line=dict(color="#38bdf8", width=2.0)
    ))
    fig_vol.add_hline(y=ann_vol, line_dash="dash", line_color="#00f2a9", annotation_text=f"Sample Mean ({ann_vol:.1f}%)")
    format_chart(fig_vol, title=f"{ticker} — 30-Day Rolling Annualized Volatility", height=380)
    fig_vol.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig_vol, use_container_width=True)

    v1, v2, v3 = st.columns(3)
    with v1:
        st.metric("Annualized Volatility", f"{ann_vol:.2f}%", "252 trading days")
    with v2:
        daily_vol = daily_returns.std() * 100.0
        st.metric("Daily Volatility (Std Dev)", f"{daily_vol:.2f}%", "1-day standard deviation")
    with v3:
        atr14 = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        st.metric("Average True Range (ATR 14)", f"${atr14:,.2f}", "Avg daily swing")

# ═══════════════════════════════════════════════════════════════════════════════
# 7. SHARPE RATIO
# ═══════════════════════════════════════════════════════════════════════════════
with tab_sharpe:
    st.markdown('<div class="topic-header">⚖️ Sharpe Ratio & Risk-Adjusted Return</div>', unsafe_allow_html=True)
    st.markdown('<div class="topic-desc">Measures how much excess return the asset delivers per unit of volatility relative to risk-free assets.</div>', unsafe_allow_html=True)

    rf_input = st.slider("Risk-Free Rate (Annual %)", min_value=0.0, max_value=10.0, value=config.DEFAULT_RISK_FREE_RATE*100.0, step=0.25, key="sharpe_rf_slider") / 100.0
    cal_sharpe = calculate_sharpe_ratio(daily_returns, risk_free_rate=rf_input)
    cal_sortino = calculate_sortino_ratio(daily_returns, risk_free_rate=rf_input)

    # Qualitative Rating
    if cal_sharpe >= 2.0:
        s_qual = "🏆 Exceptional (>2.0)"
        s_badge = "badge-bullish"
    elif cal_sharpe >= 1.0:
        s_qual = "🟢 Good (1.0 – 2.0)"
        s_badge = "badge-bullish"
    elif cal_sharpe >= 0.5:
        s_qual = "🟡 Acceptable (0.5 – 1.0)"
        s_badge = "badge-neutral"
    else:
        s_qual = "🔴 Sub-optimal (<0.5)"
        s_badge = "badge-bearish"

    st.markdown(f'<div style="margin-bottom:14px;"><span class="{s_badge}">Rating: {s_qual}</span></div>', unsafe_allow_html=True)

    s1, s2, s3 = st.columns(3)
    with s1:
        st.metric("Annualized Sharpe Ratio", f"{cal_sharpe:.2f}", f"Rf = {rf_input*100:.2f}%")
    with s2:
        st.metric("Sortino Ratio", f"{cal_sortino:.2f}", "Downside risk penalty only")
    with s3:
        mdd_abs = abs(metrics['max_drawdown'])
        calmar = (metrics['annualized_return'] / mdd_abs) if mdd_abs > 0 else 0
        st.metric("Calmar Ratio", f"{calmar:.2f}", "CAGR / Max Drawdown")

    st.markdown("""
    <div style="background:rgba(11,20,28,0.7); border:1px solid rgba(20,40,52,0.8); border-radius:10px; padding:14px 18px; margin-top:14px; font-size:0.84rem; color:#cbd5e1; line-height:1.6;">
        <b>💡 Interpretation Guide:</b><br>
        • <b>Sharpe Ratio &gt; 1.0:</b> Institutional investment-grade risk efficiency.<br>
        • <b>Sortino Ratio:</b> Unlike Sharpe, Sortino ignores upside volatility and only penalizes harmful downside swings.<br>
        • <b>Calmar Ratio:</b> Assesses the annual return achieved per unit of historical maximum drawdown.
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 8. MAXIMUM DRAWDOWN
# ═══════════════════════════════════════════════════════════════════════════════
with tab_max_dd:
    st.markdown('<div class="topic-header">📉 Maximum Drawdown (MDD)</div>', unsafe_allow_html=True)
    st.markdown('<div class="topic-desc">The peak-to-trough drop measuring the maximum loss an investor could have experienced by buying at the absolute high.</div>', unsafe_allow_html=True)

    mdd_val = metrics['max_drawdown'] * 100.0
    trough_date = drawdown_series.idxmin()
    peak_date = close_series.loc[:trough_date].idxmax()
    peak_val = close_series.loc[peak_date]
    trough_val = close_series.loc[trough_date]

    fig_mdd = go.Figure()
    fig_mdd.add_trace(go.Scatter(
        x=drawdown_series.index,
        y=drawdown_series.values * 100.0,
        mode="lines",
        name="Drawdown %",
        line=dict(color="#f87171", width=1.8),
        fill="tozeroy",
        fillcolor="rgba(248, 113, 113, 0.15)"
    ))
    format_chart(fig_mdd, title=f"{ticker} — Peak-to-Trough Drawdown Curve", height=380)
    fig_mdd.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig_mdd, use_container_width=True)

    d1, d2, d3 = st.columns(3)
    with d1:
        st.metric("Maximum Drawdown", f"{mdd_val:.2f}%", f"Peak: {peak_date.strftime('%b %d, %Y')}")
    with d2:
        st.metric("Trough Date & Price", f"${trough_val:,.2f}", trough_date.strftime("%b %d, %Y"))
    with d3:
        curr_dd = drawdown_series.iloc[-1] * 100.0
        st.metric("Current Drawdown from Peak", f"{curr_dd:.2f}%", "From all-time high in period")

# ═══════════════════════════════════════════════════════════════════════════════
# 9. ROLLING PERFORMANCE ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_rolling:
    st.markdown('<div class="topic-header">🔄 Rolling Performance Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="topic-desc">Examines whether returns and risk-efficiency were steady across cycles or concentrated in single speculative runs.</div>', unsafe_allow_html=True)

    roll_30 = daily_returns.rolling(30).apply(lambda r: (np.prod(1 + r) - 1)) * 100.0
    roll_90 = daily_returns.rolling(90).apply(lambda r: (np.prod(1 + r) - 1)) * 100.0
    roll_252 = daily_returns.rolling(252).apply(lambda r: (np.prod(1 + r) - 1)) * 100.0

    fig_roll = go.Figure()
    fig_roll.add_trace(go.Scatter(x=roll_30.index, y=roll_30.values, name="30-Day Rolling Return", line=dict(color="#38bdf8", width=1.5)))
    fig_roll.add_trace(go.Scatter(x=roll_90.index, y=roll_90.values, name="90-Day Rolling Return", line=dict(color="#f59e0b", width=1.8)))
    if len(roll_252.dropna()) > 0:
        fig_roll.add_trace(go.Scatter(x=roll_252.index, y=roll_252.values, name="1-Year Rolling Return", line=dict(color="#00f2a9", width=2.2)))
    fig_roll.add_hline(y=0, line_dash="dash", line_color="#475569")
    format_chart(fig_roll, title=f"{ticker} — Multi-Horizon Rolling Return Periods", height=420)
    fig_roll.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig_roll, use_container_width=True)

    # Rolling consistency metrics
    rp1, rp2 = st.columns(2)
    with rp1:
        pos_30 = (roll_30.dropna() > 0).mean() * 100.0
        st.metric("30-Day Windows Positive", f"{pos_30:.1f}%", "Consistency of short-term gains")
    with rp2:
        pos_90 = (roll_90.dropna() > 0).mean() * 100.0
        st.metric("90-Day Windows Positive", f"{pos_90:.1f}%", "Consistency of intermediate gains")

# ═══════════════════════════════════════════════════════════════════════════════
# 10. DRAWDOWN ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_dd_analysis:
    st.markdown('<div class="topic-header">🕳️ Drawdown Analysis & Recovery Periods</div>', unsafe_allow_html=True)
    st.markdown('<div class="topic-desc">Detailed catalog of significant historical drawdown episodes, bottom dates, and days spent underwater.</div>', unsafe_allow_html=True)

    # Build episodes table
    is_underwater = drawdown_series < 0
    episodes = []
    current_ep = None

    for dt, dd in drawdown_series.items():
        if dd < 0:
            if current_ep is None:
                current_ep = {"Start": dt, "Trough_Date": dt, "Trough_DD": dd, "End": None}
            else:
                if dd < current_ep["Trough_DD"]:
                    current_ep["Trough_DD"] = dd
                    current_ep["Trough_Date"] = dt
        else:
            if current_ep is not None:
                current_ep["End"] = dt
                episodes.append(current_ep)
                current_ep = None
    if current_ep is not None:
        current_ep["End"] = "Still in Drawdown"
        episodes.append(current_ep)

    if episodes:
        ep_df = pd.DataFrame(episodes)
        ep_df = ep_df.sort_values(by="Trough_DD").head(5)
        formatted_episodes = []
        for rank, row in enumerate(ep_df.itertuples(), 1):
            s_dt = row.Start.strftime("%Y-%m-%d")
            t_dt = row.Trough_Date.strftime("%Y-%m-%d")
            e_dt = row.End.strftime("%Y-%m-%d") if isinstance(row.End, datetime) or isinstance(row.End, pd.Timestamp) else str(row.End)
            depth_pct = f"{row.Trough_DD * 100.0:.2f}%"
            days_to_bottom = (row.Trough_Date - row.Start).days
            formatted_episodes.append({
                "Rank": f"#{rank}",
                "Start Peak": s_dt,
                "Bottom (Trough)": t_dt,
                "Recovery Date": e_dt,
                "Drawdown Depth": depth_pct,
                "Days to Trough": f"{days_to_bottom} days"
            })
        st.markdown("#### 🚨 Top 5 Worst Historical Drawdowns")
        st.dataframe(pd.DataFrame(formatted_episodes), use_container_width=True, hide_index=True)
    else:
        st.info("No significant drawdowns recorded in the selected period.")

# ═══════════════════════════════════════════════════════════════════════════════
# 11. STATISTICAL ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_stats:
    st.markdown('<div class="topic-header">📊 Statistical Analysis & Tail Risk Metrics</div>', unsafe_allow_html=True)
    st.markdown('<div class="topic-desc">Statistical distribution moments, skewness, kurtosis, and Value at Risk (VaR).</div>', unsafe_allow_html=True)

    # Statistical Moments
    mean_ret = float(daily_returns.mean())
    std_ret = float(daily_returns.std())
    skew_val = float(skew(daily_returns))
    kurt_val = float(kurtosis(daily_returns))
    
    # Parametric & Historical VaR
    var_95_hist = np.percentile(daily_returns, 5) * 100.0
    var_99_hist = np.percentile(daily_returns, 1) * 100.0
    cvar_95 = daily_returns[daily_returns <= np.percentile(daily_returns, 5)].mean() * 100.0

    st_col1, st_col2 = st.columns([1, 1])

    with st_col1:
        st.markdown("#### 📐 Distribution Moments")
        stats_table = pd.DataFrame([
            {"Metric": "Daily Mean Return", "Value": f"{mean_ret * 100.0:.3f}%"},
            {"Metric": "Daily Standard Deviation", "Value": f"{std_ret * 100.0:.3f}%"},
            {"Metric": "Annualized Volatility (252d)", "Value": f"{std_ret * np.sqrt(252) * 100.0:.2f}%"},
            {"Metric": "Skewness (Asymmetry)", "Value": f"{skew_val:.3f} ({'Left-skewed (crash risk)' if skew_val<0 else 'Right-skewed'})"},
            {"Metric": "Kurtosis (Fat Tails)", "Value": f"{kurt_val:.3f} ({'Fat Tails / Leptokurtic' if kurt_val>0 else 'Thin Tails'})"},
            {"Metric": "Historical VaR (95% Daily)", "Value": f"{var_95_hist:.2f}%"},
            {"Metric": "Historical VaR (99% Daily)", "Value": f"{var_99_hist:.2f}%"},
            {"Metric": "Expected Shortfall (CVaR 95%)", "Value": f"{cvar_95:.2f}%"}
        ])
        st.dataframe(stats_table, use_container_width=True, hide_index=True)

    with st_col2:
        # Histogram of returns with normal curve overlay
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=daily_returns.values * 100.0,
            nbinsx=45,
            name="Empirical Returns",
            marker_color="rgba(0, 242, 169, 0.6)"
        ))
        # Normal distribution overlay
        x_norm = np.linspace(daily_returns.min() * 100, daily_returns.max() * 100, 100)
        y_norm = norm.pdf(x_norm, mean_ret * 100, std_ret * 100)
        # scale to match histogram counts
        bin_width = (daily_returns.max() * 100 - daily_returns.min() * 100) / 45
        y_norm_scaled = y_norm * len(daily_returns) * bin_width
        fig_hist.add_trace(go.Scatter(x=x_norm, y=y_norm_scaled, name="Normal Fit", line=dict(color="#38bdf8", width=2)))
        format_chart(fig_hist, title="Return Distribution Histogram vs Normal Fit", height=320)
        fig_hist.update_xaxes(ticksuffix="%")
        st.plotly_chart(fig_hist, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 12. VOLUME ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_volume:
    st.markdown('<div class="topic-header">🔊 Volume Analysis & Institutional Liquidity</div>', unsafe_allow_html=True)
    st.markdown('<div class="topic-desc">Analyze trading participation, institutional accumulation spikes, and On-Balance Volume (OBV).</div>', unsafe_allow_html=True)

    vol_series = df["Volume"]
    vol_sma20 = vol_series.rolling(20).mean()

    # On-Balance Volume (OBV)
    obv = (np.sign(close_series.diff()) * vol_series).fillna(0).cumsum()

    fig_obv = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.6, 0.4], vertical_spacing=0.05)
    fig_obv.add_trace(go.Bar(x=vol_series.index, y=vol_series.values, name="Daily Volume", marker_color="#00f2a9", opacity=0.7), row=1, col=1)
    fig_obv.add_trace(go.Scatter(x=vol_sma20.index, y=vol_sma20.values, name="20-Day Volume Avg", line=dict(color="#f59e0b", width=2)), row=1, col=1)
    fig_obv.add_trace(go.Scatter(x=obv.index, y=obv.values, name="On-Balance Volume (OBV)", line=dict(color="#38bdf8", width=2)), row=2, col=1)
    format_chart(fig_obv, title=f"{ticker} — Volume Activity & Cumulative OBV Indicator", height=450)
    st.plotly_chart(fig_obv, use_container_width=True)

    vl1, vl2, vl3 = st.columns(3)
    with vl1:
        st.metric("Average Daily Volume", f"{vol_series.mean():,.0f} shares")
    with vl2:
        avg_dollar_vol = (vol_series * close_series).mean()
        st.metric("Average Dollar Volume", f"${avg_dollar_vol:,.0f} / day")
    with vl3:
        max_vol = vol_series.max()
        max_vol_dt = vol_series.idxmax().strftime("%b %d, %Y")
        st.metric("Peak Volume Day", f"{max_vol:,.0f}", max_vol_dt)

# ═══════════════════════════════════════════════════════════════════════════════
# 13. CORRELATION ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_correlation:
    st.markdown('<div class="topic-header">🔗 Correlation Analysis Across Asset Classes</div>', unsafe_allow_html=True)
    st.markdown('<div class="topic-desc">Pairwise Pearson correlation against major macro benchmarks to evaluate diversification efficacy.</div>', unsafe_allow_html=True)

    benchmark_tickers = {
        "S&P 500 (SPY)": "SPY",
        "Bitcoin (BTC)": "BTC-USD",
        "Gold (GLD)": "GLD",
        "Nasdaq 100 (QQQ)": "QQQ",
        "Treasury Bonds (TLT)": "TLT"
    }
    corr_results = {}
    for name, b_tick in benchmark_tickers.items():
        b_df, _ = MarketDataManager.fetch_data(b_tick, start_date=start_date, end_date=end_date)
        if not b_df.empty and len(b_df) > 5:
            b_ret = calculate_daily_returns(b_df["Close"])
            aligned_asset, aligned_b = daily_returns.align(b_ret, join="inner")
            if len(aligned_asset) > 5:
                corr_results[name] = float(aligned_asset.corr(aligned_b))

    if corr_results:
        corr_series = pd.Series(corr_results).sort_values()
        bar_corr_colors = ["#00f2a9" if c < 0.3 else "#f59e0b" if c < 0.7 else "#f87171" for c in corr_series.values]
        fig_corr = go.Figure()
        fig_corr.add_trace(go.Bar(
            y=corr_series.index,
            x=corr_series.values,
            orientation="h",
            marker_color=bar_corr_colors,
            text=[f"{c:.2f}" for c in corr_series.values],
            textposition="auto"
        ))
        format_chart(fig_corr, title=f"Correlation Matrix: {ticker} vs Global Asset Classes", height=340)
        fig_corr.update_xaxes(range=[-1.0, 1.0])
        st.plotly_chart(fig_corr, use_container_width=True)

        st.markdown("""
        <div style="font-size:0.78rem; color:#94a3b8; font-family:'JetBrains Mono'; margin-top:8px;">
            • <b>Green (&lt;0.30):</b> Excellent diversifier (low or negative correlation with equity risk).<br>
            • <b>Amber (0.30 – 0.70):</b> Moderate co-movement.<br>
            • <b>Red (&gt;0.70):</b> High co-movement (closely mirrors the benchmark).
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 14. BENCHMARK COMPARISON
# ═══════════════════════════════════════════════════════════════════════════════
with tab_benchmark:
    st.markdown('<div class="topic-header">⚔️ Benchmark Comparison (vs S&P 500)</div>', unsafe_allow_html=True)
    st.markdown('<div class="topic-desc">Direct relative performance, Alpha (α), and Beta (β) calculations against the standard market index.</div>', unsafe_allow_html=True)

    if not spy_df.empty and len(spy_df) > 10:
        spy_aligned_close = spy_df["Close"].reindex(close_series.index).ffill().bfill()
        # Normalized curves (start = 100)
        asset_norm = (close_series / close_series.iloc[0]) * 100.0
        spy_norm = (spy_aligned_close / spy_aligned_close.iloc[0]) * 100.0

        fig_bench = go.Figure()
        fig_bench.add_trace(go.Scatter(x=asset_norm.index, y=asset_norm.values, name=f"{ticker} (Asset)", line=dict(color="#00f2a9", width=2.5)))
        fig_bench.add_trace(go.Scatter(x=spy_norm.index, y=spy_norm.values, name="S&P 500 (SPY)", line=dict(color="#38bdf8", width=2.0, dash="dash")))
        format_chart(fig_bench, title=f"Relative Performance (Base = 100): {ticker} vs S&P 500", height=400)
        st.plotly_chart(fig_bench, use_container_width=True)

        # Regression for Beta & Alpha
        spy_ret = calculate_daily_returns(spy_aligned_close)
        ret_a, ret_b = daily_returns.align(spy_ret, join="inner")
        res = linregress(ret_b, ret_a)
        beta = res.slope
        alpha_annual = (res.intercept * 252) * 100.0
        r_squared = res.rvalue ** 2

        b1, b2, b3, b4 = st.columns(4)
        with b1:
            st.metric("Beta (β) vs S&P 500", f"{beta:.2f}", "Market sensitivity multiplier")
        with b2:
            st.metric("Annualized Alpha (α)", f"{'+' if alpha_annual>=0 else ''}{alpha_annual:.2f}%", "Excess performance generated")
        with b3:
            st.metric("R-Squared (R²)", f"{r_squared:.2f}", "% variance explained by S&P 500")
        with b4:
            outperf_pct = (asset_norm.iloc[-1] - spy_norm.iloc[-1])
            st.metric("Net Outperformance", f"{'+' if outperf_pct>=0 else ''}{outperf_pct:.2f}%", "Cumulative excess return")
    else:
        st.info("Benchmark data currently synchronizing. Please try refreshing.")

# ═══════════════════════════════════════════════════════════════════════════════
# 15. MARKET REGIME ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_regime:
    st.markdown('<div class="topic-header">🧭 Market Regime Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="topic-desc">Algorithmic classification of current macro market structure, trend strength, and tactical orientation.</div>', unsafe_allow_html=True)

    # Calculate regime parameters
    p_now = close_series.iloc[-1]
    s50 = sma50.iloc[-1] if not pd.isna(sma50.iloc[-1]) else p_now
    s20 = sma20.iloc[-1] if not pd.isna(sma20.iloc[-1]) else p_now
    vol_ann = metrics['annualized_volatility'] * 100.0

    if p_now > s50 and s20 > s50:
        regime_title = "🟢 STRONG BULLISH TREND"
        regime_desc = "Price is trading above both short and intermediate moving averages with positive slope. Favorable for trend following and holding long positions."
        tactic = "Aggressive holding, trailing stops beneath the 21 EMA, accumulation on pullbacks."
        badge_type = "badge-bullish"
    elif p_now > s50 and s20 <= s50:
        regime_title = "🟡 BULLISH CONSOLIDATION / RETRACEMENT"
        regime_desc = "Macro structure remains positive above the 50 SMA, but short-term momentum has decelerated into a consolidation zone."
        tactic = "Patience; monitor 50 SMA support for continuation entries."
        badge_type = "badge-neutral"
    elif p_now < s50 and s20 < s50:
        regime_title = "🔴 BEARISH REGIME / DOWNWARD TREND"
        regime_desc = "Price is depressed below major trend baselines. High probability of continued structural selling and distribution."
        tactic = "Defensive posture, capital preservation, hedging or short-bias."
        badge_type = "badge-bearish"
    else:
        regime_title = "🟣 HIGH-VOLATILITY CHOP"
        regime_desc = "Oscillating around moving averages with elevated volatility and low directional persistence."
        tactic = "Range trading, smaller position sizing, tight stop losses."
        badge_type = "badge-neutral"

    st.markdown(f"""
    <div style="background:rgba(11,20,28,0.8); border:1px solid rgba(0,242,169,0.3); border-radius:14px; padding:20px; margin-bottom:18px;">
        <span class="{badge_type}" style="font-size:0.9rem;">{regime_title}</span>
        <div style="font-size:1.02rem; font-weight:700; color:#ffffff; margin:12px 0 6px 0;">Regime Diagnosis:</div>
        <div style="font-size:0.86rem; color:#cbd5e1; line-height:1.5;">{regime_desc}</div>
        <div style="margin-top:14px; padding-top:10px; border-top:1px solid rgba(255,255,255,0.08); font-size:0.82rem; color:#00f2a9; font-family:'JetBrains Mono';">
            🎯 TACTICAL PLAYBOOK: {tactic}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 16. AI RESEARCH SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
with tab_ai:
    st.markdown('<div class="topic-header">🤖 AI Research Summary (Featherless AI Engine)</div>', unsafe_allow_html=True)
    st.markdown('<div class="topic-desc">Real-time institutional thesis synthesized strictly from the empirical metrics and price data analyzed above.</div>', unsafe_allow_html=True)

    gen_col1, gen_col2 = st.columns([3, 1])
    with gen_col1:
        st.write("Generate a fresh executive quantitative research brief tailored to the selected timeframe and metrics.")
    with gen_col2:
        ai_trigger = st.button("🧠 Synthesize AI Brief", type="primary", use_container_width=True, key="btn_trigger_ai_brief")

    # Display or generate analysis
    ai_cache_key = f"ai_brief_{ticker}_{start_date}_{end_date}"
    if ai_trigger or ai_cache_key in st.session_state:
        if ai_trigger or ai_cache_key not in st.session_state:
            with st.spinner(f"Featherless AI is formulating institutional quantitative brief for {ticker}..."):
                explanation = ai_client.explain_asset_analysis(
                    asset_name=selected_label,
                    ticker=ticker,
                    metrics=metrics
                )
                st.session_state[ai_cache_key] = explanation
        else:
            explanation = st.session_state[ai_cache_key]

        st.markdown(f"""
        <div style="background:rgba(11,20,28,0.85); border:1px solid #00f2a9; border-radius:12px; padding:20px; margin-top:14px; box-shadow:0 8px 30px rgba(0,242,169,0.12);">
            <div style="font-size:0.85rem; font-weight:800; color:#00f2a9; font-family:'JetBrains Mono'; margin-bottom:10px;">
                🏛️ INSTITUTIONAL QUANTITATIVE RESEARCH MEMORANDUM
            </div>
            <div style="font-size:0.9rem; color:#e2e8f0; line-height:1.7;">
                {explanation}
            </div>
            <div style="margin-top:16px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.08); font-size:0.7rem; color:#64748b; font-family:'JetBrains Mono';">
                FEATHERLESS.AI NEURAL INFERENCE · REASONING MODEL · FOR PROFESSIONAL RESEARCH ONLY
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Click **'🧠 Synthesize AI Brief'** above to generate the live quantitative thesis.")

# ─── Brand Footer ─────────────────────────────────────────────────────────────
render_brand_footer()
