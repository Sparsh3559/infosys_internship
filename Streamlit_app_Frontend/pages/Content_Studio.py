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
        "user_profile_pic": "👤",
        "show_template_save_modal": False,
        "new_template_name": "",
        "theme": "dark",
        "show_evaluation": False,
        "evaluation_scores": None,
        "user_templates": [],
        "default_templates": [
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

def evaluate_content(content: str, content_type: str, tone: str, audience: str, purpose: str):
    """Evaluate content quality and return scores"""
    evaluation_prompt = f"""Analyze this {content_type} and provide quality scores (0-100) for each criterion.

Content to evaluate:
{content}

Expected characteristics:
- Tone: {tone}
- Audience: {audience}
- Purpose: {purpose}

Provide scores in this exact JSON format:
{{
    "clarity": 85,
    "engagement": 78,
    "tone_consistency": 92,
    "audience_relevance": 88,
    "professionalism": 90
}}

Only return the JSON, no other text."""
    
    response = call_bedrock_api(evaluation_prompt, 300, 0.3)
    
    if response:
        try:
            cleaned = clean_model_output(response)
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            
            scores = json.loads(cleaned)
            scores["overall"] = int(sum(scores.values()) / len(scores))
            return scores
        except Exception as e:
            return {
                "clarity": 75,
                "engagement": 70,
                "tone_consistency": 80,
                "audience_relevance": 75,
                "professionalism": 78,
                "overall": 76
            }
    
    return None

# -------------------------------
# THEME CONFIGURATION
# -------------------------------
def get_theme_colors():
    """Return theme-specific color variables"""
    if st.session_state.theme == "dark":
        return {
            "bg_primary": "#0f1117",
            "bg_secondary": "#1a1d29",
            "bg_tertiary": "#13151f",
            "bg_card": "rgba(31, 41, 55, 0.4)",
            "bg_card_hover": "rgba(31, 41, 55, 0.6)",
            "border_color": "rgba(255, 255, 255, 0.08)",
            "border_hover": "rgba(139, 92, 246, 0.3)",
            "text_primary": "#e5e7eb",
            "text_secondary": "#9ca3af",
            "text_tertiary": "#6b7280",
            "text_accent": "#c4b5fd",
            "sidebar_nav_hover": "rgba(139, 92, 246, 0.08)",
            "input_bg": "rgba(31, 41, 55, 0.5)",
            "progress_bg": "rgba(75, 85, 99, 0.3)",
            "scrollbar_track": "rgba(31, 41, 55, 0.3)",
        }
    else:
        return {
            "bg_primary": "#f9fafb",
            "bg_secondary": "#ffffff",
            "bg_tertiary": "#f3f4f6",
            "bg_card": "rgba(255, 255, 255, 0.8)",
            "bg_card_hover": "rgba(255, 255, 255, 0.95)",
            "border_color": "rgba(0, 0, 0, 0.08)",
            "border_hover": "rgba(139, 92, 246, 0.4)",
            "text_primary": "#1f2937",
            "text_secondary": "#6b7280",
            "text_tertiary": "#9ca3af",
            "text_accent": "#7c3aed",
            "sidebar_nav_hover": "rgba(139, 92, 246, 0.1)",
            "input_bg": "rgba(255, 255, 255, 0.9)",
            "progress_bg": "rgba(229, 231, 235, 0.5)",
            "scrollbar_track": "rgba(229, 231, 235, 0.3)",
        }

# -------------------------------
# DYNAMIC STYLING BASED ON THEME
# -------------------------------
theme_colors = get_theme_colors()

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {{
        font-family: 'Inter', -apple-system, sans-serif;
        transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
    }}
    
    /* THEME BASE */
    html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"] {{
        background: {theme_colors['bg_primary']} !important;
        color: {theme_colors['text_primary']} !important;
    }}
    
    .main .block-container {{
        padding: 1rem 3rem !important;
        max-width: 100% !important;
    }}
    
    /* HIDE STREAMLIT DEFAULT NAVIGATION */
    [data-testid="stSidebarNav"] {{
        display: none !important;
    }}
    
    /* SIDEBAR STYLING */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {theme_colors['bg_secondary']} 0%, {theme_colors['bg_tertiary']} 100%) !important;
        border-right: 1px solid {theme_colors['border_color']} !important;
    }}
    
    [data-testid="stSidebar"] > div:first-child {{
        background: transparent !important;
    }}
    
    /* STYLE NAVIGATION BUTTONS AS CLEAN LABELS */
    [data-testid="stSidebar"] .stButton {{
        margin: 0.3rem 0.8rem;
    }}
    
    [data-testid="stSidebar"] .stButton > button {{
        width: 100% !important;
        background: transparent !important;
        border: none !important;
        border-left: 3px solid transparent !important;
        border-radius: 10px !important;
        color: {theme_colors['text_secondary']} !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        padding: 0.9rem 1.3rem !important;
        text-align: left !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
        justify-content: flex-start !important;
    }}
    
    [data-testid="stSidebar"] .stButton > button:hover {{
        background: {theme_colors['sidebar_nav_hover']} !important;
        color: {theme_colors['text_accent']} !important;
        border-left-color: #8b5cf6 !important;
        transform: translateX(2px) !important;
        filter: brightness(1.1) !important;
        box-shadow: none !important;
    }}
    
    [data-testid="stSidebar"] .stButton > button:active,
    [data-testid="stSidebar"] .stButton > button:focus {{
        background: linear-gradient(90deg, rgba(139, 92, 246, 0.15), transparent) !important;
        color: {theme_colors['text_accent']} !important;
        border-left-color: #8b5cf6 !important;
        box-shadow: none !important;
        outline: none !important;
    }}
    
    /* THEME TOGGLE BUTTON STYLING */
    [data-testid="stSidebar"] .stButton > button[kind="secondary"] {{
        background: transparent !important;
        border: none !important;
        border-left: 3px solid transparent !important;
    }}
    
    [data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {{
        background: {theme_colors['sidebar_nav_hover']} !important;
        border-left-color: #8b5cf6 !important;
    }}
    
    /* TOP USER GREETING */
    .top-user-greeting {{
        position: fixed;
        top: 1rem;
        left: 280px;
        z-index: 999;
        color: {theme_colors['text_secondary']};
        font-size: 0.95rem;
        font-weight: 500;
        background: {theme_colors['bg_card']};
        backdrop-filter: blur(10px);
        padding: 0.6rem 1.2rem;
        border-radius: 10px;
        border: 1px solid {theme_colors['border_color']};
    }}
    
    .top-user-greeting .user-name {{
        color: {theme_colors['text_accent']};
        font-weight: 600;
        margin-left: 0.3rem;
    }}
    
    /* HORIZONTAL 3-STEP PROGRESS BAR */
    .progress-container {{
        margin: 2rem auto 3rem;
        max-width: 700px;
    }}
    
    .progress-steps {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
        margin-bottom: 0.5rem;
    }}
    
    .progress-line {{
        position: absolute;
        top: 20px;
        left: 0;
        right: 0;
        height: 3px;
        background: {theme_colors['progress_bg']};
        z-index: 0;
    }}
    
    .progress-line-fill {{
        height: 100%;
        background: linear-gradient(90deg, #8b5cf6, #a78bfa);
        transition: width 0.5s ease;
        border-radius: 2px;
    }}
    
    .progress-step {{
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
        z-index: 1;
    }}
    
    .step-circle {{
        width: 42px;
        height: 42px;
        border-radius: 50%;
        background: {theme_colors['bg_card']};
        border: 3px solid {theme_colors['progress_bg']};
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1rem;
        color: {theme_colors['text_tertiary']};
        transition: all 0.3s ease;
        margin-bottom: 0.5rem;
    }}
    
    .step-circle.active {{
        background: linear-gradient(135deg, #8b5cf6, #a78bfa);
        border-color: #8b5cf6;
        color: white;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.5);
    }}
    
    .step-circle.completed {{
        background: linear-gradient(135deg, #10b981, #059669);
        border-color: #10b981;
        color: white;
    }}
    
    .step-label {{
        font-size: 0.85rem;
        color: {theme_colors['text_tertiary']};
        font-weight: 500;
        text-align: center;
    }}
    
    .step-label.active {{
        color: {theme_colors['text_accent']};
        font-weight: 600;
    }}
    
    .step-label.completed {{
        color: #34d399;
    }}
    
    /* HEADER TITLE */
    .header-title {{
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #c4b5fd 0%, #a78bfa 50%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 0.5rem 0;
    }}
    
    /* MODERN CARDS */
    .content-card {{
        background: {theme_colors['bg_card']};
        backdrop-filter: blur(20px);
        border: 1px solid {theme_colors['border_color']};
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }}
    
    .content-card:hover {{
        border-color: {theme_colors['border_hover']};
        box-shadow: 0 8px 30px rgba(139, 92, 246, 0.15);
        background: {theme_colors['bg_card_hover']};
    }}
    
    .card-title {{
        font-size: 1.1rem;
        font-weight: 600;
        color: {theme_colors['text_primary']};
        margin-bottom: 1rem;
    }}
    
    .card-subtitle {{
        font-size: 0.875rem;
        color: {theme_colors['text_secondary']};
        margin-bottom: 1.5rem;
    }}
    
    /* FORM INPUTS */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {{
        background: {theme_colors['input_bg']} !important;
        border: 1.5px solid {theme_colors['border_color']} !important;
        border-radius: 12px !important;
        color: {theme_colors['text_primary']} !important;
        padding: 0.85rem 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.25s ease !important;
    }}
    
    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {{
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15) !important;
        outline: none !important;
    }}
    
    .stTextArea textarea {{
        min-height: 120px !important;
    }}
    
    /* LABELS */
    .stTextInput label, .stTextArea label, .stSelectbox label, .stSlider label {{
        color: {theme_colors['text_secondary']} !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        margin-bottom: 0.5rem !important;
    }}
    
    /* UNIFIED BUTTON STYLING - GRADIENT */
    .stButton button, .stDownloadButton button {{
        background: linear-gradient(135deg, #a78bfa 0%, #ec4899 50%, #f97316 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.85rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(167, 139, 250, 0.3) !important;
        width: 100%;
    }}
    
    .stButton button:hover, .stDownloadButton button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(167, 139, 250, 0.5) !important;
        filter: brightness(1.1) !important;
    }}
    
    .stButton button:active, .stDownloadButton button:active {{
        transform: translateY(0) !important;
    }}
    
    /* PROMPT CARDS */
    .prompt-card {{
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(124, 58, 237, 0.05));
        border: 2px solid rgba(139, 92, 246, 0.15);
        border-radius: 16px;
        padding: 1.8rem;
        margin: 1rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}
    
    .prompt-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #8b5cf6, #a78bfa, #c4b5fd);
        opacity: 0;
        transition: opacity 0.3s ease;
    }}
    
    .prompt-card:hover {{
        border-color: rgba(139, 92, 246, 0.4);
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(139, 92, 246, 0.25);
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.12), rgba(124, 58, 237, 0.08));
    }}
    
    .prompt-card:hover::before {{
        opacity: 1;
    }}
    
    .prompt-title {{
        color: {theme_colors['text_accent']};
        font-weight: 600;
        font-size: 1.15rem;
        margin-bottom: 0.75rem;
    }}
    
    .prompt-text {{
        color: {theme_colors['text_primary']};
        line-height: 1.7;
        font-size: 0.95rem;
    }}
    
    /* GENERATED OUTPUT */
    .generated-output {{
        background: {theme_colors['bg_card']};
        backdrop-filter: blur(30px);
        color: {theme_colors['text_primary']};
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid rgba(139, 92, 246, 0.2);
        font-size: 1rem;
        line-height: 1.8;
        white-space: pre-wrap;
        word-wrap: break-word;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }}
    
    /* EVALUATION SECTION */
    .evaluation-intro {{
        background: {theme_colors['bg_card']};
        border: 1px solid {theme_colors['border_color']};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 2rem 0 1rem 0;
        text-align: center;
    }}
    
    .evaluation-intro-title {{
        color: {theme_colors['text_accent']};
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }}
    
    .evaluation-intro-text {{
        color: {theme_colors['text_secondary']};
        font-size: 0.9rem;
        line-height: 1.6;
    }}
    
    .evaluation-results {{
        background: {theme_colors['bg_card']};
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
    }}
    
    .evaluation-metric {{
        margin-bottom: 1.5rem;
    }}
    
    .metric-label {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }}
    
    .metric-name {{
        color: {theme_colors['text_primary']};
        font-weight: 500;
        font-size: 0.95rem;
    }}
    
    .metric-score {{
        color: {theme_colors['text_accent']};
        font-weight: 700;
        font-size: 1.1rem;
    }}
    
    .metric-bar {{
        width: 100%;
        height: 12px;
        background: {theme_colors['progress_bg']};
        border-radius: 6px;
        overflow: hidden;
        position: relative;
    }}
    
    .metric-bar-fill {{
        height: 100%;
        background: linear-gradient(90deg, #a78bfa, #ec4899, #f97316);
        border-radius: 6px;
        transition: width 0.8s ease;
        box-shadow: 0 0 10px rgba(167, 139, 250, 0.5);
    }}
    
    .overall-score {{
        margin-top: 2rem;
        padding-top: 2rem;
        border-top: 1px solid {theme_colors['border_color']};
    }}
    
    .overall-score .metric-bar {{
        height: 16px;
    }}
    
    .overall-score .metric-score {{
        font-size: 1.5rem;
        background: linear-gradient(135deg, #a78bfa, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    /* PROFILE PICTURE */
    .profile-pic-container {{
        position: relative;
        width: 120px;
        height: 120px;
        margin: 0 auto;
    }}
    
    .profile-pic {{
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: linear-gradient(135deg, #8b5cf6, #c4b5fd);
        border: 4px solid rgba(139, 92, 246, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    
    .profile-pic:hover {{
        transform: scale(1.05);
        border-color: rgba(139, 92, 246, 0.6);
    }}
    
    /* STAT CARDS */
    .stat-card {{
        text-align: center;
        padding: 1.8rem 1.2rem;
    }}
    
    .stat-value {{
        font-size: 2.8rem;
        font-weight: 700;
        margin-top: 0.5rem;
        background: linear-gradient(135deg, #8b5cf6, #c4b5fd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    .stat-label {{
        color: {theme_colors['text_secondary']};
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    /* EXPANDER */
    .streamlit-expanderHeader {{
        background: {theme_colors['bg_card']};
        border: 1px solid {theme_colors['border_color']};
        border-radius: 12px;
        padding: 1rem 1.5rem;
        color: {theme_colors['text_primary']};
        font-weight: 500;
    }}
    
    .streamlit-expanderHeader:hover {{
        background: {theme_colors['bg_card_hover']};
        border-color: {theme_colors['border_hover']};
    }}
    
    /* HIDE STREAMLIT BRANDING */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* SCROLLBAR */
    ::-webkit-scrollbar {{
        width: 10px;
        height: 10px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {theme_colors['scrollbar_track']};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: rgba(139, 92, 246, 0.5);
        border-radius: 5px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: rgba(139, 92, 246, 0.7);
    }}
    
    /* DIVIDER */
    hr {{
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.3), transparent);
        margin: 2rem 0;
    }}
    
    /* MODAL OVERLAY - PROPER IMPLEMENTATION */
    .modal-overlay {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(5px);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: fadeIn 0.3s ease;
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    
    .modal-content {{
        background: {theme_colors['bg_card']};
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 20px;
        padding: 2.5rem;
        max-width: 500px;
        width: 90%;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        animation: slideUp 0.3s ease;
    }}
    
    @keyframes slideUp {{
        from {{ 
            opacity: 0;
            transform: translateY(20px);
        }}
        to {{ 
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    /* USER INFO IN SIDEBAR */
    .sidebar-user-info {{
        padding: 1.5rem 1rem;
        text-align: center;
        margin-top: auto;
        border-top: 1px solid {theme_colors['border_color']};
    }}
    
    .sidebar-user-pic {{
        width: 70px;
        height: 70px;
        margin: 0 auto 0.75rem;
        background: linear-gradient(135deg, #8b5cf6, #c4b5fd);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        border: 3px solid rgba(139, 92, 246, 0.3);
    }}
    
    .sidebar-user-name {{
        color: {theme_colors['text_primary']};
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }}
    
    .sidebar-user-email {{
        color: {theme_colors['text_tertiary']};
        font-size: 0.8rem;
    }}
    
    /* SUCCESS/ERROR MESSAGES */
    .stSuccess, .stInfo, .stWarning, .stError {{
        background: {theme_colors['bg_card']} !important;
        border-radius: 12px !important;
        border-left: 4px solid #8b5cf6 !important;
    }}
    
    /* FILE UPLOADER STYLING */
    .stFileUploader {{
        background: {theme_colors['input_bg']} !important;
        border: 1.5px dashed {theme_colors['border_color']} !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        transition: all 0.25s ease !important;
    }}
    
    .stFileUploader:hover {{
        border-color: #8b5cf6 !important;
        background: {theme_colors['bg_card_hover']} !important;
    }}
    
    [data-testid="stFileUploadDropzone"] {{
        background: transparent !important;
    }}
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# TOP USER GREETING
# -------------------------------
st.markdown(f"""
    <div class="top-user-greeting">
        Hi, <span class="user-name">{st.session_state.user_name}</span>
    </div>
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
    
    # Navigation items - clickable labels
    nav_items = [
        ("✨", "New Content", "new_content"),
        ("📁", "Saved Drafts", "history"),
        ("📋", "Templates", "templates"),
        ("👤", "Profile", "profile"),
    ]
    
    # Create clickable navigation items
    for icon, label, page_key in nav_items:
        active_class = "active" if st.session_state.page == page_key else ""
        
        # Create a container for each nav item
        nav_container = st.container()
        
        # Check if this item was clicked
        if st.button(f"{icon} {label}", key=f"nav_{page_key}", use_container_width=True):
            st.session_state.page = page_key
            if page_key == "new_content":
                st.session_state.step = "input"
            st.rerun()
    
    st.markdown("<hr style='margin: 2rem 0 1rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # Theme Toggle
    theme_icon = "🌙" if st.session_state.theme == "dark" else "☀️"
    theme_text = "Light Mode" if st.session_state.theme == "dark" else "Dark Mode"
    
    if st.button(f"{theme_icon} {theme_text}", key="theme_toggle_btn", use_container_width=True):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()
    
    st.markdown("<hr style='margin: 1rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # User section with name and email
    st.markdown(f"""
        <div class="sidebar-user-info">
            <div class="sidebar-user-pic">
                {st.session_state.user_profile_pic}
            </div>
            <div class="sidebar-user-name">{st.session_state.user_name}</div>
            <div class="sidebar-user-email">{st.session_state.user_email}</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("pages/Login.py")

# -------------------------------
# PROGRESS BAR (HORIZONTAL)
# -------------------------------
def render_progress_bar():
    """Render horizontal 3-step progress bar"""
    steps = [
        {"num": 1, "label": "Generate Prompts", "key": "input"},
        {"num": 2, "label": "Set Preferences", "key": "preferences"},
        {"num": 3, "label": "Generate Content", "key": "generation"}
    ]
    
    # Determine current step index
    current_step_index = 0
    if st.session_state.step in ["input", "prompt_selection"]:
        current_step_index = 0
    elif st.session_state.step == "preferences":
        current_step_index = 1
    elif st.session_state.step == "generation":
        current_step_index = 2
    
    progress_percentage = (current_step_index / 2) * 100
    
    st.markdown(f"""
        <div class="progress-container">
            <div class="progress-line">
                <div class="progress-line-fill" style="width: {progress_percentage}%;"></div>
            </div>
            <div class="progress-steps">
    """, unsafe_allow_html=True)
    
    for idx, step in enumerate(steps):
        if idx < current_step_index:
            circle_class = "completed"
            label_class = "completed"
            icon = "✓"
        elif idx == current_step_index:
            circle_class = "active"
            label_class = "active"
            icon = step["num"]
        else:
            circle_class = ""
            label_class = ""
            icon = step["num"]
        
        st.markdown(f"""
            <div class="progress-step">
                <div class="step-circle {circle_class}">{icon}</div>
                <div class="step-label {label_class}">{step["label"]}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
            </div>
        </div>
    """, unsafe_allow_html=True)

# -------------------------------
# TEMPLATE SAVE MODAL
# -------------------------------
# This section is now integrated into the generation page where it's needed

# -------------------------------
# MAIN CONTENT AREA
# -------------------------------

# ========== NEW CONTENT PAGE ==========
if st.session_state.page == "new_content":
    
    render_progress_bar()
    
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
                index=0 if not st.session_state.content_type else ["", "LinkedIn Post", "Email", "Blog Post", "Tweet Thread", "Instagram Caption"].index(st.session_state.content_type),
                key="sel_content_type"
            )
            
            tone = st.selectbox(
                "Tone",
                [""] + ["Professional", "Confident", "Friendly", "Inspirational", "Conversational"],
                index=0 if not st.session_state.tone else ["", "Professional", "Confident", "Friendly", "Inspirational", "Conversational"].index(st.session_state.tone),
                key="sel_tone"
            )
            
            audience = st.selectbox(
                "Target Audience",
                [""] + ["Recruiters", "General Audience", "Technical Professionals", "Business Leaders"],
                index=0 if not st.session_state.audience else ["", "Recruiters", "General Audience", "Technical Professionals", "Business Leaders"].index(st.session_state.audience),
                key="sel_audience"
            )
        
        with col2:
            purpose = st.selectbox(
                "Purpose",
                [""] + ["Share Experience", "Showcase Skills", "Inspire Others", "Announce Achievement"],
                index=0 if not st.session_state.purpose else ["", "Share Experience", "Showcase Skills", "Inspire Others", "Announce Achievement"].index(st.session_state.purpose),
                key="sel_purpose"
            )
            
            word_limit = st.slider("Word Count", 80, 400, st.session_state.word_limit, 20, key="sel_word_limit")
            
            st.markdown(f"""
                <div style="margin-top: 1rem; padding: 1rem; background: rgba(139, 92, 246, 0.1); border-radius: 10px; border-left: 3px solid #8b5cf6;">
                    <div style="color: {theme_colors['text_secondary']}; font-size: 0.85rem; margin-bottom: 0.3rem;">Word Limit</div>
                    <div style="color: {theme_colors['text_accent']}; font-weight: 600; font-size: 1.5rem;">{word_limit} words</div>
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
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.download_button(
                    "📥 Download",
                    st.session_state.final_content,
                    "content.txt",
                    use_container_width=True
                )
            
            with col2:
                if st.button("💾 Save as Template", use_container_width=True):
                    st.session_state.show_template_save_modal = True
                    st.rerun()
            
            # Show modal inline if triggered
            if st.session_state.get("show_template_save_modal", False):
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="content-card">', unsafe_allow_html=True)
                st.markdown("### 💾 Save as Template")
                st.markdown("Give your template a name to save these preferences for future use.")
                
                template_name = st.text_input("Template Name", placeholder="e.g., My LinkedIn Strategy", key="template_name_input")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    if st.button("💾 Save Template", use_container_width=True, key="confirm_save_template"):
                        if template_name.strip():
                            new_template = {
                                "name": template_name,
                                "content_type": st.session_state.content_type,
                                "tone": st.session_state.tone,
                                "audience": st.session_state.audience,
                                "purpose": st.session_state.purpose,
                                "word_limit": st.session_state.word_limit
                            }
                            st.session_state.user_templates.append(new_template)
                            st.session_state.show_template_save_modal = False
                            st.success(f"✅ Template '{template_name}' saved!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.warning("⚠️ Please enter a template name")
                
                with col_b:
                    if st.button("Cancel", use_container_width=True, key="cancel_save_template"):
                        st.session_state.show_template_save_modal = False
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                if st.button("🔄 Regenerate", use_container_width=True):
                    st.session_state.final_content = None
                    st.session_state.show_evaluation = False
                    st.session_state.evaluation_scores = None
                    st.rerun()
            
            with col4:
                if st.button("🆕 New Content", use_container_width=True):
                    st.session_state.step = "input"
                    st.session_state.final_content = None
                    st.session_state.user_idea = ""
                    st.session_state.content_type = None
                    st.session_state.tone = None
                    st.session_state.audience = None
                    st.session_state.purpose = None
                    st.session_state.show_evaluation = False
                    st.session_state.evaluation_scores = None
                    st.rerun()
            
            # CONTENT EVALUATION SECTION
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="evaluation-intro">
                    <div class="evaluation-intro-title">📊 Content Quality Analysis</div>
                    <div class="evaluation-intro-text">
                        Get detailed insights on your content's clarity, engagement, tone accuracy, and professional quality. 
                        Our analysis helps you understand how well your content aligns with your objectives.
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if not st.session_state.show_evaluation:
                if st.button("✨ Analyze Content Quality", use_container_width=True, key="evaluate_btn"):
                    with st.spinner("🔍 Analyzing your content..."):
                        scores = evaluate_content(
                            st.session_state.final_content,
                            st.session_state.content_type,
                            st.session_state.tone,
                            st.session_state.audience,
                            st.session_state.purpose
                        )
                        if scores:
                            st.session_state.evaluation_scores = scores
                            st.session_state.show_evaluation = True
                            st.rerun()
            
            if st.session_state.show_evaluation and st.session_state.evaluation_scores:
                st.markdown('<div class="evaluation-results">', unsafe_allow_html=True)
                
                metrics = [
                    ("Clarity & Readability", "clarity", "How clear and easy to understand your content is"),
                    ("Engagement Level", "engagement", "How compelling and interesting your content is"),
                    ("Tone Consistency", "tone_consistency", "How well the tone matches your selected style"),
                    ("Audience Relevance", "audience_relevance", "How well-suited the content is for your target audience"),
                    ("Professional Quality", "professionalism", "Overall writing quality and polish")
                ]
                
                for metric_name, metric_key, metric_desc in metrics:
                    score = st.session_state.evaluation_scores.get(metric_key, 0)
                    
                    st.markdown(f"""
                        <div class="evaluation-metric">
                            <div class="metric-label">
                                <span class="metric-name">{metric_name}</span>
                                <span class="metric-score">{score}%</span>
                            </div>
                            <div class="metric-bar">
                                <div class="metric-bar-fill" style="width: {score}%;"></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                overall = st.session_state.evaluation_scores.get("overall", 0)
                st.markdown(f"""
                    <div class="evaluation-metric overall-score">
                        <div class="metric-label">
                            <span class="metric-name" style="font-size: 1.1rem; font-weight: 600;">Overall Score</span>
                            <span class="metric-score">{overall}%</span>
                        </div>
                        <div class="metric-bar">
                            <div class="metric-bar-fill" style="width: {overall}%;"></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                if st.button("🔄 Re-analyze", use_container_width=True, key="reanalyze_btn"):
                    st.session_state.show_evaluation = False
                    st.session_state.evaluation_scores = None
                    st.rerun()

# ========== HISTORY PAGE ==========
elif st.session_state.page == "history":
    st.markdown('<div class="header-title">Saved Drafts</div>', unsafe_allow_html=True)
    st.caption("Access all your previously generated content")
    st.markdown("<br>", unsafe_allow_html=True)
    
    user_email = st.session_state.get("email", "")
    history_items = get_user_history(user_email) if user_email else []
    
    if not history_items:
        st.markdown(f"""
            <div class="content-card" style="text-align: center; padding: 3rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📝</div>
                <div style="color: {theme_colors['text_secondary']}; font-size: 1.1rem;">No saved content yet</div>
                <div style="color: {theme_colors['text_tertiary']}; font-size: 0.9rem; margin-top: 0.5rem;">Create your first content to see it here</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style="color: {theme_colors['text_secondary']}; margin-bottom: 1.5rem;">
                📊 You have <strong style="color: {theme_colors['text_accent']};">{len(history_items)}</strong> saved items
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
    
    if st.session_state.default_templates:
        st.markdown("### 📋 Default Templates")
        for idx, template in enumerate(st.session_state.default_templates):
            st.markdown(f"""
                <div class="content-card">
                    <div style="display: flex; justify-content: between; align-items: start; margin-bottom: 1rem;">
                        <div style="flex: 1;">
                            <div style="color: {theme_colors['text_accent']}; font-weight: 600; font-size: 1.2rem; margin-bottom: 0.5rem;">
                                ✨ {template['name']}
                            </div>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; color: {theme_colors['text_secondary']}; font-size: 0.95rem; line-height: 1.8;">
                        <div><strong style="color: {theme_colors['text_primary']};">Type:</strong> {template['content_type']}</div>
                        <div><strong style="color: {theme_colors['text_primary']};">Tone:</strong> {template['tone']}</div>
                        <div><strong style="color: {theme_colors['text_primary']};">Audience:</strong> {template['audience']}</div>
                        <div><strong style="color: {theme_colors['text_primary']};">Purpose:</strong> {template['purpose']}</div>
                        <div><strong style="color: {theme_colors['text_primary']};">Words:</strong> {template['word_limit']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🚀 Use: {template['name']}", key=f"use_default_{idx}", use_container_width=True):
                st.session_state.content_type = template['content_type']
                st.session_state.tone = template['tone']
                st.session_state.audience = template['audience']
                st.session_state.purpose = template['purpose']
                st.session_state.word_limit = template['word_limit']
                st.session_state.page = "new_content"
                st.session_state.step = "preferences"
                st.success(f"✅ Template '{template['name']}' loaded!")
                time.sleep(1)
                st.rerun()
    
    if st.session_state.user_templates:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 💼 My Custom Templates")
        
        for idx, template in enumerate(st.session_state.user_templates):
            st.markdown(f"""
                <div class="content-card">
                    <div style="display: flex; justify-content: between; align-items: start; margin-bottom: 1rem;">
                        <div style="flex: 1;">
                            <div style="color: {theme_colors['text_accent']}; font-weight: 600; font-size: 1.2rem; margin-bottom: 0.5rem;">
                                ✨ {template['name']}
                            </div>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; color: {theme_colors['text_secondary']}; font-size: 0.95rem; line-height: 1.8;">
                        <div><strong style="color: {theme_colors['text_primary']};">Type:</strong> {template['content_type']}</div>
                        <div><strong style="color: {theme_colors['text_primary']};">Tone:</strong> {template['tone']}</div>
                        <div><strong style="color: {theme_colors['text_primary']};">Audience:</strong> {template['audience']}</div>
                        <div><strong style="color: {theme_colors['text_primary']};">Purpose:</strong> {template['purpose']}</div>
                        <div><strong style="color: {theme_colors['text_primary']};">Words:</strong> {template['word_limit']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if st.button(f"🚀 Use: {template['name']}", key=f"use_user_{idx}", use_container_width=True):
                    st.session_state.content_type = template['content_type']
                    st.session_state.tone = template['tone']
                    st.session_state.audience = template['audience']
                    st.session_state.purpose = template['purpose']
                    st.session_state.word_limit = template['word_limit']
                    st.session_state.page = "new_content"
                    st.session_state.step = "preferences"
                    st.success(f"✅ Template '{template['name']}' loaded!")
                    time.sleep(1)
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Delete", key=f"del_user_{idx}", use_container_width=True):
                    st.session_state.user_templates.pop(idx)
                    st.success("Template deleted!")
                    time.sleep(0.5)
                    st.rerun()

# ========== PROFILE PAGE ==========
elif st.session_state.page == "profile":
    st.markdown('<div class="header-title">Profile & Settings</div>', unsafe_allow_html=True)
    st.caption("Manage your profile and view your statistics")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Profile Information
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">👤 Profile Information</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
            <div style="text-align: center; padding: 2rem 1rem;">
                <div class="profile-pic-container">
                    <div class="profile-pic">
                        {st.session_state.user_profile_pic}
                    </div>
                </div>
                <div style="margin-top: 1rem; color: {theme_colors['text_secondary']}; font-size: 0.85rem;">Change profile picture</div>
            </div>
        """, unsafe_allow_html=True)
        
        # File uploader for profile picture
        uploaded_file = st.file_uploader("Upload Profile Picture", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed", key="profile_pic_upload")
        
        st.markdown("<div style='text-align: center; margin-top: 0.5rem; color: " + theme_colors['text_tertiary'] + "; font-size: 0.8rem;'>Or use emoji:</div>", unsafe_allow_html=True)
        new_pic = st.text_input("Emoji", value=st.session_state.user_profile_pic, max_chars=2, placeholder="👤", label_visibility="collapsed", key="profile_pic_input")
    
    with col2:
        name = st.text_input("Full Name", value=st.session_state.user_name, placeholder="John Doe")
        email_display = st.text_input("Email Address", value=st.session_state.user_email, disabled=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_save, col_reset = st.columns(2)
        
        with col_save:
            if st.button("💾 Save Changes", use_container_width=True):
                st.session_state.user_name = name
                if uploaded_file is not None:
                    # In a real implementation, you would save the file and update the profile pic
                    st.info("📁 Image upload feature coming soon! Using emoji for now.")
                st.session_state.user_profile_pic = new_pic if new_pic else "👤"
                st.success("✅ Profile updated successfully!")
                time.sleep(1)
                st.rerun()
        
        with col_reset:
            if st.button("↩️ Reset", use_container_width=True):
                st.info("ℹ️ Changes discarded")
                time.sleep(0.5)
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Statistics
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 Your Activity Statistics</div>', unsafe_allow_html=True)
    
    user_email = st.session_state.get("email", "")
    history_items = get_user_history(user_email) if user_email else []
    
    total_content = len(history_items)
    total_templates = len(st.session_state.default_templates) + len(st.session_state.user_templates)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
            <div style="text-align: center; padding: 2rem 1.5rem;">
                <div style="color: {theme_colors['text_tertiary']}; font-size: 0.9rem; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em;">Total Content</div>
                <div style="font-size: 3rem; font-weight: 700; color: #8b5cf6;">{total_content}</div>
                <div style="color: {theme_colors['text_secondary']}; font-size: 0.85rem; margin-top: 0.3rem;">pieces created</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style="text-align: center; padding: 2rem 1.5rem;">
                <div style="color: {theme_colors['text_tertiary']}; font-size: 0.9rem; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em;">Templates</div>
                <div style="font-size: 3rem; font-weight: 700; color: #a78bfa;">{total_templates}</div>
                <div style="color: {theme_colors['text_secondary']}; font-size: 0.85rem; margin-top: 0.3rem;">available to use</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Content Breakdown
    if history_items:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📈 Content Breakdown</div>', unsafe_allow_html=True)
        
        content_types = {}
        for item in history_items:
            content_types[item.content_type] = content_types.get(item.content_type, 0) + 1
        
        for content_type, count in content_types.items():
            percentage = (count / total_content) * 100
            st.markdown(f"""
                <div style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                        <span style="color: {theme_colors['text_primary']}; font-weight: 500;">{content_type}</span>
                        <span style="color: {theme_colors['text_accent']}; font-weight: 600;">{count} ({percentage:.0f}%)</span>
                    </div>
                    <div style="width: 100%; height: 8px; background: {theme_colors['progress_bg']}; border-radius: 4px; overflow: hidden;">
                        <div style="width: {percentage}%; height: 100%; background: linear-gradient(90deg, #8b5cf6, #a78bfa); border-radius: 4px;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
