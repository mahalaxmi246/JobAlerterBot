# 🚀 Job Alert Bot — Deploy Guide (Free, ~15 mins)

## What you need
- GitHub account (free)
- Render.com account (free)
- Brevo.com account (free) — for sending emails
- Your OpenAI API key ($5 credits you already have)

---

## Step 1 — Fill in config.py
Open `config.py` and fill in:
- Your name and email
- Your OpenAI API key
- Your skills (update this anytime!)
- Companies you want to track

---

## Step 2 — Get your Brevo API key (5 mins)
1. Go to brevo.com → Sign up free
2. Go to Settings → SMTP & API → API Keys
3. Click "Create a new API key"
4. Copy the key into `config.py` → BREVO_API_KEY
5. Go to Senders → Add your email as a verified sender

---

## Step 3 — Push to GitHub
```bash
# In your terminal (or use GitHub Desktop)
git init
git add .
git commit -m "job alert bot"
git remote add origin https://github.com/YOURUSERNAME/job-alert-bot.git
git push -u origin main
```

---

## Step 4 — Deploy on Render.com (free)

### Deploy the bot as a Cron Job:
1. Go to render.com → New → Cron Job
2. Connect your GitHub repo
3. Fill in:
   - **Name:** job-alert-bot
   - **Schedule:** `0 */12 * * *`  ← runs every 12 hours
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
4. Click "Create Cron Job"

That's it! Render will run your bot every 12 hours for free.

---

## Step 5 — Test it right now
On Render, click "Trigger Run" to run it immediately and check the logs.
You should see it scraping, matching, and sending an email.

---

## How to update your resume/skills
Just open `config.py`, update the `skills` list, and push to GitHub:
```bash
git add config.py
git commit -m "added new skills"
git push
```
Render auto-deploys. Done!

---

## Cost breakdown
| Service       | Cost         |
|---------------|--------------|
| Render Cron   | Free         |
| Brevo email   | Free (300/day)|
| OpenAI GPT-4o-mini | ~₹0.15 per run (~₹9/month) |
| **Total**     | **~₹9/month** |

Your $5 OpenAI credits = ~500+ runs = over 1 year of usage.

---

## Troubleshooting
- **No email received?** Check Render logs for errors. Check Brevo sender verification.
- **No jobs found?** Some sites block scrapers — check logs, Naukri usually works best.
- **Low match scores?** Add more skills in config.py, or lower MIN_MATCH_PERCENT to 50.
