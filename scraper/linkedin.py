"""
LinkedIn Jobs scraper using the public guest API endpoint.
No login required for basic listings. Falls back gracefully if blocked.
"""
import json
import re

from scraper.models import Job, JobSource
from scraper.http_client import RateLimitedSession

SEARCH_QUERIES = [
    "junior industrial designer",
    "junior product designer",
    "medical device designer",
    "industrial designer",
]

GUEST_API_URL = (
    "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    "?keywords={query}"
    "&location=Canada"
    "&f_TPR=r2592000"
    "&sortBy=DD"
    "&start={start}"
)

LINKEDIN_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.linkedin.com/jobs/",
}


def _parse_job_cards(html: str) -> list[dict]:
    jobs = []
    cards = re.findall(
        r'<li[^>]*class="[^"]*result-card[^"]*"[^>]*>(.*?)</li>', html, re.DOTALL
    )
    if not cards:
        cards = re.findall(r'<li[^>]*>(.*?)</li>', html, re.DOTALL)

    for card in cards:
        title_m = re.search(
            r'class="[^"]*result-card__title[^"]*"[^>]*>([^<]+)', card
        ) or re.search(r'aria-label="([^"]+)"', card)
        company_m = re.search(
            r'class="[^"]*result-card__subtitle[^"]*"[^>]*>([^<]+)', card
        )
        location_m = re.search(
            r'class="[^"]*job-result-card__location[^"]*"[^>]*>([^<]+)', card
        )
        link_m = re.search(r'href="(https://[^"]*linkedin\.com/jobs/view/[^"]+)"', card)
        id_m = re.search(r'/jobs/view/(\d+)', card)

        if not (title_m and id_m):
            continue

        raw_id = id_m.group(1)
        jobs.append(
            {
                "job_id": f"linkedin_{raw_id}",
                "title": title_m.group(1).strip(),
                "company": company_m.group(1).strip() if company_m else "Unknown",
                "location": location_m.group(1).strip() if location_m else "Canada",
                "url": link_m.group(1).strip() if link_m else f"https://www.linkedin.com/jobs/view/{raw_id}",
            }
        )
    return jobs


def scrape() -> list[Job]:
    client = RateLimitedSession(requests_per_minute=4)
    client.session.headers.update(LINKEDIN_HEADERS)
    seen_ids: set[str] = set()
    all_jobs: list[Job] = []

    for query in SEARCH_QUERIES:
        encoded = query.replace(" ", "%20")
        for start in [0, 25]:
            url = GUEST_API_URL.format(query=encoded, start=start)
            print(f"  [linkedin] Scraping: '{query}' start={start}")
            try:
                resp = client.get(url)
                raw_jobs = _parse_job_cards(resp.text)
            except Exception as e:
                print(f"  [linkedin] Skipping: {e}")
                break

            if not raw_jobs:
                break

            for rj in raw_jobs:
                if rj["job_id"] in seen_ids:
                    continue
                seen_ids.add(rj["job_id"])
                job = Job(
                    job_id=rj["job_id"],
                    source=JobSource.LINKEDIN,
                    title=rj["title"],
                    company=rj["company"],
                    location=rj["location"],
                    url=rj["url"],
                )
                all_jobs.append(job)
                print(f"    → Found: {job.title} @ {job.company}")

    print(f"  [linkedin] Total: {len(all_jobs)} jobs")
    return all_jobs
