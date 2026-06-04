import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- Configuration & Synonyms ---
# Handles synonyms (Requirement 6 - Bonus)
SYNONYMS = {
    "ml": "machine learning",
    "dl": "deep learning",
    "ai": "artificial intelligence",
    "js": "javascript",
    "ts": "typescript",
    "aws": "amazon web services",
    "gcp": "google cloud",
    "k8s": "kubernetes",
    "react.js": "react",
    "node.js": "node",
    "db": "database",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "nn": "neural networks",
    "ui/ux": "ui ux",
    "go": "golang"
}

# Predefined Job Roles with Weighted Skills (Requirement 1 & Bonus)
# Core skills are highly weighted, Bonus skills are secondary modifiers
ROLES = {
    "Backend Developer": {
        "core": ["python", "java", "node", "sql", "api", "database", "backend"],
        "bonus": ["docker", "flask", "django", "fastapi", "git", "aws", "microservices"]
    },
    "Frontend Developer": {
        "core": ["html", "css", "javascript", "react", "frontend", "ui"],
        "bonus": ["vue", "angular", "typescript", "figma", "redux", "tailwind"]
    },
    "Data Scientist": {
        "core": ["python", "machine learning", "statistics", "data analysis", "sql", "pandas"],
        "bonus": ["deep learning", "nlp", "scikit", "numpy", "tensorflow", "pytorch", "tableau"]
    },
    "Machine Learning Engineer": {
        "core": ["python", "machine learning", "deep learning", "algorithms", "model", "tensorflow", "pytorch"],
        "bonus": ["nlp", "computer vision", "docker", "kubernetes", "mlops", "aws", "gcp", "data structure"]
    },
    "DevOps Engineer": {
        "core": ["linux", "docker", "kubernetes", "ci cd", "aws", "pipeline", "automation"],
        "bonus": ["jenkins", "terraform", "bash", "gcp", "azure", "ansible", "scripting"]
    },
    "Cloud Engineer": {
        "core": ["aws", "azure", "gcp", "cloud", "infrastructure", "networking"],
        "bonus": ["terraform", "kubernetes", "docker", "security", "linux", "iam"]
    },
    "Full Stack Developer": {
        "core": ["html", "css", "javascript", "react", "node", "python", "sql", "backend", "frontend"],
        "bonus": ["docker", "api", "mongodb", "git", "aws", "typescript", "express"]
    }
}

# Weighted Multipliers
CORE_WEIGHT = 2.0
BONUS_WEIGHT = 1.0


# --- NLP Helpers ---
def clean_and_tokenize(text):
    """Normalizes text by removing punctuation and enforcing synonym structures."""
    if not text:
        return ""
    text = text.lower()
    # Normalize slashes out
    text = text.replace("ci/cd", "ci cd").replace("ui/ux", "ui ux")
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    
    # Apply standard predefined acronyms/synonyms
    for k, v in SYNONYMS.items():
        text = re.sub(rf'\b{re.escape(k)}\b', v, text)
        
    return text


def calculate_role_match(text, role_name):
    """Calculates granular match percentages and explainability data for highly-weighted skills."""
    clean_text = clean_and_tokenize(text)
    
    if role_name not in ROLES:
        return 0, [], [], []
        
    core_skills = ROLES[role_name]["core"]
    bonus_skills = ROLES[role_name]["bonus"]
    
    found_core = [s for s in core_skills if s in clean_text]
    found_bonus = [s for s in bonus_skills if s in clean_text]
    
    missing_core = [s for s in core_skills if s not in found_core]
    missing_bonus = [s for s in bonus_skills if s not in found_bonus]
    
    # Mathematical TF-like Scoring avoiding over-inflation
    max_score = (len(core_skills) * CORE_WEIGHT) + (len(bonus_skills) * BONUS_WEIGHT)
    achieved_score = (len(found_core) * CORE_WEIGHT) + (len(found_bonus) * BONUS_WEIGHT)
    
    if max_score == 0:
        return 0, [], [], []
        
    match_percentage = int((achieved_score / max_score) * 100)
    
    contributed = found_core + found_bonus
    missing = missing_core + missing_bonus
    
    return match_percentage, contributed, missing, missing_core


# --- Core Required Functions ---

# Requirement 1: Return Best Role and its %
def job_role_match(text):
    top3 = top_job_roles(text)
    if top3:
        best = top3[0]
        return best["role"], best["match_percentage"]
    return "Unknown", 0


# Requirement 2: Job Description Matching via TF-IDF / Cosine Similarity
def job_match_score(resume_text, job_description):
    """
    Advanced NLP technique matching the entire resume text against a parsed JD string.
    Returns realistic matching percentage (0-100).
    """
    r_text = clean_and_tokenize(resume_text)
    j_text = clean_and_tokenize(job_description)
    
    if not r_text.strip() or not j_text.strip():
        return 0
        
    documents = [r_text, j_text]
    vectorizer = TfidfVectorizer(stop_words='english')
    
    try:
        tfidf_matrix = vectorizer.fit_transform(documents)
        # tfidf_matrix[0:1] is the resume, tfidf_matrix[1:2] is the job description
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        # Mathematical constraint (Cosine similarity bounds between 0.0 and 1.0)
        return int(max(0.0, similarity) * 100)
    except Exception:
        return 0


# Requirement 3 & 5: Top 3 Matching Roles + Explainability
def top_job_roles(text):
    """
    Generates intelligent explainability strings and returns Top 3 roles descending.
    """
    results = []
    
    for role in ROLES.keys():
        pct, contributed, missing, missing_core = calculate_role_match(text, role)
        
        # Explainability Generation (Requirement 5)
        reason = f"Matched {len(contributed)} key industry skills. "
        if pct >= 75:
            reason += "Strong candidate profile deeply aligned with core requirements."
        elif pct >= 50:
            if missing_core:
                reason += f"Moderate match; lacks core foundational skills like '{missing_core[0]}'."
            else:
                reason += "Moderate match; could improve by picking up supplementary technologies."
        else:
            reason += "Weak match due to missing fundamental domain knowledge."
            
        results.append({
            "role": role,
            "match_percentage": pct,
            "contributed_skills": contributed,
            "missing_skills": missing,
            "missing_core": missing_core,
            "explanation": reason
        })
        
    # Sort rigorously in descending order
    results.sort(key=lambda x: x["match_percentage"], reverse=True)
    return results[:3]


# Requirement 4: Missing Skills Detection
def job_missing_skills(text, role):
    if role not in ROLES:
        return []
        
    _, _, missing, _ = calculate_role_match(text, role)
    return missing

