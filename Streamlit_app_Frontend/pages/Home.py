import streamlit as st

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="AI Content Studio - Home",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------
# HIDE STREAMLIT ELEMENTS
# -------------------------------
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] { display: none; }
        [data-testid="stSidebar"] { display: none; }
        header { visibility: hidden; }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# CUSTOM CSS
# -------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    .stApp {
        background: #0a0a0a;
        font-family: 'Inter', sans-serif;
    }
    
    /* Background Image with Blur */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url('https://images.unsplash.com/photo-1639322537228-f710d846310a?q=80&w=2832&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        filter: blur(8px) brightness(0.4);
        z-index: 0;
    }
    
    /* Dark Overlay */
    .stApp::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.6);
        z-index: 1;
    }
    
    /* Content Layer */
    .block-container {
        position: relative;
        z-index: 10;
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* Navigation */
    .nav-container {
        position: fixed;
        top: 0;
        width: 100%;
        background: rgba(15, 23, 42, 0.95);
        backdrop-filter: blur(20px);
        padding: 1rem 3rem;
        z-index: 1000;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .nav-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .nav-buttons {
        display: flex;
        gap: 1rem;
        align-items: center;
    }
    
    .logo-icon {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    
    .logo-text h1 {
        font-size: 1.3rem;
        background: linear-gradient(135deg, #a5b4fc, #c4b5fd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        margin: 0;
    }
    
    .logo-text p {
        font-size: 0.75rem;
        color: #9ca3af;
        margin: 0;
    }
    
    /* Hero Section */
    .hero-section {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 120px 2rem 4rem;
        color: white;
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, #ffffff, #a5b4fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: fadeInUp 1s ease;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: #9ca3af;
        margin-bottom: 2.5rem;
        max-width: 700px;
        animation: fadeInUp 1s ease 0.2s backwards;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Feature Cards */
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 2rem;
        margin-top: 4rem;
        max-width: 1200px;
        animation: fadeInUp 1s ease 0.6s backwards;
    }
    
    .feature-card {
        background: rgba(31, 41, 55, 0.5);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        border-color: rgba(99, 102, 241, 0.5);
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.2);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        color: #a5b4fc;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .feature-text {
        color: #9ca3af;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Section Styles */
    .content-section {
        padding: 5rem 3rem;
        color: white;
    }
    
    .section-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 3rem;
        background: linear-gradient(135deg, #a5b4fc, #c4b5fd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Steps Grid */
    .steps-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 3rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .step-card {
        text-align: center;
        padding: 2rem;
    }
    
    .step-number {
        width: 80px;
        height: 80px;
        margin: 0 auto 1.5rem;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        font-weight: 700;
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.4);
    }
    
    .step-title {
        color: #a5b4fc;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .step-text {
        color: #9ca3af;
        line-height: 1.8;
    }
    
    /* Benefits Grid */
    .benefits-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .benefit-card {
        background: rgba(31, 41, 55, 0.5);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 2.5rem;
        transition: all 0.3s ease;
    }
    
    .benefit-card:hover {
        transform: translateY(-5px);
        border-color: rgba(99, 102, 241, 0.5);
    }
    
    .benefit-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .benefit-title {
        color: #a5b4fc;
        font-size: 1.3rem;
        margin-bottom: 1rem;
    }
    
    .benefit-text {
        color: #9ca3af;
        line-height: 1.6;
    }
    
    /* Audience Grid */
    .audience-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .audience-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.8));
        border: 2px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .audience-card:hover {
        transform: scale(1.05);
        border-color: rgba(99, 102, 241, 0.5);
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.3);
    }
    
    .audience-emoji {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    .audience-title {
        color: #a5b4fc;
        font-size: 1.2rem;
        margin-bottom: 0.8rem;
    }
    
    .audience-text {
        color: #9ca3af;
        font-size: 0.9rem;
    }
    
    /* CTA Section */
    .cta-section {
        text-align: center;
        padding: 5rem 2rem;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
    }
    
    .cta-title {
        font-size: 3rem;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, #ffffff, #a5b4fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .cta-text {
        font-size: 1.2rem;
        color: #9ca3af;
        margin-bottom: 2rem;
    }
    
    /* Footer */
    .footer {
        background: rgba(15, 23, 42, 0.9);
        padding: 2rem;
        text-align: center;
        color: #6b7280;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Streamlit Buttons Override */
    .stButton button {
        background: linear-gradient(135deg, #ec4899, #f97316) !important;
        color: white !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 1rem 2.5rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        box-shadow: 0 4px 25px rgba(236, 72, 153, 0.5) !important;
        transition: all 0.3s ease !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 40px rgba(236, 72, 153, 0.7) !important;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }
        
        .hero-subtitle {
            font-size: 1rem;
        }
        
        .section-title {
            font-size: 2rem;
        }
        
        .nav-container {
            padding: 1rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# NAVIGATION BAR
# -------------------------------
st.markdown("""
    <div class="nav-container">
        <div class="nav-content">
            <div class="logo-section">
                <div class="logo-icon">✨</div>
                <div class="logo-text">
                    <h1>AI Content Studio</h1>
                    <p>Craft. Refine. Publish.</p>
                </div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Add proper spacing for fixed navbar
st.markdown('<div style="height: 90px;"></div>', unsafe_allow_html=True)

# Navigation buttons - now properly spaced below navbar
col1, col2, col3, col4 = st.columns([7, 1, 1, 1])
with col2:
    if st.button("Login", key="nav_login", use_container_width=True):
        st.switch_page("pages/Login.py")
with col3:
    if st.button("Sign Up", key="nav_signup", use_container_width=True):
        st.switch_page("pages/Register.py")
with col4:
    if st.button("Demo", key="nav_demo", use_container_width=True):
        st.switch_page("pages/Demo.py")

# Additional CSS for nav buttons styling
st.markdown("""
    <style>
    /* Nav button overrides */
    button[key^="nav_"] {
        background: transparent !important;
        border: 1.5px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 25px !important;
        padding: 0.6rem 1.5rem !important;
        font-size: 0.9rem !important;
        box-shadow: none !important;
    }
    
    button[key^="nav_"]:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.5) !important;
        transform: translateY(-2px) !important;
    }
    
    button[key="nav_signup"] {
        background: linear-gradient(135deg, #ec4899, #f97316) !important;
        border: none !important;
        box-shadow: 0 4px 20px rgba(236, 72, 153, 0.4) !important;
    }
    
    button[key="nav_signup"]:hover {
        background: linear-gradient(135deg, #ec4899, #f97316) !important;
        box-shadow: 0 6px 30px rgba(236, 72, 153, 0.6) !important;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# HERO SECTION
# -------------------------------
st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">Unlock Your Content's Potential with AI</h1>
        <p class="hero-subtitle">Craft. Refine. Pull. Effortuate & Optimize for Any Platform.</p>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("Start Free Trial", key="hero_cta", use_container_width=True):
        st.switch_page("pages/Register.py")

st.markdown("""
    <div class="features-grid">
        <div class="feature-card">
            <div class="feature-icon">📝</div>
            <h3 class="feature-title">Diverse Content Types</h3>
            <p class="feature-text">From LinkedIn posts to blog articles, create any content format</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🎨</div>
            <h3 class="feature-title">Customizable Tone</h3>
            <p class="feature-text">Match your brand voice perfectly with AI-powered tone adjustment</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <h3 class="feature-title">Targeted Publishing</h3>
            <p class="feature-text">Optimize content for your specific audience and platform</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# -------------------------------
# HOW IT WORKS SECTION
# -------------------------------
st.markdown("""
    <div class="content-section">
        <h2 class="section-title">How It Works</h2>
        <div class="steps-grid">
            <div class="step-card">
                <div class="step-number">1</div>
                <h3 class="step-title">💭 Share Your Idea</h3>
                <p class="step-text">Just type your rough idea or topic. No need to be perfect - our AI understands what you mean!</p>
            </div>
            <div class="step-card">
                <div class="step-number">2</div>
                <h3 class="step-title">✨ AI Generates</h3>
                <p class="step-text">Our smart AI analyzes your input and creates multiple refined prompts for you to choose from.</p>
            </div>
            <div class="step-card">
                <div class="step-number">3</div>
                <h3 class="step-title">⚙️ Customize</h3>
                <p class="step-text">Select your content type, tone, audience, and purpose. Make it uniquely yours!</p>
            </div>
            <div class="step-card">
                <div class="step-number">4</div>
                <h3 class="step-title">🚀 Publish</h3>
                <p class="step-text">Get polished, ready-to-publish content in seconds. Download and share anywhere!</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# -------------------------------
# WHY CHOOSE US SECTION
# -------------------------------
st.markdown("""
    <div class="content-section">
        <h2 class="section-title">Why Choose AI Content Studio?</h2>
        <div class="benefits-grid">
            <div class="benefit-card">
                <div class="benefit-icon">⚡</div>
                <h3 class="benefit-title">Lightning Fast</h3>
                <p class="benefit-text">Create professional content in minutes, not hours. Say goodbye to writer's block!</p>
            </div>
            <div class="benefit-card">
                <div class="benefit-icon">🎯</div>
                <h3 class="benefit-title">Precision Targeting</h3>
                <p class="benefit-text">Tailor your message for specific audiences - from recruiters to tech professionals.</p>
            </div>
            <div class="benefit-card">
                <div class="benefit-icon">💎</div>
                <h3 class="benefit-title">Premium Quality</h3>
                <p class="benefit-text">AI-powered content that reads like a human wrote it. Professional and authentic.</p>
            </div>
            <div class="benefit-card">
                <div class="benefit-icon">📚</div>
                <h3 class="benefit-title">Smart Templates</h3>
                <p class="benefit-text">Pre-built templates for common use cases. Start creating in seconds.</p>
            </div>
            <div class="benefit-card">
                <div class="benefit-icon">🔒</div>
                <h3 class="benefit-title">Your Data</h3>
                <p class="benefit-text">Complete privacy and security. Your ideas stay yours forever.</p>
            </div>
            <div class="benefit-card">
                <div class="benefit-icon">♾️</div>
                <h3 class="benefit-title">Unlimited</h3>
                <p class="benefit-text">No limits on ideas. Create as much content as you need.</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# -------------------------------
# WHO SHOULD USE SECTION
# -------------------------------
st.markdown("""
    <div class="content-section">
        <h2 class="section-title">Who Should Use This?</h2>
        <div class="audience-grid">
            <div class="audience-card">
                <div class="audience-emoji">💼</div>
                <h3 class="audience-title">Job Seekers</h3>
                <p class="audience-text">Craft compelling LinkedIn posts and professional updates</p>
            </div>
            <div class="audience-card">
                <div class="audience-emoji">📱</div>
                <h3 class="audience-title">Social Media Managers</h3>
                <p class="audience-text">Generate engaging posts across multiple platforms</p>
            </div>
            <div class="audience-card">
                <div class="audience-emoji">✍️</div>
                <h3 class="audience-title">Content Creators</h3>
                <p class="audience-text">Overcome writer's block and produce quality content</p>
            </div>
            <div class="audience-card">
                <div class="audience-emoji">🚀</div>
                <h3 class="audience-title">Entrepreneurs</h3>
                <p class="audience-text">Create marketing copy and announcements quickly</p>
            </div>
            <div class="audience-card">
                <div class="audience-emoji">🎓</div>
                <h3 class="audience-title">Students</h3>
                <p class="audience-text">Perfect your essays and academic content</p>
            </div>
            <div class="audience-card">
                <div class="audience-emoji">👔</div>
                <h3 class="audience-title">Professionals</h3>
                <p class="audience-text">Write reports and business communications</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# -------------------------------
# FINAL CTA SECTION
# -------------------------------
st.markdown("""
    <div class="cta-section">
        <h2 class="cta-title">Join the Future of Content Creation</h2>
        <p class="cta-text">Start creating amazing content today.</p>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("Start Free Trial", key="footer_cta", use_container_width=True):
        st.switch_page("pages/Demo.py")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("""
    <div class="footer">
        <p>© 2025 AI Content Studio. Powered by Advanced AI Technology.</p>
        <p style="margin-top: 0.5rem;">Built with ❤️ for content creators everywhere</p>
    </div>
""", unsafe_allow_html=True)