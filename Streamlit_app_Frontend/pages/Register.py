import streamlit as st
import requests
import os
import base64

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="Register - AI Content Studio",
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
# LOAD BACKGROUND IMAGE
# -----------------------------------
def load_bg_image(relative_path):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.normpath(os.path.join(base_dir, "..", relative_path))
        
        if not os.path.exists(image_path):
            alt_paths = [
                os.path.join(base_dir, relative_path),
                os.path.join(os.getcwd(), relative_path),
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
# MODERN UNIFIED STYLING
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
    padding-top: 4rem;
    margin: auto;
}}

/* REGISTER CARD */
.register-box {{
    background: rgba(17, 24, 39, 0.75);
    backdrop-filter: blur(22px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 22px;
    padding: 2.8rem;
    box-shadow: 0 25px 70px rgba(0,0,0,0.55);
}}

.register-title {{
    font-size: 2rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 0.4rem;
    background: linear-gradient(135deg, #a5b4fc, #c4b5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.register-subtitle {{
    text-align: center;
    color: #9ca3af;
    margin-bottom: 2rem;
    font-size: 0.95rem;
}}

/* INPUT LABELS */
.stTextInput > label {{
    color: #e5e7eb !important;
    font-weight: 500 !important;
    margin-bottom: 0.5rem !important;
}}

/* INPUT FIELDS */
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

/* UNIFIED GRADIENT BUTTONS */
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

/* BENEFITS SECTION */
.benefits-card {{
    background: rgba(31, 41, 55, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1.5rem 0;
}}

.benefit-item {{
    display: flex;
    align-items: center;
    gap: 12px;
    color: #d1d5db;
    font-size: 14px;
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

/* FEATURE PILLS */
.feature-pills {{
    display: flex;
    justify-content: center;
    gap: 10px;
    margin: 2rem 0 1.5rem 0;
    flex-wrap: wrap;
}}

.feature-pill {{
    background: rgba(99, 102, 241, 0.1);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 12px;
    color: #a5b4fc;
    font-weight: 500;
}}

/* FOOTER */
.footer-section {{
    text-align: center;
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
}}

.footer-text {{
    color: #9ca3af;
    font-size: 14px;
    margin-bottom: 1rem;
}}

/* SUCCESS/WARNING/ERROR MESSAGES */
.stAlert {{
    border-radius: 12px !important;
    backdrop-filter: blur(10px);
    margin: 1rem 0 !important;
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

/* SPINNER */
.stSpinner > div {{
    border-top-color: #6366f1 !important;
}}

/* DIVIDER */
hr {{
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    margin: 2rem 0;
}}
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# BACKEND CONFIG
# -----------------------------------
API_BASE = "https://infosys-internship-backend.onrender.com"

# -----------------------------------
# REGISTER UI
# -----------------------------------
st.markdown('<div class="register-box">', unsafe_allow_html=True)

st.markdown('<div class="register-title">Create Your Account</div>', unsafe_allow_html=True)
st.markdown('<div class="register-subtitle">Join AI Content Studio and start creating</div>', unsafe_allow_html=True)

# Feature Pills
st.markdown("""
    <div class="feature-pills">
        <div class="feature-pill">🎨 AI-Powered</div>
        <div class="feature-pill">⚡ Fast Setup</div>
        <div class="feature-pill">🔒 Secure</div>
        <div class="feature-pill">✨ Free to Start</div>
    </div>
""", unsafe_allow_html=True)

# Input Fields
name = st.text_input(
    "Full Name",
    placeholder="John Doe",
    key="name_input"
)

email = st.text_input(
    "Email Address",
    placeholder="your.email@example.com",
    key="email_input"
)

# Register Button
if st.button("Create Account", key="register_button"):
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

            # SUCCESS - New User
            if res.status_code == 200:
                st.success("✅ Account created successfully!")
                st.info("📧 Verification email sent. Please check your inbox to activate your account.")

                st.markdown("""
                    <div class="benefits-card">
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

                if st.button("→ Proceed to Login", key="goto_login"):
                    st.switch_page("pages/Login.py")

            # USER ALREADY EXISTS
            elif res.status_code == 400 and "already exists" in res.text:
                st.warning("⚠️ An account with this email already exists")
                st.info("You can proceed to login using your existing account")

                if st.button("→ Go to Login", key="goto_login_existing"):
                    st.switch_page("pages/Login.py")

            # OTHER ERRORS
            else:
                error_msg = res.json().get("detail", "Registration failed. Please try again.")
                st.error(f"❌ {error_msg}")

        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            st.error("🌐 Unable to connect to the service. Check your connection.")
        except requests.exceptions.RequestException:
            st.error("❌ Unable to connect to the authentication service. Please try again later.")

# Footer Section
st.markdown("---")

st.markdown("""
    <div class="footer-section">
        <p class="footer-text">Already have an account?</p>
    </div>
""", unsafe_allow_html=True)

if st.button("Sign In Instead", key="signin_button"):
    st.switch_page("pages/Login.py")

st.markdown('</div>', unsafe_allow_html=True)