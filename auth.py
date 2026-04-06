import random
import smtplib
from email.mime.text import MIMEText
from db import get_connection

import pdfplumber
import docx
from sklearn.feature_extraction.text import CountVectorizer


# ================= EMAIL SETTINGS =================
sender_email = "jayendrapilla@gmail.com"
sender_password = "wkufrbowdsisuokp"


# ================= OTP =================
def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp(email, otp):

    msg = MIMEText(f"Your OTP is: {otp}")
    msg["Subject"] = "Resume Analyzer OTP"
    msg["From"] = sender_email
    msg["To"] = email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)


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

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO resumes (user_email,file_name,score) VALUES (%s,%s,%s)",
        (str(email), str(filename), int(score))
    )

    conn.commit()
    conn.close()


def get_resumes(email):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT file_name, score, uploaded_at FROM resumes WHERE user_email=%s ORDER BY uploaded_at DESC",
        (email,)
    )

    data = cur.fetchall()

    conn.close()

    return data


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

# ✅ THIS FUNCTION RETURNS SCORE (NOT ROLE)
def resume_score(text):
    import re
    text = text.lower()
    score = 0
    
    # ----------------------------------------------------
    # 1. SECTION PRESENCE (Max 40 points)
    # ----------------------------------------------------
    sections = {
        "experience": {"keywords": ["experience", "employment", "work history", "professional background"], "weight": 15},
        "education": {"keywords": ["education", "academic", "university", "college", "degree"], "weight": 10},
        "skills": {"keywords": ["skills", "technologies", "expertise", "competencies", "toolkit"], "weight": 10},
        "projects": {"keywords": ["projects", "portfolio", "certifications", "publications"], "weight": 5}
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
    # Capped strictly to prevent keyword stuffing from dominating the score.
    skills_found = 0
    all_skills = set([skill.lower() for skills in ROLE_SKILLS.values() for skill in skills])
    
    for skill in all_skills:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text):
            skills_found += 1
            
    # Each skill gives 2.5 points, maxing out at 10 skills (25 points total)
    skill_score = min(skills_found * 2.5, 25)
    score += skill_score

    # ----------------------------------------------------
    # 3. IMPACT & ACTION VERBS (Max 20 points)
    # ----------------------------------------------------
    # Real ATS and recruiters look for impact, not just responsibilities.
    action_verbs = [
        "led", "developed", "managed", "designed", "created", "built", "analyzed", 
        "optimized", "improved", "implemented", "spearheaded", "engineered",
        "orchestrated", "executed", "increased", "decreased", "reduced", "delivered",
        "architected", "deployed", "scaled", "negotiated"
    ]
    
    verb_count = sum(1 for verb in action_verbs if re.search(r'\b' + verb + r'\b', text))
    
    # Reward 2 points per action verb, maxing out at 10 verbs (20 points total)
    impact_score = min(verb_count * 2, 20)
    score += impact_score

    # ----------------------------------------------------
    # 4. RESUME LENGTH & STRUCTURE (Max 15 points)
    # ----------------------------------------------------
    word_count = len(text.split())
    length_score = 0
    
    if word_count < 150:
        length_score = 0       # Too short, lacking substance
    elif 150 <= word_count < 300:
        length_score = 5       # Weak, needs more robust descriptions
    elif 300 <= word_count < 850:
        length_score = 15      # Optimal (Sweet spot for 1-2 pages)
    else:
        length_score = 5       # Too long, generic or unfocused
        
    score += length_score

    # ----------------------------------------------------
    # 5. HARSH PENALTY SYSTEM (Reduces Score Inflation)
    # ----------------------------------------------------
    # Missing quantified metrics (%, $, or large numbers)
    has_metrics = bool(re.search(r'[\%\$]', text) or re.search(r'\b[0-9]{2,}\b', text))
    
    if "experience" in missing_critical:
        score -= 30  # Massive penalty for no experience section
        
    if "education" in missing_critical:
        score -= 15  # Heavy penalty for no education
        
    if word_count < 150:
        score -= 15  # Double-penalize overly brief resumes
        
    if verb_count < 3:
        score -= 10  # Passive resume penalty (reads like a job description, not achievements)
        
    if not has_metrics:
        score -= 5   # Penalty for not quantifying achievements
        
    # Ensure score remains clamped between realistic ATS bounds (0 - 100)
    final_score = max(0, min(int(score), 100))
    
    return final_score
# Replaced by job_matcher.py