import streamlit as st
import requests

# -----------------------------------
# PAGE CONFIG + HIDE SIDEBAR
# -----------------------------------
st.set_page_config(layout="wide")

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
# PAGE TITLE
# -----------------------------------
st.title("Create Your Account")
st.caption("Register using your name and email address to continue")

# -----------------------------------
# INPUTS
# -----------------------------------
name = st.text_input("Full Name")
email = st.text_input("Email Address")

# -----------------------------------
# REGISTER ACTION
# -----------------------------------
if st.button("Register", key="register_btn"):
    if not name or not email:
        st.warning("Please provide both your name and email address.")
    else:
        try:
            res = requests.post(
                f"{API_BASE}/register",
                params={"name": name, "email": email},
                timeout=10
            )

            # ✅ NEW USER SUCCESS
            if res.status_code == 200:
                st.success("Verification email sent successfully.")
                st.info("Please verify your email to activate your account.")

                if st.button("Proceed to Login", key="login_after_register"):
                    st.switch_page("pages/Login.py")

            # ✅ USER ALREADY EXISTS
            elif res.status_code == 400 and "already exists" in res.text:
                st.warning("An account with this email already exists.")
                st.info("You may proceed to login using your email address.")

                if st.button("Proceed to Login", key="login_existing_user"):
                    st.switch_page("pages/Login.py")

            # ❌ OTHER ERRORS
            else:
                st.error(res.json().get("detail", "Registration failed. Please try again."))

        except requests.exceptions.RequestException:
            st.error("Unable to connect to the authentication service. Please try again later.")

# -----------------------------------
# LOGIN OPTION (ALWAYS VISIBLE)
# -----------------------------------
st.markdown("---")
st.caption("Already have an account?")
if st.button("Go to Login", key="login_footer"):
    st.switch_page("pages/Login.py")