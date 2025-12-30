import streamlit as st

def protect():
    """
    Ensures that only authenticated users can access protected pages.
    Redirects unauthenticated users to the Login page.
    """
    if "jwt" not in st.session_state:
        st.switch_page("pages/Login.py")