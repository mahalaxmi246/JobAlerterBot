"""
main.py — The brain. Run this manually or let the scheduler call it.
Handles deduplication so you never get the same job twice.
"""

import json
import os
import hashlib
from datetime import datetime

from config import COMPANIES, MIN_MATCH_PERCENT
from scraper import get_all_jobs
from matcher import filter_and_match
from emailer import send_alert_email

SEEN_JOBS_FILE = "seen_jobs.json"   # tracks already-alerted jobs


def load_seen_jobs() -> set:
    if os.path.exists(SEEN_JOBS_FILE):
        with open(SEEN_JOBS_FILE) as f:
            return set(json.load(f))
    return set()


def save_seen_jobs(seen: set):
    with open(SEEN_JOBS_FILE, "w") as f:
        json.dump(list(seen), f)


def job_id(job: dict) -> str:
    """Unique fingerprint for a job posting."""
    raw = f"{job['company']}|{job['title']}|{job['apply_link']}"
    return hashlib.md5(raw.encode()).hexdigest()


def run():
    print(f"\n{'='*50}")
    print(f"  Job Alert Bot — {datetime.now().strftime('%d %b %Y %H:%M')}")
    print(f"{'='*50}")
    print(f"  Tracking {len(COMPANIES)} companies: {', '.join(COMPANIES)}")
    print()

    # Step 1: Scrape
    print("[1/3] Scraping job listings...")
    all_jobs = get_all_jobs(COMPANIES)
    print(f"  Total raw listings found: {len(all_jobs)}\n")

    # Step 2: Deduplicate
    seen = load_seen_jobs()
    new_jobs = [j for j in all_jobs if job_id(j) not in seen]
    print(f"[2/3] New (unseen) listings: {len(new_jobs)}")
    if not new_jobs:
        print("  Nothing new since last check. Done!")
        return

    # Step 3: AI Match
    print(f"\n[3/3] Running AI matching (min {MIN_MATCH_PERCENT}% threshold)...")
    matched = filter_and_match(new_jobs, MIN_MATCH_PERCENT)
    print(f"\n  Matched jobs above threshold: {len(matched)}")

    # Step 4: Email
    if matched:
        print("\n[→] Sending alert email...")
        send_alert_email(matched)

    # Step 5: Mark all new jobs as seen (even unmatched ones)
    for job in new_jobs:
        seen.add(job_id(job))
    save_seen_jobs(seen)

    print(f"\n  Done! Next run in ~12 hours.")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    run()
