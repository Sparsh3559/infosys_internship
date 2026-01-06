import streamlit as st
import requests
import time
import re
import sys
import os
import json
from Auth_Backend.database import SessionLocal
from Auth_Backend.models import ContentHistory
from datetime import datetime

# -------------------------------
# PAGE CONFIG (Must be first!)
# -------------------------------
st.set_page_config(
    page_title="AI Content Studio",
    page_icon="✨",
    layout="wide"
)
# -------------------------------
# FIX IMPORT PATH (PROJECT ROOT)
# -------------------------------
ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
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
    st.session_state.step = "input"
if "generated_prompts" not in st.session_state:
    st.session_state.generated_prompts = []
if "selected_prompt" not in st.session_state:
    st.session_state.selected_prompt = None
if "final_content" not in st.session_state:
    st.session_state.final_content = None
if "user_idea" not in st.session_state:
    st.session_state.user_idea = ""
if "content_type" not in st.session_state:
    st.session_state.content_type = None
if "tone" not in st.session_state:
    st.session_state.tone = None
if "audience" not in st.session_state:
    st.session_state.audience = None
if "purpose" not in st.session_state:
    st.session_state.purpose = None
if "word_limit" not in st.session_state:
    st.session_state.word_limit = 150
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
# HISTORY UTILITIES (SAFE ADD)
# -------------------------------
def get_user_history(email: str):
    """Fetch all history for a user"""
    db = SessionLocal()
    items = (
        db.query(ContentHistory)
        .filter(ContentHistory.user_email == email)
        .order_by(ContentHistory.created_at.desc())
        .all()
    )
    db.close()
    return items


def delete_history_item(item_id: int):
    """Delete a single history item"""
    db = SessionLocal()
    item = db.query(ContentHistory).filter(ContentHistory.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
    db.close()


def load_history_item(item: ContentHistory):
    """
    Load history back into session (Resume Content)
    Goes to generation screen with same output
    """
    st.session_state.selected_prompt = item.title
    st.session_state.content_type = item.content_type
    st.session_state.tone = item.tone
    st.session_state.audience = item.audience
    st.session_state.purpose = item.purpose
    st.session_state.word_limit = item.word_limit
    st.session_state.final_content = item.generated_content
    st.session_state.step = "generation"
# -------------------------------
# MODERN STYLING
# -------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* ===== GLOBAL RESET ===== */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    html, body, [data-testid="stApp"] {
        background: linear-gradient(135deg, #1a1d29 0%, #0f1117 100%);
        color: #e5e7eb;
    }

    /* ===== SIDEBAR STYLING ===== */
    [data-testid="stSidebar"] {
        background: rgba(17, 24, 39, 0.95);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }

    section[data-testid="stSidebar"] * {
        background-color: transparent !important;
    }

    /* ===== MAIN CONTENT ===== */
    .block-container {
        background-color: transparent;
        padding: 2rem 3rem;
        max-width: 1200px;
    }

    /* ===== INPUT FIELDS ===== */
    .stTextArea textarea,
    .stTextInput input,
    .stSelectbox select {
        background: rgba(31, 41, 55, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        color: #e5e7eb !important;
        padding: 14px 16px !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
    }

    .stTextArea textarea:focus,
    .stTextInput input:focus,
    .stSelectbox select:focus {
        border-color: rgba(99, 102, 241, 0.5) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
        outline: none !important;
    }

    /* ===== BUTTONS ===== */
    .stButton button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    }

    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(99, 102, 241, 0.4) !important;
    }

    .stButton button:active {
        transform: translateY(0) !important;
    }

    .stButton button:disabled {
        background: rgba(75, 85, 99, 0.5) !important;
        box-shadow: none !important;
        cursor: not-allowed !important;
    }

    /* ===== SLIDER ===== */
    .stSlider > div {
        background-color: transparent !important;
    }

    .stSlider [data-baseweb="slider"] {
        background: rgba(99, 102, 241, 0.2);
    }

    /* ===== CARDS ===== */
    .modern-card {
        background: rgba(31, 41, 55, 0.5);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 28px;
        margin: 16px 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .modern-card:hover {
        border-color: rgba(99, 102, 241, 0.3);
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.15);
    }

    /* ===== PROMPT CARDS ===== */
    .prompt-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.8));
        backdrop-filter: blur(20px);
        border: 2px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .prompt-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .prompt-card:hover::before {
        opacity: 1;
    }

    .prompt-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        transform: translateY(-4px);
        box-shadow: 0 12px 35px rgba(99, 102, 241, 0.2);
    }

    .prompt-card.selected {
        border-color: #6366f1;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.1));
    }

    .prompt-title {
        color: #a5b4fc;
        font-weight: 600;
        margin-bottom: 12px;
        font-size: 17px;
        letter-spacing: -0.01em;
    }

    .prompt-text {
        color: #d1d5db;
        line-height: 1.7;
        font-size: 15px;
    }

    /* ===== SELECTED PROMPT DISPLAY ===== */
    .selected-prompt-display {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(139, 92, 246, 0.08));
        border: 2px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 24px;
        margin: 24px 0;
        backdrop-filter: blur(20px);
    }

    /* ===== CONTENT EDITOR BOX ===== */
    .editor-box {
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.9), rgba(15, 23, 42, 0.9));
        backdrop-filter: blur(30px);
        color: #e5e7eb;
        padding: 32px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        font-size: 16px;
        line-height: 1.8;
        white-space: pre-wrap;
        word-wrap: break-word;
        animation: fadeInUp 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(12px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* ===== HEADERS ===== */
    h1, h2, h3 {
        letter-spacing: -0.02em;
        font-weight: 700;
    }

    h2 {
        background: linear-gradient(135deg, #a5b4fc 0%, #c4b5fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* ===== DIVIDERS ===== */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        margin: 24px 0;
    }

    /* ===== CAPTIONS ===== */
    .caption, [data-testid="stCaptionContainer"] {
        color: #9ca3af !important;
        font-size: 14px;
        letter-spacing: 0.01em;
    }

    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        background: rgba(31, 41, 55, 0.4) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
    }

    /* ===== DOWNLOAD BUTTON ===== */
    .stDownloadButton button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    }

    /* ===== STEP INDICATOR ===== */
    .step-indicator {
        background: rgba(99, 102, 241, 0.1);
        border-left: 3px solid #6366f1;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 16px;
        color: #a5b4fc;
        font-size: 14px;
        font-weight: 500;
    }

    /* ===== SUCCESS MESSAGE ===== */
    .success-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        margin-left: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# SIDEBAR (DYNAMIC BASED ON STEP)
# -------------------------------
with st.sidebar:
    st.markdown("## ✨ AI Content Studio")
    st.caption("Transform ideas into polished content")
    st.divider()

    # STEP 1: Initial idea input
    if st.session_state.step == "input":
        st.markdown("### 💡 Step 1: Your Idea")
        prompt = st.text_area(
            "What would you like to create?",
            placeholder="Example: I won first place at a national hackathon by building an AI-powered sustainability tracker...",
            height=150,
            value=st.session_state.user_idea,
            label_visibility="collapsed"
        )
        
        st.caption("✨ Just share your rough idea - we'll refine it")
        st.divider()
        
        generate_prompts_btn = st.button("🎯 Generate Prompts", use_container_width=True)
    
    # STEP 2: Show selected idea
    elif st.session_state.step == "prompt_selection":
        st.markdown('<div class="step-indicator">📝 Your Idea</div>', unsafe_allow_html=True)
        with st.expander("View your idea"):
            st.caption(st.session_state.user_idea)
        st.divider()
        st.markdown("### 🎯 Step 2: Choose Approach")
        st.caption("Select your preferred direction")
    
    # STEP 3: Show selected prompt + preferences form
    elif st.session_state.step == "preferences":
        st.markdown('<div class="step-indicator">✓ Prompt Selected</div>', unsafe_allow_html=True)
        with st.expander("View prompt"):
            st.caption(st.session_state.selected_prompt[:150] + "...")
        
        st.divider()
        st.markdown("### ⚙️ Content Preferences")
        
        content_type_options = ["LinkedIn Post", "Email", "Advertisement", "Blog Post", "Tweet Thread"]
        content_type = st.selectbox(
            "Content Type",
            [""] + content_type_options,
            index=0 if st.session_state.content_type is None else content_type_options.index(st.session_state.content_type) + 1
        )
        if content_type:
            st.session_state.content_type = content_type

        tone_options = ["Professional", "Confident", "Friendly", "Conversational", "Inspirational"]
        tone = st.selectbox(
            "Tone",
            [""] + tone_options,
            index=0 if st.session_state.tone is None else tone_options.index(st.session_state.tone) + 1
        )
        if tone:
            st.session_state.tone = tone

        audience_options = [
            "Recruiters",
            "General Audience",
            "Technical Professionals",
            "Peers & Students",
            "Industry Leaders"
        ]
        audience = st.selectbox(
            "Target Audience",
            [""] + audience_options,
            index=0 if st.session_state.audience is None else audience_options.index(st.session_state.audience) + 1
        )
        if audience:
            st.session_state.audience = audience

        purpose_options = [
            "Share Experience",
            "Showcase Skills",
            "Inspire Others",
            "Announce Achievement"
        ]
        purpose = st.selectbox(
            "Purpose",
            [""] + purpose_options,
            index=0 if st.session_state.purpose is None else purpose_options.index(st.session_state.purpose) + 1
        )
        if purpose:
            st.session_state.purpose = purpose

        word_limit = st.slider(
            "Word Count",
            min_value=80,
            max_value=300,
            step=20,
            value=st.session_state.word_limit
        )
        st.session_state.word_limit = word_limit

        st.divider()
        
        all_selected = (
            st.session_state.content_type and 
            st.session_state.tone and 
            st.session_state.audience and 
            st.session_state.purpose
        )
        
        generate_content_btn = st.button(
            "✨ Generate Content", 
            use_container_width=True,
            disabled=not all_selected
        )
        
        if not all_selected:
            st.caption("⚠️ Complete all fields above")
    
    # STEP 4: Configuration complete
    elif st.session_state.step == "generation":
        st.markdown('<div class="step-indicator">✓ All Set</div>', unsafe_allow_html=True)
        st.caption("Your content is ready!")
    
    # Reset button
    if st.session_state.step != "input":
        st.divider()
        if st.button("🔄 Start New", use_container_width=True):
            st.session_state.step = "input"
            st.session_state.generated_prompts = []
            st.session_state.selected_prompt = None
            st.session_state.final_content = None
            st.session_state.content_type = None
            st.session_state.tone = None
            st.session_state.audience = None
            st.session_state.purpose = None
            st.session_state.word_limit = 150
            st.rerun()

    # -------------------------------
    # HISTORY SECTION
    # -------------------------------
    st.divider()
    st.markdown("### 🕒 History")

    history_search = st.text_input(
        "Search history",
        placeholder="Search by title or content",
        label_visibility="collapsed"
    )

    if "email" in st.session_state:
        history_items = get_user_history(st.session_state["email"])

        if history_search:
            history_items = [
                h for h in history_items
                if history_search.lower() in h.title.lower()
                or history_search.lower() in h.generated_content.lower()
            ]

        for item in history_items:
            with st.expander(f"📄 {item.title}"):
                st.caption(
                    f"{item.content_type} • {item.tone} • "
                    f"{item.audience} • {item.created_at.strftime('%d %b %Y, %I:%M %p')}"
                )

                col_a, col_b = st.columns(2)

                with col_a:
                    if st.button("↩ Resume", key=f"load_{item.id}"):
                        load_history_item(item)
                        st.rerun()

                with col_b:
                    if st.button("🗑 Delete", key=f"delete_{item.id}"):
                        delete_history_item(item.id)
                        st.rerun()

# -------------------------------
# MAIN AREA
# -------------------------------

# STEP 1: Generate Prompt Options
if st.session_state.step == "input":
    st.markdown("## 💭 Start with Your Raw Idea")
    st.caption("Share your thoughts - we'll transform them into clear, actionable prompts")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if 'generate_prompts_btn' in locals() and generate_prompts_btn:
        if not prompt or len(prompt.strip()) < 10:
            st.warning("⚠️ Please share a bit more detail (at least 10 characters)")
        else:
            st.session_state.user_idea = prompt
            
            with st.spinner("🔮 Analyzing and crafting your prompts..."):
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
                        st.error("❌ Failed to generate prompts. Please try again.")
                else:
                    st.error("❌ Connection error. Please try again.")

# STEP 2: Select Refined Prompt
elif st.session_state.step == "prompt_selection":
    st.markdown("## 🎯 Choose Your Direction")
    st.caption("Pick the approach that resonates with your vision")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        prompt_option_1 = st.session_state.generated_prompts[0]
        st.markdown(f"""
        <div class="prompt-card">
            <div class="prompt-title">📝 {prompt_option_1['title']}</div>
            <div class="prompt-text">{prompt_option_1['prompt']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Select This", key="select_prompt_1", use_container_width=True):
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
        
        if st.button("Select This", key="select_prompt_2", use_container_width=True):
            st.session_state.selected_prompt = prompt_option_2['prompt']
            st.session_state.step = "preferences"
            st.rerun()

# STEP 3: Set Preferences
elif st.session_state.step == "preferences":
    st.markdown("## ⚙️ Customize Your Content")
    st.caption("Fine-tune the output to match your needs")
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="selected-prompt-display">
        <div class="prompt-title">Selected Direction:</div>
        <div class="prompt-text">{st.session_state.selected_prompt}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 👈 Configure your preferences in the sidebar")

    if 'generate_content_btn' in locals() and generate_content_btn:
        st.session_state.step = "generation"
        st.rerun()

# STEP 4: Generate Final Content
elif st.session_state.step == "generation":
    st.markdown("## ✨ Your Generated Content")
    st.caption("Crafted with precision based on your preferences")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.final_content is None:
        with st.spinner("🎨 Creating your content..."):
            final_generation_prompt = (
                f"Write a {st.session_state.tone.lower()} {st.session_state.content_type.lower()} "
                f"within approximately {st.session_state.word_limit} words.\n"
                f"Audience: {st.session_state.audience}.\n"
                f"Purpose: {st.session_state.purpose}.\n"
                f"Use at most 1–2 subtle, professional emojis if appropriate.\n"
                f"Place emojis only in the title or at the very end.\n"
                f"Ensure the content is polished, confident, and complete.\n"
                f"End with a full sentence.\n"
                f"Return plain text only. Do not use HTML or markdown.\n\n"
                f"Content to develop:\n{st.session_state.selected_prompt}"
            )
            
            generated_text = call_bedrock_api(final_generation_prompt, max_tokens=st.session_state.word_limit + 50, temperature=0.7)
            
            if generated_text:
                st.session_state.final_content = clean_model_output(generated_text)
           
                # SAVE GENERATED CONTENT TO HISTORY
              
                db = SessionLocal()

                history = ContentHistory(
                    user_email=st.session_state.get("email"),
                    title=st.session_state.selected_prompt[:60],
                    content_type=st.session_state.content_type,
                    tone=st.session_state.tone,
                    audience=st.session_state.audience,
                    purpose=st.session_state.purpose,
                    word_limit=st.session_state.word_limit,
                    generated_content=st.session_state.final_content
                )

                db.add(history)
                db.commit()
                db.close()
                time.sleep(0.3)
                st.rerun()
            else:
                st.error("❌ Generation failed. Please try again.")
    
    if st.session_state.final_content:
        st.markdown(
            f'<div class="editor-box">{st.session_state.final_content}</div>',
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3, gap="medium")

        with col1:
            st.download_button(
                "📥 Download",
                st.session_state.final_content,
                file_name="content.txt",
                use_container_width=True
            )

        with col2:
            if st.button("🔄 Regenerate", use_container_width=True):
                st.session_state.final_content = None
                st.rerun()

        with col3:
            if st.button("← Try Other Prompt", use_container_width=True):
                st.session_state.step = "prompt_selection"
                st.session_state.final_content = None
                st.rerun()

        st.balloons()