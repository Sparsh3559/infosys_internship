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
# SIDEBAR (CONTROL PANEL)
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
        ["Professional", "Confident", "Friendly", "Conversational"],
        index=0
    )

    audience = st.selectbox(
        "Audience",
        [
            "Recruiters / Hiring Managers",
            "General LinkedIn Audience",
            "Technical Audience",
            "Peers / Students"
        ],
        index=0
    )

    purpose = st.selectbox(
        "Purpose",
        [
            "Share an experience",
            "Showcase skills",
            "Reflect on learning",
            "Announce an achievement"
        ],
        index=0
    )

    word_limit = st.slider(
        "Length",
        min_value=80,
        max_value=300,
        step=20,
        value=150
    )

    st.caption("Ideal for LinkedIn-style posts")

    st.divider()

    generate = st.button("✨ Generate Content", use_container_width=True)

# -------------------------------
# MAIN AREA (EDITOR)
# -------------------------------
st.markdown("## 📝 Draft Preview")
st.caption("Your generated content will appear here")

st.divider()

# Placeholder before generation
if not generate:
    st.markdown(
        """
        <div style="
            border:1px dashed #374151;
            border-radius:12px;
            padding:40px;
            text-align:center;
            color:#9ca3af;
        ">
        Adjust the inputs on the left and click <b>Generate Content</b> to see your draft here.
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------
# LOGIC
# -------------------------------
if generate:
    if not prompt or not content_type:
        st.warning("Please provide both an idea and content type.")
    else:
        final_prompt = (
            f"Write a {tone.lower()} {content_type.lower()} "
            f"within approximately {word_limit} words.\n"
            f"Audience: {audience}.\n"
            f"Purpose: {purpose}.\n"
            f"Use at most 1–2 subtle, professional emojis if appropriate.\n"
            f"Place emojis only in the title or at the very end, not inside paragraphs.\n"
            f"Ensure the content is polished, confident, and well-structured.\n"
            f"End with a complete sentence.\n"
            f"Return plain text only. Do not use HTML or markdown.\n\n"
            f"{prompt}"
        )

        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": final_prompt}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": word_limit + 50,
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

            time.sleep(0.2)

            st.markdown(
                f"""
                <style>
                .editor-box {{
                    background: linear-gradient(180deg, #111827, #0f172a);
                    color: #e5e7eb;
                    padding: 28px;
                    border-radius: 14px;
                    border: 1px solid #1f2937;
                    font-size: 16px;
                    line-height: 1.75;
                    white-space: pre-wrap;
                    animation: fadeInUp 0.4s ease-out;
                }}

                @keyframes fadeInUp {{
                    from {{
                        opacity: 0;
                        transform: translateY(6px);
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
                st.caption("✨ Tip: Adjust inputs and regenerate to refine")
            st.balloons()

        else:
            st.error("Failed to generate content")
            st.code(response.text)