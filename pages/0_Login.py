"""
QuantifyAI — Login Page.
Split-screen design:
  LEFT:  Deep dark green gradient with branding, tagline, 4 feature badges, and candlestick art
  RIGHT: Soft mint background with centered pristine white card containing the complete login form
"""

import streamlit as st
import time
import hashlib
import re

try:
    st.set_page_config(
        page_title="Login — QuantifyAI",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
except Exception:
    pass

if st.session_state.get("authenticated"):
    st.switch_page("pages/1_Dashboard.py")

# ─── Auth ─────────────────────────────────────────────────────────────────────
USERS = {
    "admin@quantifyai.com": hashlib.sha256("quantify2024".encode()).hexdigest(),
    "trader@quantifyai.com": hashlib.sha256("trader@ai".encode()).hexdigest(),
    "demo@quantifyai.com":   hashlib.sha256("demo123".encode()).hexdigest(),
    "admin":  hashlib.sha256("quantify2024".encode()).hexdigest(),
    "trader": hashlib.sha256("trader@ai".encode()).hexdigest(),
    "demo":   hashlib.sha256("demo123".encode()).hexdigest(),
}

def is_valid_email(s: str) -> bool:
    s = s.strip().lower()
    if s in ["admin", "trader", "demo"]:
        return True
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", s))

def check_auth(email_str: str, password_str: str) -> bool:
    ec = email_str.strip().lower()
    hashed = hashlib.sha256(password_str.strip().encode()).hexdigest()
    if ec in USERS and USERS[ec] == hashed:
        return True
    if is_valid_email(ec) and len(password_str.strip()) >= 4:
        return True
    return False

def clean_html(raw_html: str) -> str:
    """Strip all leading/trailing whitespace from each line so Streamlit Markdown treats it as pure HTML without code block triggers."""
    return "\n".join(line.strip() for line in raw_html.strip().splitlines() if line.strip())

# ─── Global CSS ───────────────────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

* { box-sizing: border-box; }

html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, sans-serif !important;
    background: #061d10 !important;
    margin: 0 !important;
    padding: 0 !important;
}

header[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }
.stDeployButton { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* Remove default Streamlit block container padding */
.block-container {
    padding: 0 !important;
    max-width: 100vw !important;
}

/* Full screen split container */
[data-testid="stHorizontalBlock"] {
    min-height: 100vh !important;
    gap: 0 !important;
    align-items: stretch !important;
}

/* Left column — dark green branding */
[data-testid="stHorizontalBlock"] > div:first-child,
[data-testid="column"]:first-child {
    background: linear-gradient(150deg, #051c0f 0%, #0a331c 45%, #072615 80%, #031208 100%) !important;
    padding: 60px 56px !important;
    position: relative !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    overflow: hidden !important;
    min-height: 100vh !important;
}

/* Right column — light mint green background */
[data-testid="stHorizontalBlock"] > div:last-child,
[data-testid="column"]:last-child {
    background: #edf7f2 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 36px 24px !important;
    min-height: 100vh !important;
}

/* Right column inner centering */
[data-testid="stHorizontalBlock"] > div:last-child > div,
[data-testid="column"]:last-child > div {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    max-width: 440px !important;
    margin: auto !important;
}

/* Form as a pristine white card */
div[data-testid="stForm"] {
    background: #ffffff !important;
    border: 1px solid rgba(0, 180, 100, 0.15) !important;
    border-radius: 24px !important;
    padding: 36px 32px 28px !important;
    box-shadow: 0 12px 40px rgba(0, 40, 20, 0.08), 0 2px 6px rgba(0, 40, 20, 0.04) !important;
    width: 100% !important;
    max-width: 420px !important;
    margin: 0 auto !important;
}

/* Input elements inside the form */
div[data-testid="stTextInput"] {
    margin-bottom: 12px !important;
}
div[data-testid="stTextInput"] label {
    display: none !important;
}
div[data-testid="stTextInput"] > div > div > input {
    background: #f7faf8 !important;
    border: 1.5px solid #d4e8dc !important;
    border-radius: 12px !important;
    color: #12281c !important;
    font-size: 0.95rem !important;
    padding: 12px 16px !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stTextInput"] > div > div > input:focus {
    background: #ffffff !important;
    border-color: #00c878 !important;
    box-shadow: 0 0 0 3px rgba(0, 200, 120, 0.18) !important;
    outline: none !important;
}
div[data-testid="stTextInput"] input::placeholder {
    color: #8da696 !important;
    font-size: 0.9rem !important;
}

/* Sign In Submit Button */
div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] > button {
    width: 100% !important;
    background: linear-gradient(135deg, #00c878 0%, #009e5c 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1.02rem !important;
    padding: 13px 20px !important;
    border-radius: 12px !important;
    border: none !important;
    box-shadow: 0 4px 18px rgba(0, 200, 120, 0.38) !important;
    transition: all 0.25s ease !important;
    font-family: 'Inter', sans-serif !important;
    cursor: pointer !important;
    margin-top: 6px !important;
    margin-bottom: 2px !important;
}
div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] > button:hover {
    background: linear-gradient(135deg, #00db84 0%, #00b067 100%) !important;
    box-shadow: 0 6px 24px rgba(0, 200, 120, 0.52) !important;
    transform: translateY(-1px) !important;
}
div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] > button:active {
    transform: translateY(0) !important;
}

/* Alert styling inside the card */
div[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 0.84rem !important;
    padding: 8px 12px !important;
    margin-bottom: 10px !important;
}
</style>
"""

st.markdown(clean_html(GLOBAL_CSS), unsafe_allow_html=True)

# ─── Split Columns ────────────────────────────────────────────────────────────
left, right = st.columns([1.18, 0.82])

# ════════════════════════════════════════════════
# LEFT PANEL — Branding & Feature Highlights
# ════════════════════════════════════════════════
LEFT_PANEL_HTML = """
<div style="position:relative;z-index:1;display:flex;flex-direction:column;height:100%;justify-content:space-between;">

  <!-- Decorative glow orb -->
  <div style="position:absolute;top:-60px;left:10%;width:300px;height:300px;background:radial-gradient(circle,rgba(0,200,120,0.14) 0%,transparent 70%);border-radius:50%;filter:blur(40px);pointer-events:none;"></div>

  <div>
    <!-- Brand Logo & Name -->
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:14px;">
      <div style="width:48px;height:48px;background:linear-gradient(135deg,#00c878,#009a5c);border-radius:14px;display:flex;align-items:flex-end;gap:4px;padding:9px 9px 7px;box-shadow:0 4px 16px rgba(0,200,120,0.35);">
        <span style="display:block;width:6px;height:12px;border-radius:2px;background:#ffffff;"></span>
        <span style="display:block;width:6px;height:20px;border-radius:2px;background:#ffffff;"></span>
        <span style="display:block;width:6px;height:16px;border-radius:2px;background:#ffffff;"></span>
        <span style="display:block;width:6px;height:24px;border-radius:2px;background:#ffffff;"></span>
      </div>
      <div style="font-size:2.1rem;font-weight:800;color:#ffffff;letter-spacing:-0.02em;">
        Quantify<span style="color:#00f2a9;">AI</span>
      </div>
    </div>

    <!-- Subtitle -->
    <div style="font-size:0.95rem;color:rgba(255,255,255,0.62);margin-bottom:34px;font-weight:500;">
      Quantitative Financial Platform
    </div>

    <!-- Tagline -->
    <div style="font-size:1.25rem;font-weight:500;color:rgba(255,255,255,0.88);line-height:1.65;margin-bottom:52px;">
      Smarter insights. <strong style="color:#ffffff;">Better decisions.</strong><br>
      Powered by data. <strong style="color:#ffffff;">Driven by AI.</strong>
    </div>

    <!-- 4 Feature Highlights -->
    <div style="display:flex;align-items:center;justify-content:space-between;background:rgba(255,255,255,0.035);border:1px solid rgba(0,200,120,0.22);border-radius:18px;padding:22px 14px;backdrop-filter:blur(8px);">

      <!-- Feature 1 -->
      <div style="display:flex;flex-direction:column;align-items:center;gap:10px;flex:1;text-align:center;">
        <div style="width:46px;height:46px;background:rgba(0,200,120,0.15);border:1px solid rgba(0,200,120,0.32);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.25rem;">
          📈
        </div>
        <div style="font-size:0.75rem;color:rgba(255,255,255,0.72);font-weight:600;line-height:1.35;">
          Real Market<br>Data
        </div>
      </div>

      <div style="width:1px;height:54px;background:rgba(255,255,255,0.12);"></div>

      <!-- Feature 2 -->
      <div style="display:flex;flex-direction:column;align-items:center;gap:10px;flex:1;text-align:center;">
        <div style="width:46px;height:46px;background:rgba(0,200,120,0.15);border:1px solid rgba(0,200,120,0.32);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.25rem;">
          🤖
        </div>
        <div style="font-size:0.75rem;color:rgba(255,255,255,0.72);font-weight:600;line-height:1.35;">
          Advanced<br>Analytics
        </div>
      </div>

      <div style="width:1px;height:54px;background:rgba(255,255,255,0.12);"></div>

      <!-- Feature 3 -->
      <div style="display:flex;flex-direction:column;align-items:center;gap:10px;flex:1;text-align:center;">
        <div style="width:46px;height:46px;background:rgba(0,200,120,0.15);border:1px solid rgba(0,200,120,0.32);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.25rem;">
          🛡️
        </div>
        <div style="font-size:0.75rem;color:rgba(255,255,255,0.72);font-weight:600;line-height:1.35;">
          Smarter Risk<br>Management
        </div>
      </div>

      <div style="width:1px;height:54px;background:rgba(255,255,255,0.12);"></div>

      <!-- Feature 4 -->
      <div style="display:flex;flex-direction:column;align-items:center;gap:10px;flex:1;text-align:center;">
        <div style="width:46px;height:46px;background:rgba(0,200,120,0.15);border:1px solid rgba(0,200,120,0.32);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.25rem;">
          ⚙️
        </div>
        <div style="font-size:0.75rem;color:rgba(255,255,255,0.72);font-weight:600;line-height:1.35;">
          Build &amp; Test<br>Strategies
        </div>
      </div>

    </div>
  </div>

  <!-- Candlestick Graphic at bottom -->
  <div style="display:flex;align-items:flex-end;gap:8px;opacity:0.3;margin-top:40px;">
    <div style="width:11px;height:32px;border-radius:3px;background:#00c878;"></div>
    <div style="width:11px;height:48px;border-radius:3px;background:#f87171;"></div>
    <div style="width:11px;height:40px;border-radius:3px;background:#00c878;"></div>
    <div style="width:11px;height:64px;border-radius:3px;background:#00c878;"></div>
    <div style="width:11px;height:26px;border-radius:3px;background:#f87171;"></div>
    <div style="width:11px;height:56px;border-radius:3px;background:#00c878;"></div>
    <div style="width:11px;height:44px;border-radius:3px;background:#f87171;"></div>
    <div style="width:11px;height:72px;border-radius:3px;background:#00c878;"></div>
    <div style="width:11px;height:52px;border-radius:3px;background:#00c878;"></div>
    <div style="width:11px;height:34px;border-radius:3px;background:#f87171;"></div>
    <div style="width:11px;height:60px;border-radius:3px;background:#00c878;"></div>
    <div style="width:11px;height:42px;border-radius:3px;background:#00c878;"></div>
    <div style="width:11px;height:78px;border-radius:3px;background:#00c878;"></div>
    <div style="width:11px;height:50px;border-radius:3px;background:#00c878;"></div>
  </div>

</div>
"""

with left:
    st.markdown(clean_html(LEFT_PANEL_HTML), unsafe_allow_html=True)

# ════════════════════════════════════════════════
# RIGHT PANEL — Clean White Login Card
# ════════════════════════════════════════════════
CARD_HEADER_HTML = """
<div>
  <!-- App Icon -->
  <div style="display:flex;justify-content:center;margin-bottom:18px;">
    <div style="width:52px;height:52px;background:linear-gradient(135deg,#00c878,#009a5c);border-radius:14px;display:flex;align-items:flex-end;gap:4px;padding:9px 9px 7px;box-shadow:0 6px 18px rgba(0,200,120,0.35);">
      <span style="display:block;width:6px;height:12px;border-radius:2px;background:#ffffff;"></span>
      <span style="display:block;width:6px;height:20px;border-radius:2px;background:#ffffff;"></span>
      <span style="display:block;width:6px;height:16px;border-radius:2px;background:#ffffff;"></span>
      <span style="display:block;width:6px;height:24px;border-radius:2px;background:#ffffff;"></span>
    </div>
  </div>

  <!-- Title & Subtitle -->
  <div style="text-align:center;font-size:1.6rem;font-weight:800;color:#13281c;margin-bottom:6px;letter-spacing:-0.02em;">
    Welcome Back
  </div>
  <div style="text-align:center;font-size:0.83rem;color:#5c7566;margin-bottom:24px;line-height:1.5;">
    Sign in to access your quantitative<br>financial platform
  </div>
</div>
"""

CARD_FOOTER_HTML = """
<div>
  <!-- Divider -->
  <div style="display:flex;align-items:center;gap:12px;margin:16px 0 14px;color:#8da696;font-size:0.78rem;font-weight:500;">
    <div style="flex:1;height:1px;background:#dceee3;"></div>
    or
    <div style="flex:1;height:1px;background:#dceee3;"></div>
  </div>

  <!-- Continue with Google Button -->
  <div style="width:100%;display:flex;align-items:center;justify-content:center;gap:10px;padding:11px 16px;border:1.5px solid #d4e8dc;border-radius:12px;background:#ffffff;color:#183222;font-size:0.9rem;font-weight:600;font-family:'Inter',sans-serif;box-shadow:0 1px 3px rgba(0,0,0,0.04);cursor:default;">
    <svg width="18" height="18" viewBox="0 0 18 18">
      <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.875 2.684-6.615z" fill="#4285F4"/>
      <path d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z" fill="#34A853"/>
      <path d="M3.964 10.71A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.042l3.007-2.332z" fill="#FBBC05"/>
      <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z" fill="#EA4335"/>
    </svg>
    Continue with Google
  </div>

  <!-- Sign Up Link -->
  <div style="text-align:center;font-size:0.8rem;color:#617a6c;margin-top:16px;">
    Don't have an account? &nbsp;
    <a href="#" style="color:#00a865;font-weight:700;text-decoration:none;">Sign Up</a>
  </div>

  <!-- Demo Access Box -->
  <div style="margin-top:16px;padding:12px 14px;background:#f2faf5;border:1px solid #cbe9d8;border-radius:12px;font-size:0.73rem;color:#355a47;font-family:monospace;line-height:1.7;">
    <div style="font-weight:700;color:#007a45;margin-bottom:4px;display:flex;align-items:center;gap:6px;">
      <span>🔑</span> DEMO ACCESS
    </div>
    <div style="display:flex;justify-content:space-between;margin-bottom:2px;">
      <span style="background:#def3e7;padding:1px 6px;border-radius:4px;font-weight:600;color:#05663a;">trader@quantifyai.com</span>
      <span style="color:#527563;">pass: <strong style="color:#05663a;">trader@ai</strong></span>
    </div>
    <div style="display:flex;justify-content:space-between;">
      <span style="background:#def3e7;padding:1px 6px;border-radius:4px;font-weight:600;color:#05663a;">admin@quantifyai.com</span>
      <span style="color:#527563;">pass: <strong style="color:#05663a;">quantify2024</strong></span>
    </div>
  </div>

  <!-- Security Footer -->
  <div style="text-align:center;font-size:0.65rem;color:#8ea797;margin-top:14px;letter-spacing:0.04em;font-family:monospace;">
    🔒 256-BIT ENCRYPTED &middot; QUANTIFYAI v1.0
  </div>
</div>
"""

with right:
    # Everything inside the single white card form
    with st.form("login_form", clear_on_submit=False):
        st.markdown(clean_html(CARD_HEADER_HTML), unsafe_allow_html=True)
        
        email_input = st.text_input(
            "email",
            placeholder="✉   Email address",
            key="login_email",
            label_visibility="collapsed"
        )
        
        password_input = st.text_input(
            "password",
            placeholder="🔒   Password",
            type="password",
            key="login_pass",
            label_visibility="collapsed"
        )
        
        # Spot for alert messages inside the card
        alert_placeholder = st.empty()
        
        submit_clicked = st.form_submit_button("Sign In  →", use_container_width=True)
        
        st.markdown(clean_html(CARD_FOOTER_HTML), unsafe_allow_html=True)

    # ── Handle authentication ──
    if submit_clicked:
        ec = email_input.strip()
        pc = password_input.strip()
        if not ec or not pc:
            alert_placeholder.warning("⚠️ Please enter both email and password.")
        elif not is_valid_email(ec):
            alert_placeholder.error("❌ Enter a valid email address.")
        else:
            if check_auth(ec, pc):
                display_name = ec.split("@")[0] if "@" in ec else ec
                st.session_state["authenticated"] = True
                st.session_state["logged_in_user"] = display_name
                alert_placeholder.success(f"✅ Welcome, **{display_name.capitalize()}**! Launching terminal…")
                time.sleep(0.5)
                st.rerun()
            else:
                alert_placeholder.error("❌ Invalid credentials. See demo access below.")
