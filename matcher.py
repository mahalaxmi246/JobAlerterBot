"""
matcher.py — Uses OpenAI GPT to score each job against your profile.
Returns match %, matched skills, missing skills, and a verdict.
"""

import json
from openai import OpenAI
from config import OPENAI_API_KEY, PROFILE

client = OpenAI(api_key=OPENAI_API_KEY)


def build_profile_summary(profile: dict) -> str:
    return f"""
Candidate: {profile['name']}
Degree: {profile['degree']} from {profile['college']}, graduating {profile['graduation_year']}
CGPA: {profile['cgpa']}
Skills: {', '.join(profile['skills'])}
Preferred roles: {', '.join(profile['preferred_roles'])}
Preferred locations: {', '.join(profile['preferred_locations'])}
Minimum expected salary: {profile['min_lpa']} LPA
Experience type: {profile['experience_type']}
About: {profile['about'].strip()}
""".strip()


def match_job(job: dict) -> dict | None:
    """
    Ask OpenAI to score a job posting against the candidate profile.
    Returns enriched job dict with match data, or None if it should be skipped.
    """
    profile_summary = build_profile_summary(PROFILE)

    prompt = f"""
You are a job matching assistant for Indian fresher job seekers.

CANDIDATE PROFILE:
{profile_summary}

JOB POSTING:
Company: {job['company']}
Title: {job['title']}
Source: {job['source']}
Skills mentioned: {job['skills_text']}
Salary: {job['salary']}
Description: {job['description'][:600]}

Analyze this job for the candidate and respond ONLY with valid JSON (no markdown, no explanation):
{{
  "is_fresher_role": true or false,
  "match_percent": integer 0-100,
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "salary_lpa": "extracted salary or 'Not mentioned'",
  "location": "extracted location or 'India'",
  "verdict": "one sentence — should they apply and why",
  "role_type": "SDE / Data Analyst / DevOps / Product / Other"
}}

Rules:
- match_percent should reflect skill overlap, role fit, location, and salary match
- If the job is clearly NOT for freshers (requires 3+ years exp), set is_fresher_role: false
- Be honest and specific in verdict
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",           # cheapest OpenAI model, perfect for this
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=400,
        )
        raw = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        
        # Attach match data back to job
        job["match_percent"]   = result.get("match_percent", 0)
        job["matched_skills"]  = result.get("matched_skills", [])
        job["missing_skills"]  = result.get("missing_skills", [])
        job["salary_lpa"]      = result.get("salary_lpa", job.get("salary", "N/A"))
        job["location"]        = result.get("location", "India")
        job["verdict"]         = result.get("verdict", "")
        job["role_type"]       = result.get("role_type", "Other")
        job["is_fresher_role"] = result.get("is_fresher_role", True)
        
        return job

    except Exception as e:
        print(f"    [Matcher] Error on '{job['title']}': {e}")
        return None


def filter_and_match(jobs: list[dict], min_match: int) -> list[dict]:
    """Match all jobs and return only those above the threshold."""
    matched = []
    print(f"  Analysing {len(jobs)} job listings with OpenAI...")
    
    for job in jobs:
        result = match_job(job)
        if result is None:
            continue
        if not result.get("is_fresher_role", True):
            print(f"    Skipped (not fresher): {result['title']}")
            continue
        if result["match_percent"] >= min_match:
            print(f"    ✓ Match {result['match_percent']}%: {result['title']} @ {result['company']}")
            matched.append(result)
        else:
            print(f"    ✗ Low match {result['match_percent']}%: {result['title']}")
    
    # Sort by match % descending
    matched.sort(key=lambda x: x["match_percent"], reverse=True)
    return matched
