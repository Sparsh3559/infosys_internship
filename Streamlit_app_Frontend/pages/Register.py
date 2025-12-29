import streamlit as st
import requests

API_BASE = "https://infosys-internship-backend.onrender.com"

st.title("📝 Register")

name = st.text_input("Name")
email = st.text_input("Email")

if st.button("Register"):
    if not name or not email:
        st.warning("Please fill all fields")
    else:
        try:
            res = requests.post(
                f"{API_BASE}/register",
                params={"name": name, "email": email},
                timeout=10
            )

            if res.status_code == 200:
                st.success("Verification email sent. Please check your inbox.")
            else:
                st.error(res.json().get("detail", "Registration failed"))

        except requests.exceptions.RequestException:
            st.error("Unable to reach authentication server. Please try again.")