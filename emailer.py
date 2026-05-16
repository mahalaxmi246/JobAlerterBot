"""
emailer.py — Sends a beautiful HTML alert email via Brevo (free tier).
Each email contains all matched jobs with scores, skills, and apply links.
"""

import requests
import json
from datetime import datetime
from config import BREVO_API_KEY, FROM_EMAIL, YOUR_EMAIL, YOUR_NAME, PROFILE


def match_color(pct: int) -> str:
    if pct >= 80: return "#2d7a2d"
    if pct >= 60: return "#b36b00"
    return "#c0392b"


def match_label(pct: int) -> str:
    if pct >= 80: return "Strong match"
    if pct >= 60: return "Good match"
    return "Partial match"


def skill_pill(skill: str, color: str, bg: str) -> str:
    return (
        f'<span style="display:inline-block;padding:3px 10px;margin:2px;'
        f'border-radius:20px;font-size:12px;font-weight:500;'
        f'background:{bg};color:{color};">{skill}</span>'
    )


def build_job_card(job: dict) -> str:
    pct = job["match_percent"]
    color = match_color(pct)
    label = match_label(pct)
    
    matched_pills = "".join(skill_pill(s, "#1a5c1a", "#e6f4e6") for s in job.get("matched_skills", []))
    missing_pills = "".join(skill_pill(s, "#7a3c00", "#fff0e0") for s in job.get("missing_skills", []))

    return f"""
<div style="background:#fff;border:1px solid #e0e0e0;border-radius:10px;
            padding:20px;margin-bottom:18px;font-family:Arial,sans-serif;">
  
  <!-- Header row -->
  <div style="display:flex;justify-content:space-between;align-items:flex-start;
              flex-wrap:wrap;gap:8px;margin-bottom:10px;">
    <div>
      <div style="font-size:11px;color:#888;text-transform:uppercase;
                  letter-spacing:0.05em;">{job['company']} · {job['source']}</div>
      <div style="font-size:17px;font-weight:600;color:#111;margin-top:2px;">
        {job['title']}
      </div>
      <div style="font-size:13px;color:#555;margin-top:4px;">
        📍 {job.get('location','India')} &nbsp;|&nbsp;
        💰 {job.get('salary_lpa','N/A')} &nbsp;|&nbsp;
        🏷️ {job.get('role_type','—')}
      </div>
    </div>
    <!-- Match badge -->
    <div style="text-align:center;background:{color}10;border:1.5px solid {color};
                border-radius:8px;padding:8px 14px;min-width:80px;">
      <div style="font-size:22px;font-weight:700;color:{color};">{pct}%</div>
      <div style="font-size:11px;color:{color};font-weight:500;">{label}</div>
    </div>
  </div>

  <!-- Match bar -->
  <div style="background:#f0f0f0;border-radius:4px;height:5px;margin-bottom:12px;">
    <div style="background:{color};width:{pct}%;height:5px;border-radius:4px;"></div>
  </div>

  <!-- AI verdict -->
  <div style="background:#f8f9ff;border-left:3px solid #4a6cf7;padding:8px 12px;
              border-radius:0 6px 6px 0;margin-bottom:12px;font-size:13px;color:#333;">
    🤖 <em>{job.get('verdict','')}</em>
  </div>

  <!-- Skills -->
  {'<div style="margin-bottom:8px;"><div style="font-size:11px;font-weight:600;color:#444;margin-bottom:4px;">✅ YOUR MATCHING SKILLS</div>' + matched_pills + '</div>' if matched_pills else ''}
  {'<div style="margin-bottom:8px;"><div style="font-size:11px;font-weight:600;color:#444;margin-bottom:4px;">📚 SKILLS TO LEARN</div>' + missing_pills + '</div>' if missing_pills else ''}

  <!-- Apply button -->
  <a href="{job['apply_link']}" 
     style="display:inline-block;background:#1a1a2e;color:#fff;padding:9px 20px;
            border-radius:6px;text-decoration:none;font-size:13px;font-weight:600;
            margin-top:6px;">
    Apply Now →
  </a>
</div>
"""


def build_email_html(matched_jobs: list[dict]) -> str:
    today = datetime.now().strftime("%d %b %Y")
    job_cards = "".join(build_job_card(j) for j in matched_jobs)
    companies = list(dict.fromkeys(j["company"] for j in matched_jobs))

    return f"""
<!DOCTYPE html>
<html>
<body style="background:#f4f4f4;margin:0;padding:20px;font-family:Arial,sans-serif;">
<div style="max-width:620px;margin:0 auto;">

  <!-- Header -->
  <div style="background:#1a1a2e;border-radius:12px 12px 0 0;padding:24px;text-align:center;">
    <div style="font-size:24px;font-weight:700;color:#fff;">🎯 Job Alert</div>
    <div style="color:#aaa;font-size:13px;margin-top:4px;">{today} · {len(matched_jobs)} new match{'es' if len(matched_jobs)!=1 else ''} found</div>
  </div>

  <!-- Summary bar -->
  <div style="background:#e8f0fe;padding:14px 20px;font-size:13px;color:#1a1a2e;">
    Hey <strong>{PROFILE['name']}</strong>! We scanned 
    <strong>{', '.join(companies)}</strong> and found 
    <strong>{len(matched_jobs)} role{'s' if len(matched_jobs)!=1 else ''}</strong> 
    matching your profile (min {matched_jobs[-1]['match_percent'] if matched_jobs else 0}%+ match).
  </div>

  <!-- Job cards -->
  <div style="background:#f4f4f4;padding:20px 0;">
    {job_cards}
  </div>

  <!-- Footer -->
  <div style="background:#1a1a2e;border-radius:0 0 12px 12px;padding:16px;
              text-align:center;font-size:11px;color:#888;">
    Job Alert Bot · Running automatically for {PROFILE['name']}<br>
    Update your skills anytime in config.py
  </div>

</div>
</body>
</html>
"""


def send_alert_email(matched_jobs: list[dict]) -> bool:
    """Send the alert email via Brevo API."""
    if not matched_jobs:
        print("  No matched jobs to email.")
        return False

    html = build_email_html(matched_jobs)
    subject = f"🎯 {len(matched_jobs)} Fresher Job Match{'es' if len(matched_jobs)!=1 else ''} — {', '.join(set(j['company'] for j in matched_jobs[:3]))}"

    payload = {
        "sender": {"name": "Job Alert Bot", "email": FROM_EMAIL},
        "to": [{"email": YOUR_EMAIL, "name": YOUR_NAME}],
        "subject": subject,
        "htmlContent": html,
    }

    resp = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "api-key": BREVO_API_KEY,
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
        timeout=10,
    )

    if resp.status_code in (200, 201):
        print(f"  ✓ Email sent to {YOUR_EMAIL} with {len(matched_jobs)} matches!")
        return True
    else:
        print(f"  ✗ Email failed: {resp.status_code} — {resp.text}")
        return False
