import streamlit as st

st.set_page_config(
    page_title="AI Content Studio",
    layout="wide"
)

# NOTE:
# During initial deployment, auth is disabled in Content_Studio
# This routing is safe and Streamlit-Cloud compatible

if "jwt" in st.session_state:
    st.switch_page("Content_Studio.py")
else:
    st.switch_page("Login.py")