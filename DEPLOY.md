# 🚀 Deploy Guide — Job Alert Bot

Complete setup from scratch in ~20 minutes. Everything is free except OpenAI (~₹10/month).

---

## What you need before starting

- [ ] GitHub account
- [ ] OpenAI API key 
- [ ] Brevo account (free email sender)
- [ ] Supabase account (free database)

---

## Step 1 — Clone & configure

**1.1** Download or clone this repo to your computer

**1.2** Open `config.py` and fill in:

```python
YOUR_NAME  = "Your Full Name"
YOUR_EMAIL = "youremail@gmail.com"

PROFILE = {
    "name": YOUR_NAME,
    "degree": "B.Tech IT",
    "college": "Your College Name",
    "graduation_year": "2027",
    "cgpa": "8.5",
    "skills": ["Python", "JavaScript", "React", "SQL", "Git"],
    "preferred_roles": ["SDE", "Data Analyst", "Product Analyst"],
    "preferred_locations": ["Hyderabad", "Bengaluru", "Remote"],
    "min_lpa": 10,
    "experience_type": "fresher",
    "about": "Brief about yourself..."
}

COMPANIES = [
    "Zeta", "KPMG", "Honeywell", "Groww",
    # Add as many as you want
]

MIN_MATCH_PERCENT = 60   # lower to 50 for more results
```

**1.3** Push to GitHub:

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/YOURUSERNAME/JobAlerterBot.git
git push -u origin main
```

> ⚠️ `config.py` is safe to push — all secrets (API keys) are stored in GitHub Secrets, not in this file.

---

## Step 2 — Set up Brevo (email sender)

**2.1** Go to [brevo.com](https://brevo.com) → Sign up free

**2.2** Go to **Settings → SMTP & API → API Keys** → Create new API key → Copy it

**2.3** Go to **Senders** → Add and verify your email address

---

## Step 3 — Set up Supabase (database)

**3.1** Go to [supabase.com](https://supabase.com) → Sign up with GitHub

**3.2** Click **New Project** → name it `JobAlerterBot` → set a password (simple, no special characters e.g. `JobBot1246`) → Create

**3.3** Go to your project → click the green **Connect** button (top right)

**3.4** Click **Direct** tab → copy the connection string

**3.5** Replace `[YOUR-PASSWORD]` in the URL with your password

> ⚠️ Use the **Shared Pooler** URL (contains `pooler.supabase.com`) not the direct URL — it supports IPv4 which GitHub Actions requires.

Your DATABASE_URL should look like:
```
postgresql://postgres.xxxxxxxxxxxx:YourPassword@aws-1-ap-south-1.pooler.supabase.com:5432/postgres
```

---

## Step 4 — Add GitHub Secrets

**4.1** Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**

**4.2** Click **New repository secret** and add these one by one:

| Secret Name | Value |
|-------------|-------|
| `OPENAI_API_KEY` | Your OpenAI key (starts with `sk-...`) |
| `BREVO_API_KEY` | Your Brevo API key |
| `FROM_EMAIL` | Your verified Brevo sender email |
| `DATABASE_URL` | Your Supabase pooler connection string |

---

## Step 5 — Deploy & Test

**5.1** Go to your GitHub repo → **Actions** tab

**5.2** Click **Job Alert Bot** on the left

**5.3** Click **Run workflow** → **Run workflow** (green button)

**5.4** Click on the running job → click **run-bot** → watch live logs

**5.5** Check your email inbox for the alert!

---

## Step 6 — Schedule (already set up)

The bot runs automatically every day at **10 AM IST** via GitHub Actions.

To change the time, edit `.github/workflows/job-alert.yml`:

```yaml
- cron: "30 4 * * *"   # 4:30 AM UTC = 10:00 AM IST
```

Use [crontab.guru](https://crontab.guru) to generate cron expressions.

---

## 🔄 How to update your skills anytime

```bash
# Edit config.py → update skills list → push
git add config.py
git commit -m "added new skills"
git push
```

Done! The bot picks up your new skills automatically on the next run.

---

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'config'` | `config.py` not pushed to GitHub. Remove it from `.gitignore` and push. |
| `Network is unreachable` (Supabase) | You're using the direct URL instead of the pooler URL. Use `pooler.supabase.com`. |
| `could not translate host name` | Wrong DATABASE_URL format. Check for special characters in password. |
| No email received | Check logs — either no jobs matched or Brevo sender not verified. |
| Bot runs but finds 0 jobs | Scrapers being blocked. Check logs for errors per company. |

---

## 💰 Cost breakdown

| Service | Free Tier | Your Usage | Cost |
|---------|-----------|------------|------|
| GitHub Actions | 2,000 min/month | ~5 min/day = 150 min/month | **Free** |
| Supabase | 500MB database | <1MB | **Free** |
| Brevo | 300 emails/day | 1/day | **Free** |
| OpenAI GPT-4o-mini | Pay per use | ~150 jobs/day × $0.00015 | **~₹10/month** |

**With $5 OpenAI credits = 12+ months of usage**
