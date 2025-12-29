import streamlit as st
import requests

st.title("Register")

name = st.text_input("Name")
email = st.text_input("Email")

if st.button("Register"):
    if not name or not email:
        st.warning("Fill all fields")
    else:
        res = requests.post(
            "http://localhost:8000/register",
            params={"name": name, "email": email}
        )

        if res.status_code == 200:
            st.success("Verification link sent to your email")
        else:
            st.error(res.json()["detail"])