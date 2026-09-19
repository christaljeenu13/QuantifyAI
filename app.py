"""
QuantifyAI — Quantitative Multi-Asset Financial Analysis Platform.
Executive Terminal Navigation & Application Router.
Coordinates all 7 platform suites using Streamlit's official st.navigation API.

Flow: Splash (3s) → Login (Email/Pass) → Dashboard Platform (Full Navbar)
"""

import streamlit as st
import config
from src.ui.theme import apply_custom_theme, get_color_palette
from src.ui.components import render_html, render_sidebar_branding

# Set global page configuration once for the entire platform
st.set_page_config(
    page_title="QuantifyAI — Quantitative Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Navigation & Authentication Router ──────────────────────────────────────
if not st.session_state.get("splash_done") and not st.session_state.get("authenticated"):
    # 1. First: 3-second Loading screen with no navbar
    pg = st.navigation([st.Page("pages/00_Splash.py", title="Loading")], position="hidden")
    pg.run()

elif not st.session_state.get("authenticated"):
    # 2. Next: Cyber-Luxe Login page with no navbar
    pg = st.navigation([st.Page("pages/0_Login.py", title="Login")], position="hidden")
    pg.run()

else:
    # 3. Authenticated Web Platform with Full Navbar & Original Layout
    apply_custom_theme()
    colors = get_color_palette()

    # Pin QuantifyAI logo at the very top of the sidebar (above navigation)
    st.logo(
        "assets/logo_sidebar.png",
        size="large",
        icon_image="assets/logo_icon.png",
    )

    # Modern multi-page navigation matching reference mockup Image 2
    pg = st.navigation(
        [
            st.Page("pages/1_Dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True),
            st.Page("pages/2_Asset_Analysis.py", title="Asset Analysis", icon=":material/bar_chart:"),
            st.Page("pages/3_Asset_Comparison.py", title="Asset Comparison", icon=":material/balance:"),
            st.Page("pages/4_Strategy_Backtesting.py", title="Strategy Backtesting", icon=":material/trending_up:"),
            st.Page("pages/5_Portfolio_Risk_Lab.py", title="Portfolio Risk Lab", icon=":material/speed:"),
            st.Page("pages/6_AI_Assistant.py", title="AI Assistant", icon=":material/smart_toy:"),
            st.Page("pages/7_Settings.py", title="Settings", icon=":material/settings:"),
        ],
        expanded=True
    )

    # Run active page
    pg.run()

    # Bottom Sidebar — User info + logout
    with st.sidebar:
        logged_user = st.session_state.get("logged_in_user", "User")

        st.markdown(
            f"""
            <div style="background: rgba(0,242,169,0.06); border: 1px solid rgba(0,242,169,0.15);
                 border-radius: 10px; padding: 12px 14px; margin-top: 0.8rem;">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                    <div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#00f2a9,#0082ff);
                         display:flex;align-items:center;justify-content:center;font-weight:800;font-size:0.85rem;color:#041210;">
                        {logged_user[0].upper()}
                    </div>
                    <div>
                        <div style="font-size:0.78rem;font-weight:700;color:#ffffff;">{logged_user.capitalize()}</div>
                        <div style="font-size:0.66rem;color:#00f2a9;font-family:'JetBrains Mono',monospace;">Pro · Active</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("🔓 Logout", use_container_width=True, key="sidebar_logout_btn"):
            st.session_state["authenticated"] = False
            st.session_state["splash_done"] = True
            st.session_state.pop("logged_in_user", None)
            st.rerun()

        sb_quote = """
<div style="background: rgba(11, 25, 34, 0.7); border: 1px solid rgba(0, 242, 169, 0.18); border-radius: 8px; padding: 14px; margin-top: 0.8rem;">
    <span style="color: #00f2a9; font-size: 1.6rem; font-family: Georgia, serif; line-height: 1; display: block; margin-bottom: 2px;">"</span>
    <div style="color: #94a3b8; font-size: 0.78rem; font-style: italic; line-height: 1.4;">
        Data turns uncertainty into opportunity.
    </div>
    <div style="color: #64748b; font-size: 0.72rem; margin-top: 8px; font-weight: 600;">
        — QuantifyAI
    </div>
</div>
"""
        render_html(sb_quote)
