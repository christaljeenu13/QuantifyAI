"""
QuantifyAI - Central Configuration & Environment Manager
Handles environment variables, API endpoints, asset presets, and calculation constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Load local .env if present
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Featherless AI Settings (OpenAI-compatible)
FEATHERLESS_BASE_URL = "https://api.featherless.ai/v1"
FEATHERLESS_API_KEY = os.getenv("FEATHERLESS_API_KEY", "").strip()
FEATHERLESS_DEFAULT_MODEL = os.getenv(
    "FEATHERLESS_MODEL", "Qwen/Qwen2.5-7B-Instruct"
).strip()

# Popular tested Featherless models
FEATHERLESS_AVAILABLE_MODELS = [
    "Qwen/Qwen2.5-7B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "meta-llama/Meta-Llama-3.1-70B-Instruct",
    "google/gemma-2-9b-it"
]

# Market Data Settings
MARKET_DATA_API_KEY = os.getenv("MARKET_DATA_API_KEY", "").strip()
DEFAULT_TRADING_DAYS_PER_YEAR = 252

# Quantitative Analysis Defaults
try:
    DEFAULT_RISK_FREE_RATE = float(os.getenv("RISK_FREE_RATE", "0.04"))
except ValueError:
    DEFAULT_RISK_FREE_RATE = 0.04

try:
    DEFAULT_INITIAL_CAPITAL = float(os.getenv("DEFAULT_INITIAL_CAPITAL", "10000.0"))
except ValueError:
    DEFAULT_INITIAL_CAPITAL = 10000.0

try:
    DEFAULT_TRANSACTION_FEE = float(os.getenv("DEFAULT_TRANSACTION_FEE", "0.001"))
except ValueError:
    DEFAULT_TRANSACTION_FEE = 0.001

# Core Supported Asset Presets
INITIAL_ASSETS = {
    "Gold (GLD)": {
        "ticker": "GLD",
        "name": "SPDR Gold Shares ETF",
        "category": "Commodity Proxy",
        "description": "Physically-backed Gold ETF proxy tracking bullion price.",
        "icon": "🪙"
    },
    "Gold Futures (GC=F)": {
        "ticker": "GC=F",
        "name": "COMEX Gold Continuous Contract",
        "category": "Commodity Futures",
        "description": "Continuous front-month Gold futures contract.",
        "icon": "🏆"
    },
    "Bitcoin (BTC-USD)": {
        "ticker": "BTC-USD",
        "name": "Bitcoin / US Dollar",
        "category": "Cryptocurrency",
        "description": "Decentralized digital currency benchmark.",
        "icon": "₿"
    },
    "NVIDIA (NVDA)": {
        "ticker": "NVDA",
        "name": "NVIDIA Corporation",
        "category": "Equities (Tech/AI)",
        "description": "Global leader in accelerated computing & GPU chips.",
        "icon": "🟢"
    }
}

# Optional Extended Asset Registry
EXTENDED_ASSET_PRESETS = {
    "S&P 500 (SPY)": {
        "ticker": "SPY",
        "name": "SPDR S&P 500 ETF Trust",
        "category": "Equities (Index)",
        "description": "US Large-Cap Equity benchmark ETF.",
        "icon": "📈"
    },
    "Apple (AAPL)": {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "category": "Equities (Consumer Tech)",
        "description": "Consumer electronics & software ecosystem.",
        "icon": "🍎"
    },
    "Ethereum (ETH-USD)": {
        "ticker": "ETH-USD",
        "name": "Ethereum / US Dollar",
        "category": "Cryptocurrency",
        "description": "Smart contract & decentralized compute platform.",
        "icon": "🔷"
    },
    "US 20Y Treasury (TLT)": {
        "ticker": "TLT",
        "name": "iShares 20+ Year Treasury Bond ETF",
        "category": "Fixed Income",
        "description": "Long-term US sovereign bond index proxy.",
        "icon": "🏛️"
    }
}


def is_featherless_configured() -> bool:
    """Return True if a non-placeholder Featherless API key is present."""
    key = FEATHERLESS_API_KEY
    if not key:
        return False
    if "your_" in key or "placeholder" in key.lower() or len(key) < 8:
        return False
    return True


def get_masked_api_key() -> str:
    """Safely return a masked version of the Featherless API key."""
    if not is_featherless_configured():
        return "Not Configured"
    key = FEATHERLESS_API_KEY
    if len(key) <= 8:
        return "****"
    return f"{key[:4]}...{key[-4:]}"
