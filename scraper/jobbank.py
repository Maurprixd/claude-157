"""
Job Bank Canada scraper.
Most reliable source — government site, no JS required, HTTP 410 for expired jobs.
"""
import re
import hashlib
from datetime import datetime

from scraper.models import Job, JobSource
from scraper.http_client import RateLimitedSession

BASE_URL = "https://www.jobbank.gc.ca"

SEARCH_QUERIES = [
    "industrial designer",
    "product designer",
    "junior designer",
    "design engineer product",
    "medical device designer",
    "wearable device",
]

SEARCH_URL_TEMPLATE = (
    "{base}/jobsearch/jobsearch"
    "?searchstring={query}"
    "&locationstring=Toronto+ON"
    "&fprov=ON"
    "&action=search"
    "&sort=D"
    "&bhm=1"
)


def _make_job_id(raw_id: str) -> str:
    return f"jobbank_{raw_id}"


def _parse_search_page(html: str) -> list[dict]:
    articles = re.findall(r"<article[^>]*>(.*?)</article>", html, re.DOTALL)
    jobs = []
    for article in articles:
        title_m = re.search(r'class="noctitle"[^>]*>([^<]+)', article)
        company_m = re.search(r'class="business"[^>]*>([^<]+)', article)
        id_m = re.search(r"/jobposting/(\d+)", article)
        salary_m = re.search(r'class="salary"[^>]*>([^<]+)', article)

        loc_m = re.search(
            r'<li[^>]*>\s*<span[^>]*>Location\s*</span>\s*([^<]+)', article
        )
        date_m = re.search(
            r'<span[^>]*class="[^"]*date[^"]*"[^>]*>([^<]+)</span>', article
        )

        if not (title_m and id_m):
            continue

        raw_id = id_m.group(1).strip()
        jobs.append(
            {
                "job_id": _make_job_id(raw_id),
                "raw_id": raw_id,
                "title": title_m.group(1).strip(),
                "company": company_m.group(1).strip() if company_m else "Unknown",
                "location": loc_m.group(1).strip() if loc_m else "Toronto, ON",
                "salary": salary_m.group(1).strip() if salary_m else None,
                "posted_date": date_m.group(1).strip() if date_m else None,
                "url": f"{BASE_URL}/jobsearch/jobposting/{raw_id}",
            }
        )
    return jobs


def _fetch_job_description(raw_id: str, client: RateLimitedSession) -> str:
    url = f"{BASE_URL}/jobsearch/jobposting/{raw_id}"
    try:
        resp = client.get(url)
        html = resp.text
        desc_m = re.search(
            r'<div[^>]*id="applicant-detail"[^>]*>(.*?)</div>\s*</div>',
            html,
            re.DOTALL,
        )
        if desc_m:
            raw = desc_m.group(1)
            return re.sub(r"<[^>]+>", " ", raw).strip()
        body_m = re.search(
            r'<div[^>]*class="[^"]*job-posting-description[^"]*"[^>]*>(.*?)</div>',
            html,
            re.DOTALL,
        )
        if body_m:
            return re.sub(r"<[^>]+>", " ", body_m.group(1)).strip()
        return re.sub(r"<[^>]+>", " ", html)[:3000]
    except Exception as e:
        print(f"  [jobbank] Could not fetch description for {raw_id}: {e}")
        return ""


def scrape(max_pages: int = 3) -> list[Job]:
    client = RateLimitedSession(requests_per_minute=8)
    seen_ids: set[str] = set()
    all_jobs: list[Job] = []

    for query in SEARCH_QUERIES:
        encoded_query = query.replace(" ", "+")
        url = SEARCH_URL_TEMPLATE.format(base=BASE_URL, query=encoded_query)

        for page in range(max_pages):
            page_url = url if page == 0 else f"{url}&page={page + 1}"
            print(f"  [jobbank] Scraping: '{query}' page {page + 1}")
            try:
                resp = client.get(page_url)
            except Exception as e:
                print(f"  [jobbank] Failed to fetch page: {e}")
                break

            raw_jobs = _parse_search_page(resp.text)
            if not raw_jobs:
                break

            for rj in raw_jobs:
                if rj["job_id"] in seen_ids:
                    continue
                seen_ids.add(rj["job_id"])

                desc = _fetch_job_description(rj["raw_id"], client)
                job = Job(
                    job_id=rj["job_id"],
                    source=JobSource.JOBBANK,
                    title=rj["title"],
                    company=rj["company"],
                    location=rj["location"],
                    url=rj["url"],
                    salary=rj["salary"],
                    posted_date=rj["posted_date"],
                    description=desc,
                )
                all_jobs.append(job)
                print(f"    → Found: {job.title} @ {job.company}")

    print(f"  [jobbank] Total: {len(all_jobs)} jobs")
    return all_jobs
