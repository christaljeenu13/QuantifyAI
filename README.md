# QuantifyAI — Quantitative Multi-Asset Financial Analysis Platform

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-red)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-brightgreen)
![Featherless](https://img.shields.io/badge/Featherless%20AI-OpenAI--Compatible-teal)
![Pytest](https://img.shields.io/badge/Pytest-100%25%20Passing-success)

**QuantifyAI** is an institutional-grade, data-driven quantitative financial terminal built for multi-asset market analysis, algorithmic strategy backtesting, portfolio risk modeling, and AI-assisted financial interpretation.

Developed for national-level hackathon scrutiny, QuantifyAI does not use mock data or static placeholder cards. It calculates real empirical financial statistics from historical market telemetry using standard quantitative formulas.

---

## 1. Problem Statement

Individual investors and quantitative analysts often struggle with:
1. **Siloed Asset Views:** Comparing equities, digital commodities (Bitcoin), and physical safe havens (Gold) across disparate trading calendars without proper normalization.
2. **Backtesting Flaws:** Widespread look-ahead bias, unrealistically executed fills, and ignored slippage/transaction frictions leading to phantom alpha.
3. **Black-Box Risk:** Misunderstanding that capital weight does not equal risk weight, leading to massive downside exposure.
4. **Hallucinatory AI Tools:** Generic LLMs inventing market prices or asserting speculative predictions without grounding in real mathematics.

**QuantifyAI solves this** through a clean terminal design system, mathematical rigor, zero-lookahead backtesting, Euler risk decomposition, and an OpenAI-compatible Featherless AI assistant grounded in real empirical metrics.

---

## 2. Core Modules & Capabilities

### 1. Market Overview Dashboard (`pages/1_Dashboard.py`)
* Synchronized telemetry for core assets (Gold, Bitcoin, NVIDIA).
* Live pricing, 1-day percentage deltas, period returns, and annualized volatility.
* Interactive Plotly price charts, daily return histograms, and drawdown profiles.
* Instant cache refresh and data synchronization status.

### 2. Individual Asset Deep Dive (`pages/2_Asset_Analysis.py`)
* Interactive candlestick charts with volume bars.
* Technical overlay indicators: SMA (20, 50) and EMA (12, 26).
* Momentum indicators: Wilder's smoothed RSI (14) with 30/70 thresholds, and MACD (12, 26, 9) with colored histogram.
* Complete performance metrics: Total Return, CAGR, Volatility, Sharpe, Sortino, and Max Drawdown.
* Historical calendar monthly return matrix (Year x Month heat table).
* Contextual **"Explain Asset"** action powered by Featherless AI.

### 3. Unified Multi-Asset Comparison (`pages/3_Asset_Comparison.py`)
* Multi-instrument comparison on **ONE unified page**.
* Synchronized date alignment (handling crypto 7-day vs equity 5-day trading calendars).
* Normalized performance trajectories (**Base = 100.0**).
* Side-by-side aligned metric tables.
* Pairwise Pearson correlation heatmap and Volatility vs. Return risk frontier scatter plots.
* Downloadable comparison dataset in CSV format.

### 4. Quantitative Strategy Backtester (`pages/4_Strategy_Backtesting.py`)
* Event-driven historical simulation engine with **zero look-ahead bias**.
* **Strict Execution Timing:** Signal generated on session $T$'s Close executes on session $T+1$'s Open/Close with documented slippage.
* Transaction fee and commission accounting (deducted on both entries and exits).
* Supported Strategies:
  1. Dual SMA Crossover
  2. Dual EMA Crossover
  3. Price vs SMA Trend Following
  4. Buy & Hold Benchmark
* Strategy equity curve evaluated side-by-side against Buy & Hold benchmark using identical initial capital.
* Round-trip trade ledger: entry/exit prices, fees, net PnL, duration, and win rates.
* **2D Parameter Sensitivity Matrix**: Evaluates Fast vs Slow moving average combinations across a heatmap of Sharpe ratios to test for overfitting.
* CSV export for both trade logs and equity trajectories.

### 5. Portfolio Risk Lab (`pages/5_Portfolio_Risk_Lab.py`)
* Interactive asset weight sliders with **strict 100% allocation validation**.
* One-click Equal Weight ($1/N$) allocator.
* Annualized Portfolio Volatility calculated via matrix covariance ($\sqrt{w^T \Sigma w}$).
* **Euler Risk Contribution Decomposition**: Calculates Marginal Contribution to Risk (MCR) and Percentage Risk Contribution (PRC) to reveal true asset volatility drivers.
* Tail risk evaluation: 95% Daily Historical Value at Risk (VaR) and Conditional VaR (Expected Shortfall).
* Interactive allocation donut chart and portfolio vs constituent performance trajectories.

### 6. Featherless AI Research Assistant (`pages/6_AI_Assistant.py`)
* Integrates Featherless AI via OpenAI-compatible endpoints (`https://api.featherless.ai/v1`).
* **Session State Context Injection:** Automatically injects the active asset, backtest run, or portfolio weights from other pages into the prompt.
* Strict guardrails preventing hallucinated prices or speculative guarantees.
* Preset quick-analysis prompt chips for rapid analysis.
* **Safe Local Fallback:** Works 100% offline with rule-based institutional summaries if the API key is not yet configured.

### 7. Settings & Diagnostics (`pages/7_Settings.py`)
* Connection ping utility testing connectivity to Featherless AI endpoints.
* Model selector (Llama 3.1 8B/70B, Mistral, Qwen 2.5, Gemma).
* Cache management and telemetry diagnostics.

---

## 3. Technology Stack

* **Language:** Python 3.10+
* **Frontend/UI:** Streamlit with custom dark charcoal & deep teal terminal CSS
* **Calculations:** NumPy, Pandas, SciPy
* **Visualizations:** Plotly Interactive Graphing Library
* **Market Data Provider:** Yahoo Finance via `yfinance`
* **AI Engine:** Featherless AI via `openai` Python SDK (OpenAI-compatible)
* **Configuration:** `python-dotenv`
* **Testing:** Pytest (21 deterministic unit tests)

---

## 4. Project Architecture

```
quantifyai/
├── app.py                      # Main entrypoint, system status, navigation & disclaimers
├── config.py                   # Centralized configuration & environment loader
├── requirements.txt            # Python dependencies
├── .env.example                # Template for environment variables
├── .gitignore                  # Git ignore for .env, cache, bytecode
├── README.md                   # Complete documentation
├── API_SETUP.md                # Featherless API configuration guide
├── pages/
│   ├── 1_Dashboard.py          # Market Overview & Multi-Asset Summary
│   ├── 2_Asset_Analysis.py     # Single Asset Deep Dive & Technical Indicators
│   ├── 3_Asset_Comparison.py   # Multi-Asset Comparison & Correlation Heatmap
│   ├── 4_Strategy_Backtesting.py # Backtesting Engine & Parameter Sensitivity
│   ├── 5_Portfolio_Risk_Lab.py # Portfolio Allocation & Risk Contribution
│   ├── 6_AI_Assistant.py       # Context-Aware Featherless AI Financial Chat
│   └── 7_Settings.py           # Configuration, Connection Test, Cache Management
├── src/
│   ├── api/
│   │   └── featherless_client.py # OpenAI-compatible Featherless API client
│   ├── data/
│   │   ├── asset_registry.py     # Default assets (Gold, BTC, NVDA) & metadata
│   │   ├── market_data.py        # yfinance fetcher, caching, alignment & validation
│   │   └── storage.py            # SQLite storage for saved portfolios & backtests
│   ├── analytics/
│   │   ├── indicators.py         # SMA, EMA, RSI (Wilder's), MACD, Bollinger Bands
│   │   ├── metrics.py            # Returns, CAGR, Volatility, Sharpe, Max Drawdown
│   │   └── risk.py               # Covariance matrix, VaR, CVaR, Risk Contribution
│   ├── backtesting/
│   │   ├── engine.py             # Event-driven backtester, cash/equity accounting
│   │   ├── strategies.py         # SMA Cross, EMA Cross, Price vs SMA, Buy & Hold
│   │   └── sensitivity.py        # Parameter grid sensitivity heatmap
│   ├── comparison/
│   │   └── comparative_analytics.py # Date alignment, base-100 normalization
│   ├── reporting/
│   │   └── export.py             # CSV export utilities
│   └── ui/
│       ├── theme.py              # Custom CSS injecting terminal aesthetic
│       ├── charts.py             # Plotly chart builders matching UI mockup
│       └── components.py         # Reusable metric cards, banners, chips
└── tests/
    ├── test_indicators.py        # SMA, EMA, RSI, MACD, Bollinger tests
    ├── test_metrics.py           # Returns, Volatility, Sharpe, MDD tests
    ├── test_backtesting.py       # No lookahead, fee, cash conservation tests
    ├── test_portfolio_risk.py    # Covariance, Euler decomposition, VaR tests
    ├── test_data_alignment.py    # Multi-asset alignment & base=100 tests
    └── test_ai_config.py         # Key masking & safe fallback tests
```

---

## 5. Installation & Launch (Windows PowerShell)

### Step 1: Clone or Navigate to the Workspace
```powershell
cd d:\webs\sns
```

### Step 2: Create and Activate a Virtual Environment (Optional but recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```powershell
python -m pip install -r requirements.txt
```

### Step 4: Run the Automated Unit Test Suite
```powershell
python -m pytest tests/ -v
```
*(All 21 unit tests should pass with 100% success).*

### Step 5: Configure Environment Variables (Optional for AI)
```powershell
Copy-Item .env.example .env
notepad .env
```
*(Enter your `FEATHERLESS_API_KEY`. If omitted, the app will run with offline rule-based financial commentary).*

### Step 6: Launch QuantifyAI
```powershell
python -m streamlit run app.py
```
*The application will launch on `http://localhost:8501`.*

---

## 6. Supported Assets & Proxies

| Asset | Symbol / Proxy | Category | Market Source | Trading Calendar |
| :--- | :--- | :--- | :--- | :--- |
| **Gold** | `GLD` (SPDR Gold Shares) / `GC=F` (COMEX Futures) | Commodity | Yahoo Finance | Mon–Fri (Exch. Hours) |
| **Bitcoin** | `BTC-USD` | Cryptocurrency | Yahoo Finance | 24/7 (Continuous) |
| **NVIDIA** | `NVDA` | Equities (Tech/AI) | Yahoo Finance | Mon–Fri (US Market) |
| **S&P 500** | `SPY` | Equities (Index) | Yahoo Finance | Mon–Fri (US Market) |
| **US 20Y Bonds** | `TLT` | Fixed Income | Yahoo Finance | Mon–Fri (US Market) |

---

## 7. Assumptions and Limitations

* **Execution Assumption:** Strategies execute at the next session Open ($T+1$) based on signals emitted at session Close ($T$). Intraday high-frequency limit-order fills are not modeled.
* **Rebalancing Assumption:** Portfolio Risk Lab models daily-rebalanced allocations.
* **Data Latency:** Market quotes are historical end-of-day daily bars provided by Yahoo Finance.
* **Compliance:** QuantifyAI is an educational research terminal. It does not provide personalized investment advice or execute real brokerage orders.
