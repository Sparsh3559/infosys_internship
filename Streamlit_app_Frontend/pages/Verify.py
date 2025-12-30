import streamlit as st
from urllib.parse import unquote

# -----------------------------------
# PAGE CONFIG + HIDE SIDEBAR
# -----------------------------------
st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------
# QUERY PARAMS
# -----------------------------------
params = st.query_params

# -----------------------------------
# EMAIL VERIFICATION SUCCESS
# -----------------------------------
if params.get("status") == "verified":
    st.title("Email Verified")
    st.success("Your email address has been successfully verified.")
    st.info("You can now proceed to log in and access your account.")

    if st.button("Proceed to Login"):
        st.switch_page("pages/Login.py")

# -----------------------------------
# LOGIN VERIFICATION SUCCESS
# -----------------------------------
elif "jwt" in params:
    st.session_state["jwt"] = unquote(params["jwt"])
    st.session_state["email"] = params.get("email")

    st.title("Login Successful")
    st.success("You have been logged in successfully.")
    st.info("Redirecting you to your workspace...")

    st.switch_page("pages/Content_Studio.py")

# -----------------------------------
# INVALID / EXPIRED LINK
# -----------------------------------
else:
    st.title("Invalid Link")
    st.error("This verification link is invalid or has expired.")
    st.caption("Please request a new verification or login link.")