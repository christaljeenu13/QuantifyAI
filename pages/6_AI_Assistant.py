"""
QuantifyAI — Page 6: Intelligent Assistant & Multilingual Software Guide.
Supports two modes:
  1. 📈 Market & Strategy Assistant: Real live market data, backtests, and portfolio metrics.
  2. 📘 Software & Process Guide: Complete interactive manual with 4 language options:
     - English
     - Tamil (தமிழ்)
     - Hindi (हिंदी)
     - Tanglish (Tamil-English)
"""

import streamlit as st
import config
from src.api.featherless_client import get_featherless_client
from src.data.asset_registry import get_default_registry
from src.data.market_data import MarketDataManager
from src.analytics.metrics import calculate_summary_metrics
from src.ui.theme import apply_custom_theme, get_color_palette
from src.ui.components import (
    render_html,
    render_brand_footer
)

try:
    st.set_page_config(page_title="AI Assistant & Software Guide | QuantifyAI", page_icon="🤖", layout="wide")
except Exception:
    pass

apply_custom_theme()
colors = get_color_palette()
ai_client = get_featherless_client()
registry = get_default_registry()

PCT_KEYS = {
    "total_return", "annualized_return", "annualized_volatility", "max_drawdown",
    "var_95_daily", "cvar_95_daily", "win_rate_frac"
}

def _fmt_metrics(d: dict) -> str:
    """Format a metrics dict as readable text (fractions shown as percentages)."""
    parts = []
    for k, v in d.items():
        if k in PCT_KEYS:
            parts.append(f"{k}={v * 100:.2f}%")
        elif isinstance(v, float):
            parts.append(f"{k}={v:.2f}")
        else:
            parts.append(f"{k}={v}")
    return ", ".join(parts)


def build_market_context(tickers) -> str:
    """Assemble real-data context string sent to the model for market analysis."""
    lines = []
    for t in tickers:
        df, meta = MarketDataManager.fetch_data(t, lookback_years=1)
        if df.empty:
            lines.append(f"{t}: market data unavailable right now.")
            continue
        m = calculate_summary_metrics(df["Close"], risk_free_rate=config.DEFAULT_RISK_FREE_RATE)
        lines.append(
            f"{t} [{meta['start_date']} to {meta['end_date']}, source: {meta['data_source']}]: "
            f"latest_price={m['latest_price']:.2f}, "
            f"total_return={m['total_return'] * 100:.2f}%, "
            f"cagr={m['annualized_return'] * 100:.2f}%, "
            f"annualized_volatility={m['annualized_volatility'] * 100:.2f}%, "
            f"sharpe={m['sharpe_ratio']:.2f}, sortino={m['sortino_ratio']:.2f}, "
            f"max_drawdown={m['max_drawdown'] * 100:.2f}%"
        )

    bt = st.session_state.get("last_backtest")
    if bt:
        lines.append(
            f"\nLATEST BACKTEST: {bt['strategy']} on {bt['asset']} ({bt['period']}), "
            f"capital=${bt['initial_capital']:,.0f}, fee={bt['fee_pct']}%.\n"
            f"  Strategy: {_fmt_metrics(bt['strategy_metrics'])}\n"
            f"  Buy&Hold benchmark: {_fmt_metrics(bt['benchmark_metrics'])}"
        )
    else:
        lines.append("\nLATEST BACKTEST: none has been run in this session yet.")

    pf = st.session_state.get("last_portfolio")
    if pf:
        w = ", ".join(f"{k} {v * 100:.0f}%" for k, v in pf["weights"].items())
        lines.append(
            f"\nLATEST PORTFOLIO ({pf['period']}, window {pf['window']}): weights {w}.\n"
            f"  Metrics: {_fmt_metrics(pf['metrics'])}"
        )
    else:
        lines.append("\nLATEST PORTFOLIO: none has been generated in this session yet.")

    return "\n".join(lines)


# Comprehensive QuantifyAI Platform Documentation for the Software Guide mode
SOFTWARE_GUIDE_KNOWLEDGE_BASE = """
QUANTIFYAI PLATFORM USER MANUAL & PROCESS GUIDE:

1. PLATFORM OVERVIEW & ARCHITECTURE:
- QuantifyAI is an institutional-grade quantitative financial analysis terminal.
- Core pages: 1. Dashboard, 2. Asset Analysis, 3. Asset Comparison, 4. Strategy Backtesting, 5. Portfolio Risk Lab, 6. AI Assistant, 7. Settings.
- Real-Time Data Flow: Live downloads from Yahoo Finance (yfinance) with automatic local snapshot fallback if network is unreachable. No synthetic or hallucinated data is ever used.

2. ASSET ANALYSIS PROCESS & ALL 16 CORE TOPICS:
- Step 1: Select an asset from the dropdown or search bar (e.g. NVDA, AAPL, BTC-USD, GLD, SPY).
- Step 2: Choose your custom Date Range (Start Date and End Date).
- Step 3: Explore the 16 structured analytical topics:
  1. Asset Overview: Latest price, daily change, 52-week high/low, trading volume.
  2. Historical Price Analysis: Interactive candlestick and line charts with volume overlay.
  3. SMA Analysis: 20-day, 50-day, and 200-day Simple Moving Averages.
  4. EMA Analysis: 12-day and 26-day Exponential Moving Averages for trend responsiveness.
  5. Returns Analysis: Daily return distributions, cumulative return curves, and annualized CAGR.
  6. Volatility Analysis: 21-day and 63-day rolling annualized volatility charts.
  7. Sharpe Ratio: Risk-adjusted return measure calculated as (CAGR - RiskFreeRate) / Volatility.
  8. Maximum Drawdown (MDD): Historical worst peak-to-trough drop before a new high.
  9. Rolling Performance Analysis: Rolling 3-month and 6-month returns to detect momentum shifts.
  10. Drawdown Analysis: Underwater drawdown chart, drawdown durations, and recovery periods.
  11. Statistical Analysis: Skewness, Kurtosis, 95% Daily Value-at-Risk (VaR), and CVaR.
  12. Volume Analysis: Volume trends, On-Balance-Volume (OBV), and volume moving averages.
  13. Correlation Analysis: Correlation coefficient against major benchmark indices.
  14. Benchmark Comparison: Relative alpha, beta, and outperformance vs S&P 500 (SPY) or NASDAQ (QQQ).
  15. Market Regime Analysis: Algorithmic detection of current regime (High-Momentum Bullish, Consolidating Chop, Bearish Trend).
  16. AI Research Summary: Instant institutional qualitative summary grounded in real calculated figures.

3. INVESTMENT VALUE SIMULATION PROCESS (WITH RISKS & BENEFITS):
- Step 1: Scroll to the Investment Value Simulation card in Asset Analysis.
- Step 2: Enter your Initial Amount (e.g. $1,000, $5,000, or custom amount).
- Step 3: The engine calculates exact simulated portfolio results:
  * Formula: Final Value = Initial Amount * (Close Price on Target Date / Close Price on Start Date)
  * Net Profit/Loss ($ and %) and Annualized Return (CAGR)
- Step 4: Benefits Assessment: Highlights capital compounding, total return generated, and upside capture.
- Step 5: Risk Exposure Assessment: Shows maximum peak-to-trough capital loss endured during the holding window, downside volatility, and worst-case drawdown dollar value.

4. ASSET COMPARISON PROCESS:
- Select 2 to 5 assets simultaneously.
- Performance is normalized to a $100 starting base for fair comparison.
- Provides Risk vs. Return scatter plot, Sharpe ranking table, and covariance/correlation heatmaps.

5. STRATEGY BACKTESTING PROCESS:
- Choose from 3 quantitative strategies: Dual SMA Crossover, RSI Mean Reversion, or MACD Trend.
- Configure initial capital ($) and trading fee percentage (%) to account for real execution drag.
- Review Equity Curve vs Buy & Hold Benchmark, Win Rate %, Profit Factor, and Parameter Sensitivity heatmaps.

6. PORTFOLIO RISK LAB PROCESS:
- Build multi-asset portfolios with custom percentage weights (must sum to 100%).
- Run Monte Carlo simulations (1,000 randomized return paths over a 1-year forward horizon).
- Evaluate 95% Value at Risk (VaR), Conditional VaR (Expected Shortfall), and diversification variance reduction.
"""

# Header
col_h1, col_h2 = st.columns([7, 3])
with col_h1:
    render_html("""
<div>
    <h1 style="margin: 0; font-size: 1.8rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
        🤖 QuantifyAI Intelligent Assistant
    </h1>
    <p style="margin: 2px 0 0 0; font-size: 0.88rem; color: #7e92a2;">
        Quantitative Market Intelligence, Algorithmic Reasoning & Multilingual Software Guide.
    </p>
</div>
""")
with col_h2:
    if ai_client.is_configured():
        render_html(f"""
<div style="text-align: right; padding-top: 6px;">
    <span class="quant-badge quant-badge-green" style="font-size: 0.78rem;">Model: {ai_client.model}</span>
</div>
""")
    else:
        render_html("""
<div style="text-align: right; padding-top: 6px;">
    <span class="quant-badge quant-badge-teal" style="font-size: 0.78rem;">Local Rule-Based & Multilingual Engine Active</span>
</div>
""")

st.markdown("<div style='margin-bottom: 0.8rem;'></div>", unsafe_allow_html=True)

# ─── Option / Mode & Language Selectors ───────────────────────────────────────
mode_options = [
    "📈 Market & Strategy Assistant",
    "📘 Software & Process Guide (Doubts & Manual)"
]

default_idx = 0
if st.session_state.get("ai_assistant_mode") == "📘 Software & Process Guide (Doubts & Manual)":
    default_idx = 1

col_mode, col_lang = st.columns([6, 4], vertical_alignment="center")

with col_mode:
    selected_mode = st.radio(
        "Assistant Mode",
        options=mode_options,
        index=default_idx,
        horizontal=True,
        key="ai_mode_radio",
        help="Switch between analyzing live asset data / backtests or exploring step-by-step software walkthroughs and resolving doubts."
    )

with col_lang:
    selected_lang = st.selectbox(
        "🌐 Language / மொழி / भाषा",
        options=[
            "English",
            "Tamil (தமிழ்)",
            "Hindi (हिंदी)",
            "Tanglish (Tamil-English)"
        ],
        index=0,
        key="guide_lang_choice",
        help="Select language for Software Guide explanations, FAQs, and AI answers."
    )

st.session_state["ai_assistant_mode"] = selected_mode
st.session_state["ai_language"] = selected_lang

st.markdown("<div style='border-bottom: 1px solid rgba(0, 242, 169, 0.15); margin: 0.6rem 0 1.2rem 0;'></div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# MODE 2: SOFTWARE & PROCESS GUIDE (MULTILINGUAL)
# ════════════════════════════════════════════════════════════════════════════════
if selected_mode == "📘 Software & Process Guide (Doubts & Manual)":
    # ── Language-specific Guide Banners ──
    if "tamil" in selected_lang.lower() and "tanglish" not in selected_lang.lower():
        guide_title = "QuantifyAI மென்பொருள் வழிகாட்டி & சந்தேக தீர்வு மையம்"
        guide_sub = "அனைத்து அம்சங்களின் செயல்முறைகள், 16 பகுப்பாய்வு தலைப்புகள் மற்றும் உங்கள் சந்தேகங்களுக்கான உடனடி விடைகள்."
        tab_names = [
            "🔍 சொத்து பகுப்பாய்வு & முதலீட்டு உருவகப்படுத்துதல்",
            "⚖️ சொத்து ஒப்பீடு",
            "📈 வியூகம் சோதனை (Backtesting)",
            "⚡ போர்ட்ஃபோலியோ ரிஸ்க் லேப்"
        ]
    elif "hindi" in selected_lang.lower():
        guide_title = "QuantifyAI सॉफ्टवेयर प्रोसेस और संदेह निवारण गाइड"
        guide_sub = "सभी सुविधाओं की चरण-दर-चरण प्रक्रिया, 16 विश्लेषणात्मक विषय और अपने सभी संदेहों के तुरंत उत्तर प्राप्त करें।"
        tab_names = [
            "🔍 एसेट एनालिसिस और इन्वेस्टमेंट सिमुलेशन",
            "⚖️ एसेट तुलना (Comparison)",
            "📈 स्ट्रेटेजी बैकटेस्टिंग",
            "⚡ पोर्टफोलियो रिस्क लैब"
        ]
    elif "tanglish" in selected_lang.lower():
        guide_title = "QuantifyAI Software Process & Doubts Clearance Guide"
        guide_sub = "Full step-by-step guides for each feature, 16 core analytical topics, and unga doubts-ku instant clarification."
        tab_names = [
            "🔍 Asset Analysis & Investment Simulation",
            "⚖️ Asset Comparison",
            "📈 Strategy Backtesting",
            "⚡ Portfolio Risk Lab"
        ]
    else:
        guide_title = "QuantifyAI Software Process & Doubt Resolution Guide"
        guide_sub = "Explore step-by-step workflows for every platform feature, understand all 16 analytical topics, and ask any doubt."
        tab_names = [
            "🔍 Asset Analysis & Investment Simulation",
            "⚖️ Asset Comparison",
            "📈 Strategy Backtesting",
            "⚡ Portfolio Risk Lab"
        ]

    render_html(f"""
<div style="background: rgba(0, 242, 169, 0.05); border: 1px solid rgba(0, 242, 169, 0.22); border-radius: 12px; padding: 18px 20px; margin-bottom: 1.2rem;">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 6px;">
        <div style="width: 38px; height: 38px; border-radius: 10px; background: rgba(0, 242, 169, 0.18); border: 1px solid rgba(0, 242, 169, 0.4); display: flex; align-items: center; justify-content: center; font-size: 1.2rem; color: #00f2a9;">
            📘
        </div>
        <div>
            <div style="font-size: 1.15rem; font-weight: 800; color: #ffffff;">{guide_title}</div>
            <div style="font-size: 0.82rem; color: #94a3b8;">{guide_sub}</div>
        </div>
    </div>
</div>
""")

    guide_tab1, guide_tab2, guide_tab3, guide_tab4 = st.tabs(tab_names)

    # ── TAB 1: ASSET ANALYSIS & SIMULATION ──
    with guide_tab1:
        if "tamil" in selected_lang.lower() and "tanglish" not in selected_lang.lower():
            st.markdown("""
### 🔍 சொத்து பகுப்பாய்வு (Asset Analysis) மற்றும் முதலீட்டு உருவகப்படுத்துதல்

1. **சொத்தை தேர்ந்தெடுத்தல்**:
   - `NVDA`, `AAPL`, `BTC-USD`, `GLD`, அல்லது `SPY` போன்ற பங்குகள், கிரிப்டோ அல்லது கமாடிட்டியைத் தேர்ந்தெடுக்கவும்.
2. **தேதி வரம்பை அமைத்தல்**:
   - தொடக்க தேதி (Start Date) மற்றும் முடிவு தேதியை (End Date) அமைத்து வரலாற்றுத் தரவுகளைப் பெறவும்.
3. **16 முக்கிய பகுப்பாய்வு தலைப்புகள்**:
   - **Asset Overview**: தற்போதைய விலை, தினசரி சதவீத மாற்றம், 52-வார எல்லை மற்றும் வர்த்தக அளவு.
   - **Historical Price Analysis**: இன்டராக்டிவ் கேண்டில்ஸ்டிக் மற்றும் லைன் விளக்கப்படங்கள்.
   - **SMA Analysis**: 20, 50, மற்றும் 200 நாட்கள் எளிய நகரும் சராசரிகள் (Trend Indicators).
   - **EMA Analysis**: 12 மற்றும் 26 நாட்கள் அதிவேக நகரும் சராசரிகள் (Momentum).
   - **Returns Analysis**: தினசரி வருவாய் பரவல், கூட்டு வளர்ச்சி (Cumulative Returns), மற்றும் CAGR.
   - **Volatility Analysis**: 21-நாள் மற்றும் 63-நாள் சுழலும் விலை ஏற்ற இறக்கம்.
   - **Sharpe Ratio**: ஆபத்திற்கு தகுந்த கூடுதல் வருவாய் அளவீடு (`[CAGR - Rf] / Volatility`).
   - **Maximum Drawdown**: வரலாற்று உச்சத்திலிருந்து ஏற்பட்ட அதிகபட்ச மூலதன சரிவு.
   - **Rolling Performance**: 3-மாத மற்றும் 6-மாத சுழலும் வருவாய் சுழற்சிகள்.
   - **Drawdown Analysis**: முதலீட்டு சரிவின் ஆழம் மற்றும் அது மீண்டு வர எடுத்த காலம்.
   - **Statistical Analysis**: Skewness, Kurtosis மற்றும் 95% Daily Value-at-Risk (VaR).
   - **Volume Analysis**: On-Balance Volume (OBV) மூலம் வர்த்தக அழுத்தத்தை அறிதல்.
   - **Correlation Analysis**: முக்கிய சந்தை குறியீடுகளுடன் (S&P 500, Nasdaq) ஒப்பீட்டு தொடர்பு.
   - **Benchmark Comparison**: SPY/QQQ-க்கு எதிரான Alpha மற்றும் Beta செயல்திறன்.
   - **Market Regime Analysis**: சந்தை நிலை (ஏற்றம், இறக்கம் அல்லது பக்கவாட்டு சலனம்).
   - **AI Research Summary**: உண்மையான எண்களை அடிப்படையாகக் கொண்ட தானியங்கி செயற்கை நுண்ணறிவு சுருக்கம்.
4. **💰 முதலீட்டு உருவகப்படுத்துதல் & அபாய நன்மைகள் பகுப்பாய்வு (Investment Simulation)**:
   - உங்கள் தொடக்க மூலதனத்தை உள்ளிடவும் (எ.கா. `$1,000`).
   - இறுதி தேதியை தேர்ந்தெடுத்தால், சிமுலேட்டர் இறுதி மதிப்பு மற்றும் நிகர லாப/நஷ்டத்தை ($ மற்றும் %) கணக்கிடும்.
   - **நன்மைகள் (Benefits)**: மூலதன வளர்ச்சி, கூட்டு வட்டி வருவாய், மற்றும் CAGR.
   - **அபாயங்கள் (Risks)**: குறிப்பிட்ட முதலீட்டு காலத்தில் ஏற்பட்ட அதிகபட்ச வீழ்ச்சி (Max Drawdown) மற்றும் விலை சரிவு அபாயம்.
            """)
        elif "hindi" in selected_lang.lower():
            st.markdown("""
### 🔍 एसेट एनालिसिस (Asset Analysis) और इन्वेस्टमेंट सिमुलेशन प्रक्रिया

1. **एसेट का चयन करें**:
   - ड्रॉपडाउन या सर्च बार से कोई भी स्टॉक (`NVDA`, `AAPL`), क्रिप्टो (`BTC-USD`), कमोडिटी (`GLD`), या इंडेक्स (`SPY`) चुनें।
2. **कस्टम डेट रेंज चुनें**:
   - स्टार्ट डेट और एंड डेट पिकर का उपयोग करके अपनी इच्छित ऐतिहासिक अवधि निर्धारित करें।
3. **16 मुख्य विश्लेषणात्मक विषय**:
   - **Asset Overview**: नवीनतम मूल्य, 24 घंटे का प्रतिशत परिवर्तन, 52-सप्ताह का उच्चतम/निम्नतम स्तर और वॉल्यूम।
   - **Historical Price Analysis**: इंटरैक्टिव कैंडलस्टिक चार्ट और मूविंग एवरेज।
   - **SMA Analysis**: 20, 50, और 200 दिनों के सिंपल मूविंग एवरेज।
   - **EMA Analysis**: 12 और 26 दिनों के एक्सपोनेंशियल मूविंग एवरेज।
   - **Returns Analysis**: दैनिक रिटर्न वितरण, संचयी रिटर्न और वार्षिक सीएजीआर (CAGR)।
   - **Volatility Analysis**: 21 और 63 दिनों की रोलिंग वार्षिक अस्थिरता।
   - **Sharpe Ratio**: जोखिम-समायोजित रिटर्न अनुपात (`[CAGR - Rf] / Volatility`)।
   - **Maximum Drawdown**: शीर्ष से सबसे निचली ऐतिहासिक पूंजी गिरावट।
   - **Rolling Performance**: रोलिंग 3-महीने और 6-महीने के प्रदर्शन ट्रेंड।
   - **Drawdown Analysis**: अंडरवाटर चार्ट और रिकवरी समय।
   - **Statistical Analysis**: Skewness, Kurtosis और 95% डेली वैल्यू-एट-रिस्क (VaR)।
   - **Volume Analysis**: ऑन-बैलेंस वॉल्यूम (OBV) और ट्रेंड पुष्टि।
   - **Correlation Analysis**: प्रमुख सूचकांकों के साथ सहसंबंध गुणांक।
   - **Benchmark Comparison**: एसएंडपी 500 या नैस्डैक के मुकाबले अल्फा और बीटा।
   - **Market Regime Analysis**: बुलिश, बेयरिश या कंसोलिडेशन रिजीम की पहचान।
   - **AI Research Summary**: वास्तविक गणनाओं पर आधारित स्वचालित एआई शोध सारांश।
4. **💰 इन्वेस्टमेंट वैल्यू सिमुलेशन और जोखिम व लाभ विश्लेषण**:
   - प्रारंभिक निवेश राशि दर्ज करें (जैसे `$1,000`)।
   - अंतिम तिथि चुनें। सिमुलेटर अंतिम पोर्टफोलियो मूल्य और शुद्ध लाभ/हानि ($ और %) की गणना करेगा।
   - **लाभ (Benefits)**: पूंजी वृद्धि, कंपाउंडिंग रिटर्न और अपसाइड पार्टिसिपेशन।
   - **जोखिम (Risks)**: होल्डिंग अवधि में झेली गई अधिकतम गिरावट (Max Drawdown) और डाउनसाइड वोलैटिलिटी।
            """)
        elif "tanglish" in selected_lang.lower():
            st.markdown("""
### 🔍 Asset Analysis & Investment Simulation Process (Tanglish)

1. **Asset Select Pannunga**:
   - Dropdown or search bar la ungalukku thevaiyana asset (eg. `NVDA`, `AAPL`, `BTC-USD`, `GLD`, `SPY`) choose pannunga.
2. **Date Range Choose Pannunga**:
   - Start Date and End Date pickers use panni, ungaloda historical time period set pannunga.
3. **The 16 Analytical Topics**:
   - **Asset Overview**: Current price, 1-day change %, 52-week high/low, and trading volume.
   - **Historical Price Analysis**: Interactive candlesticks with moving averages and volume.
   - **SMA Analysis**: 20, 50, and 200 days Simple Moving Averages.
   - **EMA Analysis**: 12 and 26 days Exponential Moving Averages.
   - **Returns Analysis**: Daily return distribution, cumulative returns, and CAGR %.
   - **Volatility Analysis**: 21-day and 63-day rolling volatility.
   - **Sharpe Ratio**: Risk-adjusted return metric (`[CAGR - Rf] / Volatility`).
   - **Maximum Drawdown**: Peak la irundhu bottom varai vandha worst loss %.
   - **Rolling Performance**: 3-month and 6-month rolling returns.
   - **Drawdown Analysis**: Underwater curve and recovery duration.
   - **Statistical Analysis**: Skewness, Kurtosis, and 95% Daily VaR.
   - **Volume Analysis**: On-Balance Volume (OBV) trend confirmation.
   - **Correlation Analysis**: SPY / QQQ kooda correlation coefficient.
   - **Benchmark Comparison**: SPY/QQQ vida outperformance (Alpha & Beta).
   - **Market Regime Analysis**: Bullish, Bearish, or Choppy market status.
   - **AI Research Summary**: Real data metrics vechu automated research summary.
4. **💰 Investment Value Simulation & Risks vs Benefits**:
   - Unga initial capital amount enter pannunga (eg. `$1,000`).
   - Target date select pannina, system ungaloda **Final Simulated Value**, **Net Profit/Loss ($ and %)** calculate pannum.
   - **Benefits Analysis**: Compounding growth, total profit, and annualized return.
   - **Risk Analysis**: Andha specific time la unga portfolio face panna maximum drawdown and downside risk.
            """)
        else:
            st.markdown("""
### 🔍 Asset Analysis & Investment Simulation Workflow

1. **Select an Asset**:
   - Pick any stock (e.g. `NVDA`, `AAPL`, `MSFT`), cryptocurrency (e.g. `BTC-USD`), commodity (e.g. `GLD`), or index (e.g. `SPY`, `QQQ`).
2. **Choose Custom Date Range**:
   - Use the **Start Date** and **End Date** pickers to target the exact historical period you wish to investigate.
3. **The 16 Analytical Topics**:
   - **Asset Overview**: High-level snapshot of current price, daily percentage change, 52-week bounds, and volume.
   - **Historical Price Analysis**: Interactive candlesticks with moving averages and volume distribution.
   - **SMA Analysis**: 20, 50, and 200 Simple Moving Averages for baseline trend identification.
   - **EMA Analysis**: 12 and 26 Exponential Moving Averages giving higher weight to recent sessions.
   - **Returns Analysis**: Cumulative compounding growth, daily return distributions, and annualized CAGR.
   - **Volatility Analysis**: 21-day and 63-day rolling annualized standard deviations.
   - **Sharpe Ratio**: Excess return generated per unit of total risk (`[CAGR - Rf] / Volatility`).
   - **Maximum Drawdown**: Worst historical peak-to-trough capital decline.
   - **Rolling Performance**: Rolling 3-month and 6-month returns to spot cycle shifts.
   - **Drawdown Analysis**: Underwater chart showing depth and length of capital contractions.
   - **Statistical Analysis**: Return distribution skewness, kurtosis, and 95% Value-at-Risk (VaR).
   - **Volume Analysis**: On-Balance Volume (OBV) and volume moving averages confirming price action.
   - **Correlation Analysis**: Direct correlation coefficient against major market indices.
   - **Benchmark Comparison**: Relative outperformance and beta against SPY or QQQ.
   - **Market Regime Analysis**: Algorithmic classification into Bullish, Bearish, or Choppy regimes.
   - **AI Research Summary**: Automated synthesis of mathematical metrics into actionable insights.
4. **💰 Investment Value Simulation & Risk/Benefit Analysis**:
   - Enter your initial capital (e.g. `$1,000`).
   - Select your target holding period or exit date.
   - Computes **Simulated Final Value** and **Net Profit/Loss ($ and %)**.
   - **Benefits Assessment**: Highlights compounding gains, upside participation, and capital growth.
   - **Risk Assessment**: Details maximum drawdown endured during the holding window and downside volatility.
            """)

    # ── TAB 2: ASSET COMPARISON ──
    with guide_tab2:
        if "tamil" in selected_lang.lower() and "tanglish" not in selected_lang.lower():
            st.markdown("""
### ⚖️ சொத்து ஒப்பீடு செயல்முறை (Asset Comparison)
1. **பல சொத்துக்களை தேர்ந்தெடுத்தல்**: ஒரே நேரத்தில் 2 முதல் 5 சொத்துக்களை தேர்ந்தெடுக்கவும்.
2. **$100 தொடக்க மதிப்பீடு (Normalized Performance)**: ஆரம்ப விலைகளின் வேறுபாடுகளை நீக்கி நியாயமான ஒப்பீடு செய்ய அனைத்து சொத்துக்களும் $100-ஆக சமன் செய்யப்படுகின்றன.
3. **Risk-Return Scatter Plot**: வருமானம் மற்றும் ஆபத்தின் சமநிலையை வரைபடம் மூலம் கண்டறியலாம்.
4. **Correlation Heatmap**: சொத்துக்களுக்கிடையேயான தொடர்பை அறிந்து சிறந்த போர்ட்ஃபோலியோவை உருவாக்க உதவுகிறது.
            """)
        elif "hindi" in selected_lang.lower():
            st.markdown("""
### ⚖️ एसेट तुलना प्रक्रिया (Asset Comparison)
1. **कई एसेट्स चुनें**: एक साथ 2 से 5 एसेट्स का चयन करें।
2. **$100 सामान्यीकृत प्रदर्शन**: मूल्य पूर्वाग्रह को दूर करने के लिए सभी एसेट्स को $100 के आधार पर पुनः मापा जाता है।
3. **रिस्क-रिटर्न स्कैटर प्लॉट**: यह देखने के लिए कि कौन सा एसेट सबसे अधिक कुशल है, रिटर्न बनाम अस्थिरता की कल्पना करें।
4. **सहसंबंध हीटमैप (Correlation Heatmap)**: इष्टतम विविधीकरण के लिए असंबद्ध एसेट्स की पहचान करें।
            """)
        elif "tanglish" in selected_lang.lower():
            st.markdown("""
### ⚖️ Asset Comparison Process (Tanglish)
1. **Multiple Assets Select Pannunga**: Orey nerathula 2 to 5 assets compare panna select pannalam.
2. **Normalized to $100 Base**: Ellaa assets-ayum starting date la $100 nu equalize panni, edhu nalla return thandhurukku nu fair ah compare pannalam.
3. **Risk vs Return Scatter Plot**: Annualized return vs volatility plot panni, best risk-adjusted asset edhu nu paarkalam.
4. **Correlation Heatmap**: Gold, Tech Stocks, Crypto naduvula irukura correlation matrix-ah check panni portfolio diversify pannalam.
            """)
        else:
            st.markdown("""
### ⚖️ Asset Comparison Process
1. **Select Multiple Assets**: Choose 2 to 5 assets across equities, crypto, and commodities.
2. **Normalized Performance**: All assets are rebased to `$100` at the start date for fair compounding comparison.
3. **Risk-Return Scatter Matrix**: Visualizes annualized return vs. annualized volatility to spot the most risk-efficient asset.
4. **Cross-Asset Correlation Heatmap**: Identifies uncorrelated pairs (e.g., Gold vs. Tech Stocks) for optimal portfolio diversification.
            """)

    # ── TAB 3: BACKTESTING ──
    with guide_tab3:
        if "tamil" in selected_lang.lower() and "tanglish" not in selected_lang.lower():
            st.markdown("""
### 📈 அல்காரிதமிக் வியூகம் பேக்டெஸ்டிங் (Strategy Backtesting)
1. **வியூகத்தை தேர்வு செய்தல்**: Dual SMA Crossover, RSI Mean Reversion, அல்லது MACD Momentum.
2. **தொடக்க மூலதனம் & கட்டணம்**: ஆரம்ப முதலீடு (எ.கா. `$10,000`) மற்றும் வர்த்தக கட்டண சதவீதத்தை (எ.கா. `0.1%`) உள்ளிடவும்.
3. **முடிவுகளை ஆய்வு செய்தல்**: சாதாரண Buy & Hold முறையை விட உங்கள் வியூகம் அதிக லாபம் தந்துள்ளதா என்பதை Equity Curve, Win Rate %, மற்றும் Profit Factor மூலம் ஒப்பிடலாம்.
            """)
        elif "hindi" in selected_lang.lower():
            st.markdown("""
### 📈 स्ट्रेटेजी बैकटेस्टिंग प्रक्रिया
1. **ट्रेडिंग रणनीति चुनें**: डुअल एसएमए क्रॉसओवर (SMA Crossover), आरएसआई (RSI), या एमएसीडी (MACD)।
2. **पूंजी और फीस कॉन्फ़िगर करें**: प्रारंभिक पूंजी (जैसे `$10,000`) और कमीशन/स्लिपेज के लिए फीस प्रतिशत (जैसे `0.1%`) सेट करें।
3. **प्रदर्शन मूल्यांकन**: रणनीति इक्विटी कर्व की तुलना बाय एंड होल्ड बेंचमार्क से करें और विन रेट % व प्रॉफिट फैक्टर का विश्लेषण करें।
            """)
        elif "tanglish" in selected_lang.lower():
            st.markdown("""
### 📈 Strategy Backtesting Process (Tanglish)
1. **Strategy Select Pannunga**: Dual SMA Crossover, RSI Mean Reversion, or MACD Momentum strategy choose pannunga.
2. **Capital & Fee Set Pannunga**: Starting capital (eg. `$10,000`) and broker trading fee % (eg. `0.1%`) set pannunga.
3. **Evaluate Equity Curve**: Buy & Hold benchmark-ah vida strategy nalla profit thandhurukka, Win Rate %, Profit Factor and Max Drawdown check pannalam.
            """)
        else:
            st.markdown("""
### 📈 Strategy Backtesting Process
1. **Select Strategy**: Dual SMA Crossover, RSI Mean Reversion, or MACD Trend.
2. **Set Initial Capital & Fees**: Input starting capital (e.g. `$10,000`) and fee % (e.g. `0.1%`) to realistically account for execution drag.
3. **Evaluate Performance**: Compare strategy equity curve directly against passive Buy & Hold benchmark with Win Rate %, Profit Factor, and Sharpe Ratio.
            """)

    # ── TAB 4: RISK LAB ──
    with guide_tab4:
        if "tamil" in selected_lang.lower() and "tanglish" not in selected_lang.lower():
            st.markdown("""
### ⚡ போர்ட்ஃபோலியோ ரிஸ்க் லேப் (Portfolio Risk Lab)
1. **சொத்து ஒதுக்கீடு**: உங்கள் போர்ட்ஃபோலியோவில் உள்ள பங்குகளின் சதவீதத்தை (மொத்தம் 100%) அமைக்கவும்.
2. **மான்டே கார்லோ சிமுலேஷன்**: எதிர்கால 1 வருடத்திற்கான 1,000 சாத்தியமான வருவாய் பாதைகளை உருவகப்படுத்துகிறது.
3. **95% Value at Risk (VaR)**: 95% நிச்சயத்துடன் 1 நாளில் ஏற்படக்கூடிய அதிகபட்ச இழப்பு அளவீடு.
4. **Conditional VaR (Expected Shortfall)**: மிக மோசமான சரிவு ஏற்படும் போது எதிர்பார்க்கப்படும் சராசரி இழப்பு.
            """)
        elif "hindi" in selected_lang.lower():
            st.markdown("""
### ⚡ पोर्टफोलियो रिस्क लैब प्रक्रिया
1. **पोर्टफोलियो वेट्स आवंटित करें**: विभिन्न एसेट्स के प्रतिशत वेट्स सेट करें (कुल 100% होना चाहिए)।
2. **मोंटे कार्लो सिमुलेशन**: 1-वर्षीय आगे के परिदृश्य के लिए 1,000 यादृच्छिक पथों का अनुकरण करता है।
3. **वैल्यू-एट-रिस्क (VaR 95%)**: 95% सांख्यिकीय विश्वास के साथ 1 दिन में होने वाले अधिकतम नुकसान को मापता है।
4. **कंडीशनल वीएआर (CVaR)**: चरम बाजार घटनाओं के दौरान होने वाले औसत नुकसान की गणना करता है।
            """)
        elif "tanglish" in selected_lang.lower():
            st.markdown("""
### ⚡ Portfolio Risk Lab Process (Tanglish)
1. **Portfolio Weights Allocate Pannunga**: Unga assets ku percentage weights set pannunga (Total 100% irukanum).
2. **Monte Carlo Simulation**: 1-year forward horizon ku 1,000 random market scenarios simulate panni confidence intervals paarkalam.
3. **Value at Risk (VaR 95%)**: 95% statistical confidence la 1 day la vara koodiya maximum expected loss.
4. **Conditional VaR (CVaR)**: Worst 5% days la average loss evalavu irukkum nu measure pannum.
            """)
        else:
            st.markdown("""
### ⚡ Portfolio Risk Lab Process
1. **Allocate Portfolio Weights**: Select multiple constituent assets and assign percentage weights (must total 100%).
2. **Monte Carlo Simulation**: Simulates 1,000 forward paths over a 1-year horizon to generate confidence bands.
3. **Value at Risk (VaR 95%)**: Measures maximum expected loss over a 1-day horizon with 95% statistical confidence.
4. **Conditional VaR (Expected Shortfall)**: Quantifies average loss expected during extreme tail events breaching the 95% threshold.
            """)

    # ── Multilingual Common Doubts Accordion ──
    st.markdown("<div style='margin-top: 1.4rem; font-size: 1rem; font-weight: 700; color: #ffffff;'>❓ Common Doubts & Solutions:</div>", unsafe_allow_html=True)
    
    if "tamil" in selected_lang.lower() and "tanglish" not in selected_lang.lower():
        with st.expander("கேள்வி: Investment Value Simulation எனது லாபத்தை எவ்வாறு கணக்கிடுகிறது?"):
            st.markdown("""
            **சூத்திரம்**: `இறுதி மதிப்பு = தொடக்க முதலீடு × (இறுதி தேதி விலை / தொடக்க தேதி விலை)`
            - நிகர லாபம்/நஷ்டம் = இறுதி மதிப்பு - தொடக்க முதலீடு
            - இது Yahoo Finance-ன் உண்மையான வரலாற்று விலைகளை மட்டுமே பயன்படுத்துகிறது.
            """)
        with st.expander("கேள்வி: Sharpe Ratio மற்றும் Sortino Ratio என்ன வேறுபாடு?"):
            st.markdown("""
            - **Sharpe Ratio**: மேல்நோக்கிய மற்றும் கீழ்நோக்கிய ஏற்ற இறக்கம் இரண்டையும் சமமாக கருதுகிறது.
            - **Sortino Ratio**: கீழ்நோக்கிய சரிவை (Downside Risk) மட்டுமே கருதுகிறது.
            """)
        with st.expander("கேள்வி: சந்தை தரவு எங்கிருந்து பெறப்படுகிறது?"):
            st.markdown("""
            - அனைத்து வரலாற்று விலை மற்றும் வர்த்தக அளவு தரவுகளும் நேரடியாக **Yahoo Finance (yfinance)** மூலம் பெறப்படுகின்றன.
            """)
    elif "hindi" in selected_lang.lower():
        with st.expander("प्रश्न: इन्वेस्टमेंट सिमुलेशन मेरे रिटर्न की गणना कैसे करता है?"):
            st.markdown("""
            **फॉर्मूला**: `अंतिम मूल्य = प्रारंभिक निवेश × (अंतिम तिथि क्लोज़ मूल्य / प्रारंभिक क्लोज़ मूल्य)`
            - शुद्ध लाभ/हानि = अंतिम मूल्य - प्रारंभिक निवेश
            - यह सीधे Yahoo Finance के सत्यापित ऐतिहासिक आंकड़ों का उपयोग करता है।
            """)
        with st.expander("प्रश्न: Sharpe Ratio और Sortino Ratio में क्या अंतर है?"):
            st.markdown("""
            - **Sharpe Ratio**: अपसाइड और डाउनसाइड दोनों अस्थिरता को समान रूप से मापता है।
            - **Sortino Ratio**: केवल नकारात्मक गिरावट (Downside Volatility) को दंडित करता है।
            """)
        with st.expander("प्रश्न: मार्केट डेटा कहाँ से आता है?"):
            st.markdown("""
            - सभी ऐतिहासिक डेटा सीधे **Yahoo Finance (yfinance)** से लाइव डाउनलोड किए जाते हैं।
            """)
    elif "tanglish" in selected_lang.lower():
        with st.expander("Question: Investment Simulation epdi return calculate pannudhu?"):
            st.markdown("""
            **Formula**: `Final Value = Initial Investment * (Exit Date Close / Start Date Close)`
            - Net Profit/Loss = Final Value - Initial Investment
            - Idhu Yahoo Finance oda verified real closing price data vechu mattum dhan compute aagum.
            """)
        with st.expander("Question: Sharpe Ratio kum Sortino Ratio kum enna difference?"):
            st.markdown("""
            - **Sharpe Ratio**: Rendu side volatility-ayum (upside & downside) consider pannum.
            - **Sortino Ratio**: Negative downside loss-ah mattum penalize pannum. So growth assets-ku Sortino romba accurate.
            """)
        with st.expander("Question: Platform data enga irundhu varudhu?"):
            st.markdown("""
            - Ellaa stock, crypto and commodity data-vum real-time **Yahoo Finance (yfinance)** API moolama live download aagudhu.
            """)
    else:
        with st.expander("Q: How does the Investment Value Simulation calculate my returns?"):
            st.markdown("""
            **Formula**: `Final Value = Initial Investment * (Close Price on Exit Date / Close Price on Start Date)`
            - Net Gain/Loss = Final Value - Initial Investment
            - Strictly uses verified historical closing prices from Yahoo Finance.
            """)
        with st.expander("Q: What is the difference between Sharpe Ratio and Sortino Ratio?"):
            st.markdown("""
            - **Sharpe Ratio**: Penalizes both upside and downside volatility equally.
            - **Sortino Ratio**: Penalizes only downside volatility (negative returns).
            """)
        with st.expander("Q: Where does the market data come from?"):
            st.markdown("""
            - All historical price, volume, and financial data is sourced directly from **Yahoo Finance (yfinance)**.
            """)

    # ── Quick Prompts (Multilingual) ──
    st.markdown("<div style='font-size: 0.82rem; color: #94a3b8; font-weight: 600; margin: 1.2rem 0 0.5rem 0;'>Ask a Doubt or Walkthrough Question:</div>", unsafe_allow_html=True)
    qg1, qg2, qg3, qg4 = st.columns(4)
    preset_guide_prompt = None

    if "tamil" in selected_lang.lower() and "tanglish" not in selected_lang.lower():
        with qg1:
            if st.button("🚀 Asset Analysis எப்படி பயன்படுத்துவது?", use_container_width=True):
                preset_guide_prompt = "Asset Analysis-ஐ எவ்வாறு பயன்படுத்துவது மற்றும் அதன் 16 தலைப்புகளை எவ்வாறு புரிந்துகொள்வது என்று தமிழில் விளக்குங்கள்."
        with qg2:
            if st.button("💰 முதலீட்டு சிமுலேஷன் & அபாயங்கள்", use_container_width=True):
                preset_guide_prompt = "Investment Value Simulation எவ்வாறு செயல்படுகிறது மற்றும் அதன் அபாய நன்மைகள் (Risks vs Benefits) பகுப்பாய்வை தமிழில் விளக்குங்கள்."
        with qg3:
            if st.button("🧪 வியூகம் சோதனை செய்வது எப்படி?", use_container_width=True):
                preset_guide_prompt = "QuantifyAI-ல் Strategy Backtesting செய்வது எப்படி மற்றும் கட்டணங்களை எவ்வாறு அமைப்பது என்று தமிழில் விளக்குங்கள்."
        with qg4:
            if st.button("🛡️ Risk Lab எவ்வாறு செயல்படுகிறது?", use_container_width=True):
                preset_guide_prompt = "Portfolio Risk Lab மற்றும் 95% VaR கணக்கீடு எவ்வாறு செயல்படுகிறது என்று தமிழில் விளக்குங்கள்."
    elif "hindi" in selected_lang.lower():
        with qg1:
            if st.button("🚀 Asset Analysis का उपयोग कैसे करें?", use_container_width=True):
                preset_guide_prompt = "Asset Analysis का उपयोग कैसे करें और इसके 16 विषयों को कैसे समझें, हिंदी में समझाइए।"
        with qg2:
            if st.button("💰 इन्वेस्टमेंट सिमुलेशन और जोखिम", use_container_width=True):
                preset_guide_prompt = "Investment Value Simulation कैसे काम करता है और Risks vs Benefits का विश्लेषण हिंदी में विस्तार से समझाइए।"
        with qg3:
            if st.button("🧪 Strategy Backtest कैसे करें?", use_container_width=True):
                preset_guide_prompt = "QuantifyAI में स्ट्रेटेजी बैकटेस्टिंग कैसे करें और फीस का प्रभाव कैसे देखें, हिंदी में बताएं।"
        with qg4:
            if st.button("🛡️ Risk Lab कैसे काम करता है?", use_container_width=True):
                preset_guide_prompt = "Portfolio Risk Lab, मोंटे कार्लो सिमुलेशन और 95% VaR कैसे काम करता है, हिंदी में समझाइए।"
    elif "tanglish" in selected_lang.lower():
        with qg1:
            if st.button("🚀 Asset Analysis epdi use panradhu?", use_container_width=True):
                preset_guide_prompt = "Asset Analysis epdi use panradhu and 16 topics epdi understand panradhu nu Tanglish la explain pannunga."
        with qg2:
            if st.button("💰 Investment Simulation & Risk", use_container_width=True):
                preset_guide_prompt = "Investment Value Simulation epdi work aagudhu and Risks vs Benefits analyze panradhu epdi nu Tanglish la explain pannunga."
        with qg3:
            if st.button("🧪 Strategy Backtest epdi panradhu?", use_container_width=True):
                preset_guide_prompt = "QuantifyAI la trading strategy backtest epdi panradhu and trading fees epdi effect aagum nu Tanglish la sollunga."
        with qg4:
            if st.button("🛡️ Risk Lab epdi work aagudhu?", use_container_width=True):
                preset_guide_prompt = "Portfolio Risk Lab la Monte Carlo simulation and 95% VaR epdi calculate aagudhu nu Tanglish la clear ah explain pannunga."
    else:
        with qg1:
            if st.button("🚀 How to use Asset Analysis?", use_container_width=True):
                preset_guide_prompt = "Explain the step-by-step process of using Asset Analysis, including how to select date ranges and interpret the 16 topics."
        with qg2:
            if st.button("💰 Investment Simulation process", use_container_width=True):
                preset_guide_prompt = "Explain how the Investment Value Simulation works, how returns are calculated, and how the Risk vs Benefits analysis helps me."
        with qg3:
            if st.button("🧪 How to backtest a strategy?", use_container_width=True):
                preset_guide_prompt = "Give me a step-by-step guide on how to backtest an algorithmic strategy in QuantifyAI, including fee configuration and reading results."
        with qg4:
            if st.button("🛡️ How does Risk Lab work?", use_container_width=True):
                preset_guide_prompt = "Explain how to build a portfolio in the Portfolio Risk Lab, what Monte Carlo simulation does, and how 95% VaR and CVaR are computed."

# ════════════════════════════════════════════════════════════════════════════════
# MODE 1: MARKET & STRATEGY ASSISTANT
# ════════════════════════════════════════════════════════════════════════════════
else:
    asset_options = {f"{a['name']} ({a['ticker']})": a["ticker"] for a in registry.list_assets()}
    default_labels = [k for k, v in asset_options.items() if v in ("GLD", "BTC-USD", "NVDA")]
    selected_labels = st.multiselect(
        "Active Market Context (assets the assistant analyzes):",
        options=list(asset_options.keys()),
        default=default_labels,
        key="ai_context_assets"
    )
    context_tickers = [asset_options[k] for k in selected_labels]

    known = []
    if st.session_state.get("last_backtest"):
        bt = st.session_state["last_backtest"]
        known.append(f"backtest: {bt['strategy']} on {bt['asset']}")
    if st.session_state.get("last_portfolio"):
        known.append("portfolio from Risk Lab")
    st.caption(
        "The assistant sees: 1-year metrics for the selected assets"
        + (f", plus your latest {' and '.join(known)}." if known else ". Run a backtest or build a portfolio to add more context.")
    )

    render_html("<div style='font-size: 0.8rem; color: #94a3b8; font-weight: 600; margin-bottom: 0.5rem;'>Quick Analysis Prompts:</div>")
    q1, q2, q3, q4 = st.columns(4)

    preset_market_prompt = None
    with q1:
        if st.button("Explain Sharpe Ratio", use_container_width=True):
            preset_market_prompt = "Explain Sharpe ratio, annualized volatility, and maximum drawdown in simple language, using the selected assets as examples."
    with q2:
        if st.button("Why did strategy underperform?", use_container_width=True):
            preset_market_prompt = "Using my latest backtest, did the strategy beat Buy & Hold? Explain why or why not using the metrics."
    with q3:
        if st.button("Summarize comparison", use_container_width=True):
            preset_market_prompt = "Summarize the key differences in risk, return, and drawdown between the selected assets."
    with q4:
        if st.button("What are portfolio risks?", use_container_width=True):
            preset_market_prompt = "What are the primary risks (volatility, drawdown, VaR/CVaR, concentration) in my latest portfolio?"

# ─── Chat History State ───────────────────────────────────────────────────────
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

# Render Chat Messages
if not st.session_state["chat_messages"]:
    if selected_mode == "📘 Software & Process Guide (Doubts & Manual)":
        if "tamil" in selected_lang.lower() and "tanglish" not in selected_lang.lower():
            st.info("💡 **வழிகாட்டி தயார்:** மென்பொருள் செயல்முறைகள் அல்லது உங்கள் சந்தேகங்களை கீழே கேட்கவும்.")
        elif "hindi" in selected_lang.lower():
            st.info("💡 **गाइड सहायक तैयार है:** सॉफ्टवेयर प्रक्रिया या अपने किसी भी संदेह के बारे में नीचे पूछें।")
        elif "tanglish" in selected_lang.lower():
            st.info("💡 **Software Guide Ready:** QuantifyAI pathi ungalukku irukura endha doubt ah irundhalum keazha kelunga.")
        else:
            st.info("💡 **Software Guide Assistant Ready:** Ask any question or doubt about how QuantifyAI works, feature steps, or pick a quick prompt above.")
    else:
        st.info("💡 **Market Assistant Ready:** Ask a question about your asset metrics, backtests, or portfolio, or pick a quick prompt above.")

for msg in st.session_state["chat_messages"]:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["content"])

# Chat input
if "tamil" in selected_lang.lower() and "tanglish" not in selected_lang.lower():
    input_placeholder = "உங்கள் கேள்விகள் அல்லது சந்தேகங்களை தமிழில் தட்டச்சு செய்யவும்..."
elif "hindi" in selected_lang.lower():
    input_placeholder = "अपने प्रश्न या संदेह को हिंदी में यहाँ लिखें..."
elif "tanglish" in selected_lang.lower():
    input_placeholder = "Unga doubts or software questions ah Tanglish la kelunga..."
else:
    input_placeholder = (
        "Ask any doubt or question about how the software works..."
        if selected_mode == "📘 Software & Process Guide (Doubts & Manual)"
        else "Ask a quantitative question about your assets, backtests, or portfolio..."
    )

user_query = st.chat_input(input_placeholder)

# Active prompt determination
if selected_mode == "📘 Software & Process Guide (Doubts & Manual)":
    active_input = preset_guide_prompt or user_query
else:
    active_input = preset_market_prompt or user_query

if active_input:
    st.session_state["chat_messages"].append({"role": "user", "content": active_input})

    with st.spinner("QuantifyAI Assistant is synthesizing guidance..."):
        if selected_mode == "📘 Software & Process Guide (Doubts & Manual)":
            context = SOFTWARE_GUIDE_KNOWLEDGE_BASE
        else:
            context = build_market_context(context_tickers)

        history = st.session_state["chat_messages"][-12:]
        resp = ai_client.chat_completion(
            messages=history,
            system_context=context,
            max_tokens=700,
            language=selected_lang
        )
        reply = resp.get("content", "Error synthesizing response.")
        notice = resp.get("notice")

    st.session_state["chat_messages"].append({"role": "assistant", "content": reply})
    if notice and resp.get("configured"):
        st.session_state["ai_notice"] = notice
    st.rerun()

if st.session_state.get("ai_notice"):
    st.warning(st.session_state.pop("ai_notice"))

# Controls
st.markdown("---")
bp1, bp2, bp3 = st.columns([2, 2, 6])
with bp1:
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state["chat_messages"] = []
        st.rerun()
with bp2:
    if st.button("♻️ Refresh Data Cache", use_container_width=True, help="Clears market data cache so next analysis fetches fresh quotes."):
        st.cache_data.clear()
        st.success("Cache cleared — next request fetches fresh data.")

render_brand_footer()
