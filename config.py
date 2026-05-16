# ============================================================
#  JOB ALERT BOT — CONFIG FILE
#  Fill this once. Update anytime you gain new skills.
# ============================================================

# --- YOUR DETAILS ---
import os


YOUR_NAME = "Mahalaxmi Somisetty"
YOUR_EMAIL = "mahalaxmi1246@gmail.com"       # alerts will come here

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
BREVO_API_KEY  = os.environ.get("BREVO_API_KEY", "")
FROM_EMAIL     = os.environ.get("FROM_EMAIL", YOUR_EMAIL)

# --- YOUR RESUME / PROFILE ---
# Update this whenever you learn something new!
PROFILE = {
    "name": "Mahalaxmi Somisetty",
    "degree": "B.Tech IT",              # e.g. B.Tech CSE / BCA / MCA
    "college": "VNR Vignana Jyothi Institute of Engineering & Technology",
    "graduation_year": "2027",
    "cgpa": "9.23",
    "skills": [
        "Python",
        "Java",
        "JavaScript",
        "React",
        "SQL",
        "Git",
        "REST APIs",
        "DSA",
        "HTML",
        "CSS",
        "FastAPI",
        "Node.js",
        "C++",
        "Problem Solving",
        "MongoDB"
        # Add more anytime — this is your resume skills section
    ],
    "preferred_roles": [
        "Software Engineer", "SDE", "Frontend Developer", "Backend Developer"
    ],
    "preferred_locations": ["Hyderabad", "Bengaluru", "Remote"],
    "min_lpa": 12,                       # minimum salary you want (LPA)
    "experience_type": "fresher",        # fresher / 0-1 year
    "about": """
        Final year B.Tech IT student, strong in DSA and web development.
        Looking for SDE or product roles at product-based companies.
        Quick learner, worked on 3 projects using React and Python.
    """
}

# --- COMPANIES TO TRACK ---
# Add any company name — the bot will search their careers page + Naukri + LinkedIn
COMPANIES = [
    "Zeta",
    "SuperMoney",
    "KPMG",
    "Honeywell",
    "Groww",
    "Razorpay",
    "Zepto",
    "Meesho",
    "Amazon",
    "Chargebee",
    "Goldman Sachs",
    "Morgan Stanley",
    "Flipkart",
    "IBM",
    "Microsoft",
    "Salesforce",
    "Qualcomm",
    "Oracle"
    # Add as many as you want
]

# --- ALERT SETTINGS ---
MIN_MATCH_PERCENT = 60      # only email you if match score >= this
CHECK_INTERVAL_HOURS = 24   # how often to scan (24 = once a day)
