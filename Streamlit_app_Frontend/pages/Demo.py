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

# -------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------
def init_demo_state():
    defaults = {
        "demo_idea": "",
        "demo_content_type": None,
        "demo_tone": None,
        "demo_audience": None,
        "demo_purpose": None,
        "demo_word_limit": 150,
        "theme": "dark",
        "show_demo_banner": True
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
            "bg_tertiary": "#13151f",
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
            "bg_tertiary": "#f3f4f6",
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
        transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
    }}
    
    /* THEME BASE */
    html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"] {{
        background: {theme_colors['bg_primary']} !important;
        color: {theme_colors['text_primary']} !important;
    }}
    
    .main .block-container {{
        padding: 1rem 3rem !important;
        max-width: 1400px !important;
        margin: 0 auto !important;
    }}
    
    /* HIDE STREAMLIT DEFAULTS */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    [data-testid="stSidebar"] {{display: none;}}
    
    /* DEMO BANNER */
    .demo-banner {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #8b5cf6, #ec4899, #f97316);
        color: white;
        padding: 1rem 2rem;
        text-align: center;
        z-index: 9999;
        font-weight: 600;
        font-size: 0.95rem;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.3);
    }}
    
    .demo-banner-close {{
        position: absolute;
        right: 2rem;
        top: 50%;
        transform: translateY(-50%);
        cursor: pointer;
        font-size: 1.5rem;
        opacity: 0.8;
        transition: opacity 0.2s;
    }}
    
    .demo-banner-close:hover {{
        opacity: 1;
    }}
    
    .demo-content {{
        margin-top: 80px;
    }}
    
    /* TOP NAVBAR */
    .top-navbar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem 0;
        margin-bottom: 2rem;
        border-bottom: 1px solid {theme_colors['border_color']};
    }}
    
    .logo-section {{
        display: flex;
        align-items: center;
        gap: 1rem;
    }}
    
    .logo-icon {{
        font-size: 2rem;
    }}
    
    .logo-text {{
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #c4b5fd, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    /* THEME TOGGLE BUTTON */
    .theme-toggle {{
        background: {theme_colors['bg_card']};
        border: 1px solid {theme_colors['border_color']};
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        cursor: pointer;
        transition: all 0.3s ease;
        color: {theme_colors['text_secondary']};
        font-weight: 500;
    }}
    
    .theme-toggle:hover {{
        border-color: {theme_colors['border_hover']};
        background: {theme_colors['bg_card_hover']};
        color: {theme_colors['text_accent']};
    }}
    
    /* HEADER TITLE */
    .header-title {{
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #c4b5fd 0%, #a78bfa 50%, #8b5cf6 100%);
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
    .stButton button {{
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
    
    .stButton button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(167, 139, 250, 0.5) !important;
        filter: brightness(1.1) !important;
    }}
    
    .stButton button:active {{
        transform: translateY(0) !important;
    }}
    
    /* FEATURE SHOWCASE */
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
    
    /* DEMO OVERLAY */
    .demo-overlay {{
        position: relative;
    }}
    
    .demo-overlay::after {{
        content: '🔒 Sign up to unlock full features';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(139, 92, 246, 0.95);
        color: white;
        padding: 1rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.3s ease;
        z-index: 10;
    }}
    
    .demo-overlay:hover::after {{
        opacity: 1;
    }}
    
    /* SCROLLBAR */
    ::-webkit-scrollbar {{
        width: 10px;
        height: 10px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: rgba(31, 41, 55, 0.3);
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
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# DEMO BANNER
# -------------------------------
if st.session_state.show_demo_banner:
    st.markdown("""
        <div class="demo-banner">
            ✨ You're viewing a demo version - Sign up to unlock all features and save your content!
        </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="demo-content">', unsafe_allow_html=True)

# -------------------------------
# TOP NAVBAR
# -------------------------------
col_logo, col_theme = st.columns([3, 1])

with col_logo:
    st.markdown("""
        <div class="logo-section">
            <div class="logo-icon">✨</div>
            <div class="logo-text">AI Content Studio</div>
        </div>
    """, unsafe_allow_html=True)

with col_theme:
    theme_icon = "🌙" if st.session_state.theme == "dark" else "☀️"
    theme_text = "Light" if st.session_state.theme == "dark" else "Dark"
    
    if st.button(f"{theme_icon} {theme_text}", key="theme_toggle", use_container_width=True):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

# -------------------------------
# MAIN DEMO CONTENT
# -------------------------------
st.markdown('<div class="header-title">Experience AI-Powered Content Creation</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">Try the demo below to see how easy it is to create professional content</div>', unsafe_allow_html=True)

# Feature Showcase
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

st.markdown("<hr>", unsafe_allow_html=True)

# Demo Form
st.markdown('<div class="header-title" style="font-size: 1.8rem; margin-top: 2rem;">Try It Now - Interactive Demo</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">Fill in your idea and see how the platform works</div>', unsafe_allow_html=True)

st.markdown('<div class="content-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">💭 Share Your Idea</div>', unsafe_allow_html=True)
st.markdown('<div class="card-subtitle">Tell us what you want to create - be as detailed as you like</div>', unsafe_allow_html=True)

demo_idea = st.text_area(
    "Your Idea",
    placeholder="Example: I recently won first place at a national hackathon for developing an AI-powered healthcare app that helps doctors diagnose diseases faster...",
    height=180,
    value=st.session_state.demo_idea,
    label_visibility="collapsed",
    key="demo_idea_input"
)

st.markdown('</div>', unsafe_allow_html=True)

# Preferences Preview (Locked)
st.markdown('<div class="content-card demo-overlay" style="position: relative; opacity: 0.6;">', unsafe_allow_html=True)
st.markdown('<div class="card-title">⚙️ Content Preferences (Unlock by Signing Up)</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.selectbox("Content Type", ["LinkedIn Post", "Email", "Blog Post", "Tweet Thread"], disabled=True, key="demo_type")
    st.selectbox("Tone", ["Professional", "Confident", "Friendly"], disabled=True, key="demo_tone_sel")

with col2:
    st.selectbox("Target Audience", ["Recruiters", "General Audience", "Technical Professionals"], disabled=True, key="demo_audience_sel")
    st.selectbox("Purpose", ["Share Experience", "Showcase Skills", "Inspire Others"], disabled=True, key="demo_purpose_sel")

st.markdown('</div>', unsafe_allow_html=True)

# Call to Action
st.markdown("<br>", unsafe_allow_html=True)

col_btn1, col_btn2 = st.columns([1, 1])

with col_btn1:
    if st.button("🎯 Generate Prompts - Try Demo!", use_container_width=True, key="generate_demo"):
        if len(demo_idea.strip()) < 10:
            st.warning("⚠️ Please provide more detail about your idea to see the demo in action!")
        else:
            st.session_state.demo_idea = demo_idea
            
            # Show loading animation
            with st.spinner("🔮 Preparing your demo experience..."):
                time.sleep(1.5)
            
            # Show message and redirect
            st.success("✨ Great idea! To generate prompts and access all features, please sign up for free!")
            st.info("📝 Redirecting you to registration...")
            time.sleep(2)
            
            # Redirect to register page
            st.switch_page("pages/Register.py")

with col_btn2:
    if st.button("🚀 Sign Up Now - It's Free!", use_container_width=True, type="primary", key="signup_direct"):
        st.switch_page("pages/Register.py")

# Sample Output Preview
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('<div class="header-title" style="font-size: 1.6rem;">Sample Output Preview</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">This is what you can expect after generating content</div>', unsafe_allow_html=True)

st.markdown(f"""
    <div class="content-card">
        <div class="card-title">📝 Generated LinkedIn Post (Sample)</div>
        <div style="background: {theme_colors['bg_card']}; border: 1px solid rgba(139, 92, 246, 0.2); border-radius: 12px; padding: 2rem; margin-top: 1rem; color: {theme_colors['text_primary']}; line-height: 1.8;">
            🏆 Thrilled to announce that our team won first place at the National AI Hackathon!
            
            Our AI-powered healthcare solution helps doctors diagnose diseases 3x faster, potentially saving countless lives. This wouldn't have been possible without the incredible support of my teammates and mentors.
            
            The journey taught me that innovation happens when we combine technical expertise with genuine empathy for real-world problems. Healthcare professionals deserve better tools, and we're committed to making that happen.
            
            Huge thanks to everyone who believed in our vision. This is just the beginning! 🚀
            
            #AI #Healthcare #Innovation #Hackathon #TechForGood
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="content-card" style="margin-top: 2rem;">
        <div class="card-title">📊 Quality Analysis (Sample)</div>
        <div style="margin-top: 1.5rem;">
            <div style="margin-bottom: 1.5rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: {theme_colors['text_primary']}; font-weight: 500;">Clarity & Readability</span>
                    <span style="color: {theme_colors['text_accent']}; font-weight: 700;">92%</span>
                </div>
                <div style="width: 100%; height: 10px; background: {theme_colors['progress_bg']}; border-radius: 5px; overflow: hidden;">
                    <div style="width: 92%; height: 100%; background: linear-gradient(90deg, #a78bfa, #ec4899); border-radius: 5px;"></div>
                </div>
            </div>
            
            <div style="margin-bottom: 1.5rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: {theme_colors['text_primary']}; font-weight: 500;">Engagement Level</span>
                    <span style="color: {theme_colors['text_accent']}; font-weight: 700;">88%</span>
                </div>
                <div style="width: 100%; height: 10px; background: {theme_colors['progress_bg']}; border-radius: 5px; overflow: hidden;">
                    <div style="width: 88%; height: 100%; background: linear-gradient(90deg, #a78bfa, #ec4899); border-radius: 5px;"></div>
                </div>
            </div>
            
            <div style="margin-bottom: 1.5rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: {theme_colors['text_primary']}; font-weight: 500;">Professional Quality</span>
                    <span style="color: {theme_colors['text_accent']}; font-weight: 700;">95%</span>
                </div>
                <div style="width: 100%; height: 10px; background: {theme_colors['progress_bg']}; border-radius: 5px; overflow: hidden;">
                    <div style="width: 95%; height: 100%; background: linear-gradient(90deg, #a78bfa, #ec4899); border-radius: 5px;"></div>
                </div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Final CTA
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
    <div class="content-card" style="text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(236, 72, 153, 0.1));">
        <div style="font-size: 2rem; margin-bottom: 1rem;">🚀</div>
        <div style="font-size: 1.5rem; font-weight: 700; color: {theme_colors['text_accent']}; margin-bottom: 1rem;">
            Ready to Create Amazing Content?
        </div>
        <div style="color: {theme_colors['text_secondary']}; font-size: 1rem; margin-bottom: 2rem; line-height: 1.6;">
            Sign up now to unlock all features including:<br>
            ✓ Unlimited content generation<br>
            ✓ Save and manage your drafts<br>
            ✓ Create custom templates<br>
            ✓ Quality analysis for every piece<br>
            ✓ Multiple content types and styles
        </div>
    </div>
""", unsafe_allow_html=True)

col_final1, col_final2, col_final3 = st.columns([1, 2, 1])

with col_final2:
    if st.button("🎉 Get Started Free - No Credit Card Required", use_container_width=True, key="final_cta"):
        st.switch_page("pages/Register.py")

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
    <div style="text-align: center; color: {theme_colors['text_tertiary']}; font-size: 0.85rem; padding: 2rem 0; border-top: 1px solid {theme_colors['border_color']};">
        ✨ AI Content Studio - Transform your ideas into professional content in seconds
    </div>
""", unsafe_allow_html=True)