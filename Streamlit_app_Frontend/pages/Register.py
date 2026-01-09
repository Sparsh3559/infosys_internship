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
    padding-top: 3rem;
    margin: auto;
}}

/* REGISTER CARD - MATCHING CONTENT STUDIO STYLE */
.register-box {{
    background: {theme_colors['bg_card']};
    backdrop-filter: blur(20px);
    border: 1px solid {theme_colors['border_color']};
    border-radius: 16px;
    padding: 2.5rem;
    margin-bottom: 1.5rem;
    transition: all 0.3s ease;
}}

.register-box:hover {{
    border-color: {theme_colors['border_hover']};
    box-shadow: 0 8px 30px rgba(139, 92, 246, 0.15);
    background: {theme_colors['bg_card_hover']};
}}

/* HEADER */
.register-header {{
    text-align: center;
    margin-bottom: 2rem;
}}

.register-icon {{
    font-size: 3rem;
    margin-bottom: 1rem;
}}

.register-title {{
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #c4b5fd 0%, #a78bfa 50%, #8b5cf6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.5rem 0;
}}

.register-subtitle {{
    color: {theme_colors['text_secondary']};
    font-size: 0.95rem;
    margin-bottom: 2rem;
}}

/* FEATURE PILLS */
.feature-pills {{
    display: flex;
    justify-content: center;
    gap: 10px;
    margin: 1.5rem 0 2rem 0;
    flex-wrap: wrap;
}}

.feature-pill {{
    background: rgba(139, 92, 246, 0.1);
    border: 1px solid rgba(139, 92, 246, 0.2);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 12px;
    color: {theme_colors['text_accent']};
    font-weight: 500;
}}

/* INPUT LABELS */
.stTextInput > label {{
    color: {theme_colors['text_secondary']} !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    margin-bottom: 0.5rem !important;
}}

/* INPUT FIELDS */
.stTextInput input {{
    background: {theme_colors['input_bg']} !important;
    border: 1.5px solid {theme_colors['border_color']} !important;
    border-radius: 12px !important;
    color: {theme_colors['text_primary']} !important;
    padding: 0.85rem 1rem !important;
    font-size: 0.95rem !important;
    transition: all 0.25s ease !important;
}}

.stTextInput input::placeholder {{
    color: {theme_colors['text_tertiary']} !important;
}}

.stTextInput input:focus {{
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15) !important;
    outline: none !important;
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

/* FOOTER SECTION */
.footer-section {{
    text-align: center;
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid {theme_colors['border_color']};
}}

.footer-text {{
    color: {theme_colors['text_secondary']};
    font-size: 0.9rem;
    margin-bottom: 1rem;
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

/* SPINNER */
.stSpinner > div {{
    border-top-color: #8b5cf6 !important;
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
# BACKEND CONFIG
# -----------------------------------
API_BASE = "https://infosys-internship-backend.onrender.com"

# -----------------------------------
# REGISTER UI
# -----------------------------------

st.markdown("""
    <div class="register-header">
        <div class="register-icon">✨</div>
        <div class="register-title">Create Your Account</div>
        <div class="register-subtitle">Join AI Content Studio and start creating amazing content</div>
    </div>
""", unsafe_allow_html=True)

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