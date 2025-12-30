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

# -------------------------------
# CONFIG
# -------------------------------
API_BASE = "https://infosys-internship-backend.onrender.com"

# -------------------------------
# UI
# -------------------------------
st.title("Secure Login")

st.caption("Enter your registered email address to receive a secure login link.")

email = st.text_input("Email Address")

# -------------------------------
# LOGIN ACTION
# -------------------------------
if st.button("Send Login Link"):
    if not email:
        st.warning("Please enter your email address.")
    else:
        try:
            res = requests.post(
                f"{API_BASE}/login",
                params={"email": email},
                timeout=10
            )

            if res.status_code == 200:
                st.success("Login link sent successfully.")
                st.info("Please check your email and click the link to continue.")
            else:
                st.error(res.json().get("detail", "Login request failed."))

        except requests.exceptions.RequestException:
            st.error("Unable to reach the authentication service. Please try again.")