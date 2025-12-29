import streamlit as st

st.set_page_config(page_title="AI Content Studio", layout="wide")

if "token" not in st.session_state:
    st.switch_page("pages/2_Login.py")
else:
    st.switch_page("pages/3_Content_Studio.py")