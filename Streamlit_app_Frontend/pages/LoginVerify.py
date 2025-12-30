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
# UI
# -----------------------------------
st.title("Secure Login Verification")

st.caption("Please wait while we securely sign you in.")

# -----------------------------------
# TOKEN HANDLING
# -----------------------------------
token = st.query_params.get("token")

if not token:
    st.error("The login link is invalid or incomplete.")
    st.stop()

# -----------------------------------
# VERIFY LOGIN TOKEN
# -----------------------------------
try:
    res = requests.get(
        f"{API_BASE}/login/verify",
        params={"token": token},
        timeout=10
    )

    if res.status_code == 200:
        data = res.json()

        st.session_state["jwt"] = data["jwt"]
        st.session_state["email"] = data["email"]

        st.success("Authentication successful.")
        st.info("Redirecting you to your workspace...")

        st.switch_page("pages/Content_Studio.py")

    else:
        st.error(res.json().get("detail", "Login verification failed."))

except requests.exceptions.RequestException:
    st.error("Unable to connect to the authentication service. Please try again.")