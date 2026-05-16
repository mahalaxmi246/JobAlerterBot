# 🎯 Job Alert Bot

An automated job alert system that scrapes fresher job openings from your target companies every day, matches them against your profile using AI, and sends you a beautiful email with only the relevant ones.

> Built with Python · OpenAI GPT-4o-mini · GitHub Actions · Supabase · Brevo

---

## ✨ What it does

- 🔍 **Scrapes** LinkedIn, FreshersWorld, Indeed, Naukri for your tracked companies daily
- 🤖 **AI matches** each job against your skills, role preferences, location, and expected salary
- 📧 **Emails you** only jobs above your match threshold (default 60%)
- 🚫 **Filters out** staffing agencies, non-fresher roles, and irrelevant companies
- 💾 **Never repeats** the same job twice (deduplication via Supabase)
- ⚙️ **Runs automatically** every day via GitHub Actions — completely free

---

## 🛠️ Tech Stack

| Layer | Tool | Cost |
|-------|------|------|
| Scheduler | GitHub Actions | Free |
| AI Matching | OpenAI GPT-4o-mini | ~₹10/month |
| Database | Supabase PostgreSQL | Free |
| Email | Brevo SMTP | Free (300/day) |
| Scraping | Python + BeautifulSoup | Free |

**Total cost: ~₹10/month**

---

## 📁 Project Structure

```
JobAlerterBot/
├── config.py                        # Your profile, skills, companies (edit this!)
├── main.py                          # Main runner
├── scraper.py                       # Job scraper (LinkedIn, Indeed, Naukri, FreshersWorld)
├── matcher.py                       # OpenAI job matching engine
├── emailer.py                       # Brevo email sender
├── requirements.txt                 # Python dependencies
└── .github/
    └── workflows/
        └── job-alert.yml            # GitHub Actions cron schedule
```

---

## ⚡ Quick Start

See [DEPLOY.md](DEPLOY.md) for full setup instructions.

---

## 🔄 How to update your resume

Just open `config.py`, update your skills list, and push:

```bash
git add config.py
git commit -m "added new skills"
git push
```

The bot automatically picks up your updated profile on the next run.

---

## 📬 Sample Email

Each alert email includes:
- Company name and job title
- AI match score (0–100%)
- Your matching skills ✅
- Skills you should learn 📚
- AI verdict on whether to apply
- Direct apply link

---

## 🙋 FAQ

**Why am I not getting emails?**
Either no jobs matched above your threshold, or the scraper found nothing new. Check GitHub Actions logs.

**Can I add more companies?**
Yes! Just add them to the `COMPANIES` list in `config.py` and push.

**How do I change the match threshold?**
Update `MIN_MATCH_PERCENT` in `config.py`. Lower it to 50 to get more results.

**How do I change the schedule?**
Update the cron expression in `.github/workflows/job-alert.yml`.
