"""UI layer package initialization."""
from .theme import apply_custom_theme, get_color_palette
from .charts import (
    create_candlestick_chart,
    create_performance_line_chart,
    create_drawdown_chart,
    create_indicator_chart,
    create_correlation_heatmap,
    create_risk_return_scatter,
    create_allocation_donut,
    create_sensitivity_heatmap,
    create_daily_returns_bar_chart
)
from .components import (
    render_header,
    render_metric_card,
    render_status_badge,
    render_disclaimer_footer,
    render_ticker_card_top
)
