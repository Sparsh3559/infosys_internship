import streamlit as st

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
# ROUTER ONLY (NO UI)
# -------------------------------
if "jwt" in st.session_state:
    st.switch_page("pages/Content_Studio.py")
else:
    st.switch_page("pages/Register.py")