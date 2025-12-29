import streamlit as st

def protect():
    if "jwt" not in st.session_state:
        st.switch_page("pages/Login.py")