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
# First-time users → Register
# Logged-in users → Content Studio

if "jwt" in st.session_state:
    st.switch_page("pages/Content_Studio.py")
    st.stop()
else:
    st.switch_page("pages/Register.py")
    st.stop()