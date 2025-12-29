import streamlit as st
import requests

API_BASE = "https://infosys-internship-backend.onrender.com"

st.title("🔐 Login (Magic Link)")

email = st.text_input("Email")

if st.button("Send Magic Link"):
    if not email:
        st.warning("Enter your email")
    else:
        try:
            res = requests.post(
                f"{API_BASE}/login",
                params={"email": email},
                timeout=10
            )

            if res.status_code == 200:
                st.success("Magic link sent. Check your email inbox.")
            else:
                st.error(res.json().get("detail", "Login failed"))

        except requests.exceptions.RequestException:
            st.error("Unable to reach authentication server. Please try again.")