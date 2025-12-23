import streamlit as st
import requests

# -------------------------------
# AWS BEDROCK CONFIG
# -------------------------------
BEDROCK_API_KEY = st.secrets.get("BEDROCK_API_KEY")

if not BEDROCK_API_KEY:
    st.error("BEDROCK_API_KEY not found. Please add it to Streamlit secrets.")
    st.stop()

BEDROCK_URL = (
    "https://bedrock-runtime.us-east-1.amazonaws.com/"
    "model/amazon.nova-micro-v1:0/invoke"
)

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {BEDROCK_API_KEY}"
}

# -------------------------------
# STREAMLIT UI
# -------------------------------
st.title("AI System for Personalized Content Creation")
st.write("This demo captures user input and content preferences.")
st.write("Streamlit app is running successfully")
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

# -------------------------------
# PREVIEW SECTION
# -------------------------------
if prompt and content_type:
    st.balloons()

    st.subheader("User Input Summary")

    st.text_area(
        "Your Prompt",
        value=prompt,
        height=100,
        disabled=True
    )

    st.text_area(
        "Selected Content Type",
        value=content_type,
        height=60,
        disabled=True
    )

# -------------------------------
# LOGIC
# -------------------------------
if prompt and content_type:
    if content_type == "LinkedIn Post":
        final_prompt = f"Write a professional LinkedIn post about: {prompt}"
    elif content_type == "Email":
        final_prompt = f"Write a professional email about: {prompt}"
    elif content_type == "Advertisement":
        final_prompt = f"Write a short advertisement copy about: {prompt}"
    else:
        final_prompt = f"Write a friendly conversational response about: {prompt}"

    # ✅ Correct payload for Amazon Nova
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"text": final_prompt}
                ]
            }
        ],
        "inferenceConfig": {
            "maxTokens": 300,
            "temperature": 0.7
        }
    }

    with st.spinner("Generating content using AWS Bedrock..."):
        response = requests.post(
            BEDROCK_URL,
            headers=HEADERS,
            json=payload
        )

    if response.status_code == 200:
        result = response.json()

        # ✅ Correct Nova response parsing
        generated_text = result["output"]["message"]["content"][0]["text"]

        st.subheader("Generated Content")
        st.write(generated_text)
    else:
        st.error("Failed to generate content")
        st.code(response.text)