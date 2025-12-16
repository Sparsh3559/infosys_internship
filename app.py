import streamlit as st
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Initialize model
model = genai.GenerativeModel("gemini-pro")

st.title("AI System for Personalized Content Creation")
st.write("Streamlit app is running successfully")
st.divider()

prompt = st.text_input("Enter your prompt")
st.divider()

content_type = st.selectbox(
    "Select content type",
    ["LinkedIn Post", "Email", "Advertisement", "Conversation"]
)

if prompt:
    st.balloons()

    if content_type == "LinkedIn Post":
        final_prompt = f"Write a professional LinkedIn post about: {prompt}"
    elif content_type == "Email":
        final_prompt = f"Write a professional email about: {prompt}"
    elif content_type == "Advertisement":
        final_prompt = f"Write a short advertisement copy about: {prompt}"
    else:
        final_prompt = f"Write a friendly conversational response about: {prompt}"

    with st.spinner("Generating content using Gemini..."):
        response = model.generate_content(final_prompt)

    st.subheader("Generated Content")
    st.write(response.text)