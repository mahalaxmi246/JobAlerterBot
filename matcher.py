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

STRICT RULES:
- The job must be DIRECTLY at "{job['company']}" company — not a third party, consultant, or staffing agency hiring for {job['company']} tools/skills
- If the hiring company is a staffing agency, consultant, or different company, set is_target_company: false
- If job requires 2+ years experience, set is_fresher_role: false

Respond ONLY with valid JSON (no markdown, no explanation):
{{
  "is_fresher_role": true or false,
  "is_target_company": true or false,
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
- Be honest and specific in verdict
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=400,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)

        job["match_percent"]    = result.get("match_percent", 0)
        job["matched_skills"]   = result.get("matched_skills", [])
        job["missing_skills"]   = result.get("missing_skills", [])
        job["salary_lpa"]       = result.get("salary_lpa", job.get("salary", "N/A"))
        job["location"]         = result.get("location", "India")
        job["verdict"]          = result.get("verdict", "")
        job["role_type"]        = result.get("role_type", "Other")
        job["is_fresher_role"]  = result.get("is_fresher_role", True)
        job["is_target_company"]= result.get("is_target_company", True)

        return job

    except Exception as e:
        print(f"    [Matcher] Error on '{job['title']}': {e}")
        return None


def filter_and_match(jobs: list[dict], min_match: int) -> list[dict]:
    matched = []
    print(f"  Analysing {len(jobs)} job listings with OpenAI...")

    for job in jobs:
        result = match_job(job)
        if result is None:
            continue
        if not result.get("is_fresher_role", True):
            print(f"    Skipped (not fresher): {result['title']}")
            continue
        if not result.get("is_target_company", True):
            print(f"    Skipped (not target company): {result['title']}")
            continue
        if result["match_percent"] >= min_match:
            print(f"    ✓ Match {result['match_percent']}%: {result['title']} @ {result['company']}")
            matched.append(result)
        else:
            print(f"    ✗ Low match {result['match_percent']}%: {result['title']}")

    matched.sort(key=lambda x: x["match_percent"], reverse=True)
    return matched