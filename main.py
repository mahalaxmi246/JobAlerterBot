import hashlib
import os
from datetime import datetime

import psycopg2

from config import COMPANIES, MIN_MATCH_PERCENT
from emailer import send_alert_email
from matcher import filter_and_match
from scraper import get_all_jobs

DATABASE_URL = os.environ.get("DATABASE_URL", "")


def get_db():
    return psycopg2.connect(DATABASE_URL)


def setup_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS seen_jobs (
            job_id TEXT PRIMARY KEY,
            seen_at TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


def load_seen_jobs() -> set:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT job_id FROM seen_jobs")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return set(r[0] for r in rows)


def save_seen_jobs(new_job_ids: list):
    conn = get_db()
    cur = conn.cursor()
    for job_id in new_job_ids:
        cur.execute(
            "INSERT INTO seen_jobs (job_id) VALUES (%s) ON CONFLICT DO NOTHING",
            (job_id,)
        )
    conn.commit()
    cur.close()
    conn.close()


def job_id(job: dict) -> str:
    raw = f"{job['company']}|{job['title']}|{job['apply_link']}"
    return hashlib.md5(raw.encode()).hexdigest()


def run():
    print(f"\n{'='*50}")
    print(f"  Job Alert Bot — {datetime.now().strftime('%d %b %Y %H:%M')}")
    print(f"{'='*50}")
    print(f"  Tracking {len(COMPANIES)} companies: {', '.join(COMPANIES)}")
    print()

    setup_db()

    print("[1/3] Scraping job listings...")
    all_jobs = get_all_jobs(COMPANIES)
    print(f"  Total raw listings found: {len(all_jobs)}\n")

    seen = load_seen_jobs()
    new_jobs = [j for j in all_jobs if job_id(j) not in seen]
    print(f"[2/3] New (unseen) listings: {len(new_jobs)}")
    if not new_jobs:
        print("  Nothing new since last check. Done!")
        return

    print(f"\n[3/3] Running AI matching (min {MIN_MATCH_PERCENT}% threshold)...")
    matched = filter_and_match(new_jobs, MIN_MATCH_PERCENT)
    print(f"\n  Matched jobs above threshold: {len(matched)}")

    if matched:
        print("\n[→] Sending alert email...")
        send_alert_email(matched)

    save_seen_jobs([job_id(j) for j in new_jobs])

    print(f"\n  Done! See you next run.")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    run()