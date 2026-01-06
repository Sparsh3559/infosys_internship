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
    initial_sidebar_state="expanded"
)

# -------------------------------
# FIX IMPORT PATH (PROJECT ROOT)
# -------------------------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Import database and auth
try:
    from Auth_Backend.database import SessionLocal, init_db
    from Auth_Backend.models import ContentHistory
    from utils.auth_gaurd import protect
    
    # Initialize database tables if needed
    import os
    if not os.path.exists("users.db"):
        init_db()
    
    protect()
except ImportError as e:
    st.error(f"Import Error: {str(e)}")
    st.stop()

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
        "user_name": st.session_state.get("name", "User"),
        "user_email": st.session_state.get("email", "user@example.com"),
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
# DATABASE UTILITIES
# -------------------------------
def get_user_history(email: str):
    """Fetch all history for a user"""
    try:
        db = SessionLocal()
        items = (
            db.query(ContentHistory)
            .filter(ContentHistory.user_email == email)
            .order_by(ContentHistory.created_at.desc())
            .all()
        )
        db.close()
        return items
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return []

def delete_history_item(item_id: int):
    """Delete a single history item"""
    try:
        db = SessionLocal()
        item = db.query(ContentHistory).filter(ContentHistory.id == item_id).first()
        if item:
            db.delete(item)
            db.commit()
        db.close()
    except Exception as e:
        st.error(f"Delete error: {str(e)}")

def load_history_item(item: ContentHistory):
    """Load history back into session"""
    st.session_state.selected_prompt = item.title
    st.session_state.content_type = item.content_type
    st.session_state.tone = item.tone
    st.session_state.audience = item.audience
    st.session_state.purpose = item.purpose
    st.session_state.word_limit = item.word_limit
    st.session_state.final_content = item.generated_content
    st.session_state.step = "generation"
    st.session_state.page = "new_content"

def save_to_database(email, title, content_type, tone, audience, purpose, word_limit, content):
    """Save generated content to database"""
    try:
        db = SessionLocal()
        history = ContentHistory(
            user_email=email,
            title=title[:60],
            content_type=content_type,
            tone=tone,
            audience=audience,
            purpose=purpose,
            word_limit=word_limit,
            generated_content=content
        )
        db.add(history)
        db.commit()
        db.close()
        return True
    except Exception as e:
        st.error(f"Save error: {str(e)}")
        return False

# -------------------------------
# UTILITY FUNCTIONS
# -------------------------------
def clean_model_output(text: str) -> str:
    text = re.sub(r"</?[^>]+>", "", text)
    text = text.replace("<", "").replace(">", "")
    return text.strip()

def call_bedrock_api(prompt: str, max_tokens: int = 500, temperature: float = 0.7):
    """Call Bedrock API"""
    payload = {
        "messages": [{"role": "user", "content": [{"text": prompt}]}],
        "inferenceConfig": {"maxTokens": max_tokens, "temperature": temperature}
    }
    
    try:
        response = requests.post(BEDROCK_URL, headers=HEADERS, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()["output"]["message"]["content"][0]["text"]
    except Exception as e:
        st.error(f"API Error: {str(e)}")
    return None

# -------------------------------
# MODERN STYLING - MATCHING REFERENCE DESIGN
# -------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* DARK THEME BASE */
    html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"] {
        background: #0f1117 !important;
        color: #e5e7eb !important;
    }
    
    .main .block-container {
        padding: 2rem 3rem !important;
        max-width: 100% !important;
    }
    
    /* SIDEBAR STYLING - MATCHING REFERENCE */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1d29 0%, #13151f 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }
    
    /* Sidebar Navigation Items */
    .sidebar-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.85rem 1.2rem;
        margin: 0.25rem 0.8rem;
        border-radius: 10px;
        color: #9ca3af;
        font-size: 0.95rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        border-left: 3px solid transparent;
    }
    
    .sidebar-item:hover {
        background: rgba(139, 92, 246, 0.08);
        color: #c4b5fd;
        border-left-color: #8b5cf6;
    }
    
    .sidebar-item.active {
        background: linear-gradient(90deg, rgba(139, 92, 246, 0.15), transparent);
        color: #c4b5fd;
        border-left-color: #8b5cf6;
        font-weight: 600;
    }
    
    .sidebar-item svg, .sidebar-item i {
        font-size: 1.2rem;
        width: 20px;
        height: 20px;
    }
    
    /* TOP HEADER BAR */
    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }
    
    .header-title {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #c4b5fd 0%, #a78bfa 50%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .header-actions {
        display: flex;
        gap: 1rem;
        align-items: center;
    }
    
    /* MODERN CARDS */
    .content-card {
        background: linear-gradient(135deg, rgba(31, 41, 55, 0.4), rgba(17, 24, 39, 0.6));
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .content-card:hover {
        border-color: rgba(139, 92, 246, 0.3);
        box-shadow: 0 8px 30px rgba(139, 92, 246, 0.15);
    }
    
    .card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #e5e7eb;
        margin-bottom: 1rem;
    }
    
    .card-subtitle {
        font-size: 0.875rem;
        color: #9ca3af;
        margin-bottom: 1.5rem;
    }
    
    /* FORM INPUTS - CLEAN & MODERN */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background: rgba(31, 41, 55, 0.5) !important;
        border: 1.5px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #e5e7eb !important;
        padding: 0.85rem 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.25s ease !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15) !important;
        outline: none !important;
    }
    
    .stTextArea textarea {
        min-height: 120px !important;
    }
    
    /* LABELS */
    .stTextInput label, .stTextArea label, .stSelectbox label, .stSlider label {
        color: #d1d5db !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* GRADIENT BUTTON - PRIMARY */
    .stButton button {
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.85rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3) !important;
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(139, 92, 246, 0.5) !important;
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%) !important;
    }
    
    .stButton button:active {
        transform: translateY(0) !important;
    }
    
    /* DOWNLOAD BUTTON */
    .stDownloadButton button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
    }
    
    .stDownloadButton button:hover {
        box-shadow: 0 6px 25px rgba(16, 185, 129, 0.5) !important;
    }
    
    /* PROMPT SELECTION CARDS */
    .prompt-card {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(124, 58, 237, 0.05));
        border: 2px solid rgba(139, 92, 246, 0.15);
        border-radius: 16px;
        padding: 1.8rem;
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
        height: 4px;
        background: linear-gradient(90deg, #8b5cf6, #a78bfa, #c4b5fd);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .prompt-card:hover {
        border-color: rgba(139, 92, 246, 0.4);
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(139, 92, 246, 0.25);
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.12), rgba(124, 58, 237, 0.08));
    }
    
    .prompt-card:hover::before {
        opacity: 1;
    }
    
    .prompt-title {
        color: #c4b5fd;
        font-weight: 600;
        font-size: 1.15rem;
        margin-bottom: 0.75rem;
    }
    
    .prompt-text {
        color: #d1d5db;
        line-height: 1.7;
        font-size: 0.95rem;
    }
    
    /* GENERATED CONTENT DISPLAY */
    .generated-output {
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.95), rgba(31, 41, 55, 0.9));
        backdrop-filter: blur(30px);
        color: #e5e7eb;
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid rgba(139, 92, 246, 0.2);
        font-size: 1rem;
        line-height: 1.8;
        white-space: pre-wrap;
        word-wrap: break-word;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    
    /* SLIDER */
    .stSlider {
        padding: 1rem 0;
    }
    
    .stSlider [data-baseweb="slider"] {
        background: rgba(139, 92, 246, 0.15);
        border-radius: 8px;
        padding: 0.5rem;
    }
    
    /* STATS CARDS */
    .stat-card {
        text-align: center;
        padding: 1.8rem 1.2rem;
    }
    
    .stat-value {
        font-size: 2.8rem;
        font-weight: 700;
        margin-top: 0.5rem;
        background: linear-gradient(135deg, #8b5cf6, #c4b5fd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stat-label {
        color: #9ca3af;
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* EXPANDER */
    .streamlit-expanderHeader {
        background: rgba(31, 41, 55, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        color: #e5e7eb;
        font-weight: 500;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(31, 41, 55, 0.6);
        border-color: rgba(139, 92, 246, 0.3);
    }
    
    /* HIDE STREAMLIT BRANDING */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* SCROLLBAR */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(31, 41, 55, 0.3);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(139, 92, 246, 0.5);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(139, 92, 246, 0.7);
    }
    
    /* DIVIDER */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.3), transparent);
        margin: 2rem 0;
    }
    
    /* SUCCESS/ERROR MESSAGES */
    .stSuccess, .stInfo, .stWarning, .stError {
        background: rgba(31, 41, 55, 0.6) !important;
        border-radius: 12px !important;
        border-left: 4px solid #8b5cf6 !important;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# SIDEBAR NAVIGATION
# -------------------------------
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0 1rem 0;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">✨</div>
            <div style="font-size: 1.4rem; font-weight: 700; background: linear-gradient(135deg, #c4b5fd, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                AI Content Studio
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 1rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # Navigation items
    nav_items = [
        ("🏠", "Dashboard", "dashboard"),
        ("✨", "New Content", "new_content"),
        ("📁", "Saved Drafts", "history"),
        ("📋", "Templates", "templates"),
        ("⚙️", "Account Settings", "settings"),
    ]
    
    for icon, label, page_key in nav_items:
        active_class = "active" if st.session_state.page == page_key else ""
        st.markdown(f'<div class="sidebar-item {active_class}">{icon} <span>{label}</span></div>', unsafe_allow_html=True)
        
        if st.button(label, key=f"nav_{page_key}", use_container_width=True):
            st.session_state.page = page_key
            st.rerun()
    
    st.markdown("<hr style='margin: 2rem 0 1rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # User section at bottom
    st.markdown(f"""
        <div style="padding: 1rem; text-align: center; margin-top: auto;">
            <div style="width: 60px; height: 60px; margin: 0 auto 0.75rem; background: linear-gradient(135deg, #8b5cf6, #c4b5fd); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; border: 3px solid rgba(139, 92, 246, 0.3);">
                👤
            </div>
            <div style="color: #e5e7eb; font-weight: 600; font-size: 1rem; margin-bottom: 0.25rem;">
                {st.session_state.user_name}
            </div>
            <div style="color: #6b7280; font-size: 0.85rem;">
                {st.session_state.user_email}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("pages/Login.py")

# -------------------------------
# MAIN CONTENT AREA
# -------------------------------

# ========== DASHBOARD PAGE ==========
if st.session_state.page == "dashboard":
    st.markdown('<div class="header-title">Dashboard</div>', unsafe_allow_html=True)
    st.caption("Overview of your content creation activity")
    st.markdown("<br>", unsafe_allow_html=True)
    
    user_email = st.session_state.get("email", "")
    history_items = get_user_history(user_email) if user_email else []
    recent_count = len([h for h in history_items if h.created_at.strftime("%Y-%m") == datetime.now().strftime("%Y-%m")])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="content-card stat-card">
                <div class="stat-label">Total Content</div>
                <div class="stat-value">{len(history_items)}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="content-card stat-card">
                <div class="stat-label">Templates</div>
                <div class="stat-value">{len(st.session_state.templates)}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="content-card stat-card">
                <div class="stat-label">This Month</div>
                <div class="stat-value">{recent_count}</div>
            </div>
        """, unsafe_allow_html=True)
    
    if history_items:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📝 Recent Activity")
        
        for item in history_items[:5]:
            st.markdown(f"""
                <div class="content-card">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <div style="color: #c4b5fd; font-weight: 600; font-size: 1.05rem; margin-bottom: 0.4rem;">{item.title}</div>
                            <div style="color: #6b7280; font-size: 0.875rem;">{item.created_at.strftime('%d %b %Y, %I:%M %p')}</div>
                        </div>
                        <div style="color: #9ca3af; font-size: 0.9rem; padding: 0.4rem 1rem; background: rgba(139, 92, 246, 0.1); border-radius: 8px;">
                            {item.content_type}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# ========== NEW CONTENT PAGE ==========
elif st.session_state.page == "new_content":
    
    if st.session_state.step == "input":
        st.markdown('<div class="header-title">Create New Content</div>', unsafe_allow_html=True)
        st.caption("Start with your idea and we'll help you craft the perfect prompt")
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">💭 Share Your Idea</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-subtitle">Tell us what you want to create - be as detailed as you like</div>', unsafe_allow_html=True)
        
        idea = st.text_area(
            "Your Idea",
            placeholder="Example: I recently won first place at a national hackathon for developing an AI-powered healthcare app...",
            height=180,
            value=st.session_state.user_idea,
            label_visibility="collapsed"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("🎯 Generate Prompts", use_container_width=True):
            if len(idea.strip()) < 10:
                st.warning("⚠️ Please provide more detail about your idea")
            else:
                st.session_state.user_idea = idea
                
                with st.spinner("🔮 Crafting refined prompts..."):
                    prompt = f"""Generate 2 different refined prompts from: "{idea}"
Return JSON: {{"prompt1": {{"title": "...", "prompt": "..."}}, "prompt2": {{"title": "...", "prompt": "..."}}}}"""
                    
                    response = call_bedrock_api(prompt, 800, 0.8)
                    if response:
                        try:
                            cleaned = clean_model_output(response)
                            if "```json" in cleaned:
                                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
                            prompts_data = json.loads(cleaned)
                            st.session_state.generated_prompts = [prompts_data["prompt1"], prompts_data["prompt2"]]
                            st.session_state.step = "prompt_selection"
                            st.rerun()
                        except:
                            st.error("❌ Failed to generate prompts. Please try again.")
                    else:
                        st.error("❌ Connection error. Please check your API settings.")
    
    elif st.session_state.step == "prompt_selection":
        st.markdown('<div class="header-title">Choose Your Direction</div>', unsafe_allow_html=True)
        st.caption("Select the prompt that best aligns with your vision")
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        for idx, col in enumerate([col1, col2]):
            with col:
                opt = st.session_state.generated_prompts[idx]
                st.markdown(f"""
                    <div class="prompt-card">
                        <div class="prompt-title">{opt['title']}</div>
                        <div class="prompt-text">{opt['prompt']}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("Select This Prompt", key=f"sel_{idx}", use_container_width=True):
                    st.session_state.selected_prompt = opt['prompt']
                    st.session_state.step = "preferences"
                    st.rerun()
    
    elif st.session_state.step == "preferences":
        st.markdown('<div class="header-title">Content Preferences</div>', unsafe_allow_html=True)
        st.caption("Fine-tune how your content will be generated")
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="content-card">
                <div class="card-title">📌 Selected Prompt</div>
                <div class="prompt-text" style="margin-top: 1rem;">{st.session_state.selected_prompt}</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">⚙️ Configure Your Content</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            content_type = st.selectbox(
                "Content Type",
                [""] + ["LinkedIn Post", "Email", "Blog Post", "Tweet Thread", "Instagram Caption"],
                key="sel_content_type"
            )
            
            tone = st.selectbox(
                "Tone",
                [""] + ["Professional", "Confident", "Friendly", "Inspirational", "Conversational"],
                key="sel_tone"
            )
            
            audience = st.selectbox(
                "Target Audience",
                [""] + ["Recruiters", "General Audience", "Technical Professionals", "Business Leaders"],
                key="sel_audience"
            )
        
        with col2:
            purpose = st.selectbox(
                "Purpose",
                [""] + ["Share Experience", "Showcase Skills", "Inspire Others", "Announce Achievement"],
                key="sel_purpose"
            )
            
            word_limit = st.slider("Word Count", 80, 400, 150, 20, key="sel_word_limit")
            
            st.markdown(f"""
                <div style="margin-top: 1rem; padding: 1rem; background: rgba(139, 92, 246, 0.1); border-radius: 10px; border-left: 3px solid #8b5cf6;">
                    <div style="color: #9ca3af; font-size: 0.85rem; margin-bottom: 0.3rem;">Word Limit</div>
                    <div style="color: #c4b5fd; font-weight: 600; font-size: 1.5rem;">{word_limit} words</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
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
            st.info("ℹ️ Please fill in all preferences to continue")
    
    elif st.session_state.step == "generation":
        st.markdown('<div class="header-title">Generated Content</div>', unsafe_allow_html=True)
        st.caption("Your AI-crafted content is ready")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if not st.session_state.final_content:
            with st.spinner("🎨 Creating your content..."):
                prompt = f"""Write a {st.session_state.tone} {st.session_state.content_type} in approximately {st.session_state.word_limit} words.
Audience: {st.session_state.audience}
Purpose: {st.session_state.purpose}
Content: {st.session_state.selected_prompt}

Create engaging, authentic content that resonates with the target audience."""
                
                content = call_bedrock_api(prompt, st.session_state.word_limit + 100, 0.7)
                if content:
                    st.session_state.final_content = clean_model_output(content)
                    
                    # Save to database
                    save_to_database(
                        st.session_state.get("email", ""),
                        st.session_state.selected_prompt,
                        st.session_state.content_type,
                        st.session_state.tone,
                        st.session_state.audience,
                        st.session_state.purpose,
                        st.session_state.word_limit,
                        st.session_state.final_content
                    )
                    st.rerun()
        
        if st.session_state.final_content:
            st.markdown(f'<div class="generated-output">{st.session_state.final_content}</div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    "📥 Download Content",
                    st.session_state.final_content,
                    "content.txt",
                    use_container_width=True
                )
            
            with col2:
                if st.button("🔄 Regenerate", use_container_width=True):
                    st.session_state.final_content = None
                    st.rerun()
            
            with col3:
                if st.button("🆕 New Content", use_container_width=True):
                    st.session_state.step = "input"
                    st.session_state.final_content = None
                    st.session_state.user_idea = ""
                    st.rerun()

# ========== HISTORY PAGE ==========
elif st.session_state.page == "history":
    st.markdown('<div class="header-title">Saved Drafts</div>', unsafe_allow_html=True)
    st.caption("Access all your previously generated content")
    st.markdown("<br>", unsafe_allow_html=True)
    
    user_email = st.session_state.get("email", "")
    history_items = get_user_history(user_email) if user_email else []
    
    if not history_items:
        st.markdown("""
            <div class="content-card" style="text-align: center; padding: 3rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📝</div>
                <div style="color: #9ca3af; font-size: 1.1rem;">No saved content yet</div>
                <div style="color: #6b7280; font-size: 0.9rem; margin-top: 0.5rem;">Create your first content to see it here</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style="color: #9ca3af; margin-bottom: 1.5rem;">
                📊 You have <strong style="color: #c4b5fd;">{len(history_items)}</strong> saved items
            </div>
        """, unsafe_allow_html=True)
        
        search = st.text_input("🔍 Search history", placeholder="Search by title or content...", label_visibility="collapsed")
        
        if search:
            history_items = [h for h in history_items if search.lower() in h.title.lower() or search.lower() in h.generated_content.lower()]
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        for item in history_items:
            with st.expander(f"📄 {item.title} • {item.created_at.strftime('%d %b %Y, %I:%M %p')}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Content Type:** {item.content_type}")
                    st.markdown(f"**Tone:** {item.tone}")
                    st.markdown(f"**Audience:** {item.audience}")
                
                with col2:
                    st.markdown(f"**Purpose:** {item.purpose}")
                    st.markdown(f"**Word Limit:** {item.word_limit} words")
                
                st.markdown("---")
                st.markdown("### 📝 Content")
                st.markdown(f'<div class="generated-output">{item.generated_content}</div>', unsafe_allow_html=True)
                
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.download_button(
                        "📥 Download",
                        item.generated_content,
                        file_name=f"content_{item.id}.txt",
                        key=f"download_{item.id}",
                        use_container_width=True
                    )
                
                with col_b:
                    if st.button("↩️ Load & Edit", key=f"load_{item.id}", use_container_width=True):
                        load_history_item(item)
                        st.success("✅ Content loaded!")
                        time.sleep(0.5)
                        st.rerun()
                
                with col_c:
                    if st.button("🗑️ Delete", key=f"delete_{item.id}", use_container_width=True):
                        delete_history_item(item.id)
                        st.success("Deleted!")
                        time.sleep(0.5)
                        st.rerun()

# ========== TEMPLATES PAGE ==========
elif st.session_state.page == "templates":
    st.markdown('<div class="header-title">Content Templates</div>', unsafe_allow_html=True)
    st.caption("Pre-configured templates for quick content creation")
    st.markdown("<br>", unsafe_allow_html=True)
    
    for idx, template in enumerate(st.session_state.templates):
        st.markdown(f"""
            <div class="content-card">
                <div style="display: flex; justify-content: between; align-items: start; margin-bottom: 1rem;">
                    <div style="flex: 1;">
                        <div style="color: #c4b5fd; font-weight: 600; font-size: 1.2rem; margin-bottom: 0.5rem;">
                            ✨ {template['name']}
                        </div>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; color: #9ca3af; font-size: 0.95rem; line-height: 1.8;">
                    <div><strong style="color: #d1d5db;">Type:</strong> {template['content_type']}</div>
                    <div><strong style="color: #d1d5db;">Tone:</strong> {template['tone']}</div>
                    <div><strong style="color: #d1d5db;">Audience:</strong> {template['audience']}</div>
                    <div><strong style="color: #d1d5db;">Purpose:</strong> {template['purpose']}</div>
                    <div><strong style="color: #d1d5db;">Words:</strong> {template['word_limit']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"🚀 Use Template: {template['name']}", key=f"use_template_{idx}", use_container_width=True):
            st.session_state.content_type = template['content_type']
            st.session_state.tone = template['tone']
            st.session_state.audience = template['audience']
            st.session_state.purpose = template['purpose']
            st.session_state.word_limit = template['word_limit']
            st.session_state.page = "new_content"
            st.session_state.step = "input"
            st.success(f"✅ Template '{template['name']}' loaded!")
            time.sleep(1)
            st.rerun()

# ========== SETTINGS PAGE ==========
elif st.session_state.page == "settings":
    st.markdown('<div class="header-title">Account Settings</div>', unsafe_allow_html=True)
    st.caption("Manage your profile and preferences")
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">👤 Profile Information</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""
            <div style="text-align: center; padding: 2rem 1rem;">
                <div style="width: 100px; height: 100px; margin: 0 auto; background: linear-gradient(135deg, #8b5cf6, #c4b5fd); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 3rem; border: 4px solid rgba(139, 92, 246, 0.3);">
                    👤
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        name = st.text_input("Full Name", value=st.session_state.user_name, placeholder="John Doe")
        email_display = st.text_input("Email Address", value=st.session_state.user_email, disabled=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    col_save, col_cancel = st.columns(2)
    
    with col_save:
        if st.button("💾 Save Changes", use_container_width=True):
            st.session_state.user_name = name
            st.success("✅ Settings saved successfully!")
            time.sleep(1)
            st.rerun()
    
    with col_cancel:
        if st.button("↩️ Reset", use_container_width=True):
            st.info("ℹ️ Changes discarded")
            time.sleep(0.5)
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Statistics
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 Your Statistics</div>', unsafe_allow_html=True)
    
    user_email = st.session_state.get("email", "")
    history_items = get_user_history(user_email) if user_email else []
    recent_count = len([h for h in history_items if h.created_at.strftime("%Y-%m") == datetime.now().strftime("%Y-%m")])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div style="text-align: center; padding: 1.5rem;">
                <div style="color: #6b7280; font-size: 0.9rem; margin-bottom: 0.5rem;">Total Content</div>
                <div style="font-size: 2.5rem; font-weight: 700; color: #8b5cf6;">{len(history_items)}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style="text-align: center; padding: 1.5rem;">
                <div style="color: #6b7280; font-size: 0.9rem; margin-bottom: 0.5rem;">Templates</div>
                <div style="font-size: 2.5rem; font-weight: 700; color: #a78bfa;">{len(st.session_state.templates)}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style="text-align: center; padding: 1.5rem;">
                <div style="color: #6b7280; font-size: 0.9rem; margin-bottom: 0.5rem;">This Month</div>
                <div style="font-size: 2.5rem; font-weight: 700; color: #c4b5fd;">{recent_count}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Danger Zone
    st.markdown('<div class="content-card" style="border-color: rgba(239, 68, 68, 0.3);">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">⚠️ Danger Zone</div>', unsafe_allow_html=True)
    st.warning("🗑️ **Clear All History** - This action cannot be undone and will permanently delete all your saved content")
    
    if st.button("🗑️ Clear All History", use_container_width=True):
        try:
            db = SessionLocal()
            db.query(ContentHistory).filter(ContentHistory.user_email == user_email).delete()
            db.commit()
            db.close()
            st.success("✅ All history cleared successfully")
            time.sleep(1.5)
            st.rerun()
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)