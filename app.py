import streamlit as st

st.title("AI System for Personalized Content Creation")
st.write("Streamlit app is running successfully")

prompt = st.text_input("Enter your prompt")

content_type = st.selectbox(
    "Select content type",
    ["LinkedIn Post", "Email", "Advertisement", "Conversation"]
)

if prompt:
    st.write("Prompt:", prompt)
    st.write("Content Type:", content_type)
