"""
Featherless AI Client Module.
OpenAI-compatible client interfacing with https://api.featherless.ai/v1.
Provides quantitative interpretation, contextual explanations, and safe fallback handling.
"""

from typing import Dict, Any, List, Optional
import os
import json
from openai import OpenAI
import config


QUANTITATIVE_SYSTEM_PROMPT = """You are QuantifyAI's Quantitative Research Assistant, an institutional financial analyst.
Your job is to interpret real calculated metrics, backtesting performance, and multi-asset risk data provided in context.

CRITICAL RULES:
1. Ground all analysis strictly in the provided mathematical metrics (Sharpe ratio, CAGR, Volatility, Max Drawdown, Correlations).
2. Do NOT invent prices, returns, benchmark results, or future price targets.
3. Distinguish clearly between empirical historical facts and quantitative hypothesis.
4. Keep insights structured, concise, and professional (use bullet points and bold metrics).
5. Always remind the user that historical results do not guarantee future performance and this is for research/education only.
"""


class FeatherlessClient:
    """Client for Featherless AI's OpenAI-compatible inference endpoint."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = config.FEATHERLESS_BASE_URL,
        model: Optional[str] = None
    ):
        self.api_key = (api_key if api_key is not None else config.FEATHERLESS_API_KEY).strip()
        self.base_url = base_url
        self.model = (model or config.FEATHERLESS_DEFAULT_MODEL).strip()
        self._client: Optional[OpenAI] = None
        if self.is_configured():
            try:
                self._client = OpenAI(
                    base_url=self.base_url,
                    api_key=self.api_key,
                    timeout=30.0
                )
            except Exception:
                self._client = None

    def is_configured(self) -> bool:
        """Check if API key is present and not a placeholder."""
        if not self.api_key:
            return False
        if "your_" in self.api_key or "placeholder" in self.api_key.lower() or len(self.api_key) < 8:
            return False
        return True

    def test_connection(self) -> Dict[str, Any]:
        """Test API connectivity and key validity."""
        if not self.is_configured():
            return {
                "success": False,
                "status": "not_configured",
                "message": "FEATHERLESS_API_KEY is not configured in .env. Please set your key in Settings or .env."
            }

        try:
            client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                timeout=12.0
            )
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a test ping."},
                    {"role": "user", "content": "Respond with 'PONG' only."}
                ],
                max_tokens=10,
                temperature=0.0
            )
            reply = response.choices[0].message.content.strip()
            return {
                "success": True,
                "status": "connected",
                "model": self.model,
                "message": f"Successfully connected to Featherless AI! (Echo: {reply})"
            }
        except Exception as e:
            # Safe sanitization: never leak keys in exception message
            err_str = str(e)
            if self.api_key in err_str:
                err_str = err_str.replace(self.api_key, "[REDACTED_API_KEY]")
            return {
                "success": False,
                "status": "error",
                "message": f"Featherless AI connection failed: {err_str}"
            }

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_context: str = "",
        max_tokens: int = 800,
        temperature: float = 0.3,
        language: str = "English"
    ) -> Dict[str, Any]:
        """Send chat messages to Featherless AI with injected context and target language."""
        if not self.is_configured():
            fallback = self._generate_rule_based_chat_reply(messages, system_context, language=language)
            return {
                "success": False,
                "configured": False,
                "content": fallback,
                "notice": "Featherless AI key not configured. Displaying local quantitative analysis fallback."
            }

        try:
            full_system = QUANTITATIVE_SYSTEM_PROMPT
            if system_context:
                full_system += f"\n\nCURRENT PLATFORM DATA CONTEXT:\n{system_context}"

            if "tamil" in language.lower() and "tanglish" not in language.lower():
                full_system += "\n\nLANGUAGE INSTRUCTION: Please provide your entire response in clear, formal and fluent Tamil (தமிழ்). Translate quantitative concepts accurately."
            elif "hindi" in language.lower():
                full_system += "\n\nLANGUAGE INSTRUCTION: Please provide your entire response in clear, fluent Hindi (हिंदी). Explain financial and quantitative concepts simply."
            elif "tanglish" in language.lower():
                full_system += "\n\nLANGUAGE INSTRUCTION: Please provide your entire response in friendly, conversational Tanglish (Tamil words written using English alphabets, e.g., 'Asset Analysis la first ticker select pannunga... Initial amount $1000 enter panni simulate pannalam...')."
            else:
                full_system += "\n\nLANGUAGE INSTRUCTION: Please provide your entire response in professional, clear English."

            api_messages = [{"role": "system", "content": full_system}]
            api_messages.extend(messages)

            client = self._client or OpenAI(base_url=self.base_url, api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=api_messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            content = response.choices[0].message.content
            return {
                "success": True,
                "configured": True,
                "content": content,
                "model": self.model
            }
        except Exception as e:
            err_msg = str(e)
            if self.api_key in err_msg:
                err_msg = err_msg.replace(self.api_key, "[REDACTED_API_KEY]")
            fallback = self._generate_rule_based_chat_reply(messages, system_context, language=language)
            return {
                "success": False,
                "configured": True,
                "error": err_msg,
                "content": fallback,
                "notice": f"Featherless API request encountered an error: {err_msg}. Showing local quantitative fallback."
            }

    def explain_asset_analysis(
        self, asset_name: str, ticker: str, metrics: Dict[str, Any]
    ) -> str:
        """Contextual prompt explaining single asset performance."""
        context = (
            f"Asset: {asset_name} ({ticker})\n"
            f"Total Return: {metrics.get('total_return', 0)*100:.2f}%\n"
            f"Annualized Return (CAGR): {metrics.get('annualized_return', 0)*100:.2f}%\n"
            f"Annualized Volatility: {metrics.get('annualized_volatility', 0)*100:.2f}%\n"
            f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}\n"
            f"Sortino Ratio: {metrics.get('sortino_ratio', 0):.2f}\n"
            f"Maximum Drawdown: {metrics.get('max_drawdown', 0)*100:.2f}%\n"
            f"Historical Sessions: {metrics.get('trading_days', 0)}"
        )
        prompt = (
            f"Analyze the historical performance and risk profile of {asset_name} ({ticker}) "
            f"based on the calculated metrics above. Explain what the Sharpe ratio, volatility, "
            f"and maximum drawdown indicate about this asset's risk-adjusted character."
        )
        res = self.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            system_context=context,
            max_tokens=600
        )
        return res["content"]

    def explain_backtest_performance(
        self,
        strategy_name: str,
        asset_name: str,
        strat_metrics: Dict[str, Any],
        bench_metrics: Dict[str, Any]
    ) -> str:
        """Contextual prompt explaining strategy vs benchmark backtest."""
        context = (
            f"Strategy: {strategy_name} on {asset_name}\n"
            f"Strategy Total Return: {strat_metrics.get('total_return', 0)*100:.2f}% | "
            f"Benchmark Total Return: {bench_metrics.get('total_return', 0)*100:.2f}%\n"
            f"Strategy Sharpe: {strat_metrics.get('sharpe_ratio', 0):.2f} | "
            f"Benchmark Sharpe: {bench_metrics.get('sharpe_ratio', 0):.2f}\n"
            f"Strategy Volatility: {strat_metrics.get('annualized_volatility', 0)*100:.2f}% | "
            f"Benchmark Volatility: {bench_metrics.get('annualized_volatility', 0)*100:.2f}%\n"
            f"Strategy Max Drawdown: {strat_metrics.get('max_drawdown', 0)*100:.2f}% | "
            f"Benchmark Max Drawdown: {bench_metrics.get('max_drawdown', 0)*100:.2f}%\n"
            f"Total Trades: {strat_metrics.get('total_trades', 0)} | "
            f"Win Rate: {strat_metrics.get('win_rate', 0):.1f}% | "
            f"Profit Factor: {strat_metrics.get('profit_factor', 0):.2f} | "
            f"Total Fees Paid: ${strat_metrics.get('total_fees_paid', 0):.2f}"
        )
        prompt = (
            f"Provide a rigorous quantitative critique of the {strategy_name} strategy on {asset_name}. "
            f"Did the strategy outperform or underperform Buy & Hold? Why did the crossover lag or reduce drawdowns? "
            f"Discuss trading drag (fees), whipsaws, and risk-adjusted efficiency."
        )
        res = self.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            system_context=context,
            max_tokens=650
        )
        return res["content"]

    def explain_portfolio_risk(
        self, weights: Dict[str, float], port_metrics: Dict[str, Any]
    ) -> str:
        """Contextual prompt explaining portfolio diversification & risk contributions."""
        weights_str = ", ".join([f"{k}: {v*100:.1f}%" for k, v in weights.items()])
        context = (
            f"Portfolio Allocations: {weights_str}\n"
            f"Portfolio Annualized Return: {port_metrics.get('annualized_return', 0)*100:.2f}%\n"
            f"Portfolio Volatility: {port_metrics.get('annualized_volatility', 0)*100:.2f}%\n"
            f"Portfolio Sharpe Ratio: {port_metrics.get('sharpe_ratio', 0):.2f}\n"
            f"Portfolio Max Drawdown: {port_metrics.get('max_drawdown', 0)*100:.2f}%\n"
            f"Daily VaR (95%): {port_metrics.get('var_95_daily', 0)*100:.2f}%\n"
            f"Daily CVaR (95%): {port_metrics.get('cvar_95_daily', 0)*100:.2f}%"
        )
        prompt = (
            "Analyze the diversification benefits, volatility reduction, and tail-risk exposure (VaR/CVaR) "
            "for this multi-asset portfolio based on the real metrics above."
        )
        res = self.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            system_context=context,
            max_tokens=600
        )
        return res["content"]

    def _generate_rule_based_chat_reply(
        self, messages: List[Dict[str, str]], context: str, language: str = "English"
    ) -> str:
        """Deterministic quantitative fallback when Featherless is unconfigured with multi-language support."""
        last_msg = messages[-1]["content"].lower() if messages else ""
        lang_lower = language.lower()

        # Tamil Response
        if "tamil" in lang_lower and "tanglish" not in lang_lower:
            reply = (
                "### 📊 QuantifyAI நிறுவன பகுப்பாய்வு & வழிகாட்டி (தமிழ்)\n\n"
                "> *குறிப்பு: Featherless AI மூலம் பதில்களைப் பெற **Settings** பக்கத்தில் `FEATHERLESS_API_KEY`-ஐ உள்ளிடவும்.*\n\n"
            )
            if "guide" in last_msg or "how to" in last_msg or "process" in last_msg or "doubt" in last_msg or "எப்படி" in last_msg or "விளக்கம்" in last_msg:
                reply += (
                    "**📘 QuantifyAI மென்பொருள் பயன்பாட்டு வழிகாட்டி:**\n"
                    "- **1. Asset Analysis (சொத்து பகுப்பாய்வு)**: ஒரு பங்கை (NVDA, BTC, GLD) தேர்ந்தெடுத்து தேதியை அமைக்கவும். 16 முக்கிய தலைப்புகள் (விலை, SMA, EMA, Volatility, Sharpe, Drawdown, OBV, சந்தை சூழல்) கிடைக்கும்.\n"
                    "- **2. Investment Value Simulation (முதலீட்டு உருவகப்படுத்துதல்)**: $1,000 போன்ற தொகையை உள்ளிட்டு, இலக்கு தேதியில் அது எவ்வளவு மதிப்பாக மாறியிருக்கும் என்பதையும், அதற்கான அபாயம் மற்றும் நன்மைகளையும் (Risks vs Benefits) பார்க்கலாம்.\n"
                    "- **3. Asset Comparison (சொத்து ஒப்பீடு)**: 5 சொத்துக்கள் வரை ஒரே நேரத்தில் ஒப்பிட்டு அவற்றின் ஆபத்து மற்றும் லாப விகிதங்களை ஆராயலாம்.\n"
                    "- **4. Strategy Backtesting (வியூகம் சோதனை)**: SMA, RSI போன்ற அல்காரிதம்களை இயக்கி கடந்த காலங்களில் அது எவ்வாறு செயல்பட்டது என்பதை அறியலாம்.\n"
                    "- **5. Portfolio Risk Lab**: போர்ட்ஃபோலியோ அமைத்து மான்டே கார்லோ சிமுலேஷன் மற்றும் 95% VaR கணக்கிடலாம்.\n"
                )
            elif "investment" in last_msg or "simulate" in last_msg or "1000" in last_msg or "முதலீடு" in last_msg:
                reply += (
                    "**💰 முதலீட்டு உருவகப்படுத்துதல் (Investment Simulation):**\n"
                    "- **கணக்கீடு முறை**: இறுதி மதிப்பு = தொடக்கத் தொகை × (முடிவு விலை / தொடக்க விலை).\n"
                    "- **நன்மைகள் (Benefits)**: கூட்டு வட்டி வளர்ச்சி, மூலதன லாபம் மற்றும் வருடாந்திர CAGR.\n"
                    "- **அபாயங்கள் (Risks)**: அந்த முதலீட்டு காலத்தில் ஏற்பட்ட அதிகபட்ச மூலதன இழப்பு (Max Drawdown) மற்றும் விலை ஏற்ற இறக்கம்.\n"
                )
            else:
                reply += (
                    "**முக்கிய நிதி அளவீடுகள்:**\n"
                    "- **Sharpe Ratio**: முதலீட்டின் அபாயத்திற்கு தகுந்த லாபத்தை அளவிடுகிறது (>1.0 என்பது நல்லது).\n"
                    "- **Maximum Drawdown**: வரலாற்றில் உச்சத்திலிருந்து ஏற்பட்ட மிக மோசமான மூலதன சரிவு.\n"
                    "- **VaR (95%)**: 95% நம்பிக்கையுடன் ஒரு நாளில் ஏற்படக்கூடிய அதிகபட்ச இழப்பு.\n"
                )
            return reply

        # Hindi Response
        elif "hindi" in lang_lower:
            reply = (
                "### 📊 QuantifyAI संस्थागत विश्लेषण और गाइड (हिंदी)\n\n"
                "> *सूचना: Featherless AI द्वारा गतिशील उत्तर प्राप्त करने के लिए **Settings** में `FEATHERLESS_API_KEY` सेट करें।*\n\n"
            )
            if "guide" in last_msg or "how to" in last_msg or "process" in last_msg or "doubt" in last_msg or "कैसे" in last_msg:
                reply += (
                    "**📘 QuantifyAI सॉफ्टवेयर उपयोग गाइड:**\n"
                    "- **1. Asset Analysis (एसेट एनालिसिस)**: एसेट चुनें (NVDA, BTC, GLD) और तारीख तय करें। 16 मुख्य विषयों (Price, Moving Averages, Volatility, Sharpe, Drawdown, Volume, Regime) का विश्लेषण करें।\n"
                    "- **2. Investment Value Simulation**: $1,000 जैसी राशि दर्ज करें और देखें कि समय के साथ उसका मूल्य कितना हुआ, साथ ही उसके जोखिम और लाभ (Risks vs Benefits) समझें।\n"
                    "- **3. Asset Comparison**: एक साथ 5 संपत्तियों की तुलना उनके रिस्क-रिटर्न और सहसंबंध (Correlation) के आधार पर करें।\n"
                    "- **4. Strategy Backtesting**: SMA, RSI जैसी ट्रेडिंग रणनीतियों का ऐतिहासिक परीक्षण करें और फीस का प्रभाव देखें।\n"
                    "- **5. Portfolio Risk Lab**: मोंटे कार्लो सिमुलेशन और 95% VaR के साथ अपने पोर्टफोलियो जोखिम का मूल्यांकन करें।\n"
                )
            elif "investment" in last_msg or "simulate" in last_msg or "1000" in last_msg or "निवेश" in last_msg:
                reply += (
                    "**💰 इन्वेस्टमेंट वैल्यू सिमुलेशन (Investment Simulation):**\n"
                    "- **गणना फॉर्मूला**: अंतिम मूल्य = प्रारंभिक राशि × (लक्ष्य तिथि क्लोज़ मूल्य / प्रारंभिक क्लोज़ मूल्य)।\n"
                    "- **लाभ (Benefits)**: कंपाउंडिंग लाभ, वार्षिक रिटर्न (CAGR) और पूंजी वृद्धि।\n"
                    "- **जोखिम (Risks)**: होल्डिंग अवधि के दौरान अधिकतम गिरावट (Max Drawdown) और डाउनसाइड अस्थिरता।\n"
                )
            else:
                reply += (
                    "**महत्वपूर्ण वित्तीय मेट्रिक्स:**\n"
                    "- **Sharpe Ratio**: जोखिम के मुकाबले रिटर्न को मापता है (>1.0 अच्छा माना जाता है)।\n"
                    "- **Maximum Drawdown**: शीर्ष से सबसे निचली ऐतिहासिक गिरावट।\n"
                    "- **VaR (95%)**: 95% आत्मविश्वास के साथ 1 दिन में होने वाली अधिकतम संभावित हानि।\n"
                )
            return reply

        # Tanglish Response (Tamil in English Script)
        elif "tanglish" in lang_lower:
            reply = (
                "### 📊 QuantifyAI Software Guide (Tanglish)\n\n"
                "> *Notice: Generative AI responses ku **Settings** page la `FEATHERLESS_API_KEY` set pannunga.*\n\n"
            )
            if "guide" in last_msg or "how to" in last_msg or "process" in last_msg or "doubt" in last_msg or "epdi" in last_msg:
                reply += (
                    "**📘 QuantifyAI Step-by-Step Software Guide:**\n"
                    "- **1. Asset Analysis**: First ungalukku thevaiyana asset (eg. NVDA, BTC, GLD) select pannunga. Custom date range choose pannina, 16 core analytical topics (Price, SMA/EMA, Returns, Volatility, Sharpe, Drawdown, OBV, Market Regime, AI Summary) automatically generate aagum.\n"
                    "- **2. Investment Value Simulation**: Initial investment amount (eg. $1,000) enter pannunga. Specific date range la unga portfolio value evalavu valarndhurukku nu clear-ah kaatum. Koodave **Risks vs Benefits Analysis** kedaikkum.\n"
                    "- **3. Asset Comparison**: Multiple assets-ah side-by-side compare panni, edhu nalla Sharpe ratio tharudhu nu paarkalam.\n"
                    "- **4. Strategy Backtesting**: SMA crossover, RSI strategies run panni, Buy & Hold benchmark-ah vida strategy nalla perform pannudha nu check pannalam.\n"
                    "- **5. Portfolio Risk Lab**: Unga custom weights set panni, Monte Carlo simulation & 95% VaR risk check pannalam.\n"
                )
            elif "investment" in last_msg or "simulate" in last_msg or "1000" in last_msg:
                reply += (
                    "**💰 Investment Value Simulation & Risk Breakdown:**\n"
                    "- **Calculation**: Final Value = Initial Amount * (Target Date Close / Start Date Close).\n"
                    "- **Benefits**: Total capital growth, compounding profits, and annualized CAGR.\n"
                    "- **Risks**: Andha time period la unga portfolio sandhitha maximum drawdown and downside risk.\n"
                )
            else:
                reply += (
                    "**⚡ Quick Metrics Guide:**\n"
                    "- **Sharpe Ratio**: Risk eduthathukku kedaicha extra return (>1.0 irundha romba nalladhu).\n"
                    "- **Max Drawdown**: Historical peak la irundhu bottom varai vandha maximum loss.\n"
                    "- **VaR (95%)**: 95% confidence la oru naal la vara koodiya maximum expected loss.\n"
                )
            return reply

        # Default English Response
        reply = (
            "### 📊 QuantifyAI Institutional Commentary\n\n"
            "> *Notice: To enable generative dynamic responses with Featherless AI, configure your `FEATHERLESS_API_KEY` in the **Settings** page.*\n\n"
        )

        if "guide" in last_msg or "how to" in last_msg or "process" in last_msg or "doubt" in last_msg or "software" in last_msg or "step" in last_msg:
            reply += (
                "**📘 QuantifyAI Software & Process Walkthrough:**\n"
                "- **1. Asset Analysis**: Select any asset (e.g. NVDA, BTC, GLD) and pick a custom date range. Explore all 16 analytical topics (Historical Price, Moving Averages SMA/EMA, Returns, Volatility, Sharpe, Drawdowns, Volume, Correlations, Benchmark vs SPY/QQQ, Market Regime, and AI Research Summary).\n"
                "- **2. Investment Value Simulation**: Enter an initial dollar amount (e.g. $1,000) and pick your target date to simulate final portfolio value, net gain/loss, and a comprehensive **Risk vs. Benefits Analysis**.\n"
                "- **3. Asset Comparison**: Compare up to 5 assets side-by-side on normalized performance, risk-return scatter, and correlation matrices.\n"
                "- **4. Strategy Backtesting**: Choose an algorithmic strategy (SMA Crossover, RSI, MACD), configure your initial capital and fee %, then evaluate the Equity Curve vs Buy & Hold benchmark.\n"
                "- **5. Portfolio Risk Lab**: Build custom multi-asset allocations, run Monte Carlo simulations (1,000 paths), and assess 95% Value-at-Risk (VaR) and Expected Shortfall (CVaR).\n"
                "- **6. Featherless AI & Settings**: Obtain a free API key at [featherless.ai](https://featherless.ai) and enter it in **Settings** to activate deep Llama-3/Mistral intelligence across the terminal.\n"
            )
        elif "investment" in last_msg or "simulate" in last_msg or "1000" in last_msg or "simulat" in last_msg:
            reply += (
                "**💰 Investment Value Simulation & Risk/Benefit Process:**\n"
                "- **How it Works**: Go to **Asset Analysis**, choose your start date and target date, and input your initial investment amount (e.g., $1,000).\n"
                "- **Calculation Formula**: `Final Value = Initial Amount * (Close Price on Target Date / Close Price on Start Date)`.\n"
                "- **Benefits Assessment**: Highlights compounding gains, upside participation, annualized return (CAGR), and capital growth.\n"
                "- **Risk Exposure Assessment**: Details the maximum peak-to-trough drawdown endured during the holding window, downside volatility, and worst-case drawdown value.\n"
            )
        elif "sharpe" in last_msg or "drawdown" in last_msg or "volatility" in last_msg:
            reply += (
                "**Risk-Adjusted Metrics Primer:**\n"
                "- **Sharpe Ratio**: Measures excess return per unit of total risk. Ratios above 1.0 indicate acceptable compensation for volatility, while >2.0 signifies exceptional risk-efficiency.\n"
                "- **Maximum Drawdown (MDD)**: Represents the worst-case historical peak-to-trough capital loss. Managing MDD is crucial for preventing ruin and psychological capitulation.\n"
                "- **Annualized Volatility**: Gauges statistical dispersion. Assets like Bitcoin typically exhibit 50–70% annualized volatility, whereas Gold ranges between 12–16%.\n"
            )
        elif "backtest" in last_msg or "sma" in last_msg or "strategy" in last_msg or "underperform" in last_msg:
            reply += (
                "**Quantitative Strategy Dynamics:**\n"
                "- **Trend-Following Lag**: Moving average crossovers generate signals only after a trend has developed. In range-bound chop, whipsaws incur continuous execution costs without capturing trend expansions.\n"
                "- **Trading Friction & Fees**: Each turnover event incurs bid-ask slippage and commissions. Over multiple rebalancing sessions, transaction costs noticeably dampen net compounding.\n"
                "- **Drawdown Mitigation**: Trend rules often trade upside participation in exchange for eliminating devastating tail drawdowns during extended bear regimes.\n"
            )
        elif "portfolio" in last_msg or "risk" in last_msg or "weight" in last_msg:
            reply += (
                "**Portfolio Diversification Insights:**\n"
                "- **Correlation Benefits**: Combining uncorrelated assets (e.g. Gold with tech equities or crypto) flattens portfolio volatility through covariance cancellation ($w^T \\Sigma w$).\n"
                "- **Risk Parity**: Capital weight does not equal risk weight. Highly volatile assets like BTC contribute disproportionately to portfolio variance unless their weight is explicitly sized down.\n"
                "- **Tail Risk (VaR/CVaR)**: Value at Risk denotes the minimum expected loss on 5% of worst days, while Conditional VaR (Expected Shortfall) quantifies the average loss once that threshold is breached.\n"
            )
        else:
            reply += (
                "**Quantitative Observation & Support Guidance:**\n"
                "- The platform has evaluated your historical data series using standard institutional mathematical routines.\n"
                "- For questions about features, use the **Software Guide** option in the AI Assistant or consult the Help Center popover on the Dashboard.\n"
                "- *Disclaimer: Historical performance does not guarantee future results. All analytics are for educational and research purposes only.*"
            )

        if context:
            reply += f"\n\n**Evaluated Session Context:**\n```text\n{context}\n```"

        return reply


_global_ai_client = FeatherlessClient()


def get_featherless_client() -> FeatherlessClient:
    """Return singleton FeatherlessClient instance."""
    return _global_ai_client
