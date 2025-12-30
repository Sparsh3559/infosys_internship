import streamlit as st
import requests
import time
import re
import sys
import os
import json

# -------------------------------
# PAGE CONFIG (Must be first!)
# -------------------------------
st.set_page_config(
    page_title="AI Content Studio",
    page_icon="✨",
    layout="wide"
)

# -------------------------------
# FIX IMPORT PATH
# -------------------------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from utils.auth_gaurd import protect

# -------------------------------
# ENABLE AUTH
# -------------------------------
protect()

# -------------------------------
# HIDE DEFAULT PAGE NAVIGATION
# -------------------------------
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

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
# SESSION STATE INITIALIZATION
# -------------------------------
if "step" not in st.session_state:
    st.session_state.step = "input"  # input, prompt_selection, preferences, generation
if "generated_prompts" not in st.session_state:
    st.session_state.generated_prompts = []
if "selected_prompt" not in st.session_state:
    st.session_state.selected_prompt = None
if "final_content" not in st.session_state:
    st.session_state.final_content = None
if "user_idea" not in st.session_state:
    st.session_state.user_idea = ""

# -------------------------------
# UTILITY
# -------------------------------
def clean_model_output(text: str) -> str:
    text = re.sub(r"</?[^>]+>", "", text)
    text = text.replace("<", "").replace(">", "")
    return text.strip()

def call_bedrock_api(prompt: str, max_tokens: int = 500, temperature: float = 0.7):
    """Generic function to call Bedrock API"""
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ],
        "inferenceConfig": {
            "maxTokens": max_tokens,
            "temperature": temperature
        }
    }
    
    response = requests.post(
        BEDROCK_URL,
        headers=HEADERS,
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        return result["output"]["message"]["content"][0]["text"]
    else:
        return None

# -------------------------------
# GLOBAL STYLING
# -------------------------------
st.markdown("""
    <style>
    /* ===== GLOBAL BACKGROUND ===== */
    html, body, [data-testid="stApp"] {
        background-color: #020617;
        color: #e5e7eb;
    }

    /* ===== SIDEBAR FULL DARK ===== */
    [data-testid="stSidebar"] {
        background-color: #020617;
    }

    [data-testid="stSidebar"] > div:first-child {
        background-color: #020617;
    }

    section[data-testid="stSidebar"] * {
        background-color: transparent !important;
    }

    /* ===== MAIN CONTENT AREA ===== */
    .block-container {
        background-color: #020617;
    }

    /* Inputs */
    textarea, input, select {
        background-color: #020617 !important;
        color: #e5e7eb !important;
        border: 1px solid #1f2937 !important;
    }

    /* Buttons */
    button {
        background-color: #020617 !important;
        color: #e5e7eb !important;
        border: 1px solid #1f2937 !important;
    }

    button:hover {
        border-color: #38bdf8 !important;
    }

    /* Sliders */
    .stSlider > div {
        background-color: #020617 !important;
    }

    /* Dividers */
    hr {
        border-color: #1f2937;
    }

    /* Prompt Cards */
    .prompt-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 2px solid #1f2937;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    .prompt-card:hover {
        border-color: #38bdf8;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2);
    }

    .prompt-card.selected {
        border-color: #38bdf8;
        background: linear-gradient(135deg, #1e3a5f, #0f172a);
    }

    .prompt-title {
        color: #38bdf8;
        font-weight: 600;
        margin-bottom: 8px;
        font-size: 18px;
    }

    .prompt-text {
        color: #e5e7eb;
        line-height: 1.6;
    }

    .selected-prompt-display {
        background: linear-gradient(135deg, #1e3a5f, #0f172a);
        border: 2px solid #38bdf8;
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# SIDEBAR (DYNAMIC BASED ON STEP)
# -------------------------------
with st.sidebar:
    st.markdown("## ✨ Content Studio")
    st.caption("Create clear, professional content with intent")
    st.divider()

    # STEP 1: Initial idea input
    if st.session_state.step == "input":
        st.markdown("### Step 1: Your Idea")
        prompt = st.text_area(
            "Describe your rough idea",
            placeholder="Example: I participated in a national-level hackathon and won first place...",
            height=150,
            value=st.session_state.user_idea
        )
        
        st.caption("💡 Don't worry about perfecting it - we'll refine it for you!")
        st.divider()
        
        generate_prompts_btn = st.button("🎯 Generate Prompt Options", use_container_width=True)
    
    # STEP 2: Just show what was selected
    elif st.session_state.step == "prompt_selection":
        st.markdown("### Step 1: Your Idea ✓")
        st.caption(f"_{st.session_state.user_idea[:100]}..._" if len(st.session_state.user_idea) > 100 else f"_{st.session_state.user_idea}_")
        st.divider()
        st.markdown("### Step 2: Choose Prompt")
        st.caption("Select your preferred approach below →")
    
    # STEP 3: Show selected prompt + preferences form
    elif st.session_state.step == "preferences":
        st.markdown("### Selected Prompt ✓")
        with st.expander("View selected prompt"):
            st.write(st.session_state.selected_prompt)
        
        st.divider()
        st.markdown("### Step 3: Preferences")
        
        content_type = st.selectbox(
            "Content type",
            ["LinkedIn Post", "Email", "Advertisement", "Conversation", "Blog Post", "Tweet Thread"],
            index=0
        )

        tone = st.selectbox(
            "Tone",
            ["Professional", "Confident", "Friendly", "Conversational", "Inspirational"],
            index=0
        )

        audience = st.selectbox(
            "Audience",
            [
                "Recruiters / Hiring Managers",
                "General LinkedIn Audience",
                "Technical Audience",
                "Peers / Students",
                "General Public"
            ],
            index=0
        )

        purpose = st.selectbox(
            "Purpose",
            [
                "Share an experience",
                "Showcase skills",
                "Reflect on learning",
                "Announce an achievement",
                "Inspire others"
            ],
            index=0
        )

        word_limit = st.slider(
            "Word length",
            min_value=80,
            max_value=300,
            step=20,
            value=150
        )

        st.caption("Ideal for short professional drafts")
        st.divider()
        
        generate_content_btn = st.button("✨ Generate Content", use_container_width=True)
    
    # STEP 4: Show everything that was selected
    elif st.session_state.step == "generation":
        st.markdown("### Configuration ✓")
        st.caption("All settings locked in")
        with st.expander("View details"):
            st.write(f"**Prompt:** {st.session_state.selected_prompt[:100]}...")
    
    # Reset button (always available after step 1)
    if st.session_state.step != "input":
        st.divider()
        if st.button("🔄 Start Over", use_container_width=True):
            st.session_state.step = "input"
            st.session_state.generated_prompts = []
            st.session_state.selected_prompt = None
            st.session_state.final_content = None
            st.rerun()

# -------------------------------
# MAIN AREA
# -------------------------------

# STEP 1: Generate Prompt Options from Raw Idea
if st.session_state.step == "input":
    st.markdown("## 🎯 Step 1: Start with Your Idea")
    st.caption("Just share your rough thought - we'll help you refine it into two clear prompts")
    
    if 'generate_prompts_btn' in locals() and generate_prompts_btn:
        if not prompt or len(prompt.strip()) < 10:
            st.warning("Please provide a more detailed idea (at least 10 characters).")
        else:
            st.session_state.user_idea = prompt
            
            with st.spinner("🤔 Analyzing your idea and crafting prompt options..."):
                refinement_prompt = f"""You are a prompt engineering expert. A user has shared this rough idea:

"{prompt}"

Your task: Generate 2 different refined prompts that will help create excellent content from this idea. Each prompt should:
- Be clear, specific, and actionable
- Capture the essence of the user's idea
- Offer a slightly different angle or approach
- Be ready to use for content generation

Return your response in this exact JSON format:
{{
    "prompt1": {{
        "title": "Descriptive title (5-7 words)",
        "prompt": "The complete refined prompt text that expands on the user's idea"
    }},
    "prompt2": {{
        "title": "Different descriptive title (5-7 words)",
        "prompt": "An alternative refined prompt with a different angle"
    }}
}}

Make both prompts excellent but distinctly different in their approach."""

                response_text = call_bedrock_api(refinement_prompt, max_tokens=800, temperature=0.8)
                
                if response_text:
                    try:
                        cleaned = clean_model_output(response_text)
                        if "```json" in cleaned:
                            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
                        elif "```" in cleaned:
                            cleaned = cleaned.split("```")[1].split("```")[0].strip()
                        
                        prompts_data = json.loads(cleaned)
                        st.session_state.generated_prompts = [
                            prompts_data["prompt1"],
                            prompts_data["prompt2"]
                        ]
                        st.session_state.step = "prompt_selection"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to parse prompt options. Please try again.")
                        with st.expander("Debug info"):
                            st.code(response_text)
                else:
                    st.error("Failed to generate prompt options. Please try again.")

# STEP 2: Select Refined Prompt
elif st.session_state.step == "prompt_selection":
    st.markdown("## 🎯 Step 2: Choose Your Refined Prompt")
    st.caption("Select the approach that best captures what you want to communicate")
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        prompt_option_1 = st.session_state.generated_prompts[0]
        st.markdown(f"""
        <div class="prompt-card">
            <div class="prompt-title">📝 {prompt_option_1['title']}</div>
            <div class="prompt-text">{prompt_option_1['prompt']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✅ Select This Prompt", key="select_prompt_1", use_container_width=True):
            st.session_state.selected_prompt = prompt_option_1['prompt']
            st.session_state.step = "preferences"
            st.rerun()
    
    with col2:
        prompt_option_2 = st.session_state.generated_prompts[1]
        st.markdown(f"""
        <div class="prompt-card">
            <div class="prompt-title">📝 {prompt_option_2['title']}</div>
            <div class="prompt-text">{prompt_option_2['prompt']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✅ Select This Prompt", key="select_prompt_2", use_container_width=True):
            st.session_state.selected_prompt = prompt_option_2['prompt']
            st.session_state.step = "preferences"
            st.rerun()

# STEP 3: Set Preferences (after prompt selection)
elif st.session_state.step == "preferences":
    st.markdown("## ⚙️ Step 3: Customize Your Content")
    st.caption("Now configure how you want this content delivered")
    
    st.markdown(f"""
    <div class="selected-prompt-display">
        <div class="prompt-title">Your Selected Prompt:</div>
        <div class="prompt-text">{st.session_state.selected_prompt}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 👈 Set your preferences in the sidebar, then click 'Generate Content'")

    if 'generate_content_btn' in locals() and generate_content_btn:
        st.session_state.step = "generation"
        st.rerun()

# STEP 4: Generate Final Content
elif st.session_state.step == "generation":
    st.markdown("## 📝 Your Generated Content")
    st.caption("Crafted from your refined prompt with your preferences")
    st.divider()
    
    if st.session_state.final_content is None:
        # Get the preferences from sidebar
        content_type = st.session_state.get('content_type', 'LinkedIn Post')
        tone = st.session_state.get('tone', 'Professional')
        audience = st.session_state.get('audience', 'General LinkedIn Audience')
        purpose = st.session_state.get('purpose', 'Share an experience')
        word_limit = st.session_state.get('word_limit', 150)
        
        with st.spinner("✨ Crafting your content..."):
            final_generation_prompt = (
                f"Write a {tone.lower()} {content_type.lower()} "
                f"within approximately {word_limit} words.\n"
                f"Audience: {audience}.\n"
                f"Purpose: {purpose}.\n"
                f"Use at most 1–2 subtle, professional emojis if appropriate.\n"
                f"Place emojis only in the title or at the very end.\n"
                f"Ensure the content is polished, confident, and complete.\n"
                f"End with a full sentence.\n"
                f"Return plain text only. Do not use HTML or markdown.\n\n"
                f"Content to develop:\n{st.session_state.selected_prompt}"
            )
            
            generated_text = call_bedrock_api(final_generation_prompt, max_tokens=word_limit + 50, temperature=0.7)
            
            if generated_text:
                st.session_state.final_content = clean_model_output(generated_text)
                time.sleep(0.2)
                st.rerun()
            else:
                st.error("Failed to generate content. Please try again.")
    
    # Display final content
    if st.session_state.final_content:
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
            {st.session_state.final_content}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.download_button(
                "📄 Download Content",
                st.session_state.final_content,
                file_name="generated_content.txt",
                use_container_width=True
            )

        with col2:
            if st.button("🔄 Regenerate", use_container_width=True):
                st.session_state.final_content = None
                st.rerun()

        with col3:
            if st.button("⬅️ Try Other Prompt", use_container_width=True):
                st.session_state.step = "prompt_selection"
                st.session_state.final_content = None
                st.rerun()

        st.balloons()