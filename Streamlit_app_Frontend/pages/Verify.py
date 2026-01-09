import streamlit as st
from urllib.parse import unquote
import time
import os
import base64

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="Verification - AI Content Studio",
    page_icon="✨",
    layout="wide"
)

# -----------------------------------
# THEME COLORS (DARK MODE ONLY)
# -----------------------------------
theme_colors = {
    "bg_primary": "#0f1117",
    "bg_secondary": "#1a1d29",
    "bg_tertiary": "#13151f",
    "bg_card": "rgba(31, 41, 55, 0.4)",
    "bg_card_hover": "rgba(31, 41, 55, 0.6)",
    "border_color": "rgba(255, 255, 255, 0.08)",
    "border_hover": "rgba(139, 92, 246, 0.3)",
    "text_primary": "#e5e7eb",
    "text_secondary": "#9ca3af",
    "text_tertiary": "#6b7280",
    "text_accent": "#c4b5fd",
    "input_bg": "rgba(31, 41, 55, 0.5)",
}

# -----------------------------------
# MODERN UNIFIED STYLING - MATCHING CONTENT STUDIO
# -----------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {{
    font-family: 'Inter', -apple-system, sans-serif;
    transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}}

/* THEME BASE */
html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"] {{
    background: {theme_colors['bg_primary']} !important;
    color: {theme_colors['text_primary']} !important;
}}

/* HIDE SIDEBAR & HEADER */
[data-testid="stSidebar"] {{ display: none !important; }}
[data-testid="stSidebarNav"] {{ display: none !important; }}
header[data-testid="stHeader"] {{ display: none !important; }}

.block-container {{
    max-width: 540px;
    padding-top: 4rem;
    margin: auto;
}}

/* VERIFICATION CARD - MATCHING CONTENT STUDIO STYLE */
.verify-box {{
    background: {theme_colors['bg_card']};
    backdrop-filter: blur(20px);
    border: 1px solid {theme_colors['border_color']};
    border-radius: 16px;
    padding: 2.5rem;
    margin-bottom: 1.5rem;
    transition: all 0.3s ease;
    animation: fadeInUp 0.6s ease;
}}

.verify-box:hover {{
    border-color: {theme_colors['border_hover']};
    box-shadow: 0 8px 30px rgba(139, 92, 246, 0.15);
    background: {theme_colors['bg_card_hover']};
}}

@keyframes fadeInUp {{
    from {{
        opacity: 0;
        transform: translateY(20px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

/* HEADER */
.verify-header {{
    text-align: center;
    margin-bottom: 2rem;
}}

.verify-icon {{
    font-size: 3rem;
    margin-bottom: 1rem;
}}

.verify-title {{
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #c4b5fd 0%, #a78bfa 50%, #8b5cf6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.5rem 0;
}}

.verify-subtitle {{
    color: {theme_colors['text_secondary']};
    font-size: 0.95rem;
    margin-bottom: 2rem;
}}

/* STATUS ICONS */
.status-icon {{
    font-size: 4rem;
    text-align: center;
    margin: 1.5rem 0;
}}

.success-icon {{
    animation: successPop 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}}

.error-icon {{
    animation: shake 0.5s ease-in-out;
}}

@keyframes successPop {{
    0% {{ transform: scale(0) rotate(-180deg); }}
    50% {{ transform: scale(1.2) rotate(10deg); }}
    100% {{ transform: scale(1) rotate(0deg); }}
}}

@keyframes shake {{
    0%, 100% {{ transform: translateX(0); }}
    25% {{ transform: translateX(-10px); }}
    75% {{ transform: translateX(10px); }}
}}

/* UNIFIED GRADIENT BUTTONS - MATCHING CONTENT STUDIO */
.stButton button, .stDownloadButton button {{
    background: linear-gradient(135deg, #a78bfa 0%, #ec4899 50%, #f97316 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.85rem 2rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(167, 139, 250, 0.3) !important;
    width: 100%;
    margin-top: 0.5rem !important;
}}

.stButton button:hover, .stDownloadButton button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(167, 139, 250, 0.5) !important;
    filter: brightness(1.1) !important;
}}

.stButton button:active, .stDownloadButton button:active {{
    transform: translateY(0) !important;
}}

/* BENEFITS CARD */
.benefits-card {{
    background: {theme_colors['bg_card']};
    border: 1px solid {theme_colors['border_color']};
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1.5rem 0;
}}

.benefit-item {{
    display: flex;
    align-items: center;
    gap: 12px;
    color: {theme_colors['text_secondary']};
    font-size: 0.9rem;
    margin-bottom: 12px;
    padding: 8px 0;
}}

.benefit-item:last-child {{
    margin-bottom: 0;
}}

.benefit-icon {{
    font-size: 18px;
    min-width: 24px;
}}

/* PROGRESS INDICATOR */
.progress-dots {{
    display: flex;
    justify-content: center;
    gap: 10px;
    margin: 1.5rem 0;
}}

.progress-dot {{
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: rgba(139, 92, 246, 0.4);
    animation: pulse-dot 1.5s ease-in-out infinite;
}}

.progress-dot:nth-child(2) {{
    animation-delay: 0.3s;
}}

.progress-dot:nth-child(3) {{
    animation-delay: 0.6s;
}}

@keyframes pulse-dot {{
    0%, 100% {{ transform: scale(1); opacity: 0.4; }}
    50% {{ transform: scale(1.5); opacity: 1; background: #8b5cf6; }}
}}

/* SUCCESS/WARNING/ERROR MESSAGES */
.stSuccess, .stInfo, .stWarning, .stError {{
    background: {theme_colors['bg_card']} !important;
    border-radius: 12px !important;
    border-left: 4px solid #8b5cf6 !important;
}}

.stSuccess {{
    background: rgba(34, 197, 94, 0.15) !important;
    border-left-color: #22c55e !important;
}}

.stWarning {{
    background: rgba(251, 191, 36, 0.15) !important;
    border-left-color: #fbbf24 !important;
}}

.stError {{
    background: rgba(239, 68, 68, 0.15) !important;
    border-left-color: #ef4444 !important;
}}

.stInfo {{
    background: rgba(59, 130, 246, 0.15) !important;
    border-left-color: #3b82f6 !important;
}}

/* CAPTION */
.caption {{
    text-align: center;
    color: {theme_colors['text_secondary']};
    font-size: 0.9rem;
    margin-top: 1rem;
}}

/* DIVIDER */
hr {{
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.3), transparent);
    margin: 2rem 0;
}}

/* SCROLLBAR */
::-webkit-scrollbar {{
    width: 10px;
    height: 10px;
}}

::-webkit-scrollbar-track {{
    background: rgba(31, 41, 55, 0.3);
}}

::-webkit-scrollbar-thumb {{
    background: rgba(139, 92, 246, 0.5);
    border-radius: 5px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: rgba(139, 92, 246, 0.7);
}}

/* HIDE STREAMLIT BRANDING */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# QUERY PARAMS
# -----------------------------------
params = st.query_params

# -----------------------------------
# EMAIL VERIFICATION SUCCESS
# -----------------------------------
if params.get("status") == "verified":
    st.markdown('<div class="verify-box">', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="verify-header">
            <div class="status-icon success-icon">🎉</div>
            <div class="verify-title">Email Verified</div>
            <div class="verify-subtitle">Your account is now active</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.success("✅ Your email address has been successfully verified!")
    st.info("🔓 Your account is now fully activated and ready to use")
    
    st.markdown("""
        <div class="benefits-card">
            <div class="benefit-item">
                <span class="benefit-icon">✓</span>
                <span>Email verified successfully</span>
            </div>
            <div class="benefit-item">
                <span class="benefit-icon">✓</span>
                <span>Account activated</span>
            </div>
            <div class="benefit-item">
                <span class="benefit-icon">✓</span>
                <span>Ready to start creating</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="caption">You can now log in and access all features</div>', unsafe_allow_html=True)

    if st.button("→ Proceed to Login", key="proceed_login"):
        st.switch_page("pages/Login.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------
# LOGIN VERIFICATION SUCCESS
# -----------------------------------
elif "jwt" in params:
    st.session_state["jwt"] = unquote(params["jwt"])
    st.session_state["email"] = params.get("email")
    
    st.markdown("""
        <div class="verify-header">
            <div class="status-icon success-icon">✅</div>
            <div class="verify-title">Login Successful</div>
            <div class="verify-subtitle">Welcome back to AI Content Studio</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.success("✅ You have been logged in successfully!")
    
    if st.session_state.get("email"):
        st.info(f"📧 Logged in as: {st.session_state['email']}")
    
    st.markdown("""
        <div class="benefits-card">
            <div class="benefit-item">
                <span class="benefit-icon">✓</span>
                <span>Authentication complete</span>
            </div>
            <div class="benefit-item">
                <span class="benefit-icon">✓</span>
                <span>Session created</span>
            </div>
            <div class="benefit-item">
                <span class="benefit-icon">✓</span>
                <span>Redirecting to workspace...</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="progress-dots">
            <div class="progress-dot"></div>
            <div class="progress-dot"></div>
            <div class="progress-dot"></div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="caption">Please wait while we prepare your workspace</div>', unsafe_allow_html=True)

    # Auto-redirect after brief delay
    time.sleep(2)
    st.switch_page("pages/Content_Studio.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------
# INVALID / EXPIRED LINK
# -----------------------------------
else:
    st.markdown('<div class="verify-box">', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="verify-header">
            <div class="status-icon error-icon">❌</div>
            <div class="verify-title">Invalid Link</div>
            <div class="verify-subtitle">Unable to verify your request</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.error("❌ This verification link is invalid or has expired")
    st.warning("⚠️ Verification links are valid for a limited time only")
    
    st.markdown("""
        <div class="benefits-card">
            <div class="benefit-item">
                <span class="benefit-icon">ℹ️</span>
                <span>Request a new verification link</span>
            </div>
            <div class="benefit-item">
                <span class="benefit-icon">ℹ️</span>
                <span>Check your email for the latest link</span>
            </div>
            <div class="benefit-item">
                <span class="benefit-icon">ℹ️</span>
                <span>Contact support if issues persist</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="caption">Need help? Try requesting a new link or logging in again</div>', unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Back to Login", key="back_login"):
            st.switch_page("pages/Login.py")
    
    with col2:
        if st.button("Create Account →", key="back_register"):
            st.switch_page("pages/Register.py")
    
    st.markdown('</div>', unsafe_allow_html=True)










