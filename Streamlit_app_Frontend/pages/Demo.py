import streamlit as st
import time

# -------------------------------
# PAGE CONFIG (Must be first!)
# -------------------------------
st.set_page_config(
    page_title="AI Content Studio - Demo",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide sidebar completely
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        display: none !important;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------
def init_demo_state():
    defaults = {
        "demo_idea": "",
        "theme": "dark",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_demo_state()

# -------------------------------
# THEME CONFIGURATION
# -------------------------------
def get_theme_colors():
    """Return theme-specific color variables"""
    if st.session_state.theme == "dark":
        return {
            "bg_primary": "#0f1117",
            "bg_secondary": "#1a1d29",
            "bg_card": "rgba(31, 41, 55, 0.4)",
            "bg_card_hover": "rgba(31, 41, 55, 0.6)",
            "border_color": "rgba(255, 255, 255, 0.08)",
            "border_hover": "rgba(139, 92, 246, 0.3)",
            "text_primary": "#e5e7eb",
            "text_secondary": "#9ca3af",
            "text_tertiary": "#6b7280",
            "text_accent": "#c4b5fd",
            "input_bg": "rgba(31, 41, 55, 0.5)",
            "progress_bg": "rgba(75, 85, 99, 0.3)",
        }
    else:
        return {
            "bg_primary": "#f9fafb",
            "bg_secondary": "#ffffff",
            "bg_card": "rgba(255, 255, 255, 0.8)",
            "bg_card_hover": "rgba(255, 255, 255, 0.95)",
            "border_color": "rgba(0, 0, 0, 0.08)",
            "border_hover": "rgba(139, 92, 246, 0.4)",
            "text_primary": "#1f2937",
            "text_secondary": "#6b7280",
            "text_tertiary": "#9ca3af",
            "text_accent": "#7c3aed",
            "input_bg": "rgba(255, 255, 255, 0.9)",
            "progress_bg": "rgba(229, 231, 235, 0.5)",
        }

theme_colors = get_theme_colors()

# -------------------------------
# STYLING
# -------------------------------
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {{
        font-family: 'Inter', -apple-system, sans-serif;
    }}
    
    html, body, [data-testid="stApp"] {{
        background: {theme_colors['bg_primary']} !important;
        color: {theme_colors['text_primary']} !important;
    }}
    
    .main .block-container {{
        padding: 1rem 3rem !important;
        max-width: 1400px !important;
    }}
    
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    .demo-banner {{
        background: linear-gradient(135deg, #8b5cf6, #ec4899, #f97316);
        color: white;
        padding: 1rem 2rem;
        text-align: center;
        font-weight: 600;
        font-size: 0.95rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.3);
    }}
    
    .logo-section {{
        text-align: center;
        padding: 2rem 0;
    }}
    
    .logo-icon {{
        font-size: 3rem;
        margin-bottom: 1rem;
    }}
    
    .logo-text {{
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #c4b5fd, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    .header-title {{
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #c4b5fd, #a78bfa, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 2rem 0 0.5rem 0;
        text-align: center;
    }}
    
    .header-subtitle {{
        text-align: center;
        color: {theme_colors['text_secondary']};
        font-size: 1.1rem;
        margin-bottom: 3rem;
    }}
    
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
    }}
    
    .card-title {{
        font-size: 1.3rem;
        font-weight: 600;
        color: {theme_colors['text_primary']};
        margin-bottom: 1rem;
    }}
    
    .card-subtitle {{
        font-size: 0.95rem;
        color: {theme_colors['text_secondary']};
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }}
    
    .stTextArea textarea {{
        background: {theme_colors['input_bg']} !important;
        border: 1.5px solid {theme_colors['border_color']} !important;
        border-radius: 12px !important;
        color: {theme_colors['text_primary']} !important;
        padding: 1rem !important;
        font-size: 0.95rem !important;
        min-height: 150px !important;
    }}
    
    .stTextArea textarea:focus {{
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15) !important;
    }}
    
    .stButton button {{
        background: linear-gradient(135deg, #a78bfa, #ec4899, #f97316) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.85rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(167, 139, 250, 0.3) !important;
        width: 100%;
    }}
    
    .stButton button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(167, 139, 250, 0.5) !important;
    }}
    
    .feature-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin: 3rem 0;
    }}
    
    .feature-card {{
        background: {theme_colors['bg_card']};
        border: 1px solid {theme_colors['border_color']};
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }}
    
    .feature-card:hover {{
        border-color: {theme_colors['border_hover']};
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(139, 92, 246, 0.2);
    }}
    
    .feature-icon {{
        font-size: 3rem;
        margin-bottom: 1rem;
    }}
    
    .feature-title {{
        color: {theme_colors['text_accent']};
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }}
    
    .feature-desc {{
        color: {theme_colors['text_secondary']};
        font-size: 0.9rem;
        line-height: 1.6;
    }}
    
    .sample-output {{
        background: {theme_colors['bg_card']};
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 16px;
        padding: 2rem;
        color: {theme_colors['text_primary']};
        line-height: 1.8;
        margin: 1.5rem 0;
    }}
    
    .metric-bar-container {{
        margin-bottom: 1.5rem;
    }}
    
    .metric-label {{
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    }}
    
    .metric-name {{
        color: {theme_colors['text_primary']};
        font-weight: 500;
    }}
    
    .metric-score {{
        color: {theme_colors['text_accent']};
        font-weight: 700;
        font-size: 1.1rem;
    }}
    
    .metric-bar {{
        width: 100%;
        height: 10px;
        background: {theme_colors['progress_bg']};
        border-radius: 5px;
        overflow: hidden;
    }}
    
    .metric-bar-fill {{
        height: 100%;
        background: linear-gradient(90deg, #a78bfa, #ec4899);
        border-radius: 5px;
    }}
    
    .cta-box {{
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(236, 72, 153, 0.1));
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 16px;
        padding: 3rem 2rem;
        text-align: center;
        margin: 3rem 0;
    }}
    
    .cta-icon {{
        font-size: 3rem;
        margin-bottom: 1rem;
    }}
    
    .cta-title {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {theme_colors['text_accent']};
        margin-bottom: 1rem;
    }}
    
    .cta-text {{
        color: {theme_colors['text_secondary']};
        font-size: 1rem;
        line-height: 1.8;
        margin-bottom: 2rem;
    }}
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# MAIN CONTENT
# -------------------------------

# Demo Banner
st.markdown("""
    <div class="demo-banner">
        ✨ You're viewing a demo version - Sign up to unlock all features and save your content!
    </div>
""", unsafe_allow_html=True)

# Logo
st.markdown("""
    <div class="logo-section">
        <div class="logo-icon">✨</div>
        <div class="logo-text">AI Content Studio</div>
    </div>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="header-title">Experience AI-Powered Content Creation</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">Try the demo below to see how easy it is to create professional content</div>', unsafe_allow_html=True)

# Feature Grid
st.markdown(f"""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Smart Prompts</div>
            <div class="feature-desc">AI generates multiple refined prompts from your basic idea</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">Instant Generation</div>
            <div class="feature-desc">Create professional content in seconds, not hours</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🎨</div>
            <div class="feature-title">Multiple Styles</div>
            <div class="feature-desc">LinkedIn posts, blogs, tweets, emails and more</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Quality Analysis</div>
            <div class="feature-desc">Get detailed insights on clarity, engagement, and tone</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">💾</div>
            <div class="feature-title">Save & Reuse</div>
            <div class="feature-desc">Store templates and access your content history</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🔄</div>
            <div class="feature-title">Regenerate</div>
            <div class="feature-desc">Not happy? Generate new variations instantly</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("<hr style='border: none; height: 1px; background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.3), transparent); margin: 3rem 0;'>", unsafe_allow_html=True)

# Demo Form Section
st.markdown('<div class="header-title" style="font-size: 1.8rem; margin-top: 2rem;">Try It Now</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">Fill in your idea and see how the platform works</div>', unsafe_allow_html=True)

st.markdown('<div class="content-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">💭 Share Your Idea</div>', unsafe_allow_html=True)
st.markdown('<div class="card-subtitle">Tell us what you want to create - be as detailed as you like</div>', unsafe_allow_html=True)

demo_idea = st.text_area(
    "Your Idea",
    placeholder="Example: I recently won first place at a national hackathon for developing an AI-powered healthcare app that helps doctors diagnose diseases faster. I want to share this achievement on LinkedIn to connect with recruiters and inspire other developers...",
    height=150,
    value=st.session_state.demo_idea,
    label_visibility="collapsed",
    key="demo_idea_input"
)

st.markdown('</div>', unsafe_allow_html=True)

# Action Buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("🎯 Generate Prompts - Try Demo!", key="generate_demo"):
        if len(demo_idea.strip()) < 10:
            st.warning("⚠️ Please provide more detail about your idea")
        else:
            with st.spinner("🔮 Preparing your demo experience..."):
                time.sleep(1.5)
            st.success("✨ Great idea! To generate prompts and access all features, please sign up for free!")
            st.info("📝 Redirecting you to registration...")
            time.sleep(2)
            st.switch_page("pages/Register.py")

with col2:
    if st.button("🚀 Sign Up Now - It's Free!", key="signup_direct"):
        st.switch_page("pages/Register.py")

# Sample Output Section
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('<div class="header-title" style="font-size: 1.6rem;">Sample Output Preview</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">This is what you can expect after generating content</div>', unsafe_allow_html=True)

st.markdown('<div class="content-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">📝 Generated LinkedIn Post (Sample)</div>', unsafe_allow_html=True)
st.markdown("""
    <div class="sample-output">
        🏆 Thrilled to announce that our team won first place at the National AI Hackathon!<br><br>
        
        Our AI-powered healthcare solution helps doctors diagnose diseases 3x faster, potentially saving countless lives. This wouldn't have been possible without the incredible support of my teammates and mentors.<br><br>
        
        The journey taught me that innovation happens when we combine technical expertise with genuine empathy for real-world problems. Healthcare professionals deserve better tools, and we're committed to making that happen.<br><br>
        
        Huge thanks to everyone who believed in our vision. This is just the beginning! 🚀<br><br>
        
        #AI #Healthcare #Innovation #Hackathon #TechForGood
    </div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Quality Analysis Sample
st.markdown('<div class="content-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">📊 Quality Analysis (Sample)</div>', unsafe_allow_html=True)

metrics = [
    ("Clarity & Readability", 92),
    ("Engagement Level", 88),
    ("Tone Consistency", 95),
    ("Audience Relevance", 90),
    ("Professional Quality", 93)
]

for metric_name, score in metrics:
    st.markdown(f"""
        <div class="metric-bar-container">
            <div class="metric-label">
                <span class="metric-name">{metric_name}</span>
                <span class="metric-score">{score}%</span>
            </div>
            <div class="metric-bar">
                <div class="metric-bar-fill" style="width: {score}%;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Final CTA
st.markdown(f"""
    <div class="cta-box">
        <div class="cta-icon">🚀</div>
        <div class="cta-title">Ready to Create Amazing Content?</div>
        <div class="cta-text">
            Sign up now to unlock all features including:<br>
            ✓ Unlimited content generation<br>
            ✓ Save and manage your drafts<br>
            ✓ Create custom templates<br>
            ✓ Quality analysis for every piece<br>
            ✓ Multiple content types and styles
        </div>
    </div>
""", unsafe_allow_html=True)

col_final = st.columns([1, 2, 1])
with col_final[1]:
    if st.button("🎉 Get Started Free", key="final_cta"):
        st.switch_page("pages/Register.py")

# Footer
st.markdown(f"""
    <div style="text-align: center; color: {theme_colors['text_tertiary']}; font-size: 0.85rem; padding: 3rem 0 2rem 0; border-top: 1px solid {theme_colors['border_color']}; margin-top: 3rem;">
        ✨ AI Content Studio - Transform your ideas into professional content in seconds
    </div>
""", unsafe_allow_html=True)