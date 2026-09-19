"""
QuantifyAI — Loading Page.
Faithful reproduction of reference design:
- Deep dark violet/purple canvas (#110426 -> #1a083a)
- 7-bar glowing magenta/pink waveform equalizer animation
- Spaced 'LOADING' typographic label
- Exactly 3-second display duration
- Automatic transition to the Login page
"""

import streamlit as st
import time

try:
    st.set_page_config(
        page_title="Loading — QuantifyAI",
        page_icon="📈",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
except Exception:
    pass

# If already authenticated, redirect straight to dashboard
if st.session_state.get("authenticated"):
    st.switch_page("pages/1_Dashboard.py")

# Mark splash as shown for this session
st.session_state["splash_done"] = True

# ─── Full-Screen Purple Waveform Loading Screen ──────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap');

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: #0b1922 !important;
    color: #ffffff !important;
    overflow: hidden !important;
}

/* Hide all Streamlit default chrome */
header[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }
.stDeployButton { display: none !important; }
.block-container {
    padding: 0 !important;
    max-width: 100vw !important;
}

/* Full Viewport Container matching reference image */
.loading-viewport {
    position: fixed;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: radial-gradient(circle at 50% 45%, #041210 0%, #0b1922 50%, #041210 100%);
    z-index: 99999;
}

/* Ambient glow orb behind the waveform */
.loading-viewport::before {
    content: "";
    position: absolute;
    width: 280px;
    height: 280px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0, 242, 169, 0.18) 0%, rgba(0, 130, 255, 0.08) 45%, transparent 70%);
    filter: blur(40px);
    pointer-events: none;
}

/* Waveform Bars Container */
.waveform-container {
    position: relative;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    gap: 8px;
    height: 96px;
    margin-bottom: 28px;
}

/* Individual Waveform Bar */
.wf-bar {
    width: 7px;
    border-radius: 999px;
    background: #00f2a9;
    box-shadow: 
        0 0 10px rgba(0, 242, 169, 0.9),
        0 0 22px rgba(0, 242, 169, 0.5),
        0 0 36px rgba(0, 242, 169, 0.25);
    transform-origin: bottom center;
    animation: barBounce 1.2s ease-in-out infinite alternate;
}

/* Heights & Staggered delays matching reference image visual curve */
.wf-bar:nth-child(1) { height: 42px;  animation-delay: 0.05s; }
.wf-bar:nth-child(2) { height: 72px;  animation-delay: 0.35s; }
.wf-bar:nth-child(3) { height: 56px;  animation-delay: 0.65s; }
.wf-bar:nth-child(4) { height: 92px;  animation-delay: 0.20s; } /* center tallest */
.wf-bar:nth-child(5) { height: 68px;  animation-delay: 0.50s; }
.wf-bar:nth-child(6) { height: 38px;  animation-delay: 0.80s; }
.wf-bar:nth-child(7) { height: 62px;  animation-delay: 0.25s; }

@keyframes barBounce {
    0% {
        transform: scaleY(0.42);
        opacity: 0.72;
        box-shadow: 0 0 8px rgba(0, 242, 169, 0.6);
    }
    50% {
        transform: scaleY(0.85);
        opacity: 0.95;
    }
    100% {
        transform: scaleY(1.08);
        opacity: 1;
        box-shadow: 
            0 0 14px rgba(0, 242, 169, 1),
            0 0 30px rgba(0, 242, 169, 0.7);
    }
}

/* Typography matching reference image */
.loading-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.92rem;
    font-weight: 700;
    color: #7e92a2;
    letter-spacing: 0.38em;
    text-transform: uppercase;
    text-indent: 0.38em; /* optical centering for letter-spacing */
    user-select: none;
    animation: labelBreathe 1.8s ease-in-out infinite alternate;
}

@keyframes labelBreathe {
    0%   { opacity: 0.65; color: #7e92a2; }
    100% { opacity: 1.00; color: #00f2a9; }
}

/* Subtle progress bar at bottom */
.mini-progress {
    position: absolute;
    bottom: 36px;
    width: 140px;
    height: 2px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 999px;
    overflow: hidden;
}

.mini-fill {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, #00f2a9 0%, #0082ff 100%);
    box-shadow: 0 0 8px rgba(0, 242, 169, 0.8);
    animation: fillProgress 3s cubic-bezier(0.2, 0.8, 0.4, 1) forwards;
}

@keyframes fillProgress {
    0%   { width: 0%; }
    40%  { width: 55%; }
    80%  { width: 88%; }
    100% { width: 100%; }
}
</style>

<div class="loading-viewport">
    <div class="waveform-container">
        <div class="wf-bar"></div>
        <div class="wf-bar"></div>
        <div class="wf-bar"></div>
        <div class="wf-bar"></div>
        <div class="wf-bar"></div>
        <div class="wf-bar"></div>
        <div class="wf-bar"></div>
    </div>
    <div class="loading-label">LOADING</div>
    <div class="mini-progress">
        <div class="mini-fill"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Exact 3-Second Loading Sequence ────────────────────────────────────────
# Use short sleep intervals so the browser paints the animated DOM immediately
timer_placeholder = st.empty()
for _ in range(10):
    timer_placeholder.markdown(
        '<span style="font-size:0.001px;color:transparent;opacity:0;">.</span>',
        unsafe_allow_html=True
    )
    time.sleep(0.3)  # 10 x 0.3s = 3.0 seconds

timer_placeholder.empty()

# Automatically transition to Login via router
st.rerun()
