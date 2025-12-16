import streamlit as st

st.title("AI System for Personalized Content Creation")
st.write("This demo captures user input and content preferences.")
st.divider()

# Input fields
prompt = st.text_input("Enter your prompt")
st.divider()

content_type = st.selectbox(
    "Select content type",
    ["LinkedIn Post", "Email", "Advertisement", "Conversation"],
    index=None,
    placeholder="Choose a content type"
)

# Output section
if prompt and content_type:
    st.balloons()

    st.subheader("User Input Summary")

    # Prompt display box
    with st.container():
        st.text_area(
            "Your Prompt",
            value=prompt,
            height=100,
            disabled=True
        )

    # Content type display box
    with st.container():
        st.text_area(
            "Selected Content Type",
            value=content_type,
            height=60,
            disabled=True
        )