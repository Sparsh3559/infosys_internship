import streamlit as st

# -------------------------------
# PAGE CONFIG + HIDE SIDEBAR
# -------------------------------
st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="stSidebarNav"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# CENTER CONTAINER
# -------------------------------
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("## ✅ Email Verified Successfully")

    st.success(
        "Your email has been verified successfully. "
        "You can now log in to your account."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔐 Go to Login", use_container_width=True):
        st.switch_page("pages/Login.py")