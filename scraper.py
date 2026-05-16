"""
scraper.py — Uses reliable RSS feeds and job APIs that never get blocked.
Sources:
  1. Indeed RSS feed (public, never blocked)
  2. LinkedIn Jobs (public)
  3. Naukri RSS feeds
  4. FreshersWorld (India-specific fresher jobs)
"""

import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote_plus

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def scrape_indeed_rss(company: str) -> list[dict]:
    """Indeed RSS feed — public, reliable, never blocked."""
    jobs = []
    try:
        query = quote_plus(f"{company} fresher")
        url = f"https://in.indeed.com/rss?q={query}&l=India&sort=date"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "xml")
        items = soup.find_all("item")
        for item in items[:8]:
            title = item.find("title")
            link = item.find("link")
            description = item.find("description")
            if title:
                desc_text = BeautifulSoup(description.get_text() if description else "", "html.parser").get_text(" ", strip=True)[:600]
                jobs.append({
                    "title": title.get_text(strip=True),
                    "company": company,
                    "source": "Indeed",
                    "skills_text": desc_text,
                    "salary": "Check listing",
                    "apply_link": link.get_text(strip=True) if link else f"https://in.indeed.com/jobs?q={query}",
                    "description": desc_text,
                    "location": "India",
                })
    except Exception as e:
        print(f"  [Indeed RSS] Error for {company}: {e}")
    return jobs


def scrape_naukri_rss(company: str) -> list[dict]:
    """Naukri RSS — more reliable than HTML scraping."""
    jobs = []
    try:
        query = quote_plus(f"{company} fresher")
        url = f"https://www.naukri.com/rss/jobsearch/jobsearch.xml?qp={query}&type=rss&version=2"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "xml")
        items = soup.find_all("item")
        for item in items[:8]:
            title = item.find("title")
            link = item.find("link")
            description = item.find("description")
            if title:
                desc_text = BeautifulSoup(description.get_text() if description else "", "html.parser").get_text(" ", strip=True)[:600]
                jobs.append({
                    "title": title.get_text(strip=True),
                    "company": company,
                    "source": "Naukri",
                    "skills_text": desc_text,
                    "salary": "Check listing",
                    "apply_link": link.get_text(strip=True) if link else f"https://www.naukri.com/{company.lower()}-jobs",
                    "description": desc_text,
                    "location": "India",
                })
    except Exception as e:
        print(f"  [Naukri RSS] Error for {company}: {e}")
    return jobs


def scrape_linkedin_rss(company: str) -> list[dict]:
    """LinkedIn Jobs public search."""
    jobs = []
    try:
        query = quote_plus(f"{company}")
        url = (
            f"https://www.linkedin.com/jobs/search/?keywords={query}"
            f"&location=India&f_E=1&f_JT=F&sortBy=DD"
        )
        resp = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select("div.base-card") or soup.select(".job-search-card")
        for card in cards[:6]:
            title_el = card.select_one("h3.base-search-card__title") or card.select_one("h3")
            link_el = card.select_one("a.base-card__full-link") or card.select_one("a")
            location_el = card.select_one(".job-search-card__location")
            if title_el:
                jobs.append({
                    "title": title_el.get_text(strip=True),
                    "company": company,
                    "source": "LinkedIn",
                    "skills_text": "",
                    "salary": "Check listing",
                    "apply_link": link_el["href"].split("?")[0] if link_el and link_el.get("href") else url,
                    "description": card.get_text(" ", strip=True)[:600],
                    "location": location_el.get_text(strip=True) if location_el else "India",
                })
    except Exception as e:
        print(f"  [LinkedIn] Error for {company}: {e}")
    return jobs


def scrape_freshersworld(company: str) -> list[dict]:
    """FreshersWorld — specifically for fresher jobs in India."""
    jobs = []
    try:
        slug = company.lower().replace(' ', '-')
        url = f"https://www.freshersworld.com/jobs/jobsearch/{slug}-fresher-jobs"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select(".job-container") or soup.select(".job-details")
        for card in cards[:5]:
            title_el = card.select_one("h3") or card.select_one(".job-title")
            link_el = card.select_one("a")
            if title_el:
                href = link_el.get("href", "") if link_el else ""
                jobs.append({
                    "title": title_el.get_text(strip=True),
                    "company": company,
                    "source": "FreshersWorld",
                    "skills_text": card.get_text(" ", strip=True)[:400],
                    "salary": "Check listing",
                    "apply_link": "https://www.freshersworld.com" + href if href.startswith("/") else url,
                    "description": card.get_text(" ", strip=True)[:600],
                    "location": "India",
                })
    except Exception as e:
        print(f"  [FreshersWorld] Error for {company}: {e}")
    return jobs


def get_all_jobs(companies: list[str]) -> list[dict]:
    """Main function — scrapes all sources for all companies."""
    all_jobs = []
    for company in companies:
        print(f"  Scraping: {company}...")
        indeed_jobs   = scrape_indeed_rss(company)
        naukri_jobs   = scrape_naukri_rss(company)
        linkedin_jobs = scrape_linkedin_rss(company)
        freshers_jobs = scrape_freshersworld(company)
        company_jobs  = indeed_jobs + naukri_jobs + linkedin_jobs + freshers_jobs
        print(f"    Found {len(company_jobs)} listings (Indeed:{len(indeed_jobs)} Naukri:{len(naukri_jobs)} LinkedIn:{len(linkedin_jobs)} Freshers:{len(freshers_jobs)})")
        all_jobs.extend(company_jobs)
        time.sleep(1)
    return all_jobs