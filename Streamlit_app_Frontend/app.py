import streamlit as st

st.set_page_config(layout="wide")

# Hide sidebar completely
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="stSidebarNav"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True
)

# Router (NO UI here)
if "jwt" in st.session_state:
    st.switch_page("pages/Content_Studio.py")
    st.stop()
else:
    st.switch_page("pages/Register.py")
    st.stop()