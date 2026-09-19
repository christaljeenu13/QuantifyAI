"""
Reusable High-Fidelity UI Components Module.
Uses st.html to render custom styled HTML components with zero Markdown parsing interference.
"""

from typing import Optional, List
import streamlit as st
from .theme import (
    get_color_palette,
    render_svg_wave,
    generate_mini_sparkline_svg,
    generate_full_width_sparkline_svg
)

COLORS = get_color_palette()


def render_html(html_str: str):
    """Render HTML directly into the DOM using st.html (or fallback)."""
    if hasattr(st, "html"):
        st.html(html_str)
    else:
        st.markdown(html_str, unsafe_allow_html=True)


def render_header(
    title: str,
    subtitle: str = "",
    badge: str = "QUANTIFYAI v1.0",
    badge_type: str = "green"
):
    """Render standardized top terminal header with title, subtitle, and badge."""
    badge_class = f"quant-badge quant-badge-{badge_type}"
    html = f"""
<div style="margin-bottom: 1.25rem;">
    <div style="display: flex; align-items: center; gap: 10px;">
        <h1 style="margin: 0; font-size: 1.8rem; font-weight: 800; letter-spacing: -0.02em; color: #ffffff;">
            {title}
        </h1>
        <span class="{badge_class}">{badge}</span>
    </div>
    <p style="margin: 4px 0 0 0; font-size: 0.88rem; color: #7e92a2;">
        {subtitle}
    </p>
</div>
"""
    render_html(html)


def render_status_badge(text: str, badge_type: str = "green") -> str:
    """Return HTML string for an inline badge."""
    return f'<span class="quant-badge quant-badge-{badge_type}">{text}</span>'


def render_top_navigation():
    """No-op: Removed from all pages per user specification."""
    pass


def render_welcome_banner(
    user_name: str = "Analyst",
    subtitle: str = "Turn market data into insights.",
    date_range_str: str = "Jan 01, 2023 — Jan 01, 2025"
):
    """Render signature Welcome Banner matching Reference Screen 1."""
    html = f"""
<div class="quant-welcome-banner">
    <div style="display: flex; align-items: center; gap: 16px; z-index: 1;">
        <div style="width: 44px; height: 44px; border-radius: 10px; background: linear-gradient(135deg, rgba(0, 242, 169, 0.28), rgba(5, 150, 105, 0.12)); border: 1px solid rgba(0, 242, 169, 0.55); display: flex; align-items: center; justify-content: center; font-size: 1.35rem; box-shadow: 0 0 16px rgba(0, 242, 169, 0.35); color: #00f2a9;">
            ⚡
        </div>
        <div>
            <div style="font-size: 1.6rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
                Welcome Back, {user_name}
            </div>
            <div style="font-size: 0.9rem; color: #7e9aa8; margin-top: 2px;">
                {subtitle}
            </div>
        </div>
    </div>
    <div style="display: flex; align-items: center; gap: 12px; z-index: 1;">
        <div style="background: #091218; border: 1px solid {COLORS['border_teal']}; border-radius: 6px; padding: 6px 14px; font-size: 0.8rem; color: #94a3b8; font-family: 'JetBrains Mono', monospace;">
            📅 {date_range_str}
        </div>
        <div class="quant-badge quant-badge-green" style="padding: 6px 12px; font-size: 0.8rem;">
            <span class="pulse-dot"></span> Live Data
        </div>
    </div>
</div>
"""
    render_html(html)


def render_ticker_card_top(
    label: str,
    ticker: str,
    price: float,
    change_pct: float,
    icon: str
):
    """Render top section of interactive ticker card above sparkline."""
    is_pos = change_pct >= 0
    badge_cls = "quant-badge-green" if is_pos else "quant-badge-red"
    sign = "+" if is_pos else ""

    if "gold" in label.lower() or "gld" in ticker.lower() or "gc=" in ticker.lower():
        icon_bg = "rgba(245, 158, 11, 0.15)"
        icon_border = "rgba(245, 158, 11, 0.4)"
        icon_symbol = "Au"
    elif "btc" in ticker.lower():
        icon_bg = "rgba(249, 115, 22, 0.15)"
        icon_border = "rgba(249, 115, 22, 0.4)"
        icon_symbol = "₿"
    else:
        icon_bg = "rgba(0, 242, 169, 0.15)"
        icon_border = "rgba(0, 242, 169, 0.4)"
        icon_symbol = "N"

    html = f"""
<div class="ticker-card-top">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
        <div style="display: flex; align-items: center; gap: 9px;">
            <div style="width: 28px; height: 28px; border-radius: 50%; background: {icon_bg}; border: 1px solid {icon_border}; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; font-weight: 700; color: #ffffff;">
                {icon_symbol}
            </div>
            <span style="font-size: 0.88rem; font-weight: 600; color: #ffffff;">{label}</span>
        </div>
        <span class="quant-badge quant-badge-teal" style="font-size: 0.68rem; font-weight: 700;">{ticker}</span>
    </div>
    <div style="display: flex; align-items: baseline; gap: 10px;">
        <div class="quant-val" style="font-size: 1.8rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">${price:,.2f}</div>
        <span class="quant-badge {badge_cls}" style="font-size: 0.78rem; font-weight: 700; font-family: 'JetBrains Mono', monospace;">{sign}{change_pct:.2f}%</span>
    </div>
</div>
"""
    render_html(html)


def render_metric_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    is_positive: Optional[bool] = None,
    subtext: str = ""
):
    """Render compact, styled quantitative metric card."""
    delta_html = ""
    if delta:
        delta_class = "quant-delta-pos" if is_positive else "quant-delta-neg"
        delta_html = f"<div class='{delta_class}'>{delta}</div>"

    subtext_html = ""
    if subtext:
        subtext_html = f"<div style='font-size: 0.72rem; color: #64748b; margin-top: 4px;'>{subtext}</div>"

    html = f"""
<div class="quant-card-compact">
    <div class="quant-label">{label}</div>
    <div class="quant-val">{value}</div>
    {delta_html}
    {subtext_html}
</div>
"""
    render_html(html)


def render_sidebar_branding():
    """Render branding and abstract wave in the sidebar matching Mockup."""
    wave_svg = render_svg_wave(height=40, width="100%", opacity=0.7)
    html = f"""
<div style="margin-top: 1rem; text-align: center;">
    {wave_svg}
    <div style="font-size: 0.72rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 6px;">
        Smarter Investing<br>Through Data & AI
    </div>
</div>
"""
    st.sidebar.markdown("---")
    if hasattr(st.sidebar, "html"):
        st.sidebar.html(html)
    else:
        st.sidebar.markdown(html, unsafe_allow_html=True)


def render_brand_footer():
    """Render signature footer bar matching the reference image."""
    wave_svg = render_svg_wave(height=30, width="120", opacity=0.8)
    html = f"""
<div class="quant-bottom-bar">
    <div style="display: flex; align-items: center; gap: 10px;">
        <div style="width: 22px; height: 22px; border-radius: 4px; background: #00f2a9; color: #041210; font-weight: 800; display: flex; align-items: center; justify-content: center; font-size: 0.8rem;">Q</div>
        <span style="font-weight: 700; color: #ffffff; font-size: 0.92rem;">Quantify<span style="color: #00f2a9;">AI</span></span>
        <span style="color: #475569; margin: 0 4px;">|</span>
        <span style="font-size: 0.8rem; color: #7e92a2;">Analyze. Backtest. Compare. Get AI-Powered Insights.</span>
    </div>
    <div style="display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 0.8rem; font-style: italic; color: #94a3b8;">"Data drives better decisions."</span>
        {wave_svg}
    </div>
</div>
<div style="font-size: 0.7rem; color: #475569; text-align: center; margin-top: 0.6rem; margin-bottom: 1.5rem;">
    LEGAL DISCLAIMER: For research and educational purposes only. Historical results do not guarantee future performance.
</div>
"""
    render_html(html)


def render_disclaimer_footer():
    """Alias for render_brand_footer."""
    render_brand_footer()
