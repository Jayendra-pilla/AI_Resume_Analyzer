import random
import smtplib
from email.mime.text import MIMEText

from db import get_connection
import streamlit as st
import pdfplumber
import docx
from sklearn.feature_extraction.text import CountVectorizer
from dotenv import load_dotenv
import os
load_dotenv()
# ================= OTP =================
def generate_otp():
    return str(random.randint(100000, 999999))
# ================= EMAIL OTP =================
def send_otp(email, otp):
    sender_email = st.secrets["EMAIL_USER"]
    sender_password = st.secrets["EMAIL_PASS"]

    msg = MIMEText(
        f"""
Hello,

Your Resume Analyzer OTP is: {otp}

This OTP will expire in 5 minutes.

Do not share this OTP with anyone.

Regards,
Resume Analyzer Team
"""
    )

    msg["Subject"] = "Resume Analyzer OTP"
    msg["From"] = sender_email
    msg["To"] = email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(
            sender_email,
            email,
            msg.as_string()
        )

# ================= USER FUNCTIONS =================
def user_exists(email):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    conn.close()

    return user


def save_user(name, email, password):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users (name,email,password,verified) VALUES (%s,%s,%s,%s)",
        (name, email, password, True)
    )

    conn.commit()
    conn.close()


def verify_login(email, password):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE email=%s AND password=%s",
        (email, password)
    )

    user = cur.fetchone()

    conn.close()

    return user


# ================= RESUME DATABASE =================
def save_resume(email, filename, score):

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM resumes WHERE user_email=%s AND file_name=%s",
            (str(email), str(filename))
        )
        existing = cur.fetchall()

        if existing:
            cur.execute(
                "UPDATE resumes SET score=%s, uploaded_at=CURRENT_TIMESTAMP WHERE user_email=%s AND file_name=%s",
                (int(score), str(email), str(filename))
            )
        else:
            cur.execute(
                "INSERT INTO resumes (user_email,file_name,score) VALUES (%s,%s,%s)",
                (str(email), str(filename), int(score))
            )

        conn.commit()
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise e
    finally:
        if 'conn' in locals():
            cur.close()
            conn.close()


def get_resumes(email):

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT file_name, MAX(score) as score, MAX(uploaded_at) as uploaded_at FROM resumes WHERE user_email=%s GROUP BY file_name ORDER BY uploaded_at DESC",
            (email,)
        )

        data = cur.fetchall()
        return data
    except Exception as e:
        raise e
    finally:
        if 'conn' in locals():
            cur.close()
            conn.close()


# ================= AI RESUME TEXT =================
def extract_text(file):

    text = ""

    if file.name.endswith(".pdf"):

        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

    elif file.name.endswith(".docx"):

        doc = docx.Document(file)

        for para in doc.paragraphs:
            text += para.text

    return text.lower()


# ================= AI RESUME SCORE =================#

# ================= AI RESUME SCORE =================#

ROLE_SKILLS = {

    "Backend Developer": ["python", "java", "node", "django", "flask", "sql"],
    "Frontend Developer": ["html", "css", "javascript", "react"],
    "Full Stack Developer": ["html", "css", "javascript", "react", "node", "python"],
    "Data Scientist": ["python", "pandas", "numpy", "machine learning"],
    "Machine Learning Engineer": ["machine learning", "deep learning", "tensorflow"],
    "DevOps Engineer": ["docker", "kubernetes", "aws"],
    "Android Developer": ["java", "kotlin", "android"],
    "UI/UX Designer": ["figma", "design", "wireframe"],
    "Cyber Security Analyst": ["security", "network", "kali"],
    "Cloud Engineer": ["aws", "azure", "gcp"]
}

def resume_score(text):
    import re
    text = text.lower()
    score = 0
    
    # ----------------------------------------------------
    # 1. SECTION PRESENCE (Max 20 points - Reduced from 40)
    # ----------------------------------------------------
    sections = {
        "experience": {"keywords": ["experience", "employment", "work history", "professional background"], "weight": 8},
        "education": {"keywords": ["education", "academic", "university", "college", "degree"], "weight": 5},
        "skills": {"keywords": ["skills", "technologies", "expertise", "competencies", "toolkit"], "weight": 5},
        "projects": {"keywords": ["projects", "portfolio", "certifications", "publications"], "weight": 2}
    }
    
    section_score = 0
    missing_critical = []
    
    for sec_name, data in sections.items():
        if any(kw in text for kw in data["keywords"]):
            section_score += data["weight"]
        else:
            if sec_name in ["experience", "education"]:
                missing_critical.append(sec_name)
    
    score += section_score

    # ----------------------------------------------------
    # 2. SKILL MATCHING (Max 25 points)
    # ----------------------------------------------------
    # Now requires 25 distinct tech/soft skills to get max points instead of 10.
    skills_found = 0
    all_skills = set([skill.lower() for skills in ROLE_SKILLS.values() for skill in skills])
    
    for skill in all_skills:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text):
            skills_found += 1
            
    skill_score = min(skills_found * 1, 25)
    score += skill_score

    # ----------------------------------------------------
    # 3. IMPACT & ACTION VERBS (Max 20 points)
    # ----------------------------------------------------
    action_verbs = [
        "led", "developed", "managed", "designed", "created", "built", "analyzed", 
        "optimized", "improved", "implemented", "spearheaded", "engineered",
        "orchestrated", "executed", "increased", "decreased", "reduced", "delivered",
        "architected", "deployed", "scaled", "negotiated"
    ]
    
    verb_count = sum(1 for verb in action_verbs if re.search(r'\b' + verb + r'\b', text))
    impact_score = min(verb_count * 2, 20)
    score += impact_score

    # ----------------------------------------------------
    # 4. RESUME LENGTH & STRUCTURE (Max 15 points)
    # ----------------------------------------------------
    word_count = len(text.split())
    length_score = 0
    
    if word_count < 150:
        length_score = 0       # Too short
    elif 150 <= word_count < 300:
        length_score = 5       # Weak
    elif 300 <= word_count < 850:
        length_score = 15      # Optimal
    else:
        length_score = 8       # Too long, penalized slightly
        
    score += length_score

    # ----------------------------------------------------
    # 5. QUANTIFIABLE METRICS (Max 20 points)
    # ----------------------------------------------------
    # Look for numbers (2+ digits), percentages, or dollar amounts representing impact.
    metric_matches = re.findall(r'\b\d{2,}\b|\b\d+[\%]\b|\$[\d\.]+', text)
    metric_score = min(len(metric_matches) * 4, 20)
    score += metric_score

    # ----------------------------------------------------
    # 6. HARSH PENALTY SYSTEM
    # ----------------------------------------------------
    if "experience" in missing_critical:
        score -= 40  # Destroy score if no experience
        
    if "education" in missing_critical:
        score -= 20  
        
    if word_count < 150:
        score -= 20  
        
    if verb_count < 5:
        score -= 15  # Penalize passive language heavily
        
    if len(metric_matches) < 2:
        score -= 20  # Crucial missing piece: Not quantifying achievements!
        
    final_score = max(0, min(int(score), 100))
    
    return final_score
# Replaced by job_matcher.py