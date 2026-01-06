import streamlit as st
import requests
import os
import base64

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="Login - AI Content Studio",
    page_icon="✨",
    layout="wide"
)

# -----------------------------------
# HIDE SIDEBAR & HEADER
# -----------------------------------
st.markdown("""
<style>
[data-testid="stSidebar"] { display: none; }
[data-testid="stSidebarNav"] { display: none; }
header[data-testid="stHeader"] { display: none; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# LOAD BACKGROUND IMAGE (LOCAL, SAFE)
# -----------------------------------
def load_bg_image(relative_path):
    try:
        # Get the directory containing Login.py
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level and join with relative_path
        image_path = os.path.normpath(os.path.join(base_dir, "..", relative_path))
        
        # Check if file exists
        if not os.path.exists(image_path):
            # Try alternative paths
            alt_paths = [
                os.path.join(base_dir, relative_path),  # Same directory level
                os.path.join(os.getcwd(), relative_path),  # Current working directory
            ]
            
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    image_path = alt_path
                    break
            else:
                return None
        
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception as e:
        return None

bg_image = load_bg_image("assets/bg_copy.jpg")

# -----------------------------------
# BACKGROUND + GLOBAL STYLES
# -----------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {{
    font-family: 'Inter', sans-serif;
}}

html, body, [data-testid="stApp"] {{
    {f'''background:
        linear-gradient(rgba(10,10,20,0.88), rgba(10,10,20,0.88)),
        url("data:image/jpg;base64,{bg_image}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;''' if bg_image else 'background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);'}
    color: #e5e7eb;
    margin: 0;
    padding: 0;
}}

.block-container {{
    max-width: 520px;
    padding-top: 5rem;
    margin: auto;
}}

.login-box {{
    background: rgba(17, 24, 39, 0.75);
    backdrop-filter: blur(22px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 22px;
    padding: 2.8rem;
    box-shadow: 0 25px 70px rgba(0,0,0,0.55);
}}

.login-title {{
    font-size: 2rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 0.4rem;
    background: linear-gradient(135deg, #a5b4fc, #c4b5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.login-subtitle {{
    text-align: center;
    color: #9ca3af;
    margin-bottom: 2rem;
    font-size: 0.95rem;
}}

.stTextInput > label {{
    color: #e5e7eb !important;
    font-weight: 500 !important;
    margin-bottom: 0.5rem !important;
}}

.stTextInput input {{
    background: rgba(15, 23, 42, 0.9) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 14px !important;
    padding: 15px !important;
    color: #e5e7eb !important;
    font-size: 15px !important;
}}

.stTextInput input::placeholder {{
    color: #6b7280 !important;
}}

.stTextInput input:focus {{
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.25) !important;
    outline: none !important;
}}

.stButton button {{
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 14px !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    width: 100%;
    color: white !important;
    box-shadow: 0 10px 30px rgba(99,102,241,0.4);
    transition: all 0.3s ease !important;
    cursor: pointer !important;
}}

.stButton button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 15px 40px rgba(99,102,241,0.5) !important;
}}

.stButton button:active {{
    transform: translateY(0px) !important;
}}

.footer {{
    text-align: center;
    margin-top: 1.8rem;
    font-size: 13px;
    color: #9ca3af;
    line-height: 1.6;
}}

/* Success/Warning/Error messages styling */
.stAlert {{
    border-radius: 12px !important;
    backdrop-filter: blur(10px);
}}

.stSuccess {{
    background: rgba(34, 197, 94, 0.15) !important;
    border: 1px solid rgba(34, 197, 94, 0.3) !important;
    color: #86efac !important;
}}

.stWarning {{
    background: rgba(251, 191, 36, 0.15) !important;
    border: 1px solid rgba(251, 191, 36, 0.3) !important;
    color: #fde047 !important;
}}

.stError {{
    background: rgba(239, 68, 68, 0.15) !important;
    border: 1px solid rgba(239, 68, 68, 0.3) !important;
    color: #fca5a5 !important;
}}

.stInfo {{
    background: rgba(59, 130, 246, 0.15) !important;
    border: 1px solid rgba(59, 130, 246, 0.3) !important;
    color: #93c5fd !important;
}}

/* Spinner styling */
.stSpinner > div {{
    border-top-color: #6366f1 !important;
}}
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# BACKEND CONFIG
# -----------------------------------
API_BASE = "https://infosys-internship-backend.onrender.com"

# -----------------------------------
# LOGIN UI
# -----------------------------------
st.markdown('<div class="login-box">AI Content Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="login-subtitle">Secure login via email verification</div>', unsafe_allow_html=True)

email = st.text_input(
    "Email Address",
    placeholder="your.email@example.com",
    key="email_input"
)

if st.button("Send Login Link", key="login_button"):
    if not email:
        st.warning("⚠️ Please enter your email address")
    elif "@" not in email or "." not in email:
        st.warning("⚠️ Please enter a valid email address")
    else:
        try:
            with st.spinner("Sending secure login link..."):
                res = requests.post(
                    f"{API_BASE}/login",
                    params={"email": email},
                    timeout=10
                )

            if res.status_code == 200:
                st.success("✅ Login link sent successfully!")
                st.info("📧 Check your email to continue")
            else:
                error_msg = res.json().get("detail", "Login failed")
                st.error(f"❌ {error_msg}")

        except requests.exceptions.Timeout:
            st.error("❌ Request timeout. Please try again.")
        except requests.exceptions.ConnectionError:
            st.error("❌ Unable to connect to authentication service")
        except requests.exceptions.RequestException as e:
            st.error("❌ An error occurred. Please try again.")

st.markdown("""
<div class="footer">
    🔒 Passwordless • Secure • Fast<br>
    By continuing, you agree to the platform terms
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
