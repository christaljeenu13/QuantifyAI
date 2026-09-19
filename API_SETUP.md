# QuantifyAI — Featherless AI & API Setup Guide

This guide details how to securely configure **Featherless AI** and market data feeds in **QuantifyAI** on Windows without exposing credentials.

---

## 1. Security First: Zero-Credential Exposure

QuantifyAI strictly enforces credential safety:
* **Never commit `.env` to Git.** It is already registered in `.gitignore`.
* **Never paste your API key in public chat channels or issues.**
* The platform features automated API key masking (`sk-1234...abcd`) across all UI pages and diagnostic logs.
* If no API key is provided, the platform **gracefully defaults to local quantitative rule-based analysis**, ensuring 100% of all market calculations, charts, backtests, and risk analytics continue to work offline.

---

## 2. Obtain a Featherless AI Key

1. Navigate to [Featherless AI](https://featherless.ai/) and create an account.
2. Go to your **API Keys** dashboard.
3. Generate a new API Key (begins with standard prefix).
4. Copy the key to your clipboard.

---

## 3. Local Configuration via `.env` (Recommended)

In the root directory of the project:

### PowerShell:
```powershell
# Copy the example environment file
Copy-Item .env.example .env

# Open .env in your text editor (e.g. Notepad)
notepad .env
```

### Set the following variables in `.env`:
```ini
# Featherless AI Configuration (OpenAI-compatible)
FEATHERLESS_API_KEY=your_actual_featherless_api_key_here
FEATHERLESS_MODEL=meta-llama/Meta-Llama-3.1-8B-Instruct

# Market Data (yfinance is free & public; no key needed)
MARKET_DATA_API_KEY=

# Quantitative Analysis Defaults
RISK_FREE_RATE=0.04
DEFAULT_INITIAL_CAPITAL=10000.0
DEFAULT_TRANSACTION_FEE=0.001
```

Save and close the file. The changes will take effect automatically upon starting the application.

---

## 4. Alternative: Session-Only UI Configuration

If you do not wish to write to disk:
1. Launch QuantifyAI.
2. Navigate to **Page 7: Settings & API**.
3. Expand **🔑 Session-Only Key Override**.
4. Paste your key and click **Apply Key to Current Session**.
5. Click **Run Connection Ping** to verify connectivity with Featherless endpoints (`https://api.featherless.ai/v1`).
*(Note: Session keys are stored in volatile browser memory and expire when the browser tab closes).*

---

## 5. Supported Featherless AI Models

The following tested models are available in the dropdown selector on Page 6 & 7:
* `meta-llama/Meta-Llama-3.1-8B-Instruct` (Default, fast & precise)
* `meta-llama/Meta-Llama-3.1-70B-Instruct` (Deep quantitative reasoning)
* `mistralai/Mistral-7B-Instruct-v0.3` (Concise financial summaries)
* `Qwen/Qwen2.5-7B-Instruct` (Complex multi-step quantitative tasks)
* `google/gemma-2-9b-it` (Analytical education)

---

## 6. Market Data Provider Information

* **Provider:** Yahoo Finance via `yfinance`
* **API Key:** Not required. Public historical daily OHLCV quotes are streamed automatically.
* **Assets Covered:**
  * Gold: `GLD` (SPDR Gold Shares ETF) / `GC=F` (COMEX Continuous Futures)
  * Bitcoin: `BTC-USD`
  * NVIDIA: `NVDA`
  * Extensible to any ticker (e.g. `SPY`, `AAPL`, `ETH-USD`, `TLT`).
