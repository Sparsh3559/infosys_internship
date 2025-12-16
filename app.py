import streamlit as st

st.title("AI System for Personalized Content Creation")
st.write("This demo captures user input and content preferences.")
st.divider()

# User input
prompt = st.text_input("Enter your prompt")
st.divider()

# Content type selection (no default selection)
content_type = st.selectbox(
    "Select content type",
    ["LinkedIn Post", "Email", "Advertisement", "Conversation"],
    index=None,
    placeholder="Choose a content type"
)

# Display output only when both are provided
if prompt and content_type:
    st.balloons()

    st.subheader("User Input Summary")
    st.write("Your prompt:")
    st.write(prompt)

    st.write("Selected content type:")
    st.write(content_type)