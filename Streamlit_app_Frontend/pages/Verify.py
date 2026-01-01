import streamlit as st
from urllib.parse import unquote
import time

# -----------------------------------
# PAGE CONFIG + HIDE SIDEBAR
# -----------------------------------
st.set_page_config(
    page_title="Verification - AI Content Studio",
    page_icon="✨",
    layout="wide"
)

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="stSidebarNav"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------
# MODERN STYLING (SAME AS REGISTER)
# -----------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* ===== GLOBAL RESET ===== */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    html, body, [data-testid="stApp"] {
        background: linear-gradient(135deg, #1a1d29 0%, #0f1117 100%);
        color: #e5e7eb;
    }

    /* ===== MAIN CONTAINER ===== */
    .block-container {
        background-color: transparent;
        padding-top: 4rem;
        max-width: 520px;
        margin: 0 auto;
    }

    /* ===== HIDE DEFAULT HEADERS ===== */
    header[data-testid="stHeader"] {
        display: none;
    }

    /* ===== CUSTOM LOGO/TITLE ===== */
    .verification-header {
        text-align: center;
        margin-bottom: 2.5rem;
    }

    .verification-logo {
        font-size: 3rem;
        margin-bottom: 1rem;
        animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.05); opacity: 0.9; }
    }

    .verification-title {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #a5b4fc 0%, #c4b5fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }

    .verification-subtitle {
        color: #9ca3af;
        font-size: 1rem;
        font-weight: 400;
        letter-spacing: 0.01em;
    }

    /* ===== VERIFICATION CARD ===== */
    .verification-card {
        background: rgba(31, 41, 55, 0.5);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
        animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* ===== STATUS ICONS ===== */
    .status-icon {
        font-size: 4rem;
        margin: 1.5rem 0;
        text-align: center;
    }

    .success-icon {
        animation: successPop 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }

    .error-icon {
        animation: shake 0.5s ease-in-out;
    }

    @keyframes successPop {
        0% { transform: scale(0) rotate(-180deg); }
        50% { transform: scale(1.2) rotate(10deg); }
        100% { transform: scale(1) rotate(0deg); }
    }

    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }

    /* ===== PRIMARY BUTTON ===== */
    .stButton button[kind="primary"],
    .stButton button:not([kind="secondary"]) {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 16px 32px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important;
        letter-spacing: 0.02em !important;
        margin-top: 1rem !important;
    }

    .stButton button[kind="primary"]:hover,
    .stButton button:not([kind="secondary"]):hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(99, 102, 241, 0.5) !important;
    }

    .stButton button[kind="primary"]:active,
    .stButton button:not([kind="secondary"]):active {
        transform: translateY(0) !important;
    }

    /* ===== SECONDARY BUTTONS ===== */
    .stButton button[kind="secondary"] {
        background: rgba(99, 102, 241, 0.1) !important;
        color: #a5b4fc !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        border-radius: 12px !important;
        padding: 14px 28px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        margin-top: 0.5rem !important;
    }

    .stButton button[kind="secondary"]:hover {
        background: rgba(99, 102, 241, 0.15) !important;
        border-color: rgba(99, 102, 241, 0.5) !important;
        transform: translateY(-1px) !important;
    }

    /* ===== ALERTS/MESSAGES ===== */
    .stAlert {
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(10px) !important;
        margin-top: 1rem !important;
        animation: slideIn 0.4s ease-out;
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-10px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    /* ===== CAPTIONS ===== */
    .caption, [data-testid="stCaptionContainer"] {
        color: #9ca3af !important;
        font-size: 14px !important;
        text-align: center !important;
        letter-spacing: 0.01em !important;
    }

    /* ===== DIVIDER ===== */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        margin: 2rem 0 1.5rem 0;
    }

    /* ===== BENEFITS LIST ===== */
    .benefits-list {
        background: rgba(17, 24, 39, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
    }

    .benefit-item {
        display: flex;
        align-items: center;
        gap: 12px;
        color: #d1d5db;
        font-size: 14px;
        margin-bottom: 12px;
    }

    .benefit-item:last-child {
        margin-bottom: 0;
    }

    .benefit-icon {
        font-size: 18px;
    }

    /* ===== PROGRESS INDICATOR ===== */
    .progress-dots {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin: 1.5rem 0;
    }

    .progress-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: rgba(99, 102, 241, 0.3);
        animation: pulse-dot 1.5s ease-in-out infinite;
    }

    .progress-dot:nth-child(2) {
        animation-delay: 0.3s;
    }

    .progress-dot:nth-child(3) {
        animation-delay: 0.6s;
    }

    @keyframes pulse-dot {
        0%, 100% { transform: scale(1); opacity: 0.3; }
        50% { transform: scale(1.5); opacity: 1; }
    }
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
    st.markdown("""
        <div class="verification-header">
            <div class="verification-logo">✅</div>
            <h1 class="verification-title">Email Verified</h1>
            <p class="verification-subtitle">Your account is now active</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="verification-card">', unsafe_allow_html=True)
    
    st.markdown('<div class="status-icon success-icon">🎉</div>', unsafe_allow_html=True)
    
    st.success("✅ Your email address has been successfully verified!")
    st.info("🔓 Your account is now fully activated and ready to use")
    
    st.markdown("""
        <div class="benefits-list">
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

    st.caption("You can now log in and access all features")

    if st.button("→ Proceed to Login", key="proceed_login", type="primary"):
        st.switch_page("pages/Login.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------
# LOGIN VERIFICATION SUCCESS
# -----------------------------------
elif "jwt" in params:
    st.session_state["jwt"] = unquote(params["jwt"])
    st.session_state["email"] = params.get("email")

    st.markdown("""
        <div class="verification-header">
            <div class="verification-logo">🔐</div>
            <h1 class="verification-title">Login Successful</h1>
            <p class="verification-subtitle">Welcome back to AI Content Studio</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="verification-card">', unsafe_allow_html=True)
    
    st.markdown('<div class="status-icon success-icon">✅</div>', unsafe_allow_html=True)
    
    st.success("✅ You have been logged in successfully!")
    
    if st.session_state.get("email"):
        st.info(f"📧 Logged in as: {st.session_state['email']}")
    
    st.markdown("""
        <div class="benefits-list">
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

    st.caption("Please wait while we prepare your workspace")

    # Auto-redirect after brief delay
    time.sleep(2)
    st.switch_page("pages/Content_Studio.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------
# INVALID / EXPIRED LINK
# -----------------------------------
else:
    st.markdown("""
        <div class="verification-header">
            <div class="verification-logo">⚠️</div>
            <h1 class="verification-title">Invalid Link</h1>
            <p class="verification-subtitle">Unable to verify your request</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="verification-card">', unsafe_allow_html=True)
    
    st.markdown('<div class="status-icon error-icon">❌</div>', unsafe_allow_html=True)
    
    st.error("❌ This verification link is invalid or has expired")
    st.warning("⚠️ Verification links are valid for a limited time only")
    
    st.markdown("""
        <div class="benefits-list">
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

    st.caption("Need help? Try requesting a new link or logging in again")

    st.markdown("---")

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Back to Login", key="back_login", type="secondary"):
            st.switch_page("pages/Login.py")
    
    with col2:
        if st.button("Create Account →", key="back_register", type="secondary"):
            st.switch_page("pages/Register.py")
    
    st.markdown('</div>', unsafe_allow_html=True)