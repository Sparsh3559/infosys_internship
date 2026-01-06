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
        "user_name": st.session_state.get("name", "User"),
        "user_email": st.session_state.get("email", "user@example.com"),
        "user_avatar": "👤",
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
    
    /* TOP NAVBAR */
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
    .hamburger span { width: 20px; height: 2px; background: #a5b4fc; border-radius: 2px; }
    
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
    
    /* SIDE MENU */
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
    
    /* MAIN CONTENT */
    .main-content {
        margin-top: 70px;
        padding: 2rem 3rem;
        transition: margin-left 0.3s ease;
        min-height: calc(100vh - 70px);
    }
    
    .main-content.shifted { margin-left: 280px; }
    
    /* INPUTS */
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
    
    /* BUTTONS */
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
    
    /* CARDS */
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
    
    /* MISC */
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
    
    .stat-card { text-align: center; padding: 1.5rem; }
    .stat-value { font-size: 2.5rem; font-weight: 700; margin-top: 0.5rem; }
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
""", unsafe_allow_html=True)

# Hidden interaction buttons
col_menu, col_profile = st.columns(2)
with col_menu:
    if st.button("Toggle Menu", key="menu-toggle"):
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
st.markdown(f'<div class="{menu_class}">', unsafe_allow_html=True)

menu_items = [
    ("🏠", "Dashboard", "dashboard"),
    ("✨", "New Content", "new_content"),
    ("📁", "History", "history"),
    ("📋", "Templates", "templates"),
    ("⚙️", "Settings", "settings"),
    ("🚪", "Logout", "logout")
]

for icon, label, page_key in menu_items:
    active = "active" if st.session_state.page == page_key else ""
    st.markdown(f'<div class="menu-item {active}">{icon} {label}</div>', unsafe_allow_html=True)
    
    if st.button(label, key=f"nav_{page_key}"):
        if page_key == "logout":
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
    
    user_email = st.session_state.get("email", "")
    history_items = get_user_history(user_email) if user_email else []
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="content-card stat-card">
                <div style="color: #6366f1; font-weight: 600;">Total Content</div>
                <div class="stat-value" style="color: #a5b4fc;">{len(history_items)}</div>
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
        recent_count = len([h for h in history_items if h.created_at.strftime("%Y-%m") == datetime.now().strftime("%Y-%m")])
        st.markdown(f"""
            <div class="content-card stat-card">
                <div style="color: #10b981; font-weight: 600;">This Month</div>
                <div class="stat-value" style="color: #34d399;">{recent_count}</div>
            </div>
        """, unsafe_allow_html=True)
    
    if history_items:
        st.markdown("### 📝 Recent Activity")
        for item in history_items[:5]:
            st.markdown(f"""
                <div class="content-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="color: #a5b4fc; font-weight: 600; margin-bottom: 0.3rem;">{item.title}</div>
                            <div style="color: #6b7280; font-size: 0.85rem;">{item.created_at.strftime('%d %b %Y, %I:%M %p')}</div>
                        </div>
                        <div style="color: #9ca3af; font-size: 0.9rem;">{item.content_type}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# ========== NEW CONTENT PAGE ==========
elif st.session_state.page == "new_content":
    
    if st.session_state.step == "input":
        st.markdown("## 💭 Start with Your Idea")
        st.caption("Share your thoughts - we'll transform them into refined prompts")
        
        idea = st.text_area(
            "Your Idea",
            placeholder="Example: I won first place at a national hackathon...",
            height=150,
            value=st.session_state.user_idea
        )
        
        if st.button("🎯 Generate Prompts", use_container_width=True):
            if len(idea.strip()) < 10:
                st.warning("⚠️ Please provide more detail")
            else:
                st.session_state.user_idea = idea
                
                with st.spinner("🔮 Analyzing..."):
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
                            st.error("❌ Failed to parse. Try again.")
                    else:
                        st.error("❌ Connection error")
    
    elif st.session_state.step == "prompt_selection":
        st.markdown("## 🎯 Choose Your Direction")
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
                
                if st.button("Select This", key=f"sel_{idx}", use_container_width=True):
                    st.session_state.selected_prompt = opt['prompt']
                    st.session_state.step = "preferences"
                    st.rerun()
    
    elif st.session_state.step == "preferences":
        st.markdown("## ⚙️ Content Preferences")
        
        st.markdown(f"""
            <div class="content-card">
                <div class="prompt-title">Selected Prompt:</div>
                <div class="prompt-text">{st.session_state.selected_prompt}</div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            content_type = st.selectbox("Content Type", [""] + ["LinkedIn Post", "Email", "Blog Post", "Tweet Thread"])
            tone = st.selectbox("Tone", [""] + ["Professional", "Confident", "Friendly", "Inspirational"])
            audience = st.selectbox("Audience", [""] + ["Recruiters", "General Audience", "Technical Professionals"])
        
        with col2:
            purpose = st.selectbox("Purpose", [""] + ["Share Experience", "Showcase Skills", "Inspire Others"])
            word_limit = st.slider("Word Count", 80, 300, 150, 20)
        
        if content_type and tone and audience and purpose:
            st.session_state.content_type = content_type
            st.session_state.tone = tone
            st.session_state.audience = audience
            st.session_state.purpose = purpose
            st.session_state.word_limit = word_limit
            
            if st.button("✨ Generate Content", use_container_width=True):
                st.session_state.step = "generation"
                st.rerun()
    
    elif st.session_state.step == "generation":
        st.markdown("## ✨ Your Generated Content")
        
        if not st.session_state.final_content:
            with st.spinner("🎨 Creating..."):
                prompt = f"""Write a {st.session_state.tone} {st.session_state.content_type} in ~{st.session_state.word_limit} words.
Audience: {st.session_state.audience}. Purpose: {st.session_state.purpose}.
Content: {st.session_state.selected_prompt}"""
                
                content = call_bedrock_api(prompt, st.session_state.word_limit + 50, 0.7)
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
            st.markdown(f'<div class="editor-box">{st.session_state.final_content}</div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button("📥 Download", st.session_state.final_content, "content.txt")
            with col2:
                if st.button("🔄 Regenerate"):
                    st.session_state.final_content = None
                    st.rerun()
            with col3:
                if st.button("🔙 Start Over"):
                    st.session_state.step = "input"
                    st.session_state.final_content = None
                    st.rerun()

# ========== HISTORY PAGE ==========
elif st.session_state.page == "history":
    st.markdown("## 📁 Content History")
    
    user_email = st.session_state.get("email", "")
    history_items = get_user_history(user_email) if user_email else []
    
    if not history_items:
        st.info("📝 No history yet. Create your first content!")
    else:
        st.caption(f"You have {len(history_items)} saved items")
        
        search = st.text_input("🔍 Search history", placeholder="Search by title or content...")
        
        if search:
            history_items = [h for h in history_items if search.lower() in h.title.lower() or search.lower() in h.generated_content.lower()]
        
        for item in history_items:
            with st.expander(f"📄 {item.title} - {item.created_at.strftime('%d %b %Y, %I:%M %p')}", expanded=False):
                st.markdown("### 📋 Details")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Type:** {item.content_type}")
                    st.markdown(f"**Tone:** {item.tone}")
                
                with col2:
                    st.markdown(f"**Audience:** {item.audience}")
                    st.markdown(f"**Purpose:** {item.purpose}")
                
                st.markdown(f"**Word Limit:** {item.word_limit}")
                st.markdown("---")
                
                st.markdown("### ✨ Generated Content")
                st.markdown(f'<div class="editor-box">{item.generated_content}</div>', unsafe_allow_html=True)
                
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.download_button(
                        "📥 Download",
                        item.generated_content,
                        file_name=f"content_{item.id}.txt",
                        key=f"download_{item.id}"
                    )
                
                with col_b:
                    if st.button("↩️ Resume", key=f"load_{item.id}"):
                        load_history_item(item)
                        st.success("✅ Content loaded!")
                        time.sleep(0.5)
                        st.rerun()
                
                with col_c:
                    if st.button("🗑️ Delete", key=f"delete_{item.id}"):
                        delete_history_item(item.id)
                        st.success("Deleted!")
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
        email_display = st.text_input("Email Address", value=st.session_state.user_email, disabled=True)
        avatar = st.text_input("Avatar Emoji", value=st.session_state.user_avatar, max_chars=2, placeholder="👤")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        col_save, col_reset = st.columns(2)
        
        with col_save:
            if st.button("💾 Save Changes", use_container_width=True):
                st.session_state.user_name = name
                st.session_state.user_avatar = avatar if avatar else "👤"
                st.success("✅ Settings saved!")
                time.sleep(1)
                st.rerun()
        
        with col_reset:
            if st.button("🔄 Reset Avatar", use_container_width=True):
                st.session_state.user_avatar = "👤"
                st.info("ℹ️ Avatar reset to default")
                time.sleep(1)
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Account statistics
    st.markdown("### 📊 Account Statistics")
    
    user_email = st.session_state.get("email", "")
    history_items = get_user_history(user_email) if user_email else []
    recent_count = len([h for h in history_items if h.created_at.strftime("%Y-%m") == datetime.now().strftime("%Y-%m")])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="content-card" style="text-align: center;">
                <div style="color: #6b7280; font-size: 0.9rem;">Total Content</div>
                <div style="font-size: 2rem; font-weight: 700; color: #6366f1; margin-top: 0.5rem;">
                    {len(history_items)}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="content-card" style="text-align: center;">
                <div style="color: #6b7280; font-size: 0.9rem;">Templates</div>
                <div style="font-size: 2rem; font-weight: 700; color: #8b5cf6; margin-top: 0.5rem;">
                    {len(st.session_state.templates)}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
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
    
    st.warning("🗑️ **Clear All History** - This action cannot be undone")
    
    if st.button("🗑️ Clear All History", use_container_width=True):
        try:
            db = SessionLocal()
            db.query(ContentHistory).filter(ContentHistory.user_email == user_email).delete()
            db.commit()
            db.close()
            st.success("✅ All history cleared")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)