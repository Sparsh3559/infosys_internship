import streamlit as st
import requests

# -------------------------------
# PAGE CONFIG + HIDE SIDEBAR
# -------------------------------
st.set_page_config(
    page_title="Login - AI Content Studio",
    page_icon="🔐",
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

# -------------------------------
# CONFIG
# -------------------------------
API_BASE = "https://infosys-internship-backend.onrender.com"

# -------------------------------
# MODERN STYLING
# -------------------------------
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
        padding-top: 5rem;
        max-width: 500px;
        margin: 0 auto;
    }

    /* ===== HIDE DEFAULT HEADERS ===== */
    header[data-testid="stHeader"] {
        display: none;
    }

    /* ===== CUSTOM LOGO/TITLE ===== */
    .login-header {
        text-align: center;
        margin-bottom: 3rem;
    }

    .login-logo {
        font-size: 3rem;
        margin-bottom: 1rem;
        animation: float 3s ease-in-out infinite;
    }

    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }

    .login-title {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #a5b4fc 0%, #c4b5fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }

    .login-subtitle {
        color: #9ca3af;
        font-size: 1rem;
        font-weight: 400;
        letter-spacing: 0.01em;
    }

    /* ===== LOGIN CARD ===== */
    .login-card {
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

    /* ===== BUTTON ===== */
    .stButton button {
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

    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(99, 102, 241, 0.5) !important;
    }

    .stButton button:active {
        transform: translateY(0) !important;
    }

    /* ===== ALERTS/MESSAGES ===== */
    .stAlert {
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(10px) !important;
        margin-top: 1rem !important;
    }

    /* Success message */
    [data-testid="stNotification"] > div,
    .element-container:has(.stSuccess) {
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

    /* ===== FOOTER ===== */
    .login-footer {
        text-align: center;
        margin-top: 2rem;
        color: #6b7280;
        font-size: 13px;
    }

    .login-footer a {
        color: #a5b4fc;
        text-decoration: none;
        font-weight: 500;
        transition: color 0.3s ease;
    }

    .login-footer a:hover {
        color: #c4b5fd;
    }

    /* ===== FEATURE PILLS ===== */
    .feature-pills {
        display: flex;
        justify-content: center;
        gap: 12px;
        margin-top: 2rem;
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

    /* ===== SECURITY BADGE ===== */
    .security-badge {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        margin-top: 1.5rem;
        padding: 12px;
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 10px;
        font-size: 13px;
        color: #6ee7b7;
    }

    /* ===== DIVIDER ===== */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        margin: 2rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# CUSTOM HEADER
# -------------------------------
st.markdown("""
    <div class="login-header">
        <div class="login-logo">✨</div>
        <h1 class="login-title">Welcome Back</h1>
        <p class="login-subtitle">Sign in to continue to AI Content Studio</p>
    </div>
""", unsafe_allow_html=True)

# -------------------------------
# LOGIN CARD
# -------------------------------
st.markdown('<div class="login-card">', unsafe_allow_html=True)

st.caption("Enter your registered email to receive a secure login link")
st.markdown("<br>", unsafe_allow_html=True)

email = st.text_input(
    "Email Address",
    placeholder="your.email@example.com",
    label_visibility="visible"
)

# -------------------------------
# LOGIN ACTION
# -------------------------------
if st.button("Send Login Link"):
    if not email:
        st.warning("⚠️ Please enter your email address")
    elif "@" not in email or "." not in email:
        st.warning("⚠️ Please enter a valid email address")
    else:
        try:
            with st.spinner("🔐 Sending secure link..."):
                res = requests.post(
                    f"{API_BASE}/login",
                    params={"email": email},
                    timeout=10
                )

            if res.status_code == 200:
                st.success("✅ Login link sent successfully!")
                st.info("📧 Check your email and click the link to continue")
                
                # Security badge
                st.markdown("""
                    <div class="security-badge">
                        🔒 Secure authentication via email
                    </div>
                """, unsafe_allow_html=True)
            else:
                error_msg = res.json().get("detail", "Login request failed")
                st.error(f"❌ {error_msg}")

        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            st.error("🌐 Unable to reach authentication service. Check your connection.")
        except requests.exceptions.RequestException as e:
            st.error("❌ An error occurred. Please try again later.")

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# FEATURES SECTION
# -------------------------------
st.markdown("""
    <div class="feature-pills">
        <div class="feature-pill">🔒 Secure</div>
        <div class="feature-pill">⚡ Fast</div>
        <div class="feature-pill">✨ No Password</div>
    </div>
""", unsafe_allow_html=True)

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("""
    <div class="login-footer">
        <p>Don't have an account? <a href="#">Sign up</a></p>
        <p style="margin-top: 1rem;">By continuing, you agree to our Terms & Privacy Policy</p>
    </div>
""", unsafe_allow_html=True)