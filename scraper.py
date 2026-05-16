"""
scraper.py — Finds fresh job postings from:
  1. Each company's official careers page
  2. Naukri.com search
  3. LinkedIn Jobs search
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import quote_plus

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Known career page URLs for popular Indian companies
# Bot will also auto-discover unknown ones via Google
KNOWN_CAREER_PAGES = {
    "Zeta":       "https://zeta.tech/careers",
    "Razorpay":   "https://razorpay.com/jobs",
    "Groww":      "https://groww.in/careers",
    "Meesho":     "https://meesho.io/careers",
    "Zepto":      "https://www.zepto.team/careers",
    "KPMG":       "https://kpmg.com/in/en/home/careers.html",
    "Honeywell":  "https://careers.honeywell.com",
    "SuperMoney": "https://supermoney.com/careers",
}


def scrape_naukri(company: str, experience: str = "0") -> list[dict]:
    """Search Naukri.com for fresher jobs at a company."""
    jobs = []
    try:
        query = quote_plus(f"{company} fresher")
        url = f"https://www.naukri.com/{company.lower().replace(' ', '-')}-jobs?experience={experience}"
        
        # Naukri public search URL
        search_url = f"https://www.naukri.com/jobs-in-india?keyword={query}&experience=0"
        resp = requests.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Naukri job cards
        cards = soup.select("article.jobTuple") or soup.select(".cust-job-tuple")
        for card in cards[:10]:
            title_el = card.select_one(".title") or card.select_one("a.title")
            company_el = card.select_one(".comp-name") or card.select_one(".companyInfo")
            skills_el = card.select_one(".tags-gt") or card.select_one(".skill-list")
            salary_el = card.select_one(".salary")
            link_el = card.select_one("a.title") or card.select_one("a")

            if title_el:
                jobs.append({
                    "title": title_el.get_text(strip=True),
                    "company": company,
                    "source": "Naukri",
                    "skills_text": skills_el.get_text(" ", strip=True) if skills_el else "",
                    "salary": salary_el.get_text(strip=True) if salary_el else "Not mentioned",
                    "apply_link": link_el["href"] if link_el and link_el.get("href") else search_url,
                    "description": card.get_text(" ", strip=True)[:800],
                })
    except Exception as e:
        print(f"  [Naukri] Error for {company}: {e}")
    return jobs


def scrape_linkedin(company: str) -> list[dict]:
    """Search LinkedIn public job listings (no login needed for basic search)."""
    jobs = []
    try:
        query = quote_plus(f"{company} fresher engineer analyst")
        url = (
            f"https://www.linkedin.com/jobs/search/?keywords={query}"
            f"&location=India&f_E=1"  # f_E=1 = Entry level
        )
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        cards = soup.select("div.base-card") or soup.select(".job-search-card")
        for card in cards[:8]:
            title_el = card.select_one(".base-search-card__title") or card.select_one("h3")
            company_el = card.select_one(".base-search-card__subtitle")
            link_el = card.select_one("a.base-card__full-link") or card.select_one("a")
            location_el = card.select_one(".job-search-card__location")

            if title_el:
                jobs.append({
                    "title": title_el.get_text(strip=True),
                    "company": company,
                    "source": "LinkedIn",
                    "skills_text": "",
                    "salary": "Check listing",
                    "apply_link": link_el["href"] if link_el and link_el.get("href") else url,
                    "description": card.get_text(" ", strip=True)[:800],
                    "location": location_el.get_text(strip=True) if location_el else "India",
                })
    except Exception as e:
        print(f"  [LinkedIn] Error for {company}: {e}")
    return jobs


def scrape_career_page(company: str) -> list[dict]:
    """Scrape the company's own careers page."""
    jobs = []
    url = KNOWN_CAREER_PAGES.get(company)
    
    if not url:
        # Try to auto-discover via a Google-style search URL
        query = quote_plus(f"{company} careers jobs site:{company.lower().replace(' ','')}.com")
        url = f"https://www.google.com/search?q={query}"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Generic job keyword search on the page
        fresher_keywords = ["fresher", "graduate", "entry", "0-1", "new grad", "campus", "2024", "2025"]
        
        # Look for job-like links
        all_links = soup.find_all("a", href=True)
        for link in all_links:
            text = link.get_text(strip=True).lower()
            href = link["href"]
            
            # Filter for job-looking links
            if any(kw in text for kw in ["engineer", "analyst", "developer", "associate", "intern"]):
                if any(kw in text for kw in fresher_keywords) or len(text) > 10:
                    full_url = href if href.startswith("http") else url.rstrip("/") + "/" + href.lstrip("/")
                    jobs.append({
                        "title": link.get_text(strip=True),
                        "company": company,
                        "source": f"{company} Careers",
                        "skills_text": "",
                        "salary": "Check listing",
                        "apply_link": full_url,
                        "description": text[:400],
                    })
                    if len(jobs) >= 5:
                        break
    except Exception as e:
        print(f"  [CareerPage] Error for {company}: {e}")
    return jobs


def get_all_jobs(companies: list[str]) -> list[dict]:
    """Main function — scrapes all sources for all companies."""
    all_jobs = []
    for company in companies:
        print(f"  Scraping: {company}...")
        
        naukri_jobs   = scrape_naukri(company)
        linkedin_jobs = scrape_linkedin(company)
        career_jobs   = scrape_career_page(company)
        
        company_jobs = naukri_jobs + linkedin_jobs + career_jobs
        print(f"    Found {len(company_jobs)} listings")
        all_jobs.extend(company_jobs)
        time.sleep(1.5)   # polite delay between companies
    
    return all_jobs
