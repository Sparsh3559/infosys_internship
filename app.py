import streamlit as st
import requests
import json
import time

# -------------------------------
# AWS BEDROCK CONFIG
# -------------------------------
BEDROCK_API_KEY = st.secrets["BEDROCK_API_KEY"]

BEDROCK_URL = "https://bedrock-runtime.us-east-1.amazonaws.com/model/amazon.nova-micro-v1:0/invoke"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {BEDROCK_API_KEY}"
}

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="AI Content Studio",
    page_icon="✨",
    layout="wide"
)

# -------------------------------
# SIDEBAR (≈30%)
# -------------------------------
with st.sidebar:
    st.markdown("## ✨ Content Studio")
    st.caption("Craft clear, professional content effortlessly")

    st.divider()

    prompt = st.text_area(
        "Describe your idea",
        placeholder="Example: I participated in a national-level hackathon...",
        height=120
    )

    content_type = st.selectbox(
        "Where will this content be used?",
        ["LinkedIn Post", "Email", "Advertisement", "Conversation"],
        index=None,
        placeholder="Select content type"
    )

    tone = st.selectbox(
        "Tone",
        ["Professional", "Friendly", "Confident", "Conversational", "Minimal"],
        index=0
    )

    word_limit = st.slider(
        "Length",
        min_value=80,
        max_value=300,
        step=20,
        value=150
    )

    st.divider()

    generate = st.button("✨ Generate Content", use_container_width=True)

# -------------------------------
# MAIN AREA (≈70%)
# -------------------------------
st.markdown("## 📝 Draft Preview")
st.caption("Your generated content will appear here")

st.divider()

# -------------------------------
# LOGIC
# -------------------------------
if generate:
    if not prompt or not content_type:
        st.warning("Please provide both an idea and content type.")
    else:
        # Prompt engineering (simple & clean)
        final_prompt = (
            f"Write a {tone.lower()} {content_type.lower()} "
            f"within {word_limit} words about the following:\n\n{prompt}"
        )

        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": final_prompt}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": word_limit,
                "temperature": 0.7
            }
        }

        with st.spinner("Crafting your draft..."):
            response = requests.post(
                BEDROCK_URL,
                headers=HEADERS,
                json=payload
            )

        if response.status_code == 200:
            result = response.json()
            generated_text = result["output"]["message"]["content"][0]["text"]

            # Subtle animation
            with st.container():
                time.sleep(0.2)
                st.markdown(
    f"""
    <style>
    .editor-box {{
        background: linear-gradient(180deg, #111827, #0f172a);
        color: #e5e7eb;
        padding: 24px;
        border-radius: 14px;
        border: 1px solid #1f2937;
        font-size: 16px;
        line-height: 1.7;
        white-space: pre-wrap;
        animation: fadeInUp 0.5s ease-out;
    }}

    @keyframes fadeInUp {{
        from {{
            opacity: 0;
            transform: translateY(8px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    </style>

    <div class="editor-box">
        {generated_text}
    </div>
    """,
    unsafe_allow_html=True
)

            st.divider()

            col1, col2 = st.columns(2)

            with col1:
                st.download_button(
                    "📄 Copy Content",
                    generated_text,
                    file_name="generated_content.txt"
                )

            with col2:
                st.caption("✨ Tip: Adjust tone or length and regenerate for refinement")

        else:
            st.error("Failed to generate content")
            st.code(response.text)