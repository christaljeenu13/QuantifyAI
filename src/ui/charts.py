"""
Plotly Chart Factory Module — High-Fidelity Terminal Visualizations.
Produces charts matching the QuantifyAI neon-glowing aesthetic:
Spline smoothing, dark slate canvas (#080d12), and coordinated palette.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import config
from .theme import get_color_palette

COLORS = get_color_palette()

ASSET_LINE_COLORS = {
    "GLD": "#f59e0b",
    "Gold (GLD)": "#f59e0b",
    "Gold": "#f59e0b",
    "GC=F": "#f59e0b",
    "Gold (XAU/USD)": "#f59e0b",
    "BTC-USD": "#38bdf8",
    "Bitcoin (BTC-USD)": "#38bdf8",
    "Bitcoin": "#38bdf8",
    "Bitcoin (BTC)": "#38bdf8",
    "NVDA": "#00f2a9",
    "NVIDIA (NVDA)": "#00f2a9",
    "NVIDIA": "#00f2a9",
    "SPY": "#a855f7",
    "Strategy": "#00f2a9",
    "Buy & Hold": "#38bdf8",
    "Benchmark": "#38bdf8"
}

FALLBACK_PALETTE = [
    "#00f2a9", "#38bdf8", "#f59e0b", "#f472b6", "#a78bfa", "#34d399", "#fb923c"
]


def _apply_dark_layout(
    fig: go.Figure,
    title: str = "",
    height: int = 400,
    show_legend: bool = True,
    x_title: str = "",
    y_title: str = ""
) -> go.Figure:
    """Standardize layout and fonts across all Plotly charts with green gradient background."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(6, 10, 14, 0.0)",
        plot_bgcolor="rgba(8, 13, 18, 1.0)",
        font=dict(family="Inter, sans-serif", color="#e2e8f0", size=12),
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(size=14, color="#ffffff"),
            x=0.01,
            y=0.97
        ),
        margin=dict(l=45, r=20, t=40 if title else 20, b=35),
        height=height,
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#0b151d",
            bordercolor=COLORS["border_teal"],
            font=dict(family="JetBrains Mono, monospace", size=11, color="#ffffff")
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color="#94a3b8"),
            bgcolor="rgba(0,0,0,0)"
        ) if show_legend else dict(visible=False),
        # Green gradient radial glow shapes as background overlays
        shapes=[
            # Bottom-left emerald glow
            dict(
                type="rect",
                xref="paper", yref="paper",
                x0=0, y0=0, x1=1, y1=1,
                fillcolor="rgba(0, 242, 169, 0.03)",
                line_width=0,
                layer="below"
            ),
        ]
    )
    fig.update_xaxes(
        gridcolor="rgba(20, 40, 52, 0.8)",
        zerolinecolor=COLORS["border_teal"],
        title_text=x_title,
        title_font=dict(size=11, color=COLORS["text_muted"])
    )
    fig.update_yaxes(
        gridcolor="rgba(20, 40, 52, 0.8)",
        zerolinecolor=COLORS["border_teal"],
        title_text=y_title,
        title_font=dict(size=11, color=COLORS["text_muted"])
    )
    # Add green corner gradient via a diagonal line overlay for emerald glow effect
    fig.add_shape(
        type="rect",
        xref="paper", yref="paper",
        x0=0, y0=0, x1=0.35, y1=0.35,
        fillcolor="rgba(0, 242, 169, 0.04)",
        line_width=0,
        layer="below"
    )
    fig.add_shape(
        type="rect",
        xref="paper", yref="paper",
        x0=0.65, y0=0.65, x1=1, y1=1,
        fillcolor="rgba(0, 210, 255, 0.025)",
        line_width=0,
        layer="below"
    )
    return fig


def create_performance_line_chart(
    df: pd.DataFrame,
    title: str = "Market Performance (Normalized)",
    y_title: str = "Price (USD)",
    is_normalized: bool = False
) -> go.Figure:
    """Create clean multi-trace line chart with spline smoothing."""
    fig = go.Figure()

    cols = df.columns if isinstance(df, pd.DataFrame) else [df.name]
    for idx, col in enumerate(cols):
        series = df[col] if isinstance(df, pd.DataFrame) else df
        col_str = str(col)
        color = ASSET_LINE_COLORS.get(col_str, FALLBACK_PALETTE[idx % len(FALLBACK_PALETTE)])

        fig.add_trace(
            go.Scatter(
                x=series.index,
                y=series.values,
                mode="lines",
                name=col_str,
                line=dict(color=color, width=2.5, shape="spline", smoothing=1.1),
                hovertemplate=f"<b>{col_str}</b>: %{{y:.2f}}<extra></extra>"
            )
        )

    if is_normalized:
        fig.add_hline(y=100.0, line_dash="dash", line_color="#475569", opacity=0.7)

    _apply_dark_layout(fig, title=title, y_title=y_title, height=390)
    return fig


def create_candlestick_chart(
    df: pd.DataFrame,
    ticker: str,
    show_sma: bool = True,
    show_ema: bool = True,
    sma_windows: List[int] = [20, 50],
    ema_windows: List[int] = [12, 26]
) -> go.Figure:
    """Create OHLC Candlestick chart with moving average overlays and volume subplots."""
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.75, 0.25]
    )

    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="OHLC",
            increasing_line_color=COLORS["accent_green"],
            decreasing_line_color=COLORS["negative_red"],
            increasing_fillcolor=COLORS["accent_green"],
            decreasing_fillcolor=COLORS["negative_red"]
        ),
        row=1,
        col=1
    )

    # Overlays
    if show_sma:
        from src.analytics.indicators import calculate_sma
        colors = ["#38bdf8", "#f59e0b"]
        for idx, w in enumerate(sma_windows):
            sma = calculate_sma(df["Close"], window=w)
            c = colors[idx % len(colors)]
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=sma,
                    mode="lines",
                    name=f"SMA {w}",
                    line=dict(color=c, width=1.6)
                ),
                row=1,
                col=1
            )

    if show_ema:
        from src.analytics.indicators import calculate_ema
        colors = ["#f472b6", "#a78bfa"]
        for idx, w in enumerate(ema_windows):
            ema = calculate_ema(df["Close"], span=w)
            c = colors[idx % len(colors)]
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=ema,
                    mode="lines",
                    name=f"EMA {w}",
                    line=dict(color=c, width=1.4, dash="dot")
                ),
                row=1,
                col=1
            )

    # Volume bars
    if "Volume" in df.columns:
        vol_colors = [
            COLORS["accent_green"] if c >= o else COLORS["negative_red"]
            for c, o in zip(df["Close"], df["Open"])
        ]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df["Volume"],
                name="Volume",
                marker_color=vol_colors,
                opacity=0.6
            ),
            row=2,
            col=1
        )

    fig.update_layout(xaxis_rangeslider_visible=False)
    _apply_dark_layout(fig, title=f"{ticker} Price & Technical Overlays", height=460)
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    return fig


def create_drawdown_chart(
    drawdown_series: pd.Series, title: str = "Drawdown (Underwater Profile)"
) -> go.Figure:
    """Create underwater area chart representing percentage drawdown."""
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=drawdown_series.index,
            y=drawdown_series.values * 100.0,
            mode="lines",
            name="Drawdown",
            line=dict(color=COLORS["negative_red"], width=1.8),
            fill="tozeroy",
            fillcolor="rgba(248, 113, 113, 0.18)",
            hovertemplate="Drawdown: %{y:.2f}%<extra></extra>"
        )
    )

    _apply_dark_layout(fig, title=title, y_title="Drawdown (%)", height=280)
    fig.update_yaxes(ticksuffix="%")
    return fig


def create_indicator_chart(df: pd.DataFrame, indicator_type: str = "rsi") -> go.Figure:
    """Render technical indicators (RSI or MACD)."""
    fig = go.Figure()

    if indicator_type.lower() == "rsi":
        from src.analytics.indicators import calculate_rsi
        rsi = calculate_rsi(df["Close"], period=14)

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=rsi,
                mode="lines",
                name="RSI (14)",
                line=dict(color="#38bdf8", width=2.0),
                hovertemplate="RSI: %{y:.2f}<extra></extra>"
            )
        )
        fig.add_hline(y=70, line_dash="dash", line_color=COLORS["negative_red"], annotation_text="Overbought (70)")
        fig.add_hline(y=30, line_dash="dash", line_color=COLORS["accent_green"], annotation_text="Oversold (30)")
        fig.add_hline(y=50, line_dash="dot", line_color="#475569", opacity=0.5)

        _apply_dark_layout(fig, title="Relative Strength Index (RSI 14)", y_title="RSI", height=280)
        fig.update_yaxes(range=[0, 100])

    elif indicator_type.lower() == "macd":
        from src.analytics.indicators import calculate_macd
        macd_df = calculate_macd(df["Close"])

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=macd_df["MACD"],
                mode="lines",
                name="MACD",
                line=dict(color="#00f2a9", width=2.0)
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=macd_df["Signal"],
                mode="lines",
                name="Signal",
                line=dict(color="#f59e0b", width=1.6, dash="dot")
            )
        )
        hist_colors = [
            COLORS["accent_green"] if h >= 0 else COLORS["negative_red"]
            for h in macd_df["Histogram"]
        ]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=macd_df["Histogram"],
                name="Histogram",
                marker_color=hist_colors,
                opacity=0.75
            )
        )

        _apply_dark_layout(fig, title="MACD (12, 26, 9)", y_title="Value", height=280)

    return fig


def create_correlation_heatmap(corr_df: pd.DataFrame) -> go.Figure:
    """Create correlation matrix heatmap with custom dark-teal gradient."""
    fig = go.Figure()

    custom_colorscale = [
        [0.0, "#08121a"],
        [0.5, "#0e2938"],
        [1.0, "#00f2a9"]
    ]

    fig.add_trace(
        go.Heatmap(
            z=corr_df.values,
            x=list(corr_df.columns),
            y=list(corr_df.index),
            colorscale=custom_colorscale,
            zmin=-1.0,
            zmax=1.0,
            text=np.round(corr_df.values, 2),
            texttemplate="%{text}",
            textfont=dict(size=13, color="#ffffff", family="JetBrains Mono"),
            colorbar=dict(
                title="Corr",
                tickfont=dict(color="#94a3b8")
            )
        )
    )

    _apply_dark_layout(fig, title="Pairwise Correlation Heatmap", height=340)
    return fig


def create_risk_return_scatter(summary_df: pd.DataFrame, height: int = 360) -> go.Figure:
    """Create comprehensive Volatility vs Return Risk/Return graph with Capital Allocation Line, frontier curve, and asset nodes."""
    if summary_df is None or summary_df.empty:
        fig = go.Figure()
        _apply_dark_layout(fig, title="Risk vs Return Profile (No Data)", height=height)
        return fig

    fig = go.Figure()

    vols = []
    rets = []
    sharpes = []
    names = []
    node_data = []

    for idx, row in summary_df.iterrows():
        name = str(row["Asset"])
        vol_raw = row.get("Annualized Volatility", 0.0)
        ret_raw = row.get("Annualized Return", 0.0)
        sharpe_raw = row.get("Sharpe Ratio", 0.0)
        mdd_raw = row.get("Max Drawdown", 0.0)

        try:
            vol = float(vol_raw) * 100.0 if float(vol_raw) < 5.0 else float(vol_raw)
        except Exception:
            vol = 0.0
        try:
            ret = float(ret_raw) * 100.0 if float(ret_raw) < 15.0 else float(ret_raw)
        except Exception:
            ret = 0.0
        try:
            sharpe = float(sharpe_raw)
        except Exception:
            sharpe = 0.0
        try:
            mdd = float(mdd_raw) * 100.0 if abs(float(mdd_raw)) <= 1.0 else float(mdd_raw)
        except Exception:
            mdd = 0.0

        vols.append(vol)
        rets.append(ret)
        sharpes.append(sharpe)
        names.append(name)
        color = ASSET_LINE_COLORS.get(name, FALLBACK_PALETTE[idx % len(FALLBACK_PALETTE)])
        node_data.append((name, vol, ret, sharpe, mdd, color))

    rf_pct = getattr(config, "DEFAULT_RISK_FREE_RATE", 0.042) * 100.0
    max_vol = max(vols) if vols else 30.0
    max_x = max(max_vol * 1.3, 20.0)

    # 1. Add Capital Allocation Line (CAL) from (0, rf_pct) to max Sharpe asset
    if vols and max_vol > 0:
        best_idx = int(np.argmax(sharpes)) if sharpes else 0
        best_vol = vols[best_idx]
        best_ret = rets[best_idx]
        best_name = names[best_idx]
        best_s = sharpes[best_idx]

        if best_vol > 0:
            cal_slope = (best_ret - rf_pct) / best_vol
            cal_x = [0.0, best_vol, max_x]
            cal_y = [rf_pct, best_ret, rf_pct + cal_slope * max_x]

            fig.add_trace(
                go.Scatter(
                    x=cal_x,
                    y=cal_y,
                    mode="lines",
                    name=f"Capital Allocation Line ({best_name} Sharpe {best_s:.2f})",
                    line=dict(color="#00f2a9", width=2, dash="dash"),
                    hoverinfo="skip"
                )
            )

    # 2. Add Risk-Reward Empirical Frontier Curve if multiple assets exist
    if len(vols) >= 2:
        sorted_pairs = sorted(zip(vols, rets), key=lambda p: p[0])
        s_vols, s_rets = zip(*sorted_pairs)
        try:
            # Quadratic fit for empirical risk-return curve
            poly_deg = min(2, len(vols) - 1)
            poly_coefs = np.polyfit(s_vols, s_rets, deg=poly_deg)
            curve_x = np.linspace(min(s_vols) * 0.85, max_x, 50)
            curve_y = np.polyval(poly_coefs, curve_x)

            fig.add_trace(
                go.Scatter(
                    x=curve_x,
                    y=curve_y,
                    mode="lines",
                    name="Risk-Reward Frontier Curve",
                    line=dict(color="rgba(56, 189, 248, 0.55)", width=2.2, shape="spline"),
                    hoverinfo="skip"
                )
            )
        except Exception:
            pass

    # 3. Add asset scatter nodes with high-visibility markers
    for name, vol, ret, sharpe, mdd, color in node_data:
        fig.add_trace(
            go.Scatter(
                x=[vol],
                y=[ret],
                mode="markers+text",
                name=name,
                text=[f"  {name}"],
                textposition="middle right",
                cliponaxis=False,
                textfont=dict(family="Inter, sans-serif", size=12, color="#ffffff"),
                marker=dict(
                    size=16,
                    color=color,
                    line=dict(width=2.2, color="#ffffff"),
                    opacity=0.95
                ),
                hovertemplate=(
                    f"<b>{name}</b><br>"
                    f"• Ann. Volatility (Risk): <b>{vol:.2f}%</b><br>"
                    f"• Ann. Return (Reward): <b>{ret:.2f}%</b><br>"
                    f"• Sharpe Ratio: <b>{sharpe:.2f}</b><br>"
                    f"• Max Drawdown: <b>{mdd:.2f}%</b>"
                    "<extra></extra>"
                )
            )
        )

    # 4. Add baseline Risk-Free Rate horizontal line
    fig.add_hline(
        y=rf_pct,
        line_dash="dot",
        line_color="rgba(0, 242, 169, 0.4)",
        line_width=1.5,
        annotation_text=f"Risk-Free Benchmark ({rf_pct:.1f}%)",
        annotation_position="bottom right",
        annotation_font=dict(size=10, color="#94a3b8")
    )

    # 5. Zero return line
    fig.add_hline(
        y=0,
        line_dash="solid",
        line_color="rgba(255, 255, 255, 0.15)",
        line_width=1
    )

    # 6. Mean Volatility vertical line as risk dividing threshold
    if vols:
        avg_vol = float(np.mean(vols))
        fig.add_vline(
            x=avg_vol,
            line_dash="dot",
            line_color="rgba(255, 255, 255, 0.18)",
            line_width=1.2,
            annotation_text=f"Avg Risk ({avg_vol:.1f}%)",
            annotation_position="top right",
            annotation_font=dict(size=10, color="#64748b")
        )

    _apply_dark_layout(
        fig,
        title="Risk vs Return Profile (Capital Allocation & Sharpe Frontier)",
        x_title="Annualized Volatility — Risk (%)",
        y_title="Annualized Return — Reward (%)",
        height=height
    )

    fig.update_layout(
        hovermode="closest",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
        xaxis=dict(
            ticksuffix="%",
            gridcolor="rgba(255, 255, 255, 0.06)",
            zerolinecolor="rgba(255, 255, 255, 0.15)",
            rangemode="tozero",
            range=[0, max_x]
        ),
        yaxis=dict(
            ticksuffix="%",
            gridcolor="rgba(255, 255, 255, 0.06)",
            zerolinecolor="rgba(255, 255, 255, 0.15)"
        )
    )
    return fig


def create_allocation_donut(
    weights_dict: Dict[str, float],
    show_labels: bool = True,
    height: int = 320,
    center_text: str = "",
    center_subtext: str = "",
    custom_colors: Optional[List[str]] = None
) -> go.Figure:
    """Create modern donut chart of portfolio asset allocation with optional center metrics."""
    labels = list(weights_dict.keys())
    values = [weights_dict[k] * 100.0 for k in labels]
    if custom_colors:
        colors = custom_colors
    else:
        colors = [ASSET_LINE_COLORS.get(k, FALLBACK_PALETTE[i % len(FALLBACK_PALETTE)]) for i, k in enumerate(labels)]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.68,
                marker=dict(colors=colors, line=dict(color="#060a0e", width=2.5)),
                textinfo="label+percent" if show_labels else "none",
                textposition="outside" if show_labels else "none",
                hoverinfo="label+value+percent",
                textfont=dict(family="Inter, sans-serif", size=12, color="#ffffff")
            )
        ]
    )

    _apply_dark_layout(fig, title="Asset Allocation" if show_labels else "", height=height, show_legend=False)
    if not show_labels:
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))

    if center_text:
        sub_html = f"<br><span style='font-size:11px;color:#7e92a2;font-weight:400;'>{center_subtext}</span>" if center_subtext else ""
        fig.update_layout(
            annotations=[
                dict(
                    text=f"<b>{center_text}</b>{sub_html}",
                    x=0.5,
                    y=0.5,
                    font=dict(size=18, family="JetBrains Mono, Inter, sans-serif", color="#ffffff"),
                    showarrow=False
                )
            ]
        )

    return fig


def create_risk_contribution_bar_chart(risk_df: pd.DataFrame) -> go.Figure:
    """Create vertical bar chart of Euler risk contribution matching Panel 5."""
    fig = go.Figure()
    colors = [ASSET_LINE_COLORS.get(t, FALLBACK_PALETTE[i % len(FALLBACK_PALETTE)]) for i, t in enumerate(risk_df["Asset"])]

    fig.add_trace(
        go.Bar(
            x=risk_df["Asset"],
            y=risk_df["Risk Contribution (%)"],
            marker_color=colors,
            text=np.round(risk_df["Risk Contribution (%)"], 1),
            texttemplate="%{text}%",
            textposition="outside",
            textfont=dict(family="JetBrains Mono, monospace", size=11, color="#ffffff")
        )
    )

    _apply_dark_layout(fig, title="Risk Contribution (%)", y_title="Contribution (%)", height=320, show_legend=False)
    fig.update_yaxes(ticksuffix="%")
    return fig


def create_sensitivity_heatmap(
    grid_df: pd.DataFrame, title: str = "Parameter Sensitivity Grid (Sharpe Ratio)"
) -> go.Figure:
    """Create 2D heatmap showing performance across parameter pairs."""
    fig = go.Figure(
        data=go.Heatmap(
            z=grid_df.values,
            x=list(grid_df.columns),
            y=list(grid_df.index),
            colorscale=[[0, "#f87171"], [0.5, "#0e2938"], [1, "#00f2a9"]],
            text=np.round(grid_df.values, 2),
            texttemplate="%{text}",
            textfont=dict(family="JetBrains Mono", size=12, color="#ffffff"),
            colorbar=dict(title="Sharpe")
        )
    )
    _apply_dark_layout(
        fig,
        title=title,
        x_title="Slow Moving Average Period",
        y_title="Fast Moving Average Period",
        height=380
    )
    return fig


def create_daily_returns_bar_chart(
    returns: pd.Series, title: str = "", height: int = 280
) -> go.Figure:
    """Render daily returns as colored bar chart."""
    fig = go.Figure()
    bar_colors = [
        COLORS["accent_green"] if r >= 0 else COLORS["negative_red"] for r in returns
    ]

    fig.add_trace(
        go.Bar(
            x=returns.index,
            y=returns.values * 100.0,
            marker_color=bar_colors,
            name="Daily Return"
        )
    )

    _apply_dark_layout(fig, title=title, y_title="Daily Return (%)" if title else "", height=height)
    fig.update_yaxes(ticksuffix="%")
    if not title:
        fig.update_layout(margin=dict(l=35, r=15, t=10, b=25))
    return fig


def create_sparkline_chart(
    values: List[float], is_positive: bool = True, height: int = 56, fill_area: bool = True
) -> go.Figure:
    """Create lightweight mini sparkline curve with glowing line matching Image 2 mockup."""
    fig = go.Figure()
    color = COLORS["accent_green"] if is_positive else COLORS["negative_red"]
    fill_color = "rgba(0, 242, 169, 0.16)" if is_positive else "rgba(248, 113, 113, 0.16)"

    y_vals = list(values) if values and len(values) >= 2 else [10, 11, 13, 12, 15, 17, 16, 20]
    x_vals = list(range(len(y_vals)))

    scatter_kwargs = dict(
        x=x_vals,
        y=y_vals,
        mode="lines",
        line=dict(color=color, width=2.6, shape="spline", smoothing=1.3),
        hoverinfo="skip"
    )
    if fill_area:
        scatter_kwargs["fill"] = "tozeroy"
        scatter_kwargs["fillcolor"] = fill_color

    fig.add_trace(go.Scatter(**scatter_kwargs))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=2, b=0),
        height=height,
        xaxis=dict(visible=False, showgrid=False, zeroline=False),
        yaxis=dict(visible=False, showgrid=False, zeroline=False),
        showlegend=False
    )
    return fig


def create_price_comparison_chart(
    df: pd.DataFrame,
    height: int = 370
) -> go.Figure:
    """Create normalized percentage return comparison chart matching Image 2."""
    fig = go.Figure()

    color_map = {
        "GLD": "#eab308",
        "Gold (GLD)": "#eab308",
        "Gold": "#eab308",
        "BTC-USD": "#f97316",
        "Bitcoin (BTC-USD)": "#f97316",
        "Bitcoin": "#f97316",
        "NVDA": "#00f2a9",
        "NVIDIA (NVDA)": "#00f2a9",
        "NVIDIA": "#00f2a9"
    }

    cols = df.columns
    for idx, col in enumerate(cols):
        series = df[col].dropna()
        if series.empty:
            continue
        base_val = float(series.iloc[0])
        if base_val == 0:
            base_val = 1e-6
        pct_return = ((series / base_val) - 1.0) * 100.0
        c = color_map.get(str(col), FALLBACK_PALETTE[idx % len(FALLBACK_PALETTE)])

        fig.add_trace(
            go.Scatter(
                x=pct_return.index,
                y=pct_return.values,
                mode="lines",
                name=str(col),
                line=dict(color=c, width=2.4, shape="spline", smoothing=1.2),
                hovertemplate=f"<b>{col}</b>: %{{y:+.2f}}%<extra></extra>"
            )
        )

    fig.add_hline(y=0.0, line_dash="dash", line_color="#334155", opacity=0.8)

    _apply_dark_layout(fig, title="", y_title="", height=height, show_legend=False)
    fig.update_yaxes(ticksuffix="%", gridcolor="rgba(255,255,255,0.05)")
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)")
    fig.update_layout(
        margin=dict(l=40, r=20, t=15, b=25),
        hovermode="x unified"
    )
    return fig
