import streamlit as st
import requests

# -----------------------------------
# PAGE CONFIG + HIDE SIDEBAR
# -----------------------------------
st.set_page_config(
    page_title="Register - AI Content Studio",
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
# MODERN STYLING
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
    .register-header {
        text-align: center;
        margin-bottom: 2.5rem;
    }

    .register-logo {
        font-size: 3rem;
        margin-bottom: 1rem;
        animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.05); opacity: 0.9; }
    }

    .register-title {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #a5b4fc 0%, #c4b5fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }

    .register-subtitle {
        color: #9ca3af;
        font-size: 1rem;
        font-weight: 400;
        letter-spacing: 0.01em;
    }

    /* ===== REGISTER CARD ===== */
    .register-card {
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

    /* ===== INPUT FIELDS ===== */
    .stTextInput > div > div > input {
        background: rgba(17, 24, 39, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #e5e7eb !important;
        padding: 16px 18px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: rgba(99, 102, 241, 0.6) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15), 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        outline: none !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #6b7280 !important;
    }

    /* ===== LABELS ===== */
    .stTextInput > label {
        color: #d1d5db !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        margin-bottom: 8px !important;
        letter-spacing: 0.01em !important;
    }

    /* ===== PRIMARY BUTTON (Register) ===== */
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

    /* ===== SECONDARY BUTTONS (Navigation) ===== */
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

    /* ===== FOOTER SECTION ===== */
    .register-footer {
        text-align: center;
        margin-top: 2rem;
    }

    .footer-text {
        color: #9ca3af;
        font-size: 14px;
        margin-bottom: 1rem;
    }

    /* ===== FEATURE PILLS ===== */
    .feature-pills {
        display: flex;
        justify-content: center;
        gap: 12px;
        margin: 2rem 0;
        flex-wrap: wrap;
    }

    .feature-pill {
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 12px;
        color: #a5b4fc;
        font-weight: 500;
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
    <div class="register-header">
        <div class="register-logo">✨</div>
        <h1 class="register-title">Create Your Account</h1>
        <p class="register-subtitle">Join AI Content Studio and start creating</p>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------
# REGISTER CARD
# -----------------------------------
st.markdown('<div class="register-card">', unsafe_allow_html=True)

st.caption("Enter your details to get started")
st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------
# INPUTS
# -----------------------------------
name = st.text_input(
    "Full Name",
    placeholder="John Doe",
    label_visibility="visible"
)

email = st.text_input(
    "Email Address",
    placeholder="your.email@example.com",
    label_visibility="visible"
)

# -----------------------------------
# REGISTER ACTION
# -----------------------------------
if st.button("Create Account", key="register_btn", type="primary"):
    if not name or not email:
        st.warning("⚠️ Please provide both your name and email address")
    elif "@" not in email or "." not in email:
        st.warning("⚠️ Please enter a valid email address")
    elif len(name.strip()) < 2:
        st.warning("⚠️ Please enter your full name")
    else:
        try:
            with st.spinner("🚀 Creating your account..."):
                res = requests.post(
                    f"{API_BASE}/register",
                    params={"name": name, "email": email},
                    timeout=10
                )

            # ✅ NEW USER SUCCESS
            if res.status_code == 200:
                st.success("✅ Account created successfully!")
                st.info("📧 Verification email sent. Please check your inbox to activate your account.")

                st.markdown("""
                    <div class="benefits-list">
                        <div class="benefit-item">
                            <span class="benefit-icon">✉️</span>
                            <span>Check your email for the verification link</span>
                        </div>
                        <div class="benefit-item">
                            <span class="benefit-icon">🔒</span>
                            <span>Click the link to activate your account</span>
                        </div>
                        <div class="benefit-item">
                            <span class="benefit-icon">✨</span>
                            <span>Start creating amazing content</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                if st.button("→ Proceed to Login", key="login_after_register", type="secondary"):
                    st.switch_page("pages/Login.py")

            # ✅ USER ALREADY EXISTS
            elif res.status_code == 400 and "already exists" in res.text:
                st.warning("⚠️ An account with this email already exists")
                st.info("You can proceed to login using your existing account")

                if st.button("→ Go to Login", key="login_existing_user", type="secondary"):
                    st.switch_page("pages/Login.py")

            # ❌ OTHER ERRORS
            else:
                error_msg = res.json().get("detail", "Registration failed. Please try again.")
                st.error(f"❌ {error_msg}")

        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            st.error("🌐 Unable to connect to the service. Check your connection.")
        except requests.exceptions.RequestException:
            st.error("❌ Unable to connect to the authentication service. Please try again later.")

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------
# FEATURES SECTION
# -----------------------------------
st.markdown("""
    <div class="feature-pills">
        <div class="feature-pill">🎨 AI-Powered</div>
        <div class="feature-pill">⚡ Fast Setup</div>
        <div class="feature-pill">🔒 Secure</div>
        <div class="feature-pill">✨ Free to Start</div>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------
# LOGIN OPTION (ALWAYS VISIBLE)
# -----------------------------------
st.markdown("---")

st.markdown("""
    <div class="register-footer">
        <p class="footer-text">Already have an account?</p>
    </div>
""", unsafe_allow_html=True)

if st.button("Sign In Instead", key="login_footer", type="secondary"):
    st.switch_page("pages/Login.py")