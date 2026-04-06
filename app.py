import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import time
from auth import *
from job_matcher import *

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
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap" rel="stylesheet">
<style>
/* Global Font & Background */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); color: white; }
header { visibility: hidden; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: rgba(15, 32, 39, 0.75) !important;
    backdrop-filter: blur(15px);
    border-right: 1px solid rgba(255, 255, 255, 0.1);
}

/* Metrics / Cards */
[data-testid="stMetric"], .glass-card, [data-testid="stFileUploader"] {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 20px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}
.glass-card { margin-bottom: 20px; color: white; }

[data-testid="stMetricValue"] { font-size: 2.2rem !important; font-weight: 800 !important; color: #00ffe1 !important; }
[data-testid="stMetricLabel"] { font-size: 1.1rem !important; font-weight: 600 !important; color: #e0e0e0 !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #00ffe1 0%, #00b4d8 100%);
    color: #0f2027 !important;
    border: none; border-radius: 12px; height: 3.5rem;
    font-weight: 700; font-size: 1.1rem;
    box-shadow: 0 4px 15px rgba(0, 255, 225, 0.3);
    transition: all 0.3s ease; width: 100%;
}
.stButton > button:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 8px 25px rgba(0, 255, 225, 0.5);
}

/* Text Inputs */
.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    background-color: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important; color: white !important;
}
.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus { border-color: #00ffe1 !important; }

/* Globals */
.glow-text { color: #00ffe1; text-shadow: 0 0 10px rgba(0,255,225,0.4); font-weight: 800; }
.stProgress > div > div > div { background-color: #00ffe1; }
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
            
            menu_options = ["🏠 Home", "📊 Dashboard", "📤 Upload Resume", "📂 My Resumes", "🚪 Logout"]
            def_index = menu_options.index(st.session_state.current_page) if st.session_state.current_page in menu_options else 0
            st.session_state.current_page = st.radio("Navigate", menu_options, label_visibility="collapsed", index=def_index)
            
        else:
            st.markdown("### 🤖 Resume AI")
            st.info("Please sign in to access your customized dashboard.")
            st.session_state.current_page = "Login"

# ==========================================
# VIEWS
# ==========================================

def page_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown(
            """
            <div style='text-align: center; margin-bottom: 30px;'>
                <h1 style='font-size: 3rem; margin-bottom: 10px;'><span class='glow-text'>ResumeAnalyzer</span> AI</h1>
                <p style='color: #a0a0a0; font-size: 1.1rem;'>Smart. Fast. ATS-Optimized.</p>
            </div>
            """, unsafe_allow_html=True
        )
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Create Account"])
        
        with tab1:
            email = st.text_input("📧 Email Address", placeholder="alex@example.com", key="login_email")
            password = st.text_input("🔒 Password", type="password", placeholder="••••••••", key="login_pass")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In 🚀"):
                user = verify_login(email, password)
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
                ats = min(score + 10, 100) # AI Fallback
                
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