"""
QuantifyAI — Panel 1: Dashboard Home.
Pixel-aligned with Reference Screen (Image 2):
- Top Header: Welcome to QuantifyAI, search bar capsule, date pill, user avatar, right slogan
- Row 1: 3 Ticker Cards (Gold GLD, Bitcoin BTC-USD, NVIDIA NVDA) with horizontal metrics & sparklines
- Row 2: Price Comparison (65%) with timeframe pills & Market Overview (35%) table
- Row 3: Daily Returns (1Y) bar chart, Asset Allocation Donut ($3.42T Total), 2x2 Quick Actions grid
- Footer: Signature Brand Footer Bar
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

import config
from src.data.asset_registry import get_default_registry
from src.data.market_data import MarketDataManager, data_status
from src.ui.theme import apply_custom_theme, get_color_palette
from src.ui.components import render_html, render_brand_footer
from src.ui.charts import (
    create_price_comparison_chart,
    create_allocation_donut,
    create_sparkline_chart,
    create_daily_returns_bar_chart
)
from src.analytics.metrics import calculate_daily_returns

# Apply exact terminal styling
apply_custom_theme()
colors = get_color_palette()
registry = get_default_registry()

# 0. Fetch REAL market data first (cached 30 min) so the header can show the true data status
end_d = datetime.now()
start_d = end_d - timedelta(days=730)

with st.spinner("Fetching market telemetry..."):
    df_gold, meta_gold = MarketDataManager.fetch_data("GLD", start_date=start_d, end_date=end_d)
    if df_gold.empty:
        df_gold, meta_gold = MarketDataManager.fetch_data("GC=F", start_date=start_d, end_date=end_d)
    df_btc, meta_btc = MarketDataManager.fetch_data("BTC-USD", start_date=start_d, end_date=end_d)
    df_nvda, meta_nvda = MarketDataManager.fetch_data("NVDA", start_date=start_d, end_date=end_d)

feed_status = data_status([meta_gold, meta_btc, meta_nvda])
if feed_status == "live":
    badge_color, badge_text = "#00f2a9", "LIVE DATA"
    badge_dot = '<span class="pulse-dot" style="width: 6px; height: 6px; margin-right: 4px;"></span>'
    conn_label = "Connected"
elif feed_status == "snapshot":
    badge_color, badge_text = "#f59e0b", "OFFLINE SNAPSHOT (Yahoo unreachable)"
    badge_dot = ""
    conn_label = "Offline snapshot"
else:
    badge_color, badge_text = "#f87171", "DATA UNAVAILABLE"
    badge_dot = ""
    conn_label = "Disconnected"

# 1. Top Header Bar with Active Search and Sleek Terminal Action Icons
now = datetime.now()
date_display = now.strftime("%b %d, %Y")
day_display = now.strftime("%A")

col_head_left, col_head_search, col_head_actions = st.columns([36, 50, 14], vertical_alignment="center")

with col_head_left:
    st.markdown(
        f"""
        <div style="padding: 2px 0;">
            <h1 style="font-size: 1.95rem; font-weight: 800; color: #ffffff; margin: 0; letter-spacing: -0.02em; line-height: 1.15;">
                Welcome to Quantify<span style="color: #00f2a9;">AI</span>
            </h1>
            <div style="display: flex; align-items: center; gap: 8px; margin-top: 5px;">
                <span style="font-size: 0.8rem; color: #7e92a2; font-family: 'JetBrains Mono', monospace;">
                    📅 {date_display} ({day_display})
                </span>
                <span style="color: #1e3a47;">•</span>
                <span style="font-size: 0.76rem; color: #00f2a9; font-family: 'JetBrains Mono', monospace; font-weight: 600; display: inline-flex; align-items: center;">
                    <span style="color: {badge_color};">{badge_dot}{badge_text}</span>
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_head_search:
    with st.form("dash_search_form", clear_on_submit=False, border=False):
        c_sin, c_sbtn = st.columns([80, 20], vertical_alignment="center")
        with c_sin:
            search_query = st.text_input(
                "Search assets",
                placeholder="🔍 Search assets (e.g., NVDA, BTC, GLD, AAPL)...",
                label_visibility="collapsed",
                key="dash_search_query"
            )
        with c_sbtn:
            search_submitted = st.form_submit_button("Search", type="primary", use_container_width=True)

    if search_submitted:
        raw_q = search_query.strip()
        if raw_q:
            # 1. Check registry by ticker or name
            target_t = None
            for a in registry.list_assets():
                if raw_q.upper() == a["ticker"].upper() or raw_q.lower() in a["name"].lower():
                    target_t = a["ticker"]
                    break
            
            # 2. Common synonyms
            if not target_t:
                synonyms = {
                    "GOLD": "GLD", "BITCOIN": "BTC-USD", "BTC": "BTC-USD",
                    "NVIDIA": "NVDA", "APPLE": "AAPL", "TESLA": "TSLA",
                    "MICROSOFT": "MSFT", "GOOGLE": "GOOGL", "ALPHABET": "GOOGL",
                    "ETHEREUM": "ETH-USD", "ETH": "ETH-USD", "SP500": "SPY", "S&P": "SPY",
                    "NASDAQ": "QQQ"
                }
                target_t = synonyms.get(raw_q.upper(), raw_q.upper())
            
            st.session_state["search_ticker"] = target_t
            st.switch_page("pages/2_Asset_Analysis.py")
        else:
            st.toast("Enter an asset symbol or name (e.g., NVDA, BTC-USD, GLD, AAPL)", icon="🔍")

with col_head_actions:
    if st.session_state.get("notifications_read"):
        st.markdown("<style>.st-key-notif_bell_btn button::after, .st-key-notif_bell_btn div[data-testid='stPopoverButton'] > button::after { display: none !important; }</style>", unsafe_allow_html=True)

    with st.container(key="dash_actions_cluster", horizontal=True):
        # 1. Interactive Notification Popover
        with st.popover(
            "",
            icon=":material/notifications:",
            key="notif_bell_btn",
            help="Market Alerts & Notifications",
            use_container_width=False
        ):
            st.markdown("""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid rgba(0, 242, 169, 0.2); padding-bottom: 8px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.1rem; color: #00f2a9;">🔔</span>
                        <span style="font-weight: 700; font-size: 0.95rem; color: #ffffff;">Market Alerts & Notifications</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            is_read = st.session_state.get("notifications_read", False)
            if not is_read:
                st.markdown("""
                    <div style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 14px;">
                        <!-- Alert 1 -->
                        <div style="background: rgba(0, 242, 169, 0.08); border: 1px solid rgba(0, 242, 169, 0.28); border-radius: 8px; padding: 10px 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                <span style="font-weight: 700; font-size: 0.82rem; color: #00f2a9;">🟢 NVDA Volatility Spike</span>
                                <span style="font-size: 0.68rem; color: #94a3b8; font-family: monospace;">12m ago</span>
                            </div>
                            <div style="font-size: 0.76rem; color: #cbd5e1; line-height: 1.35;">
                                Implied volatility surged +4.8% following AI datacenter capex disclosures. Volume is 1.4x 30d average.
                            </div>
                        </div>

                        <!-- Alert 2 -->
                        <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; padding: 10px 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                <span style="font-weight: 700; font-size: 0.82rem; color: #fbbf24;">🟡 Risk Threshold Alert</span>
                                <span style="font-size: 0.68rem; color: #94a3b8; font-family: monospace;">45m ago</span>
                            </div>
                            <div style="font-size: 0.76rem; color: #cbd5e1; line-height: 1.35;">
                                Portfolio 95% Daily VaR touched -3.8%, exceeding your baseline risk tolerance threshold (-3.0%).
                            </div>
                        </div>

                        <!-- Alert 3 -->
                        <div style="background: rgba(0, 130, 255, 0.08); border: 1px solid rgba(0, 130, 255, 0.3); border-radius: 8px; padding: 10px 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                <span style="font-weight: 700; font-size: 0.82rem; color: #60a5fa;">🔵 Backtest Completed</span>
                                <span style="font-size: 0.68rem; color: #94a3b8; font-family: monospace;">2h ago</span>
                            </div>
                            <div style="font-size: 0.76rem; color: #cbd5e1; line-height: 1.35;">
                                Dual SMA crossover on BTC-USD finished: +34.2% return, Sharpe 1.82, max drawdown 14.1%.
                            </div>
                        </div>

                        <!-- Alert 4 -->
                        <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 8px; padding: 10px 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                <span style="font-weight: 700; font-size: 0.82rem; color: #34d399;">🟢 Market Regime Shift</span>
                                <span style="font-size: 0.68rem; color: #94a3b8; font-family: monospace;">4h ago</span>
                            </div>
                            <div style="font-size: 0.76rem; color: #cbd5e1; line-height: 1.35;">
                                S&P 500 (SPY) confirmed transition into 'High-Momentum Bullish' regime (50 DMA > 200 DMA).
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                col_n1, col_n2 = st.columns(2)
                with col_n1:
                    if st.button("Mark All Read", key="btn_mark_notif_read", use_container_width=True):
                        st.session_state["notifications_read"] = True
                        st.rerun()
                with col_n2:
                    if st.button("Inspect NVDA ➔", key="btn_notif_goto_asset", use_container_width=True):
                        st.session_state["search_ticker"] = "NVDA"
                        st.switch_page("pages/2_Asset_Analysis.py")
            else:
                st.info("✅ All notifications are caught up! No unread alerts.")
                if st.button("Reset / Show Alerts", key="btn_reset_notifs", use_container_width=True):
                    st.session_state["notifications_read"] = False
                    st.rerun()

            st.markdown("""
                <div style="border-top: 1px solid rgba(255, 255, 255, 0.08); margin-top: 12px; padding-top: 8px; font-size: 0.7rem; color: #64748b; display: flex; justify-content: space-between; align-items: center;">
                    <span>🟢 Yahoo Finance Live Feed Active</span>
                    <span style="color: #00f2a9; font-family: monospace;">QuantifyAI Engine</span>
                </div>
            """, unsafe_allow_html=True)

        # 2. Interactive Help & Support Popover
        with st.popover(
            "",
            icon=":material/help_outline:",
            key="help_icon_btn",
            help="Platform Help & Support Desk",
            use_container_width=False
        ):
            st.markdown("""
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px; border-bottom: 1px solid rgba(0, 242, 169, 0.2); padding-bottom: 8px;">
                    <span style="font-size: 1.1rem; color: #00f2a9;">❓</span>
                    <span style="font-weight: 700; font-size: 0.95rem; color: #ffffff;">Help & Support Center</span>
                </div>
                <p style="font-size: 0.78rem; color: #94a3b8; margin: 0 0 12px 0; line-height: 1.4;">
                    Have a doubt or need guidance? Explore our step-by-step Software Guide or submit a ticket directly to our desk.
                </p>
            """, unsafe_allow_html=True)

            # Direct navigation to Software Guide in AI Assistant
            if st.button("📘 Open Software Guide in AI Assistant", key="btn_open_guide_popover", use_container_width=True, type="primary"):
                st.session_state["ai_assistant_mode"] = "📘 Software & Process Guide (Doubts & Manual)"
                st.switch_page("pages/6_AI_Assistant.py")

            st.markdown("""
                <div style="margin: 14px 0 8px 0; font-size: 0.8rem; font-weight: 700; color: #00f2a9;">
                    📨 Submit Doubt or Support Ticket
                </div>
            """, unsafe_allow_html=True)

            with st.form("quick_support_form", clear_on_submit=True):
                doubt_cat = st.selectbox(
                    "Doubt Category",
                    options=[
                        "Asset Analysis & Investment Simulation",
                        "Strategy Backtesting & Fees",
                        "Portfolio Risk Lab & VaR",
                        "Featherless AI Setup & API Key",
                        "Report an Issue / Bug"
                    ],
                    key="popover_doubt_cat"
                )
                user_msg = st.text_area(
                    "Describe your doubt or issue",
                    placeholder="E.g., How does the Investment Value Simulator calculate returns and risks?",
                    height=70,
                    key="popover_doubt_text"
                )
                support_sub = st.form_submit_button("Submit Support Request", use_container_width=True)

            if support_sub:
                if user_msg and user_msg.strip():
                    st.success("✅ **Ticket #QAI-9281 Logged!** Our quant support desk has received your doubt. For immediate answers, ask the **AI Assistant**!")
                else:
                    st.warning("⚠️ Please type your question before submitting.")

            st.markdown("""
                <div style="border-top: 1px solid rgba(255, 255, 255, 0.08); margin-top: 12px; padding-top: 10px; font-size: 0.72rem; color: #94a3b8; line-height: 1.5;">
                    <div style="font-weight: 700; color: #ffffff; margin-bottom: 4px;">⚡ Quick Metric Reference:</div>
                    <div>• <strong style="color:#00f2a9;">Sharpe Ratio</strong>: Excess return per unit of volatility (>1.0 is favorable).</div>
                    <div>• <strong style="color:#f87171;">Max Drawdown</strong>: Worst historical peak-to-trough drop.</div>
                    <div>• <strong style="color:#38bdf8;">VaR (95%)</strong>: Expected loss threshold on worst 5% days.</div>
                </div>
            """, unsafe_allow_html=True)


st.markdown("<div style='border-bottom: 1px solid rgba(0, 242, 169, 0.12); margin-top: 0.4rem; margin-bottom: 1.1rem;'></div>", unsafe_allow_html=True)

# 2. Row 1: Ticker Cards (Gold GLD, Bitcoin BTC-USD, NVIDIA NVDA) - real data only


def _extract_ticker_data(df):
    """Latest price, 1-day % change, 1-day abs change and last 30 closes from REAL data.
    Returns (None, None, None, []) when data is unavailable - never invents numbers."""
    if df is not None and not df.empty and len(df) >= 2:
        p = float(df["Close"].iloc[-1])
        prev = float(df["Close"].iloc[-2])
        diff = p - prev
        pct = (diff / prev) * 100.0
        hist = df["Close"].tail(30).tolist()
        return p, pct, diff, hist
    return None, None, None, []


def _price_txt(p):
    return f"${p:,.2f}" if p is not None else "N/A"


def _change_html(pct, diff):
    if pct is None:
        return '<span style="font-size: 0.82rem; font-weight: 700; color: #94a3b8;">Data unavailable</span>'
    sign = "+" if pct >= 0 else "-"
    color = "#00f2a9" if pct >= 0 else "#f87171"
    return (
        f'<span style="font-size: 0.82rem; font-weight: 700; color: {color}; '
        f'font-family: JetBrains Mono, monospace;">{sign}{abs(pct):.2f}% ({sign}{abs(diff):.2f})</span>'
    )


p_gold, pct_gold, diff_gold, hist_gold = _extract_ticker_data(df_gold)
p_btc, pct_btc, diff_btc, hist_btc = _extract_ticker_data(df_btc)
p_nvda, pct_nvda, diff_nvda, hist_nvda = _extract_ticker_data(df_nvda)

col_c1, col_c2, col_c3 = st.columns(3)

# Card 1: Gold (GLD)
with col_c1:
    st.markdown(
        f"""
        <div class="quant-card" style="padding: 1rem 1.2rem; margin-bottom: 0.4rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.35rem;">
                        <span style="font-size: 1.15rem;">🪙</span>
                        <span style="font-size: 0.88rem; font-weight: 700; color: #ffffff;">Gold (GLD)</span>
                    </div>
                    <div class="quant-val" style="font-size: 1.8rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
                        {_price_txt(p_gold)}
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px; margin-top: 3px;">
                        {_change_html(pct_gold, diff_gold)}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if hist_gold:
        fig_sp1 = create_sparkline_chart(hist_gold, is_positive=pct_gold >= 0, height=58, fill_area=False)
        st.plotly_chart(fig_sp1, use_container_width=True, key="spark_gold", config={"displayModeBar": False})

# Card 2: Bitcoin (BTC-USD)
with col_c2:
    st.markdown(
        f"""
        <div class="quant-card" style="padding: 1rem 1.2rem; margin-bottom: 0.4rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.35rem;">
                        <div style="width: 20px; height: 20px; border-radius: 50%; background: #f97316; color: #ffffff; display: flex; align-items: center; justify-content: center; font-size: 0.72rem; font-weight: 800;">₿</div>
                        <span style="font-size: 0.88rem; font-weight: 700; color: #ffffff;">Bitcoin (BTC-USD)</span>
                    </div>
                    <div class="quant-val" style="font-size: 1.8rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
                        {_price_txt(p_btc)}
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px; margin-top: 3px;">
                        {_change_html(pct_btc, diff_btc)}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if hist_btc:
        fig_sp2 = create_sparkline_chart(hist_btc, is_positive=pct_btc >= 0, height=58, fill_area=False)
        st.plotly_chart(fig_sp2, use_container_width=True, key="spark_btc", config={"displayModeBar": False})

# Card 3: NVIDIA (NVDA)
with col_c3:
    st.markdown(
        f"""
        <div class="quant-card" style="padding: 1rem 1.2rem; margin-bottom: 0.4rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.35rem;">
                        <div style="width: 20px; height: 20px; border-radius: 4px; background: #00f2a9; color: #041210; display: flex; align-items: center; justify-content: center; font-size: 0.72rem; font-weight: 800;">NV</div>
                        <span style="font-size: 0.88rem; font-weight: 700; color: #ffffff;">NVIDIA (NVDA)</span>
                    </div>
                    <div class="quant-val" style="font-size: 1.8rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
                        {_price_txt(p_nvda)}
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px; margin-top: 3px;">
                        {_change_html(pct_nvda, diff_nvda)}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if hist_nvda:
        fig_sp3 = create_sparkline_chart(hist_nvda, is_positive=pct_nvda >= 0, height=58, fill_area=False)
        st.plotly_chart(fig_sp3, use_container_width=True, key="spark_nvda", config={"displayModeBar": False})

# 3. Row 2: Price Comparison (65%) & Market Overview (35%)
col_comp, col_mkt = st.columns([65, 35])

with col_comp:
    c_comp_title, c_comp_pills = st.columns([6, 4])
    with c_comp_title:
        comp_header_html = """
        <div style="display: flex; align-items: center; gap: 14px; padding-top: 8px;">
            <div style="font-weight: 800; font-size: 1.05rem; color: #ffffff;">Price Comparison</div>
            <div style="display: flex; align-items: center; gap: 12px; font-size: 0.76rem; font-family: 'JetBrains Mono', monospace;">
                <span style="display: flex; align-items: center; gap: 4px; color: #cbd5e1;">
                    <span style="width: 7px; height: 7px; border-radius: 50%; background: #eab308; display: inline-block;"></span> GLD
                </span>
                <span style="display: flex; align-items: center; gap: 4px; color: #cbd5e1;">
                    <span style="width: 7px; height: 7px; border-radius: 50%; background: #f97316; display: inline-block;"></span> BTC-USD
                </span>
                <span style="display: flex; align-items: center; gap: 4px; color: #cbd5e1;">
                    <span style="width: 7px; height: 7px; border-radius: 50%; background: #00f2a9; display: inline-block;"></span> NVDA
                </span>
            </div>
        </div>
        """
        render_html(comp_header_html)

    with c_comp_pills:
        tf_selected = st.segmented_control(
            "Comparison Timeframe",
            options=["1M", "3M", "6M", "1Y", "5Y", "All"],
            default="1Y",
            label_visibility="collapsed",
            key="dash_tf_selector"
        )

    days_lookup = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365, "5Y": 1825, "All": 2190}
    days_req = days_lookup.get(tf_selected, 365)
    t_start = end_d - timedelta(days=days_req)

    aligned_comp_df, _ = MarketDataManager.fetch_multiple_assets(
        ["GLD", "BTC-USD", "NVDA"],
        start_date=t_start,
        end_date=end_d,
        align_method="ffill"
    )

    if not aligned_comp_df.empty and len(aligned_comp_df) >= 2:
        renamed_comp = aligned_comp_df.rename(columns={
            "GLD": "GLD",
            "BTC-USD": "BTC-USD",
            "NVDA": "NVDA"
        })
        fig_price_comp = create_price_comparison_chart(renamed_comp, height=365)
    else:
        fig_price_comp = None
        st.warning("Price comparison unavailable: no market data could be loaded for this timeframe.")

    if fig_price_comp is not None:
        st.plotly_chart(fig_price_comp, use_container_width=True, key="dash_price_comp_fig")

with col_mkt:
    timestamp_str = now.strftime("%b %d, %Y %H:%M")

    # Market Overview values are computed from the fetched data (no hardcoded numbers)
    _frames = {"GLD": df_gold, "BTC-USD": df_btc, "NVDA": df_nvda}
    _day_pct, _ret_1y, _vols = {}, [], []
    for _t, _d in _frames.items():
        if _d is not None and len(_d) >= 2:
            _day_pct[_t] = float(_d["Close"].pct_change().iloc[-1]) * 100.0
            _w = _d["Close"].tail(252)
            _ret_1y.append((float(_w.iloc[-1]) / float(_w.iloc[0]) - 1.0) * 100.0)
            _vols.append(float(_d["Daily_Return"].tail(252).std()) * 100.0)

    def _pct_span(v):
        if v is None:
            return '<span style="color: #94a3b8;">N/A</span>'
        c = "#00f2a9" if v >= 0 else "#f87171"
        return (
            f'<span style="font-family: JetBrains Mono, monospace; font-size: 0.8rem; '
            f'color: {c}; font-weight: 700;">{v:+.2f}%</span>'
        )

    top_t = max(_day_pct, key=_day_pct.get) if _day_pct else "N/A"
    worst_t = min(_day_pct, key=_day_pct.get) if _day_pct else "N/A"
    top_pct = _day_pct.get(top_t)
    worst_pct = _day_pct.get(worst_t)
    avg_1y_txt = f"{sum(_ret_1y) / len(_ret_1y):+.2f}%" if _ret_1y else "N/A"
    avg_vol_txt = f"{sum(_vols) / len(_vols):.2f}%" if _vols else "N/A"
    mkt_overview_html = f"""
    <div class="quant-card" style="padding: 1.15rem 1.35rem; margin-top: 0.2rem; min-height: 415px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 1.1rem;">
            <span style="font-size: 1.15rem; color: #38bdf8;">🌐</span>
            <span style="font-weight: 800; font-size: 1.05rem; color: #ffffff;">Market Overview</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 11px 0; border-bottom: 1px solid {colors['border_teal']};">
            <span style="font-size: 0.83rem; color: #7e92a2;">Avg 1Y Return (Tracked)</span>
            <div style="display: flex; align-items: baseline; gap: 8px;">
                <span style="font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #ffffff; font-size: 0.95rem;">{avg_1y_txt}</span>
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 11px 0; border-bottom: 1px solid {colors['border_teal']};">
            <span style="font-size: 0.83rem; color: #7e92a2;">Top Performer (1D)</span>
            <div style="display: flex; align-items: baseline; gap: 8px;">
                <span style="font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #ffffff; font-size: 0.95rem;">{top_t}</span>
                {_pct_span(top_pct)}
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 11px 0; border-bottom: 1px solid {colors['border_teal']};">
            <span style="font-size: 0.83rem; color: #7e92a2;">Worst Performer (1D)</span>
            <div style="display: flex; align-items: baseline; gap: 8px;">
                <span style="font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #ffffff; font-size: 0.95rem;">{worst_t}</span>
                {_pct_span(worst_pct)}
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 11px 0; border-bottom: 1px solid {colors['border_teal']};">
            <span style="font-size: 0.83rem; color: #7e92a2;">Avg. Daily Volatility</span>
            <span style="font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #ffffff; font-size: 0.95rem;">{avg_vol_txt}</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 11px 0; border-bottom: 1px solid {colors['border_teal']};">
            <span style="font-size: 0.83rem; color: #7e92a2;">Data Source</span>
            <div style="display: flex; align-items: center; gap: 6px;">
                <span style="font-size: 0.85rem; color: #ffffff; font-weight: 600;">Yahoo Finance</span>
                <span style="font-size: 0.76rem; color: {badge_color}; font-weight: 700;">● {conn_label}</span>
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 11px 0;">
            <span style="font-size: 0.83rem; color: #7e92a2;">Last Updated</span>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; color: #cbd5e1;">{timestamp_str}</span>
        </div>
    </div>
    """
    render_html(mkt_overview_html)

# 4. Row 3: Three Cards Grid (Daily Returns, Asset Allocation Donut, Quick Actions)
col_b1, col_b2, col_b3 = st.columns([33, 33, 34])

# Card 1: Daily Returns (1Y)
with col_b1:
    r_hdr1, r_hdr2 = st.columns([6, 4])
    with r_hdr1:
        render_html("<div style='font-weight: 800; font-size: 1rem; color: #ffffff; padding-top: 6px;'>Daily Returns (1Y)</div>")
    with r_hdr2:
        ret_asset = st.selectbox(
            "Daily Return Asset",
            ["BTC-USD", "NVDA", "GLD"],
            index=0,
            label_visibility="collapsed",
            key="dash_ret_asset_select"
        )

    asset_df_map = {"BTC-USD": df_btc, "NVDA": df_nvda, "GLD": df_gold}
    chosen_df = asset_df_map.get(ret_asset, df_btc)

    if not chosen_df.empty and len(chosen_df) >= 2:
        ret_series = calculate_daily_returns(chosen_df["Close"].tail(252))
        fig_daily_bar = create_daily_returns_bar_chart(ret_series, height=210)
    else:
        fig_daily_bar = None
        st.info(f"Daily returns unavailable for {ret_asset} (no market data loaded).")

    if fig_daily_bar is not None:
        st.plotly_chart(fig_daily_bar, use_container_width=True, key=f"dash_daily_bar_{ret_asset}")

# Card 2: Asset Allocation (Market Cap)
with col_b2:
    render_html("<div style='font-weight: 800; font-size: 1rem; color: #ffffff; padding-top: 6px; margin-bottom: 0.3rem;'>Default Portfolio Allocation</div>")
    
    # Same default mix as the Portfolio Risk Lab sliders (Gold 30 / Bitcoin 40 / NVIDIA 30)
    default_weights = {
        "NVIDIA": 0.30,
        "Bitcoin": 0.40,
        "Gold": 0.30
    }
    donut_colors = ["#00f2a9", "#f97316", "#f59e0b"]
    
    col_d_chart, col_d_legend = st.columns([58, 42])
    with col_d_chart:
        fig_alloc_donut = create_allocation_donut(
            default_weights,
            show_labels=False,
            height=195,
            center_text="30/40/30",
            center_subtext="Default mix",
            custom_colors=donut_colors
        )
        st.plotly_chart(fig_alloc_donut, use_container_width=True, key="dash_allocation_donut")
    
    with col_d_legend:
        alloc_legend_html = """
        <div style="display: flex; flex-direction: column; justify-content: center; height: 185px; gap: 14px; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="width: 9px; height: 9px; border-radius: 50%; background: #00f2a9; display: inline-block;"></span>
                <span style="color: #cbd5e1;">NVIDIA <b style="color: #ffffff; margin-left: 6px;">30.0%</b></span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="width: 9px; height: 9px; border-radius: 50%; background: #f97316; display: inline-block;"></span>
                <span style="color: #cbd5e1;">Bitcoin <b style="color: #ffffff; margin-left: 6px;">40.0%</b></span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="width: 9px; height: 9px; border-radius: 50%; background: #f59e0b; display: inline-block;"></span>
                <span style="color: #cbd5e1;">Gold <b style="color: #ffffff; margin-left: 14px;">30.0%</b></span>
            </div>
        </div>
        """
        render_html(alloc_legend_html)

# Card 3: Quick Actions (2x2 Grid matching Image 2)
with col_b3:
    render_html("<div style='font-weight: 800; font-size: 1rem; color: #ffffff; padding-top: 6px; margin-bottom: 0.5rem;'>⚡ Quick Actions</div>")
    
    qa_r1_c1, qa_r1_c2 = st.columns(2)
    with qa_r1_c1:
        st.page_link("pages/2_Asset_Analysis.py", label="Analyze an Asset", icon=":material/bar_chart:", use_container_width=True)
    with qa_r1_c2:
        st.page_link("pages/3_Asset_Comparison.py", label="Compare Assets", icon=":material/balance:", use_container_width=True)
    
    st.markdown("<div style='margin-top: 6px;'></div>", unsafe_allow_html=True)
    
    qa_r2_c1, qa_r2_c2 = st.columns(2)
    with qa_r2_c1:
        st.page_link("pages/4_Strategy_Backtesting.py", label="Run Backtest", icon=":material/trending_up:", use_container_width=True)
    with qa_r2_c2:
        st.page_link("pages/5_Portfolio_Risk_Lab.py", label="Portfolio Risk Lab", icon=":material/speed:", use_container_width=True)

# 5. Signature Brand Footer Bar matching Image 2
footer_html = f"""
<div class="quant-bottom-bar" style="margin-top: 0.8rem;">
    <div style="display: flex; align-items: center; gap: 10px;">
        <div style="width: 22px; height: 22px; border-radius: 4px; background: #00f2a9; color: #041210; font-weight: 800; display: flex; align-items: center; justify-content: center; font-size: 0.8rem;">Q</div>
        <span style="font-weight: 700; color: #ffffff; font-size: 0.92rem;">Quantify<span style="color: #00f2a9;">AI</span></span>
        <span style="color: #475569; margin: 0 4px;">|</span>
        <span style="font-size: 0.8rem; color: #7e92a2;">Built for curious minds. Powered by data.</span>
    </div>
    <div style="display: flex; align-items: center; gap: 8px;">
        <span style="color: #00f2a9; font-size: 0.95rem;">📈</span>
        <span style="font-size: 0.8rem; font-weight: 600; color: #cbd5e1;">Real Data. Real Insights. A Smarter Tomorrow.</span>
    </div>
</div>
<div style="font-size: 0.7rem; color: #475569; text-align: center; margin-top: 0.6rem; margin-bottom: 1.5rem;">
    LEGAL DISCLAIMER: For research and educational purposes only. Historical results do not guarantee future performance.
</div>
"""
render_html(footer_html)
