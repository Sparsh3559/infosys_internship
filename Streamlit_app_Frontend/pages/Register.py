import streamlit as st
import requests

# -------------------------------
# PAGE CONFIG + HIDE SIDEBAR
# -------------------------------
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

API_BASE = "https://infosys-internship-backend.onrender.com"

st.title("📝 Register")

name = st.text_input("Name")
email = st.text_input("Email")

# -------------------------------
# REGISTER
# -------------------------------
if st.button("Register", key="register_btn"):
    if not name or not email:
        st.warning("Please fill all fields")
    else:
        try:
            res = requests.post(
                f"{API_BASE}/register",
                params={"name": name, "email": email},
                timeout=10
            )

            if res.status_code == 200:
                st.success("Verification email sent. Please check your inbox.")
                st.info("After verifying your email, log in below.")

                if st.button("Go to Login", key="login_after_register"):
                    st.switch_page("pages/Login.py")

            elif res.status_code == 400 and "already exists" in res.text:
                st.warning("User already exists.")
                st.info("You can log in using your email.")

                if st.button("Go to Login", key="login_existing_user"):
                    st.switch_page("pages/Login.py")

            else:
                st.error(res.json().get("detail", "Registration failed"))

        except requests.exceptions.RequestException:
            st.error("Unable to reach authentication server. Please try again.")

# -------------------------------
# ALWAYS SHOW LOGIN OPTION
# -------------------------------
st.markdown("---")
st.caption("Already registered?")
if st.button("Go to Login", key="login_footer"):
    st.switch_page("pages/Login.py")