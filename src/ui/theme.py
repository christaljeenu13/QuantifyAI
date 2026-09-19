"""
QuantifyAI Terminal Design System — High-Fidelity Fintech Theme.
Implements exact visual aesthetic: Ultra-dark pitch charcoal (#060a0e), deep teal surfaces (#0b1319),
electric neon-green (#00f2a9) positive accents, coral-red (#f87171) indicators,
glowing wave graphics, and monospace telemetry metrics.
"""

import base64
import streamlit as st

COLOR_PALETTE = {
    "bg_main": "#060a0e",
    "bg_sidebar": "#070b0e",
    "bg_surface": "#0b1319",
    "bg_surface_alt": "#0f1a22",
    "border_teal": "#142834",
    "border_teal_hover": "#00f2a9",
    "accent_green": "#00f2a9",
    "accent_emerald": "#10b981",
    "accent_cyan": "#38bdf8",
    "accent_gold": "#f59e0b",
    "text_primary": "#ffffff",
    "text_secondary": "#cbd5e1",
    "text_muted": "#7e92a2",
    "text_dim": "#475569",
    "negative_red": "#f87171",
    "chart_bg": "#080d12",
    "grid_line": "#121e27"
}


def get_color_palette():
    """Return dictionary of theme hex codes."""
    return COLOR_PALETTE


def render_svg_wave(height: int = 45, width: str = "100%", opacity: float = 0.8) -> str:
    """Return an inline SVG string for the signature QuantifyAI emerald wave ribbon."""
    raw_svg = f"""<svg width="400" height="60" viewBox="0 0 400 60" fill="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="waveGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#00f2a9" stop-opacity="0.8"/>
                <stop offset="50%" stop-color="#00d2ff" stop-opacity="0.5"/>
                <stop offset="100%" stop-color="#00f2a9" stop-opacity="0.1"/>
            </linearGradient>
            <linearGradient id="waveFill" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="#00f2a9" stop-opacity="0.15"/>
                <stop offset="100%" stop-color="#00f2a9" stop-opacity="0.0"/>
            </linearGradient>
        </defs>
        <path d="M0 40 C 60 10, 140 55, 200 30 C 260 5, 340 45, 400 20 L 400 60 L 0 60 Z" fill="url(#waveFill)" />
        <path d="M0 40 C 60 10, 140 55, 200 30 C 260 5, 340 45, 400 20" stroke="url(#waveGrad)" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M0 48 C 70 20, 150 48, 220 38 C 290 28, 350 42, 400 32" stroke="#00f2a9" stroke-width="1.2" stroke-opacity="0.4" stroke-linecap="round"/>
    </svg>"""
    b64 = base64.b64encode(raw_svg.encode("utf-8")).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{b64}" style="width: {width}; height: {height}px; display: block; opacity: {opacity};" alt="wave" />'


def generate_mini_sparkline_svg(values, is_positive: bool = True, height: int = 32, width: int = 120) -> str:
    """Generate an inline mini SVG sparkline curve for KPI ticker cards."""
    if not values or len(values) < 2:
        return ""
    min_v = min(values)
    max_v = max(values)
    rng = max_v - min_v if max_v != min_v else 1.0

    points = []
    w_step = width / (len(values) - 1)
    for i, v in enumerate(values):
        x = i * w_step
        y = height - 4 - ((v - min_v) / rng) * (height - 8)
        points.append(f"{x:.1f},{y:.1f}")

    pts_str = " ".join(points)
    color = COLOR_PALETTE["accent_green"] if is_positive else COLOR_PALETTE["negative_red"]
    fill_color = "rgba(0, 242, 169, 0.12)" if is_positive else "rgba(248, 113, 113, 0.12)"

    first_x = "0"
    last_x = f"{width}"
    area_pts = f"{pts_str} {last_x},{height} {first_x},{height}"

    raw_svg = f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
        <polygon points="{area_pts}" fill="{fill_color}"/>
        <polyline points="{pts_str}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>"""
    b64 = base64.b64encode(raw_svg.encode("utf-8")).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{b64}" style="width: {width}px; height: {height}px; display: block;" alt="sparkline" />'


def generate_full_width_sparkline_svg(values, is_positive: bool = True, height: int = 50, unique_id: str = "spark") -> str:
    """Generate a 100% width responsive SVG sparkline curve with gradient area fill matching Panel 1 mockup."""
    if not values or len(values) < 2:
        return ""
    min_v = min(values)
    max_v = max(values)
    rng = max_v - min_v if max_v != min_v else 1.0

    width = 300
    points = []
    w_step = width / (len(values) - 1)
    for i, v in enumerate(values):
        x = i * w_step
        y = (height - 6) - ((v - min_v) / rng) * (height - 14)
        points.append(f"{x:.1f},{y:.1f}")

    pts_str = " ".join(points)
    last_pt = points[-1].split(",")
    last_x, last_y = last_pt[0], last_pt[1]

    color = COLOR_PALETTE["accent_green"] if is_positive else COLOR_PALETTE["negative_red"]
    grad_id = f"grad_{unique_id}_{int(min_v)}"

    area_pts = f"0,{height} {pts_str} {width},{height}"

    raw_svg = f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" preserveAspectRatio="none" fill="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="{grad_id}" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="{color}" stop-opacity="0.32"/>
                <stop offset="100%" stop-color="{color}" stop-opacity="0.0"/>
            </linearGradient>
        </defs>
        <polygon points="{area_pts}" fill="url(#{grad_id})"/>
        <polyline points="{pts_str}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="{last_x}" cy="{last_y}" r="3.5" fill="{color}" />
    </svg>"""
    b64 = base64.b64encode(raw_svg.encode("utf-8")).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{b64}" style="width: 100%; height: {height}px; display: block; margin-top: 4px;" alt="sparkline" />'


def apply_custom_theme():
    """Inject the complete dark fintech terminal stylesheet."""
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Reset and global setup */
    * {{
        box-sizing: border-box;
    }}

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: {COLOR_PALETTE['text_primary']} !important;
        background-color: {COLOR_PALETTE['bg_main']} !important;
    }}

    .stApp {{
        background-color: {COLOR_PALETTE['bg_main']};
        background-image: radial-gradient(circle at 90% 10%, rgba(0, 242, 169, 0.05) 0%, transparent 45%),
                          radial-gradient(circle at 10% 90%, rgba(0, 210, 255, 0.04) 0%, transparent 45%);
    }}

    /* Hide standard Streamlit header clutter */
    header[data-testid="stHeader"] {{
        background: transparent !important;
        height: 0 !important;
        min-height: 0 !important;
    }}

    footer {{
        visibility: hidden;
    }}

    /* Remove Streamlit default top padding on main content area */
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }}

    /* Hide deploy button */
    .stDeployButton {{
        display: none !important;
    }}

    #MainMenu {{
        visibility: hidden;
    }}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        display: flex !important;
        visibility: visible !important;
        background-color: {COLOR_PALETTE['bg_sidebar']} !important;
        border-right: 1px solid {COLOR_PALETTE['border_teal']} !important;
    }}

    section[data-testid="stSidebar"] .block-container {{
        padding: 0.5rem 0.9rem !important;
    }}

    section[data-testid="stSidebar"] > div:first-child {{
        padding-top: 0.4rem !important;
    }}

    /* Sidebar Navigation Links */
    section[data-testid="stSidebar"] a {{
        border-radius: 8px !important;
        padding: 0.6rem 0.9rem !important;
        font-weight: 500 !important;
        color: #94a3b8 !important;
        transition: all 0.2s ease !important;
        margin-bottom: 4px !important;
    }}

    section[data-testid="stSidebar"] a:hover {{
        background: rgba(0, 242, 169, 0.08) !important;
        color: {COLOR_PALETTE['accent_green']} !important;
    }}

    section[data-testid="stSidebar"] a[aria-current="page"] {{
        background: linear-gradient(90deg, rgba(0, 242, 169, 0.18) 0%, rgba(11, 23, 31, 0.85) 100%) !important;
        border: 1px solid rgba(0, 242, 169, 0.4) !important;
        border-left: 4px solid #00f2a9 !important;
        color: #00f2a9 !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 16px rgba(0, 242, 169, 0.15) !important;
    }}

    section[data-testid="stSidebar"] a[aria-current="page"] span,
    section[data-testid="stSidebar"] a[aria-current="page"] p {{
        color: #00f2a9 !important;
        font-weight: 700 !important;
    }}

    /* High-Fidelity Cards */
    .quant-card {{
        background: {COLOR_PALETTE['bg_surface']};
        border: 1px solid {COLOR_PALETTE['border_teal']};
        border-radius: 10px;
        padding: 1.25rem 1.4rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.45);
        margin-bottom: 1rem;
        transition: border-color 0.25s ease, box-shadow 0.25s ease;
    }}

    .quant-card:hover {{
        border-color: rgba(0, 242, 169, 0.35);
        box-shadow: 0 6px 24px rgba(0, 242, 169, 0.06);
    }}

    .quant-card-compact {{
        background: {COLOR_PALETTE['bg_surface']};
        border: 1px solid {COLOR_PALETTE['border_teal']};
        border-radius: 8px;
        padding: 0.85rem 1.1rem;
        margin-bottom: 0.75rem;
    }}

    /* Ticker Card Split Containers for Sparkline */
    .ticker-card-top {{
        background: {COLOR_PALETTE['bg_surface']};
        border: 1px solid {COLOR_PALETTE['border_teal']};
        border-bottom: none;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        padding: 1.15rem 1.3rem 0.2rem 1.3rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.45);
    }}

    .ticker-card-bottom {{
        background: {COLOR_PALETTE['bg_surface']};
        border: 1px solid {COLOR_PALETTE['border_teal']};
        border-top: none;
        border-bottom-left-radius: 10px;
        border-bottom-right-radius: 10px;
        margin-top: -6px;
        margin-bottom: 0.6rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.45);
        overflow: hidden;
    }}

    /* Welcome Banner matching Reference Screen 1 */
    .quant-welcome-banner {{
        background: linear-gradient(135deg, #0d1a24 0%, #08121a 100%);
        border: 1px solid {COLOR_PALETTE['border_teal']};
        border-radius: 12px;
        padding: 1.4rem 1.8rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }}

    .quant-welcome-banner::after {{
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 300px;
        height: 100%;
        background: radial-gradient(circle at 100% 50%, rgba(0, 242, 169, 0.1) 0%, transparent 70%);
        pointer-events: none;
    }}

    /* Monospace Typography for Numbers */
    .quant-val {{
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1.7rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }}

    .quant-val-small {{
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1.25rem;
        font-weight: 700;
        color: #ffffff;
    }}

    .quant-label {{
        font-size: 0.76rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: {COLOR_PALETTE['text_muted']};
        margin-bottom: 0.35rem;
    }}

    .quant-delta-pos {{
        color: {COLOR_PALETTE['accent_green']} !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.88rem;
        font-weight: 600;
    }}

    .quant-delta-neg {{
        color: {COLOR_PALETTE['negative_red']} !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.88rem;
        font-weight: 600;
    }}

    /* Pulsing Live Dot */
    .pulse-dot {{
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: {COLOR_PALETTE['accent_green']};
        box-shadow: 0 0 8px {COLOR_PALETTE['accent_green']};
        margin-right: 6px;
        animation: pulse 1.8s infinite;
    }}

    @keyframes pulse {{
        0% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.4; transform: scale(0.85); }}
        100% {{ opacity: 1; transform: scale(1); }}
    }}

    /* Badges */
    .quant-badge {{
        display: inline-flex;
        align-items: center;
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }}

    .quant-badge-green {{
        background: rgba(0, 242, 169, 0.12);
        color: {COLOR_PALETTE['accent_green']};
        border: 1px solid rgba(0, 242, 169, 0.3);
    }}

    .quant-badge-teal {{
        background: rgba(56, 189, 248, 0.12);
        color: {COLOR_PALETTE['accent_cyan']};
        border: 1px solid rgba(56, 189, 248, 0.3);
    }}

    .quant-badge-red {{
        background: rgba(248, 113, 113, 0.12);
        color: {COLOR_PALETTE['negative_red']};
        border: 1px solid rgba(248, 113, 113, 0.3);
    }}

    /* Buttons */
    .stButton>button {{
        background: #0f1c26 !important;
        color: #ffffff !important;
        border: 1px solid {COLOR_PALETTE['border_teal']} !important;
        border-radius: 7px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.45rem 1.2rem !important;
        transition: all 0.2s ease !important;
    }}

    .stButton>button:hover {{
        border-color: {COLOR_PALETTE['accent_green']} !important;
        color: {COLOR_PALETTE['accent_green']} !important;
        box-shadow: 0 0 12px rgba(0, 242, 169, 0.25) !important;
    }}

    .stButton>button[kind="primary"] {{
        background: linear-gradient(135deg, #00f2a9 0%, #00c78a 100%) !important;
        color: #041210 !important;
        border: none !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 14px rgba(0, 242, 169, 0.35) !important;
    }}

    .stButton>button[kind="primary"]:hover {{
        background: linear-gradient(135deg, #2bf9bc 0%, #03dc9a 100%) !important;
        box-shadow: 0 4px 20px rgba(0, 242, 169, 0.5) !important;
        color: #000000 !important;
    }}

    /* Quick Action Button Overrides (multi-line pre-wrap without truncation) */
    div[data-testid="column"] .stButton > button {{
        white-space: pre-wrap !important;
        word-break: break-word !important;
        height: auto !important;
        min-height: 82px !important;
        padding: 0.75rem 0.45rem !important;
        text-align: center !important;
        border-radius: 9px !important;
        background: #0b1319 !important;
        border: 1px solid #142834 !important;
    }}

    div[data-testid="column"] .stButton > button:hover {{
        border-color: #00f2a9 !important;
        background: #0e1922 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 242, 169, 0.2) !important;
    }}

    div[data-testid="column"] .stButton > button p {{
        font-size: 0.74rem !important;
        line-height: 1.35 !important;
        margin: 0 !important;
        white-space: pre-wrap !important;
        word-break: break-word !important;
    }}

    /* Quick Action Page Links */
    div[data-testid="column"] a[data-testid="stPageLink-NavLink"] {{
        background: #0b1319 !important;
        border: 1px solid #142834 !important;
        border-radius: 9px !important;
        padding: 0.8rem 0.5rem !important;
        text-align: center !important;
        justify-content: center !important;
        min-height: 56px !important;
        transition: all 0.2s ease !important;
        text-decoration: none !important;
    }}

    div[data-testid="column"] a[data-testid="stPageLink-NavLink"]:hover {{
        border-color: #00f2a9 !important;
        background: #0e1922 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 242, 169, 0.2) !important;
    }}

    div[data-testid="column"] a[data-testid="stPageLink-NavLink"] span,
    div[data-testid="column"] a[data-testid="stPageLink-NavLink"] p {{
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: #ffffff !important;
        white-space: normal !important;
    }}

    /* Input controls */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {{
        background-color: #091218 !important;
        border: 1px solid {COLOR_PALETTE['border_teal']} !important;
        border-radius: 7px !important;
        color: #ffffff !important;
    }}

    div[data-baseweb="select"] > div:hover, div[data-baseweb="input"] > div:hover {{
        border-color: {COLOR_PALETTE['border_teal_hover']} !important;
    }}

    /* Tab navigation pills */
    .stTabs [data-baseweb="tab-list"] {{
        border-bottom: 1px solid {COLOR_PALETTE['border_teal']};
        gap: 8px;
    }}

    .stTabs [data-baseweb="tab"] {{
        padding: 7px 16px;
        color: {COLOR_PALETTE['text_muted']} !important;
        font-weight: 600;
        font-size: 0.88rem;
    }}

    .stTabs [aria-selected="true"] {{
        color: {COLOR_PALETTE['accent_green']} !important;
        border-bottom: 2px solid {COLOR_PALETTE['accent_green']} !important;
    }}

    /* Quick Action Cards matching Mockup */
    .quick-action-card {{
        background: #0b1319;
        border: 1px solid {COLOR_PALETTE['border_teal']};
        border-radius: 9px;
        padding: 0.9rem 1rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }}

    .quick-action-card:hover {{
        border-color: {COLOR_PALETTE['accent_green']};
        background: #0e1922;
        transform: translateY(-2px);
    }}

    /* Page Links in Quick Actions matching Image 2 */
    a[data-testid="stPageLink-NavLink"] {{
        background: #0b141c !important;
        border: 1px solid rgba(0, 242, 169, 0.22) !important;
        border-radius: 8px !important;
        padding: 0.9rem 0.5rem !important;
        color: #ffffff !important;
        transition: all 0.22s ease !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        text-decoration: none !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35) !important;
        min-height: 68px !important;
        gap: 6px !important;
        text-align: center !important;
    }}

    a[data-testid="stPageLink-NavLink"]:hover {{
        background: #10212c !important;
        border-color: {COLOR_PALETTE['accent_green']} !important;
        box-shadow: 0 6px 20px rgba(0, 242, 169, 0.25) !important;
        transform: translateY(-2px) !important;
    }}

    a[data-testid="stPageLink-NavLink"] p,
    a[data-testid="stPageLink-NavLink"] span {{
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        color: #cbd5e1 !important;
        margin: 0 !important;
        white-space: normal !important;
        overflow: visible !important;
        text-align: center !important;
        line-height: 1.25 !important;
    }}

    a[data-testid="stPageLink-NavLink"]:hover p,
    a[data-testid="stPageLink-NavLink"]:hover span {{
        color: #00f2a9 !important;
    }}

    /* Glassy Search Bar Container */
    div[data-testid="stForm"]:has(input[aria-label="Search assets"]),
    div[data-testid="stForm"]:has(input[placeholder*="Search assets"]) {{
        background: rgba(13, 23, 33, 0.6) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
        border: 1px solid rgba(0, 242, 169, 0.25) !important;
        border-radius: 28px !important;
        padding: 3px 5px 3px 14px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.45), inset 0 1px 1px rgba(255, 255, 255, 0.08) !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}

    div[data-testid="stForm"]:has(input[aria-label="Search assets"]):hover,
    div[data-testid="stForm"]:has(input[aria-label="Search assets"]):focus-within,
    div[data-testid="stForm"]:has(input[placeholder*="Search assets"]):hover,
    div[data-testid="stForm"]:has(input[placeholder*="Search assets"]):focus-within {{
        border-color: rgba(0, 242, 169, 0.6) !important;
        background: rgba(15, 28, 40, 0.72) !important;
        box-shadow: 0 4px 28px rgba(0, 242, 169, 0.25), inset 0 1px 2px rgba(255, 255, 255, 0.15) !important;
    }}

    /* Inner input in glassy search bar */
    div[data-testid="stForm"]:has(input[aria-label="Search assets"]) div[data-baseweb="input"] > div,
    div[data-testid="stForm"]:has(input[placeholder*="Search assets"]) div[data-baseweb="input"] > div {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        height: 38px !important;
        min-height: 38px !important;
    }}

    div[data-testid="stForm"]:has(input[aria-label="Search assets"]) input,
    div[data-testid="stForm"]:has(input[placeholder*="Search assets"]) input {{
        background: transparent !important;
        color: #ffffff !important;
        font-size: 0.88rem !important;
        font-family: 'Inter', sans-serif !important;
    }}

    div[data-testid="stForm"]:has(input[aria-label="Search assets"]) input::placeholder,
    div[data-testid="stForm"]:has(input[placeholder*="Search assets"]) input::placeholder {{
        color: #7e92a2 !important;
    }}

    /* Glassy Search Button */
    div[data-testid="stForm"]:has(input[aria-label="Search assets"]) .stButton > button,
    div[data-testid="stForm"]:has(input[placeholder*="Search assets"]) .stButton > button {{
        min-height: 36px !important;
        height: 36px !important;
        border-radius: 20px !important;
        background: linear-gradient(135deg, #00f2a9 0%, #00c78a 100%) !important;
        color: #041210 !important;
        font-weight: 700 !important;
        font-size: 0.82rem !important;
        border: none !important;
        box-shadow: 0 2px 12px rgba(0, 242, 169, 0.35) !important;
        padding: 0 18px !important;
        transition: all 0.2s ease !important;
    }}

    div[data-testid="stForm"]:has(input[aria-label="Search assets"]) .stButton > button:hover,
    div[data-testid="stForm"]:has(input[placeholder*="Search assets"]) .stButton > button:hover {{
        background: linear-gradient(135deg, #2bf9bc 0%, #03dc9a 100%) !important;
        box-shadow: 0 4px 20px rgba(0, 242, 169, 0.55) !important;
        transform: translateY(-1px) !important;
        color: #000000 !important;
    }}


    /* Actions Cluster Container (Notification + Help icon buttons) */
    .st-key-dash_actions_cluster {{
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-end !important;
        gap: 10px !important;
    }}

    /* ── Notification Bell Icon Button (supports st.button and st.popover) ── */
    .st-key-notif_bell_btn button,
    .st-key-notif_bell_btn div[data-testid="stPopoverButton"] > button {{
        min-height: 40px !important;
        height: 40px !important;
        width: 40px !important;
        border-radius: 50% !important;
        background: rgba(13, 23, 33, 0.65) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
        position: relative !important;
        transition: all 0.2s ease !important;
    }}

    .st-key-notif_bell_btn button:hover,
    .st-key-notif_bell_btn div[data-testid="stPopoverButton"] > button:hover {{
        border-color: #00f2a9 !important;
        box-shadow: 0 0 16px rgba(0, 242, 169, 0.4) !important;
        transform: translateY(-1px) !important;
    }}

    .st-key-notif_bell_btn button span[data-testid="stIconMaterial"],
    .st-key-notif_bell_btn div[data-testid="stPopoverButton"] button span[data-testid="stIconMaterial"] {{
        color: #ffffff !important;
        font-size: 1.3rem !important;
    }}

    /* Green badge "4" on notification bell */
    .st-key-notif_bell_btn button::after,
    .st-key-notif_bell_btn div[data-testid="stPopoverButton"] > button::after {{
        content: "4";
        position: absolute;
        top: -2px;
        right: -2px;
        width: 17px;
        height: 17px;
        background: #10b981;
        color: #ffffff;
        font-size: 0.62rem;
        font-weight: 800;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 6px rgba(16, 185, 129, 0.8);
        border: 1.5px solid #060a0e;
        pointer-events: none;
    }}

    /* ── Help Icon Button (supports st.button and st.popover) ── */
    .st-key-help_icon_btn button,
    .st-key-help_icon_btn div[data-testid="stPopoverButton"] > button {{
        min-height: 40px !important;
        height: 40px !important;
        width: 40px !important;
        border-radius: 50% !important;
        background: rgba(13, 23, 33, 0.65) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
        transition: all 0.2s ease !important;
    }}

    .st-key-help_icon_btn button:hover,
    .st-key-help_icon_btn div[data-testid="stPopoverButton"] > button:hover {{
        border-color: #00f2a9 !important;
        box-shadow: 0 0 16px rgba(0, 242, 169, 0.4) !important;
        transform: translateY(-1px) !important;
    }}

    .st-key-help_icon_btn button span[data-testid="stIconMaterial"],
    .st-key-help_icon_btn div[data-testid="stPopoverButton"] button span[data-testid="stIconMaterial"] {{
        color: #ffffff !important;
        font-size: 1.3rem !important;
    }}

    /* ── Popover Body Container Styling ── */
    div[data-testid="stPopoverBody"] {{
        background: #0b151e !important;
        border: 1px solid rgba(0, 242, 169, 0.28) !important;
        border-radius: 14px !important;
        box-shadow: 0 18px 45px rgba(0, 0, 0, 0.75), 0 0 20px rgba(0, 242, 169, 0.12) !important;
        padding: 16px 18px !important;
        color: #e2e8f0 !important;
    }}

    /* Bottom Terminal Brand Footer matching Mockup */
    .quant-bottom-bar {{
        margin-top: 1rem;
        padding: 1.2rem 1.6rem;
        background: #080e14;
        border-top: 1px solid {COLOR_PALETTE['border_teal']};
        border-radius: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

