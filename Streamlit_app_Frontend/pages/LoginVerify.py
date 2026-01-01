import streamlit as st
import requests
import time

# -----------------------------------
# PAGE CONFIG + HIDE SIDEBAR
# -----------------------------------
st.set_page_config(
    page_title="Verifying Login - AI Content Studio",
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
# CONFIG
# -----------------------------------
API_BASE = "https://infosys-internship-backend.onrender.com"

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

    /* ===== LOADING SPINNER ===== */
    .loading-container {
        text-align: center;
        padding: 2rem 0;
    }

    .spinner {
        display: inline-block;
        width: 50px;
        height: 50px;
        border: 4px solid rgba(99, 102, 241, 0.2);
        border-top: 4px solid #6366f1;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 1rem;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .loading-text {
        color: #d1d5db;
        font-size: 16px;
        font-weight: 500;
        margin-top: 1rem;
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

    /* ===== STATUS ICONS ===== */
    .status-icon {
        font-size: 3rem;
        margin: 1rem 0;
        text-align: center;
    }

    .success-icon {
        animation: successPop 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }

    @keyframes successPop {
        0% { transform: scale(0); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
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
    </style>
""", unsafe_allow_html=True)

# -----------------------------------
# CUSTOM HEADER
# -----------------------------------
st.markdown("""
    <div class="verification-header">
        <div class="verification-logo">🔐</div>
        <h1 class="verification-title">Secure Login Verification</h1>
        <p class="verification-subtitle">Please wait while we verify your identity</p>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------
# VERIFICATION CARD
# -----------------------------------
st.markdown('<div class="verification-card">', unsafe_allow_html=True)

# -----------------------------------
# TOKEN HANDLING
# -----------------------------------
token = st.query_params.get("token")

if not token:
    st.markdown('<div class="status-icon">❌</div>', unsafe_allow_html=True)
    st.error("❌ The login link is invalid or incomplete")
    st.warning("⚠️ Please request a new login link from the login page")
    
    st.markdown("---")
    
    if st.button("← Back to Login", key="back_to_login", type="secondary"):
        st.switch_page("pages/Login.py")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# -----------------------------------
# LOADING STATE
# -----------------------------------
st.markdown("""
    <div class="loading-container">
        <div class="spinner"></div>
        <p class="loading-text">Verifying your login credentials...</p>
    </div>
""", unsafe_allow_html=True)

st.caption("This should only take a moment")

# -----------------------------------
# VERIFY LOGIN TOKEN
# -----------------------------------
try:
    with st.spinner("🔒 Authenticating..."):
        res = requests.get(
            f"{API_BASE}/login/verify",
            params={"token": token},
            timeout=10
        )

    if res.status_code == 200:
        data = res.json()

        # Store credentials
        st.session_state["jwt"] = data["jwt"]
        st.session_state["email"] = data["email"]

        # Success state
        st.markdown('<div class="status-icon success-icon">✅</div>', unsafe_allow_html=True)
        st.success("✅ Authentication successful!")
        st.info(f"📧 Welcome back, {data['email']}!")

        st.markdown("""
            <div class="benefits-list">
                <div class="benefit-item">
                    <span class="benefit-icon">✓</span>
                    <span>Identity verified securely</span>
                </div>
                <div class="benefit-item">
                    <span class="benefit-icon">✓</span>
                    <span>Session created successfully</span>
                </div>
                <div class="benefit-item">
                    <span class="benefit-icon">✓</span>
                    <span>Redirecting to your workspace...</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Auto-redirect after brief delay
        time.sleep(2)
        st.switch_page("pages/Content_Studio.py")

    else:
        # Error state
        st.markdown('<div class="status-icon">❌</div>', unsafe_allow_html=True)
        error_msg = res.json().get("detail", "Login verification failed")
        st.error(f"❌ {error_msg}")
        st.warning("⚠️ Your login link may have expired or is invalid")

        st.markdown("---")
        
        if st.button("← Try Again", key="retry_login", type="secondary"):
            st.switch_page("pages/Login.py")

except requests.exceptions.Timeout:
    st.markdown('<div class="status-icon">⏱️</div>', unsafe_allow_html=True)
    st.error("⏱️ Request timed out. Please try again.")
    
    if st.button("← Back to Login", key="timeout_login", type="secondary"):
        st.switch_page("pages/Login.py")

except requests.exceptions.ConnectionError:
    st.markdown('<div class="status-icon">🌐</div>', unsafe_allow_html=True)
    st.error("🌐 Unable to connect to the service. Check your connection.")
    
    if st.button("← Back to Login", key="connection_login", type="secondary"):
        st.switch_page("pages/Login.py")

except requests.exceptions.RequestException:
    st.markdown('<div class="status-icon">❌</div>', unsafe_allow_html=True)
    st.error("❌ Unable to connect to the authentication service. Please try again later.")
    
    if st.button("← Back to Login", key="error_login", type="secondary"):
        st.switch_page("pages/Login.py")

st.markdown('</div>', unsafe_allow_html=True)