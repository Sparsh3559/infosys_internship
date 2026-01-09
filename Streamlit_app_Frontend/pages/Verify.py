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
    padding-top: 5rem;
    margin: auto;
}}

/* VERIFICATION CARD */
.verify-box {{
    background: rgba(17, 24, 39, 0.75);
    backdrop-filter: blur(22px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 22px;
    padding: 2.8rem;
    box-shadow: 0 25px 70px rgba(0,0,0,0.55);
    animation: fadeInUp 0.6s ease;
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

.verify-title {{
    font-size: 2rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 0.4rem;
    background: linear-gradient(135deg, #a5b4fc, #c4b5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.verify-subtitle {{
    text-align: center;
    color: #9ca3af;
    margin-bottom: 2rem;
    font-size: 0.95rem;
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
    margin-top: 0.5rem !important;
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
    background: rgba(99, 102, 241, 0.4);
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
    50% {{ transform: scale(1.5); opacity: 1; background: #6366f1; }}
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

/* CAPTION */
.caption {{
    text-align: center;
    color: #9ca3af;
    font-size: 14px;
    margin-top: 1rem;
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
# QUERY PARAMS
# -----------------------------------
params = st.query_params

# -----------------------------------
# EMAIL VERIFICATION SUCCESS
# -----------------------------------
if params.get("status") == "verified":
    st.markdown('<div class="verify-box">', unsafe_allow_html=True)
    
    st.markdown('<div class="verify-title">Email Verified</div>', unsafe_allow_html=True)
    st.markdown('<div class="verify-subtitle">Your account is now active</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="status-icon success-icon">🎉</div>', unsafe_allow_html=True)
    
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

    st.markdown('<div class="verify-box">', unsafe_allow_html=True)
    
    st.markdown('<div class="verify-title">Login Successful</div>', unsafe_allow_html=True)
    st.markdown('<div class="verify-subtitle">Welcome back to AI Content Studio</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="status-icon success-icon">✅</div>', unsafe_allow_html=True)
    
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
    
    st.markdown('<div class="verify-title">Invalid Link</div>', unsafe_allow_html=True)
    st.markdown('<div class="verify-subtitle">Unable to verify your request</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="status-icon error-icon">❌</div>', unsafe_allow_html=True)
    
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