import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import time
import os
from dotenv import load_dotenv

# Initialize environment variables centrally before local imports
load_dotenv()

from auth import *
from job_matcher import *
from resume_comparator import compare_resumes

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="AI Resume Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)
pio.templates.default = "plotly_dark"

# ==========================================
# CUSTOM CSS / PREMIUM DESIGN
# ==========================================
def inject_custom_css():
    css = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;600;800&display=swap" rel="stylesheet">
<style>
/* Global Font & Animated Background */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3, h4, h5, h6, .glow-text { font-family: 'Outfit', sans-serif; }

@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.stApp { 
    background: linear-gradient(-45deg, #091219, #0f2027, #203a43, #2c5364, #122129); 
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    color: white; 
}
#MainMenu { visibility: hidden; }
header { background: transparent !important; }

/* Sidebar Premium */
[data-testid="stSidebar"] {
    background-color: rgba(9, 18, 25, 0.65) !important;
    backdrop-filter: blur(25px);
    -webkit-backdrop-filter: blur(25px);
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

/* Hide Radio Button Circle & Style like modern menu items */
div[role="radiogroup"] > label {
    background: rgba(255, 255, 255, 0.03);
    padding: 12px 20px;
    border-radius: 10px;
    margin-bottom: 5px;
    border: 1px solid transparent;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
div[role="radiogroup"] > label:hover {
    background: rgba(0, 255, 225, 0.1);
    border: 1px solid rgba(0, 255, 225, 0.3);
    transform: translateX(5px);
}
/* Note: Streamlit's internal exact targetting for radio circles is hard, we just style the whole label container */

/* Premium Glassmorphism Cards */
[data-testid="stMetric"], .glass-card, [data-testid="stFileUploader"], .login-glass {
    background: rgba(20, 30, 40, 0.4);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.4), inset 0 1px 0 0 rgba(255,255,255,0.05);
    padding: 24px;
    transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.4s ease, border-color 0.4s ease;
}
.glass-card, .login-glass { margin-bottom: 24px; color: white; }
.glass-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 50px 0 rgba(0, 255, 225, 0.15), inset 0 1px 0 0 rgba(255,255,255,0.1);
    border: 1px solid rgba(0, 255, 225, 0.2);
}

/* Feature Hover Cards */
.feature-card {
    text-align: center; padding: 30px; height: 100%;
}
.feature-card h1 { font-size: 3.5rem; margin: 0 0 20px 0; transition: transform 0.3s ease; }
.feature-card:hover h1 { transform: scale(1.15) rotate(5deg); }
.feature-card h3 { color: white; margin-bottom: 15px; font-family: 'Outfit', sans-serif; font-weight: 600; }
.feature-card p { color: #a0a0a0; line-height: 1.6; font-size: 1rem; }

/* Dashboard Blur Preview Effect */
.blurred-preview {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: url('https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2070&auto=format&fit=crop');
    background-size: cover;
    background-position: center;
    opacity: 0.15;
    filter: blur(30px);
    z-index: -1;
    pointer-events: none;
}

[data-testid="stMetricValue"] { font-size: 2.5rem !important; font-family: 'Outfit', sans-serif; font-weight: 800 !important; color: #00ffe1 !important; }
[data-testid="stMetricLabel"] { font-size: 1.1rem !important; font-weight: 500 !important; color: #b0c4de !important; letter-spacing: 0.5px; text-transform: uppercase; }

/* Premium Buttons */
.stButton > button {
    background: linear-gradient(135deg, #00ffe1 0%, #00b4d8 100%);
    color: #041014 !important;
    border: none; border-radius: 12px; height: 3.5rem;
    font-weight: 700; font-size: 1.15rem; font-family: 'Outfit', sans-serif;
    box-shadow: 0 4px 20px rgba(0, 255, 225, 0.3);
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); width: 100%;
    text-transform: uppercase; letter-spacing: 1px;
}
.stButton > button:hover {
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 12px 30px rgba(0, 255, 225, 0.5);
    background: linear-gradient(135deg, #0cebeb 0%, #20e3b2 50%, #29ffc6 100%);
}

/* Secondary Buttons/Tabs */
.stTabs [data-baseweb="tab"] {
    background: transparent; border: none !important; color: #a0a0a0; font-family: 'Outfit', sans-serif; font-size: 1.1rem;
}
.stTabs [aria-selected="true"] {
    color: #00ffe1 !important; border-bottom: 3px solid #00ffe1 !important;
}

/* Text Inputs */
.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    background-color: rgba(0, 0, 0, 0.4) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important; color: white !important;
    font-size: 1.05rem; padding: 14px;
}
.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus { 
    border-color: #00ffe1 !important; 
    box-shadow: 0 0 0 1px #00ffe1 !important;
}

/* Globals */
.glow-text { 
    background: linear-gradient(to right, #00ffe1, #00b4d8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 30px rgba(0,255,225,0.4); 
    font-weight: 800; 
}
.stProgress > div > div > div { background: linear-gradient(90deg, #00ffe1 0%, #00b4d8 100%); }
</style>
"""
    css = css.replace('\n', ' ').replace('    ', ' ')
    st.markdown(css, unsafe_allow_html=True)


# ==========================================
# SESSION STATE
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Home"
if "email" not in st.session_state:
    st.session_state.email = ""
if "name" not in st.session_state:
    st.session_state.name = ""
if "otp" not in st.session_state:
    st.session_state.otp = None
if "otp_email" not in st.session_state:
    st.session_state.otp_email = None
if "last_upload_stats" not in st.session_state:
    st.session_state.last_upload_stats = None


# ==========================================
# SIDEBAR
# ==========================================
def render_sidebar():
    with st.sidebar:
        if st.session_state.logged_in:
            st.markdown(
                f"""
                <div style="text-align: center; padding: 15px 0;">
                    <img src="https://api.dicebear.com/7.x/initials/svg?seed={st.session_state.name}&backgroundColor=0f2027&textColor=00ffe1" 
                         width="90" style="border-radius: 50%; border: 2px solid #00ffe1;">
                    <h3 style="margin: 15px 0 5px 0; color: white;">{st.session_state.name}</h3>
                    <p style="color: #cfcfcf; font-size: 13px; margin: 0;">{st.session_state.email}</p>
                    <div style="display: inline-block; background: rgba(0, 255, 0, 0.15); padding: 4px 12px; border-radius: 20px; margin-top: 10px; border: 1px solid rgba(0,255,0,0.3);">
                        <span style="color: #00ff00; font-size: 12px; font-weight: 700;">● Online</span>
                    </div>
                </div>
                """, unsafe_allow_html=True
            )
            st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 20px 0;'>", unsafe_allow_html=True)
            
            menu_options = ["🏠 Home", "📊 Dashboard", "📤 Upload Resume", "🚀 Resume Evolution Dashboard", "📂 My Resumes", "🚪 Logout"]
            def_index = menu_options.index(st.session_state.current_page) if st.session_state.current_page in menu_options else 0
            
            selected_page = st.radio("Navigate", menu_options, label_visibility="collapsed", index=def_index)
            if selected_page != st.session_state.current_page:
                st.session_state.current_page = selected_page
                st.rerun()
            
        else:
            st.markdown("### 🤖 Resume AI")
            st.info("Please sign in to access your customized dashboard.")
            st.session_state.current_page = "Login"

# ==========================================
# VIEWS
# ==========================================

def page_login():
    # Blurred background overlay for the dashboard illusion
    st.markdown("<div class='blurred-preview'></div>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1.2, 1], gap="large")
    
    with col_left:
        st.markdown(
            """
            <div style='margin-top: 20px; padding-right: 20px;'>
                <h1 style='font-size: 4.5rem; line-height: 1.1; margin-bottom: 20px;'>
                    🚀 <span class='glow-text'>ResumeAnalyzer</span> AI
                </h1>
                <p style='color: #b0c4de; font-size: 1.4rem; font-weight: 300; margin-bottom: 40px;'>
                    Smart • Fast • ATS-Optimized
                </p>
                <div style='border-radius: 16px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,255,225,0.15); border: 1px solid rgba(255,255,255,0.05);'>
                    <img src='https://images.unsplash.com/photo-1620712943543-bcc4688e7485?q=80&w=1000&auto=format&fit=crop' width='100%' style='display:block; opacity: 0.9; filter: contrast(1.1) saturate(1.2);'>
                </div>
            </div>
            """, unsafe_allow_html=True
        )
        
    with col_right:
        st.markdown("<div class='login-glass'>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Create Account"])
        
        with tab1:
            st.markdown("<h3 style='margin-bottom:20px; color:white;'>Welcome Back</h3>", unsafe_allow_html=True)
            email = st.text_input("📧 Email Address", placeholder="alex@example.com", key="login_email")
            password = st.text_input("🔒 Password", type="password", placeholder="••••••••", key="login_pass")
            
            # Visual placeholder 'Remember me'
            st.checkbox("Remember me for 30 days", value=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In 🚀"):
                user = verify_login(email.strip(), password.strip())
                if user:
                    st.session_state.logged_in = True
                    st.session_state.email = email
                    st.session_state.name = user[1] if len(user)>1 else email.split("@")[0]
                    st.session_state.current_page = "🏠 Home"
                    st.success("Login Successful ✅")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid credentials")
                    
        with tab2:
            st.markdown("<h3 style='margin-bottom:20px; color:white;'>Join the Platform</h3>", unsafe_allow_html=True)
            reg_name = st.text_input("👤 Full Name", placeholder="Alex Doe")
            reg_email = st.text_input("📧 Email Address", placeholder="alex@example.com", key="reg_email")
            reg_password = st.text_input("🔒 Password", type="password", placeholder="••••••••", key="reg_pass")
            
            if st.button("Send Access OTP"):
                if user_exists(reg_email):
                    st.error("User already exists")
                else:
                    otp = generate_otp()
                    send_otp(reg_email, otp)
                    st.session_state.otp = otp
                    st.session_state.otp_email = reg_email
                    st.success("OTP sent to your email!")
                    
            otp_input = st.text_input("Enter OTP")
            if st.button("Verify & Register"):
                if otp_input and otp_input == st.session_state.otp and reg_email == st.session_state.otp_email:
                    save_user(reg_name, reg_email, reg_password)
                    st.success("Account created successfully ✅. Please login.")
                else:
                    st.error("Invalid OTP")
                    
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # Feature Highlights (Below Login)
    f1, f2, f3 = st.columns(3)
    features = [
        ("📊", "Smart ATS Scoring", "We simulate exact Applicant Tracking Systems algorithms to pre-screen you against top industry standards."),
        ("🤖", "AI Job Matching", "Automatically match your extracted skills against thousands of job profiles to find your perfect fit."),
        ("🚀", "Resume Evolution Insights", "Track your progress over time and see granular analytics on how to lift your resume to the next level.")
    ]
    
    for col, (icon, title, desc) in zip([f1, f2, f3], features):
        col.markdown(f"""
        <div class="glass-card feature-card">
            <h1>{icon}</h1>
            <h3>{title}</h3>
            <p>{desc}</p>
        </div>
        """, unsafe_allow_html=True)


def page_home():
    st.markdown("""
    <div style="text-align: center; padding: 60px 0 40px 0;">
        <h1 style="font-size: 3.8rem; font-weight: 800; margin-bottom: 10px;">
            <span style="color: white;">Master the</span> <span class="glow-text">ATS Algorithms</span>
        </h1>
        <p style="color: #a0a0a0; font-size: 1.25rem; max-width: 650px; margin: 0 auto 40px auto; line-height: 1.6;">
            Leverage top-tier AI models to uncover hidden weaknesses in your resume. Get detailed analytics, missing skill breakdowns, and actionable tips to land your dream job.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    colA, colB, colC = st.columns([1, 1, 1])
    with colB:
        if st.button("🚀 Upload Current Resume"):
            st.session_state.current_page = "📤 Upload Resume"
            st.rerun()
            
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    f1, f2, f3 = st.columns(3)
    features = [
        ("⚡", "Deep Skill Extraction", "We extract over 150,000 tech & soft skills to form a perfect radar profile."),
        ("🎯", "ATS Pre-screening", "We simulate exact Applicant Tracking Systems algorithms to pre-screen you."),
        ("📊", "Granular Analytics", "Visualize missing elements, compare against market standards, and track history.")
    ]
    
    for col, (icon, title, desc) in zip([f1, f2, f3], features):
        col.markdown(f"""
        <div class="glass-card" style="text-align: center; padding: 30px; height: 100%;">
            <h1 style="font-size: 3rem; margin: 0 0 15px 0;">{icon}</h1>
            <h3 style="color: white; margin-bottom: 15px;">{title}</h3>
            <p style="color: #a0a0a0; line-height: 1.5; font-size: 0.95rem;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)


def page_upload():
    st.markdown("<h1 style='margin-bottom: 0;'><span class='glow-text'>📥 Upload Your Resume</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #cfcfcf; margin-bottom: 30px;'>Drag and drop your resume below to get instant AI-powered feedback.</p>", unsafe_allow_html=True)
    
    job_desc = st.text_area("📋 Target Job Description (Optional but recommended for ATS)", height=120, placeholder="Paste the job requirements here...")
    uploaded_file = st.file_uploader("📂 Choose a file", type=["pdf", "docx"], help="Upload PDF or DOCX file")
            
    if uploaded_file is not None:
        st.markdown("---")
        with st.spinner("🧠 AI is analyzing your resume..."):
            
            # --- REAL BACKEND LOGIC ---
            text = extract_text(uploaded_file)
            score = resume_score(text)
            
            # Semantic Job & NLP Matching
            top_roles_data = top_job_roles(text)
            if top_roles_data:
                role = top_roles_data[0]["role"]
                missing = top_roles_data[0]["missing_skills"]
            else:
                role = "Unknown"
                missing = []
                
            if job_desc and len(job_desc) > 10:
                ats = job_match_score(text, job_desc)
            else:
                ats = int(score * 0.85) # Strict AI Fallback, no longer adding free points
                
            st.session_state.last_upload_stats = {
                "score": score,
                "role": role,
                "ats": ats,
                "missing": missing,
                "text": text,
                "filename": uploaded_file.name,
                "top_roles": top_roles_data
            }
            
            try:
                # Rely purely on the DB's UPSERT logic to avoid duplicates 
                # without accidentally blocking valid consecutive uploads of the same file.
                save_resume(st.session_state.email, uploaded_file.name, score)
            except Exception as e:
                st.error(f"⚠️ Could not save to database: {e}")
            
        st.success(f"✨ Analysis Complete for `{uploaded_file.name}`!")
        
        # Display short summary
        st.markdown("### 🤖 Quick AI Suggestions")
        sugg_col1, sugg_col2 = st.columns(2)
        with sugg_col1:
            if missing:
                missing_str = "".join([f"<li><b>{s}</b></li>" for s in missing[:5]])
            else:
                missing_str = "<li>You have all the core skills!</li>"
                
            st.markdown(f"""
            <div class='glass-card' style='border-left: 5px solid #ff4b4b;'>
                <h4 style='color: #ff4b4b; margin-top: 0;'>❌ Missing Skills Detected</h4>
                <ul style="color: #e0e0e0; line-height: 1.6;">{missing_str}</ul>
            </div>
            """, unsafe_allow_html=True)
            
        with sugg_col2:
            st.markdown("""
            <div class='glass-card' style='border-left: 5px solid #00ffe1;'>
                <h4 style='color: #00ffe1; margin-top: 0;'>💡 ATS Optimization Tips</h4>
                <ul style="color: #e0e0e0; line-height: 1.6;">
                    <li><b>Keywords:</b> Use exact phrasing from the JD.</li>
                    <li><b>Quantify Impact:</b> 'Improved speed by 40%' instead of 'Made it faster'.</li>
                    <li><b>Formatting:</b> Remove complex table formatting for parsing accuracy.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            if st.button("📈 View Detailed Dashboard"):
                st.session_state.current_page = "📊 Dashboard"
                st.rerun()


def page_dashboard():
    stats = st.session_state.last_upload_stats
    if not stats:
        st.warning("Please upload a resume first to see your dashboard.")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Go to Upload"):
            st.session_state.current_page = "📤 Upload Resume"
            st.rerun()
        return

    st.markdown("<h1 style='margin-bottom: 0;'><span class='glow-text'>Command Center</span></h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #a0a0a0; margin-bottom: 30px;'>Analysis for: {stats['filename']}</p>", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric(label="📄 Resume Score", value=f"{stats['score']}/100")
    with m2: st.metric(label="🤖 ATS Compatibility", value=f"{stats['ats']}%")
    with m3: st.metric(label="🎯 Predicted Best Role", value=stats['role'])
    with m4: st.metric(label="🚀 Missing Core Skills", value=len(stats['missing']))

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📈 Visual Performance Matrix")
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.markdown("<h4 style='text-align:center; margin-bottom: 20px;'>Current Skill Radar</h4>", unsafe_allow_html=True)
        
        top_role_data = stats.get("top_roles", [])[0] if stats.get("top_roles") else None
        if top_role_data:
            all_target_skills = list(set(top_role_data["contributed_skills"] + top_role_data["missing_skills"]))
            categories = all_target_skills[:6] if all_target_skills else ['communication']
            r_vals = [90 if cat in top_role_data["contributed_skills"] else 20 for cat in categories]
        else:
            categories = ['python', 'sql', 'machine learning', 'data analysis', 'aws', 'java']
            text_lower = stats['text'].lower()
            r_vals = [90 if cat in text_lower else 20 for cat in categories]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=r_vals, theta=[c.title() for c in categories], fill='toself', line_color='#00ffe1', fillcolor='rgba(0, 255, 225, 0.25)'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100], color="white", gridcolor="rgba(255,255,255,0.1)"),
                       angularaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)")),
            showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=40, r=40, t=20, b=20)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with c2:
        st.markdown("<h4 style='text-align:center; margin-bottom: 20px;'>Score Breakdown: Resume vs ATS</h4>", unsafe_allow_html=True)
        scores_df = pd.DataFrame({
            'Category': ['Overall Content', 'ATS Keyword Match', 'Format/Sections'],
            'Score': [stats['score'], stats['ats'], min(stats['score']+5, 100)]
        })
        fig_bar = px.bar(scores_df, x='Category', y='Score', text='Score', color='Score', color_continuous_scale=['#203a43', '#00ffe1'])
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)", title=""),
            yaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)", range=[0,100], title=""),
            coloraxis_showscale=False, margin=dict(l=20, r=20, t=20, b=20)
        )
        fig_bar.update_traces(textposition='outside', textfont=dict(color="white"))
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🏆 AI Career Architect Suggestions")
    
    top_roles = stats.get("top_roles", [])
    if top_roles:
        cols = st.columns(3)
        for idx, role_data in enumerate(top_roles):
            with cols[idx]:
                st.markdown(f"""
                <div class='glass-card' style='border-top: 4px solid #00ffe1; padding: 15px;'>
                    <h4 style='color: #00ffe1; margin: 0 0 10px 0;'>#{idx+1} {role_data['role']}</h4>
                    <h2 style='margin: 0 0 10px 0;'>{role_data['match_percentage']}% Match</h2>
                    <p style='color: #a0a0a0; font-size: 0.9rem; margin-bottom: 10px;'>{role_data['explanation']}</p>
                    <p style='font-size: 0.85rem; color: #4CAF50;'><b>Owned:</b> {', '.join(role_data['contributed_skills'][:4])}</p>
                    <p style='font-size: 0.85rem; color: #ff4b4b;'><b>Missing:</b> {', '.join(role_data['missing_skills'][:4])}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("No advanced career matching data found. Please re-upload your resume.")


def page_compare():
    st.markdown("<h1 style='margin-bottom: 0;'><span class='glow-text'>🚀 Resume Evolution Dashboard</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #cfcfcf; margin-bottom: 30px;'>See how your resume improvements lift your score.</p>", unsafe_allow_html=True)
    
    # Target Job Desc (shared)
    job_desc = st.text_area("📋 Target Job Description (Optional)", height=100, placeholder="Paste job requirements for ATS matching here...")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h3 style='text-align: center; color: #ff4b4b;'>Past Resume (Baseline)</h3>", unsafe_allow_html=True)
        old_file = st.file_uploader("Upload Old Resume", type=["pdf", "docx"], key="old_res")
    with col2:
        st.markdown("<h3 style='text-align: center; color: #00ffe1;'>Next-Gen Resume (Evolution)</h3>", unsafe_allow_html=True)
        new_file = st.file_uploader("Upload New Resume", type=["pdf", "docx"], key="new_res")
        
    if old_file and new_file:
        if st.button("🚀 Analyze Evolution"):
            with st.spinner("Calculating Evolution Progress..."):
                old_text = extract_text(old_file)
                new_text = extract_text(new_file)
                
                res = compare_resumes(old_text, new_text, job_desc)
                
                st.markdown("---")
                
                # --- METRICS ---
                m1, m2, m3 = st.columns(3)
                with m1:
                    diff_color = "#00ffe1" if res['score_diff'] >= 0 else "#ff4b4b"
                    arrow = "↑" if res['score_diff'] >= 0 else "↓"
                    st.markdown(f"<div class='glass-card' style='text-align:center;'><h4>Overall Lift</h4><h1 style='color:{diff_color};'>{arrow} {abs(res['score_diff'])} pts</h1></div>", unsafe_allow_html=True)
                with m2:
                    ats_color = "#00ffe1" if res['ats_diff'] >= 0 else "#ff4b4b"
                    ats_arrow = "↑" if res['ats_diff'] >= 0 else "↓"
                    st.markdown(f"<div class='glass-card' style='text-align:center;'><h4>ATS Lift</h4><h1 style='color:{ats_color};'>{ats_arrow} {abs(res['ats_diff'])}%</h1></div>", unsafe_allow_html=True)
                with m3:
                    score = res['new_score']
                    st.markdown(f"<div class='glass-card' style='text-align:center;'><h4>New Score Level</h4><h1 style='color:#00ffe1;'>{score}</h1></div>", unsafe_allow_html=True)
                
                # --- VISUALIZATION / EVOLUTION ---
                st.markdown("### 🌌 Evolution Progress Tracker")
                
                # Plotly Chart showing Evolution
                fig = go.Figure()
                
                # Add Line connecting them first so it sits behind
                fig.add_trace(go.Scatter(
                    x=[1, 2], y=[res['old_score'], res['new_score']],
                    mode='lines',
                    line=dict(color='rgba(255,255,255,0.3)', width=2, dash='dash'),
                    hoverinfo='skip'
                ))

                # Old Resume (Gravity)
                fig.add_trace(go.Scatter(
                    x=[1], y=[res['old_score']],
                    mode='markers+text',
                    marker=dict(size=40, color='#ff4b4b', symbol='circle', opacity=0.8, line=dict(width=3, color='white')),
                    text=["Past Score"], textposition="bottom center",
                    name="Past", hoverinfo="y+name"
                ))
                
                # New Resume (Evolution)
                fig.add_trace(go.Scatter(
                    x=[2], y=[res['new_score']],
                    mode='markers+text',
                    marker=dict(size=60, color='#00ffe1', symbol='circle', opacity=1.0, line=dict(width=4, color='white')),
                    text=["Next-Gen Score"], textposition="top center",
                    name="Next-Gen", hoverinfo="y+name"
                ))
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(visible=False, range=[0.5, 2.5]),
                    yaxis=dict(title="Score Altitude", range=[0, 110], color="white", gridcolor="rgba(255,255,255,0.1)"),
                    showlegend=False,
                    height=450,
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # --- AI INSIGHTS ---
                st.markdown("### 🧠 AI Analysis")
                for insight in res['insights']:
                    st.markdown(f"<div style='margin-bottom:10px; padding:15px; background:rgba(255,255,255,0.05); border-left: 4px solid #00ffe1; border-radius: 4px;'>{insight}</div>", unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    if res['added_skills']:
                        st.markdown("<div class='glass-card' style='border-top:3px solid #00ffe1;'><h4>🔥 Skills Acquired</h4><p>" + ", ".join(res['added_skills']).title() + "</p></div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='glass-card' style='border-top:3px solid #00ffe1;'><h4>🔥 Skills Acquired</h4><p>No new recognizable technical skills.</p></div>", unsafe_allow_html=True)
                with col_s2:
                    if res['removed_skills']:
                        st.markdown("<div class='glass-card' style='border-top:3px solid #ff4b4b;'><h4>🗑️ Skills Dropped</h4><p>" + ", ".join(res['removed_skills']).title() + "</p></div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='glass-card' style='border-top:3px solid #ff4b4b;'><h4>🗑️ Skills Dropped</h4><p>None! Great job keeping your core skills.</p></div>", unsafe_allow_html=True)


def page_history():
    st.markdown("<h1 style='margin-bottom: 0;'><span class='glow-text'>📂 My Resumes</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #cfcfcf; margin-bottom: 30px;'>Track your resume improvement history.</p>", unsafe_allow_html=True)
    
    # Get Real data
    try:
        data = get_resumes(st.session_state.email)
    except Exception as e:
        st.error(f"⚠️ Could not load history: {e}")
        return
    
    if not data:
        st.info("No resumes uploaded yet.")
        return
        
    df = pd.DataFrame(data, columns=["Resume File", "Score", "Upload Date"])
    
    rows_html = ""
    for _, row in df.iterrows():
        score = row['Score']
        badge_class = "badge-bad" if score < 60 else ("badge-ok" if score <= 80 else "badge-good")
        rows_html += f'''
        <tr>
            <td>📄 {row["Resume File"]}</td>
            <td><span class="{badge_class}">{score}%</span></td>
            <td>{row["Upload Date"].strftime("%Y-%m-%d %H:%M:%S") if hasattr(row["Upload Date"], "strftime") else row["Upload Date"]}</td>
        </tr>
        '''

    table_html = f"""
    <style>
    .glass-table {{ width: 100%; border-collapse: collapse; color: white; font-size: 0.95rem; }}
    .glass-table th, .glass-table td {{ padding: 18px 20px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }}
    .glass-table th {{ background: rgba(255,255,255,0.05); font-weight: 700; color: #00ffe1; text-transform: uppercase; font-size: 0.85rem; }}
    .glass-table tr:hover {{ background: rgba(0,255,225,0.05); transition: background 0.3s; }}
    .badge-bad {{ background: rgba(255, 75, 75, 0.2); border: 1px solid rgba(255,75,75,0.4); color: #ff4b4b; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 0.85rem; }}
    .badge-ok  {{ background: rgba(255, 170, 0, 0.2); border: 1px solid rgba(255,170,0,0.4); color: #ffaa00; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 0.85rem; }}
    .badge-good {{ background: rgba(0, 255, 0, 0.2); border: 1px solid rgba(0,255,0,0.4); color: #00ff00; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 0.85rem; }}
    </style>
    <div class="glass-card" style="padding: 0; overflow: hidden;">
        <table class="glass-table">
            <thead>
                <tr>
                    <th>Resume File</th>
                    <th>Score</th>
                    <th>Upload Date</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    table_html = table_html.replace('\n', ' ').replace('    ', ' ')
    st.markdown(table_html, unsafe_allow_html=True)
    
    if len(df) > 1:
        st.markdown("### 📈 Improvement Trend")
        fig_trend = px.line(df, x="Upload Date", y="Score", markers=True, line_shape="spline", color_discrete_sequence=["#00ffe1"])
        fig_trend.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)", range=[0, 100]), margin=dict(l=20, r=20, t=30, b=20)
        )
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# MAIN ROUTING LOGIC
# ==========================================
def main():
    inject_custom_css()
    render_sidebar()
    
    if not st.session_state.logged_in:
        page_login()
    else:
        if st.session_state.current_page == "🏠 Home":
            page_home()
        elif st.session_state.current_page == "📊 Dashboard":
            page_dashboard()
        elif st.session_state.current_page == "📤 Upload Resume":
            page_upload()
        elif st.session_state.current_page == "🚀 Resume Evolution Dashboard":
            page_compare()
        elif st.session_state.current_page == "📂 My Resumes":
            page_history()
        elif st.session_state.current_page == "🚪 Logout":
            st.session_state.logged_in = False
            st.session_state.current_page = "Login"
            st.session_state.email = ""
            st.session_state.name = ""
            st.rerun()

if __name__ == "__main__":
    main()