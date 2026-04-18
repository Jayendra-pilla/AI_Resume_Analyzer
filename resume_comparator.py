import re
from auth import resume_score, ROLE_SKILLS
from job_matcher import job_match_score

def extract_skills(text):
    """Extracts a set of distinct skills found in the text based on ROLE_SKILLS."""
    text_lower = text.lower()
    all_skills = set([skill.lower() for skills in ROLE_SKILLS.values() for skill in skills])
    
    found_skills = set()
    for skill in all_skills:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill)
            
    return found_skills

def count_action_verbs(text):
    action_verbs = [
        "led", "developed", "managed", "designed", "created", "built", "analyzed", 
        "optimized", "improved", "implemented", "spearheaded", "engineered",
        "orchestrated", "executed", "increased", "decreased", "reduced", "delivered",
        "architected", "deployed", "scaled", "negotiated"
    ]
    text_lower = text.lower()
    count = sum(1 for verb in action_verbs if re.search(r'\b' + verb + r'\b', text_lower))
    return count

def count_metrics(text):
    metric_matches = re.findall(r'\b\d{2,}\b|\b\d+[\%]\b|\$[\d\.]+', text)
    return len(metric_matches)

def generate_insights(oldscor_score, new_e, added_skills, new_verbs, new_metrics):
    insights = []
    
    if new_score > old_score + 10:
        insights.append("🚀 Massive overall improvement detected! Your new resume is much stronger.")
    elif new_score > old_score:
        insights.append("📈 Solid progress. Your new resume scores higher generally.")
    elif new_score < old_score:
        insights.append("⚠️ Score dropped. Check if you accidentally removed impact metrics or keywords.")
        
    if new_verbs > 0:
        insights.append(f"💪 Stronger action verbs added. You included {new_verbs} more impactful verbs.")
    elif new_verbs < 0:
        insights.append("📉 You lost some action verbs. Make sure you lead bullet points with strong verbs.")
        
    if new_metrics > 0:
        insights.append(f"📊 Quantified impact improved. Added {new_metrics} more metrics or numbers.")
        
    if added_skills:
        insights.append(f"🧠 Added {len(added_skills)} new technical/soft skills, boosting ATS matches.")
        
    if not insights:
        insights.append("🔄 Changes detected, but scores remain relatively stable.")
        
    return insights

def compare_resumes(old_text, new_text, target_job=None):
    """
    Compares two resumes and returns a detailed analysis dictionary.
    """
    old_score = resume_score(old_text)
    new_score = resume_score(new_text)
    
    old_ats = job_match_score(old_text, target_job) if target_job else int(old_score * 0.85)
    new_ats = job_match_score(new_text, target_job) if target_job else int(new_score * 0.85)
    
    old_skills = extract_skills(old_text)
    new_skills = extract_skills(new_text)
    
    added_skills = new_skills - old_skills
    removed_skills = old_skills - new_skills
    
    old_verbs = count_action_verbs(old_text)
    new_verbs = count_action_verbs(new_text)
    verb_diff = new_verbs - old_verbs
    
    old_metrics = count_metrics(old_text)
    new_metrics = count_metrics(new_text)
    metric_diff = new_metrics - old_metrics
    
    insights = generate_insights(old_score, new_score, added_skills, verb_diff, metric_diff)
    
    return {
        "score_diff": new_score - old_score,
        "ats_diff": new_ats - old_ats,
        "old_score": old_score,
        "new_score": new_score,
        "old_ats": old_ats,
        "new_ats": new_ats,
        "added_skills": list(added_skills),
        "removed_skills": list(removed_skills),
        "insights": insights
    }
 