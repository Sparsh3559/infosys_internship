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
    base_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(base_dir, "..", relative_path)
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_image = load_bg_image("assets/bgi_copy.jpg")

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
    background:
        linear-gradient(rgba(10,10,20,0.88), rgba(10,10,20,0.88)),
        url("data:image/jpg;base64,{bg_image}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    color: #e5e7eb;
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
}}

.login-subtitle {{
    text-align: center;
    color: #9ca3af;
    margin-bottom: 2rem;
}}

.stTextInput input {{
    background: rgba(15, 23, 42, 0.9) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 14px !important;
    padding: 15px !important;
    color: #e5e7eb !important;
}}

.stTextInput input:focus {{
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.25) !important;
}}

.stButton button {{
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border-radius: 14px !important;
    padding: 14px !important;
    font-weight: 600 !important;
    width: 100%;
    box-shadow: 0 10px 30px rgba(99,102,241,0.4);
}}

.stButton button:hover {{
    transform: translateY(-2px);
}}

.footer {{
    text-align: center;
    margin-top: 1.8rem;
    font-size: 13px;
    color: #9ca3af;
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
st.markdown('<div class="login-box">', unsafe_allow_html=True)

st.markdown('<div class="login-title">AI Content Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="login-subtitle">Secure login via email verification</div>', unsafe_allow_html=True)

email = st.text_input(
    "Email Address",
    placeholder="your.email@example.com"
)

if st.button("Send Login Link"):
    if not email:
        st.warning("Please enter your email address")
    elif "@" not in email or "." not in email:
        st.warning("Please enter a valid email address")
    else:
        try:
            with st.spinner("Sending secure login link..."):
                res = requests.post(
                    f"{API_BASE}/login",
                    params={"email": email},
                    timeout=10
                )

            if res.status_code == 200:
                st.success("Login link sent successfully")
                st.info("Check your email to continue")
            else:
                st.error(res.json().get("detail", "Login failed"))

        except requests.exceptions.RequestException:
            st.error("Unable to connect to authentication service")

st.markdown("""
<div class="footer">
    🔒 Passwordless • Secure • Fast<br>
    By continuing, you agree to the platform terms
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)