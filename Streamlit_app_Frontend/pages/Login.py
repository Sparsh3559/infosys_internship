import streamlit as st
import requests

st.title("Login")

email = st.text_input("Email")

if st.button("Send Magic Link"):
    if not email:
        st.warning("Enter email")
    else:
        res = requests.post(
            "http://localhost:8000/register",
            params={"name": "User", "email": email}
        )
        st.success("Check your email for login link")