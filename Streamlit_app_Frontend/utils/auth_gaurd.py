import streamlit as st

def protect():
    # Check JWT in session
    if "jwt" not in st.session_state:
        st.warning("Please login to continue")
        st.switch_page("Login.py")