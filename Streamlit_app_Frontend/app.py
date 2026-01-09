import streamlit as st

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="AI Content Studio",
    layout="wide"
)

# -----------------------------------
# HIDE SIDEBAR COMPLETELY
# -----------------------------------
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
# ROUTER 
# -----------------------------------

current_page = st.query_params.get("page")

# ✅ Allow Verify & Login pages to open naturally
if current_page in ["verify", "login"]:
    st.stop()

# ✅ Logged-in users
if "jwt" in st.session_state:
    st.switch_page("pages/Content_Studio.py")
    st.stop()

# ✅ Default: Home (Landing Page)
st.switch_page("pages/Home.py")
st.stop()