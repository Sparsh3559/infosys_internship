import streamlit as st

def protect():
    # User must be authenticated
    if "jwt" not in st.session_state:
        st.switch_page("pages/Login.py")