"""
QuantifyAI — Page 7: Settings & API Diagnostics.
Centralized environment configuration, Featherless AI connection testing,
model selection, and local telemetry cache controls.
"""

import streamlit as st
import config
from src.api.featherless_client import FeatherlessClient, get_featherless_client
from src.ui.theme import apply_custom_theme, get_color_palette
from src.ui.components import (
    render_sidebar_branding,
    render_brand_footer
)

try:
    st.set_page_config(page_title="Settings | QuantifyAI", page_icon="⚙️", layout="wide")
except Exception:
    pass
apply_custom_theme()
colors = get_color_palette()
ai_client = get_featherless_client()

# Header
st.markdown(
    """
    <div style="margin-bottom: 1.2rem;">
        <h1 style="margin: 0; font-size: 1.75rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
            Terminal Settings & Diagnostics
        </h1>
        <p style="margin: 2px 0 0 0; font-size: 0.88rem; color: #7e92a2;">
            Environment configuration, Featherless AI connectivity, and market data telemetry controls.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

tab_api, tab_env, tab_cache = st.tabs([
    "🤖 Featherless AI Configuration",
    "📝 Local Environment Setup Guide",
    "🧹 Cache & Diagnostics"
])

with tab_api:
    st.markdown("### 🔌 Featherless AI Engine")
    st.markdown(
        "QuantifyAI integrates with **Featherless AI** using its OpenAI-compatible endpoint. "
        "Your API key remains local and is never logged or exposed."
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Base URL:** `https://api.featherless.ai/v1`")
        status_color = "green" if config.is_featherless_configured() else "red"
        status_text = "CONFIGURED & SECURED" if config.is_featherless_configured() else "NOT CONFIGURED"
        st.markdown(
            f'**API Key Status:** <span class="quant-badge quant-badge-{status_color}">{status_text}</span> '
            f'(`{config.get_masked_api_key()}`)',
            unsafe_allow_html=True
        )

    with c2:
        model_options = config.FEATHERLESS_AVAILABLE_MODELS
        selected_model = st.selectbox(
            "Active Inference Model",
            options=model_options,
            index=0 if config.FEATHERLESS_DEFAULT_MODEL not in model_options else model_options.index(config.FEATHERLESS_DEFAULT_MODEL)
        )

    # Temporary In-Session Key Option
    with st.expander("🔑 Session-Only Key Override (Optional)"):
        st.markdown(
            "<span style='font-size: 0.8rem; color: #94a3b8;'>"
            "Enter an ephemeral API key for the current browser session. For persistent use, set <code>FEATHERLESS_API_KEY</code> in your local <code>.env</code>."
            "</span>",
            unsafe_allow_html=True
        )
        session_key = st.text_input("Enter Featherless API Key", type="password", help="Never saved to disk or git")
        if st.button("Apply Key to Current Session"):
            if session_key.strip():
                ai_client.api_key = session_key.strip()
                ai_client.model = selected_model
                st.success("Session API key applied! Run the connection test below.")

    # Connection Test Action
    st.markdown("---")
    st.markdown("#### ⚡ Connection Diagnostic Test")
    if st.button("Run Connection Ping", type="primary"):
        with st.spinner(f"Pinging Featherless AI with model {selected_model}..."):
            test_client = FeatherlessClient(
                api_key=ai_client.api_key,
                base_url=config.FEATHERLESS_BASE_URL,
                model=selected_model
            )
            result = test_client.test_connection()

            if result["success"]:
                st.success(f"🎉 **Status: Connected!** {result['message']}")
            else:
                st.error(f"❌ **Status: Diagnostic Failed.** {result['message']}")

with tab_env:
    st.markdown("### 🔒 Secure Local Setup Instructions")
    st.markdown(
        """
        QuantifyAI follows standard 12-factor application security practices:
        - **Secrets reside strictly in `.env`**, which is excluded from Git by `.gitignore`.
        - **No API keys are committed** to the repository or logged in terminal output.
        - The application functions seamlessly in offline rule-based mode even without an AI key.
        """
    )

    st.code(
        """# Copy the template to .env and insert your Featherless key:
Copy-Item .env.example .env
notepad .env

# Set:
FEATHERLESS_API_KEY=your_actual_key_here
FEATHERLESS_MODEL=Qwen/Qwen2.5-7B-Instruct""",
        language="powershell"
    )

with tab_cache:
    st.markdown("### 🧹 Cache & Storage Management")
    from src.data.market_data import SNAP_DIR
    st.caption(
        "Market data is cached in memory for 30 minutes. Every successful Yahoo Finance download is also "
        "saved to the local `data_cache` folder as an offline backup, used only when Yahoo is unreachable."
    )
    _snaps = sorted(SNAP_DIR.glob("*.csv")) if SNAP_DIR.exists() else []
    st.markdown(f"**Offline snapshots saved:** {len(_snaps)}" + (f" ({', '.join(p.stem for p in _snaps)})" if _snaps else ""))
    if st.button("Clear Streamlit Telemetry Cache"):
        st.cache_data.clear()
        st.success("✅ Telemetry cache cleared successfully!")

render_brand_footer()
