import streamlit as st
import requests

def protect():
    if "token" not in st.session_state:
        st.switch_page("pages/2_Login.py")