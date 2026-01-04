import streamlit as st
import requests
import time
import re
import sys
import os
import json
from datetime import datetime

# -------------------------------
# PAGE CONFIG (Must be first!)
# -------------------------------
st.set_page_config(
    page_title="AI Content Studio",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
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
def init_session_state():
    defaults = {
        "page": "new_content",
        "menu_open": False,
        "step": "input",
        "generated_prompts": [],
        "selected_prompt": None,
        "final_content": None,
        "user_idea": "",
        "content_type": None,
        "tone": None,
        "audience": None,
        "purpose": None,
        "word_limit": 150,
        "user_name": "John Doe",
        "user_email": "john@example.com",
        "user_avatar": "👤",
        "saved_drafts": [],
        "templates": [
            {
                "name": "Professional Achievement",
                "content_type": "LinkedIn Post",
                "tone": "Professional",
                "audience": "Recruiters",
                "purpose": "Announce Achievement",
                "word_limit": 150
            },
            {
                "name": "Tech Blog Post",
                "content_type": "Blog Post",
                "tone": "Conversational",
                "audience": "Technical Professionals",
                "purpose": "Share Experience",
                "word_limit": 250
            },
            {
                "name": "Inspirational Story",
                "content_type": "Tweet Thread",
                "tone": "Inspirational",
                "audience": "General Audience",
                "purpose": "Inspire Others",
                "word_limit": 120
            }
        ]
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# -------------------------------
# UTILITY FUNCTIONS
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
    
    try:
        response = requests.post(
            BEDROCK_URL,
            headers=HEADERS,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["output"]["message"]["content"][0]["text"]
    except Exception as e:
        st.error(f"API Error: {str(e)}")
    
    return None

def save_draft(idea, prompt, content, selections):
    """Save draft to history"""
    draft = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "idea": idea[:50] + "..." if len(idea) > 50 else idea,
        "full_idea": idea,
        "prompt": prompt,
        "content": content,
        "selections": selections
    }
    st.session_state.saved_drafts.insert(0, draft)
    if len(st.session_state.saved_drafts) > 50:  # Keep only last 50
        st.session_state.saved_drafts = st.session_state.saved_drafts[:50]

# -------------------------------
# MODERN STYLING
# -------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    html, body, [data-testid="stApp"] {
        background: linear-gradient(135deg, #1a1d29 0%, #0f1117 100%);
        color: #e5e7eb;
    }
    
    .block-container { padding: 0 !important; max-width: 100% !important; }
    
    /* ===== TOP NAVBAR ===== */
    .top-navbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 70px;
        background: rgba(17, 24, 39, 0.95);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 2rem;
        z-index: 1000;
    }
    
    .navbar-left { display: flex; align-items: center; gap: 1.5rem; }
    
    .hamburger {
        width: 40px;
        height: 40px;
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 10px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .hamburger:hover { background: rgba(99, 102, 241, 0.2); }
    .hamburger span {
        width: 20px;
        height: 2px;
        background: #a5b4fc;
        border-radius: 2px;
    }
    
    .app-title {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #a5b4fc 0%, #c4b5fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .navbar-right { display: flex; align-items: center; gap: 1.5rem; }
    
    .user-greeting { color: #9ca3af; font-size: 0.95rem; }
    .user-name { color: #a5b4fc; font-weight: 600; margin-left: 0.3rem; }
    
    .user-avatar {
        width: 45px;
        height: 45px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid rgba(99, 102, 241, 0.3);
    }
    
    .user-avatar:hover { transform: scale(1.05); }
    
    /* ===== SIDE MENU ===== */
    .side-menu {
        position: fixed;
        top: 70px;
        left: -280px;
        width: 280px;
        height: calc(100vh - 70px);
        background: rgba(17, 24, 39, 0.98);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        transition: left 0.3s ease;
        z-index: 999;
        overflow-y: auto;
        padding: 1rem 0;
    }
    
    .side-menu.open { left: 0; }
    
    .menu-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem 1.5rem;
        color: #9ca3af;
        cursor: pointer;
        transition: all 0.3s ease;
        border-left: 3px solid transparent;
    }
    
    .menu-item:hover {
        background: rgba(99, 102, 241, 0.1);
        color: #a5b4fc;
        border-left-color: #6366f1;
    }
    
    .menu-item.active {
        background: rgba(99, 102, 241, 0.15);
        color: #a5b4fc;
        border-left-color: #6366f1;
        font-weight: 600;
    }
    
    /* ===== MAIN CONTENT ===== */
    .main-content {
        margin-top: 70px;
        padding: 2rem 3rem;
        transition: margin-left 0.3s ease;
        min-height: calc(100vh - 70px);
    }
    
    .main-content.shifted { margin-left: 280px; }
    
    /* ===== INPUTS ===== */
    .stTextArea textarea, .stTextInput input, .stSelectbox select {
        background: rgba(31, 41, 55, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        color: #e5e7eb !important;
        padding: 14px 16px !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextArea textarea:focus, .stTextInput input:focus, .stSelectbox select:focus {
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
    
    .stButton button:disabled {
        background: rgba(75, 85, 99, 0.5) !important;
        box-shadow: none !important;
    }
    
    .stDownloadButton button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    }
    
    /* ===== CARDS ===== */
    .content-card {
        background: rgba(31, 41, 55, 0.5);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
    }
    
    .prompt-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.8));
        border: 2px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
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
    
    .prompt-card:hover::before { opacity: 1; }
    .prompt-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        transform: translateY(-4px);
        box-shadow: 0 12px 35px rgba(99, 102, 241, 0.2);
    }
    
    .prompt-title {
        color: #a5b4fc;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    .prompt-text {
        color: #d1d5db;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    .template-card {
        background: rgba(31, 41, 55, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .template-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.15);
    }
    
    .editor-box {
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.9), rgba(15, 23, 42, 0.9));
        backdrop-filter: blur(30px);
        color: #e5e7eb;
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        font-size: 16px;
        line-height: 1.8;
        white-space: pre-wrap;
        word-wrap: break-word;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* ===== MISC ===== */
    h2 {
        background: linear-gradient(135deg, #a5b4fc 0%, #c4b5fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        margin: 1.5rem 0;
    }
    
    .stat-card {
        text-align: center;
        padding: 1.5rem;
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin-top: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# TOP NAVBAR
# -------------------------------
st.markdown(f"""
    <div class="top-navbar">
        <div class="navbar-left">
            <div class="hamburger" id="hamburger-btn">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <div class="app-title">AI Content Studio</div>
        </div>
        <div class="navbar-right">
            <div class="user-greeting">
                Hi, <span class="user-name">{st.session_state.user_name}</span>
            </div>
            <div class="user-avatar" id="profile-btn">
                {st.session_state.user_avatar}
            </div>
        </div>
    </div>
    
    <script>
        const hamburger = document.getElementById('hamburger-btn');
        const profile = document.getElementById('profile-btn');
        
        if (hamburger) {{
            hamburger.onclick = () => {{
                const menuToggle = window.parent.document.querySelector('[data-testid="stButton"] button[kind="primary"]');
                if (menuToggle) menuToggle.click();
            }};
        }}
        
        if (profile) {{
            profile.onclick = () => {{
                const profileBtn = window.parent.document.querySelectorAll('[data-testid="stButton"] button')[1];
                if (profileBtn) profileBtn.click();
            }};
        }}
    </script>
""", unsafe_allow_html=True)

# Hidden interaction buttons
col_menu, col_profile = st.columns(2)
with col_menu:
    if st.button("Toggle Menu", key="menu-toggle", type="primary"):
        st.session_state.menu_open = not st.session_state.menu_open
        st.rerun()

with col_profile:
    if st.button("Profile", key="profile-click"):
        st.session_state.page = "settings"
        st.rerun()

# -------------------------------
# SIDE MENU
# -------------------------------
menu_class = "side-menu open" if st.session_state.menu_open else "side-menu"
st.markdown(f'<div class="{menu_class}" id="side-menu">', unsafe_allow_html=True)

menu_items = [
    ("🏠", "Dashboard", "dashboard"),
    ("✨", "New Content", "new_content"),
    ("📁", "Saved Drafts", "drafts"),
    ("📋", "Templates", "templates"),
    ("⚙️", "Account Settings", "settings"),
    ("🚪", "Logout", "logout")
]

for icon, label, page_key in menu_items:
    active = "active" if st.session_state.page == page_key else ""
    st.markdown(f'<div class="menu-item {active}" style="font-size: 0.95rem;">{icon} {label}</div>', unsafe_allow_html=True)
    
    if st.button(label, key=f"nav_{page_key}"):
        if page_key == "logout":
            # Clear session and redirect to login
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("pages/Login.py")
        else:
            st.session_state.page = page_key
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# MAIN CONTENT AREA
# -------------------------------
content_class = "main-content shifted" if st.session_state.menu_open else "main-content"
st.markdown(f'<div class="{content_class}">', unsafe_allow_html=True)

# ========== DASHBOARD PAGE ==========
if st.session_state.page == "dashboard":
    st.markdown("## 📊 Dashboard")
    st.caption("Overview of your content creation activity")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="content-card stat-card">
                <div style="color: #6366f1; font-weight: 600;">Total Drafts</div>
                <div class="stat-value" style="color: #a5b4fc;">{len(st.session_state.saved_drafts)}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="content-card stat-card">
                <div style="color: #8b5cf6; font-weight: 600;">Templates</div>
                <div class="stat-value" style="color: #c4b5fd;">{len(st.session_state.templates)}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        recent_count = len([d for d in st.session_state.saved_drafts if d['timestamp'].startswith(datetime.now().strftime("%Y-%m"))])
        st.markdown(f"""
            <div class="content-card stat-card">
                <div style="color: #10b981; font-weight: 600;">This Month</div>
                <div class="stat-value" style="color: #34d399;">{recent_count}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Recent Activity
    if st.session_state.saved_drafts:
        st.markdown("### 📝 Recent Activity")
        for draft in st.session_state.saved_drafts[:5]:
            st.markdown(f"""
                <div class="content-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="color: #a5b4fc; font-weight: 600; margin-bottom: 0.3rem;">{draft['idea']}</div>
                            <div style="color: #6b7280; font-size: 0.85rem;">{draft['timestamp']}</div>
                        </div>
                        <div style="color: #9ca3af; font-size: 0.9rem;">
                            {draft['selections'].get('content_type', 'N/A')}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# ========== NEW CONTENT PAGE ==========
elif st.session_state.page == "new_content":
    
    # STEP 1: Input Idea
    if st.session_state.step == "input":
        st.markdown("## 💭 Start with Your Idea")
        st.caption("Share your thoughts - we'll transform them into refined prompts")
        
        idea = st.text_area(
            "Your Idea",
            placeholder="Example: I won first place at a national hackathon by building an AI-powered sustainability tracker...",
            height=150,
            value=st.session_state.user_idea
        )
        
        if st.button("🎯 Generate Prompts", use_container_width=True):
            if len(idea.strip()) < 10:
                st.warning("⚠️ Please provide more detail (at least 10 characters)")
            else:
                st.session_state.user_idea = idea
                
                with st.spinner("🔮 Analyzing and crafting prompts..."):
                    refinement_prompt = f"""You are a prompt engineering expert. Generate 2 different refined prompts from this idea:

"{idea}"

Each prompt should be clear, specific, and offer a different angle.

Return ONLY valid JSON in this format:
{{
    "prompt1": {{"title": "Short title", "prompt": "Full refined prompt"}},
    "prompt2": {{"title": "Different title", "prompt": "Alternative refined prompt"}}
}}"""
                    
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
                            st.error(f"❌ Failed to parse prompts. Please try again.")
                    else:
                        st.error("❌ Failed to connect to API. Please try again.")
    
    # STEP 2: Select Prompt
    elif st.session_state.step == "prompt_selection":
        st.markdown("## 🎯 Choose Your Direction")
        st.caption("Select the approach that best fits your vision")
        
        col1, col2 = st.columns(2, gap="large")
        
        for idx, col in enumerate([col1, col2]):
            with col:
                opt = st.session_state.generated_prompts[idx]
                st.markdown(f"""
                    <div class="prompt-card">
                        <div class="prompt-title">📝 {opt['title']}</div>
                        <div class="prompt-text">{opt['prompt']}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Select This Prompt", key=f"select_{idx}", use_container_width=True):
                    st.session_state.selected_prompt = opt['prompt']
                    st.session_state.step = "preferences"
                    st.rerun()
    
    # STEP 3: Set Preferences
    elif st.session_state.step == "preferences":
        st.markdown("## ⚙️ Customize Your Content")
        st.caption("Configure preferences to match your needs")
        
        st.markdown(f"""
            <div class="content-card">
                <div class="prompt-title">Selected Prompt:</div>
                <div class="prompt-text">{st.session_state.selected_prompt}</div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            content_type = st.selectbox(
                "Content Type",
                [""] + ["LinkedIn Post", "Email", "Advertisement", "Blog Post", "Tweet Thread"],
                index=0 if not st.session_state.content_type else [""] + ["LinkedIn Post", "Email", "Advertisement", "Blog Post", "Tweet Thread"].index(st.session_state.content_type)
            )
            
            tone = st.selectbox(
                "Tone",
                [""] + ["Professional", "Confident", "Friendly", "Conversational", "Inspirational"],
                index=0 if not st.session_state.tone else [""] + ["Professional", "Confident", "Friendly", "Conversational", "Inspirational"].index(st.session_state.tone)
            )
            
            audience = st.selectbox(
                "Target Audience",
                [""] + ["Recruiters", "General Audience", "Technical Professionals", "Peers & Students", "Industry Leaders"],
                index=0 if not st.session_state.audience else [""] + ["Recruiters", "General Audience", "Technical Professionals", "Peers & Students", "Industry Leaders"].index(st.session_state.audience)
            )
        
        with col2:
            purpose = st.selectbox(
                "Purpose",
                [""] + ["Share Experience", "Showcase Skills", "Inspire Others", "Announce Achievement"],
                index=0 if not st.session_state.purpose else [""] + ["Share Experience", "Showcase Skills", "Inspire Others", "Announce Achievement"].index(st.session_state.purpose)
            )
            
            word_limit = st.slider(
                "Word Count",
                min_value=80,
                max_value=300,
                step=20,
                value=st.session_state.word_limit
            )
        
        if content_type and tone and audience and purpose:
            st.session_state.content_type = content_type
            st.session_state.tone = tone
            st.session_state.audience = audience
            st.session_state.purpose = purpose
            st.session_state.word_limit = word_limit
            
            if st.button("✨ Generate Content", use_container_width=True):
                st.session_state.step = "generation"
                st.rerun()
        else:
            st.info("ℹ️ Please complete all fields above to continue")
    
    # STEP 4: Generate Content
    elif st.session_state.step == "generation":
        st.markdown("## ✨ Your Generated Content")
        st.caption("Crafted with precision based on your preferences")
        
        if not st.session_state.final_content:
            with st.spinner("🎨 Creating your content..."):
                generation_prompt = f"""Write a {st.session_state.tone.lower()} {st.session_state.content_type.lower()} in approximately {st.session_state.word_limit} words.

Audience: {st.session_state.audience}
Purpose: {st.session_state.purpose}

Use 1-2 professional emojis if appropriate. Return plain text only, no markdown or HTML.

Content to develop:
{st.session_state.selected_prompt}"""
                
                generated_text = call_bedrock_api(generation_prompt, max_tokens=st.session_state.word_limit + 50, temperature=0.7)
                
                if generated_text:
                    st.session_state.final_content = clean_model_output(generated_text)
                    
                    # Save to drafts
                    save_draft(
                        st.session_state.user_idea,
                        st.session_state.selected_prompt,
                        st.session_state.final_content,
                        {
                            "content_type": st.session_state.content_type,
                            "tone": st.session_state.tone,
                            "audience": st.session_state.audience,
                            "purpose": st.session_state.purpose,
                            "word_limit": st.session_state.word_limit
                        }
                    )
                    st.rerun()
                else:
                    st.error("❌ Generation failed. Please try again.")
        
        if st.session_state.final_content:
            st.markdown(f'<div class="editor-box">{st.session_state.final_content}</div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3, gap="medium")
            
            with col1:
                st.download_button(
                    "📥 Download Content",
                    st.session_state.final_content,
                    file_name="generated_content.txt",
                    use_container_width=True
                )
            
            with col2:
                if st.button("🔄 Regenerate", use_container_width=True):
                    st.session_state.final_content = None
                    st.rerun()
            
            with col3:
                if st.button("🔙 Start Over", use_container_width=True):
                    st.session_state.step = "input"
                    st.session_state.final_content = None
                    st.session_state.user_idea = ""
                    st.session_state.selected_prompt = None
                    st.session_state.generated_prompts = []
                    st.rerun()
            
            st.success("✅ Content saved to Saved Drafts!")

# ========== SAVED DRAFTS PAGE ==========
elif st.session_state.page == "drafts":
    st.markdown("## 📁 Saved Drafts")
    st.caption(f"You have {len(st.session_state.saved_drafts)} saved drafts")
    
    if not st.session_state.saved_drafts:
        st.info("📝 No drafts yet. Create your first content from the 'New Content' page!")
        
        if st.button("➕ Create New Content", use_container_width=True):
            st.session_state.page = "new_content"
            st.rerun()
    else:
        # Display drafts
        for idx, draft in enumerate(st.session_state.saved_drafts):
            with st.expander(f"📄 {draft['idea']} - {draft['timestamp']}", expanded=False):
                st.markdown("### 📋 Selections")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Content Type:** {draft['selections'].get('content_type', 'N/A')}")
                    st.markdown(f"**Tone:** {draft['selections'].get('tone', 'N/A')}")
                
                with col2:
                    st.markdown(f"**Audience:** {draft['selections'].get('audience', 'N/A')}")
                    st.markdown(f"**Purpose:** {draft['selections'].get('purpose', 'N/A')}")
                
                st.markdown(f"**Word Limit:** {draft['selections'].get('word_limit', 'N/A')}")
                
                st.markdown("---")
                
                st.markdown("### 💡 Original Idea")
                st.write(draft.get('full_idea', draft['idea']))
                
                st.markdown("### 🎯 Refined Prompt")
                st.info(draft['prompt'])
                
                st.markdown("### ✨ Generated Content")
                st.markdown(f'<div class="editor-box">{draft["content"]}</div>', unsafe_allow_html=True)
                
                # Action buttons for each draft
                col_a, col_b = st.columns(2)
                with col_a:
                    st.download_button(
                        "📥 Download",
                        draft['content'],
                        file_name=f"draft_{draft['timestamp'].replace(':', '-').replace(' ', '_')}.txt",
                        key=f"download_draft_{idx}"
                    )
                
                with col_b:
                    if st.button("🗑️ Delete", key=f"delete_draft_{idx}"):
                        st.session_state.saved_drafts.pop(idx)
                        st.success("Draft deleted!")
                        time.sleep(0.5)
                        st.rerun()

# ========== TEMPLATES PAGE ==========
elif st.session_state.page == "templates":
    st.markdown("## 📋 Content Templates")
    st.caption("Pre-configured templates for quick content creation")
    
    for idx, template in enumerate(st.session_state.templates):
        st.markdown(f"""
            <div class="template-card">
                <div style="color: #a5b4fc; font-weight: 600; font-size: 1.1rem; margin-bottom: 0.8rem;">
                    ✨ {template['name']}
                </div>
                <div style="color: #9ca3af; font-size: 0.9rem; line-height: 1.6;">
                    <strong>Type:</strong> {template['content_type']}<br>
                    <strong>Tone:</strong> {template['tone']}<br>
                    <strong>Audience:</strong> {template['audience']}<br>
                    <strong>Purpose:</strong> {template['purpose']}<br>
                    <strong>Word Limit:</strong> {template['word_limit']} words
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"🚀 Use This Template", key=f"use_template_{idx}", use_container_width=True):
            # Load template settings
            st.session_state.content_type = template['content_type']
            st.session_state.tone = template['tone']
            st.session_state.audience = template['audience']
            st.session_state.purpose = template['purpose']
            st.session_state.word_limit = template['word_limit']
            
            # Go to new content page
            st.session_state.page = "new_content"
            st.session_state.step = "input"
            
            st.success(f"✅ Template '{template['name']}' loaded! Now enter your idea to continue.")
            time.sleep(1.5)
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)

# ========== SETTINGS PAGE ==========
elif st.session_state.page == "settings":
    st.markdown("## ⚙️ Account Settings")
    st.caption("Manage your profile information")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
            <div class="content-card" style="text-align: center;">
                <div style="font-size: 5rem; margin: 1rem 0;">{st.session_state.user_avatar}</div>
                <div style="color: #9ca3af; font-size: 0.9rem;">Profile Avatar</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        
        name = st.text_input("Full Name", value=st.session_state.user_name, placeholder="John Doe")
        email = st.text_input("Email Address", value=st.session_state.user_email, placeholder="john@example.com")
        avatar = st.text_input("Avatar Emoji", value=st.session_state.user_avatar, max_chars=2, placeholder="👤")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        col_save, col_reset = st.columns(2)
        
        with col_save:
            if st.button("💾 Save Changes", use_container_width=True):
                st.session_state.user_name = name
                st.session_state.user_email = email
                st.session_state.user_avatar = avatar if avatar else "👤"
                st.success("✅ Settings saved successfully!")
                time.sleep(1)
                st.rerun()
        
        with col_reset:
            if st.button("🔄 Reset to Default", use_container_width=True):
                st.session_state.user_name = "John Doe"
                st.session_state.user_email = "john@example.com"
                st.session_state.user_avatar = "👤"
                st.info("ℹ️ Settings reset to default values")
                time.sleep(1)
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Account statistics
    st.markdown("### 📊 Account Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="content-card" style="text-align: center;">
                <div style="color: #6b7280; font-size: 0.9rem;">Total Drafts</div>
                <div style="font-size: 2rem; font-weight: 700; color: #6366f1; margin-top: 0.5rem;">
                    {len(st.session_state.saved_drafts)}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="content-card" style="text-align: center;">
                <div style="color: #6b7280; font-size: 0.9rem;">Available Templates</div>
                <div style="font-size: 2rem; font-weight: 700; color: #8b5cf6; margin-top: 0.5rem;">
                    {len(st.session_state.templates)}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        recent_count = len([d for d in st.session_state.saved_drafts if d['timestamp'].startswith(datetime.now().strftime("%Y-%m"))])
        st.markdown(f"""
            <div class="content-card" style="text-align: center;">
                <div style="color: #6b7280; font-size: 0.9rem;">This Month</div>
                <div style="font-size: 2rem; font-weight: 700; color: #10b981; margin-top: 0.5rem;">
                    {recent_count}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Danger zone
    st.markdown("### ⚠️ Danger Zone")
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    st.warning("🗑️ **Clear All Drafts** - This action cannot be undone")
    
    if st.button("🗑️ Clear All Drafts", use_container_width=True):
        st.session_state.saved_drafts = []
        st.success("✅ All drafts have been cleared")
        time.sleep(1)
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)