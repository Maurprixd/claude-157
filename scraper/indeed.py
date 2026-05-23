"""
Indeed Canada scraper via RSS feeds.
Falls back gracefully if RSS is blocked in this environment.
"""
import re
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus

from scraper.models import Job, JobSource
from scraper.http_client import RateLimitedSession

RSS_QUERIES = [
    "junior industrial designer",
    "junior product designer",
    "product design",
    "industrial designer",
    "medical device designer",
]

RSS_URL_TEMPLATE = (
    "https://ca.indeed.com/rss"
    "?q={query}"
    "&l=Toronto%2C+ON"
    "&radius=50"
    "&sort=date"
    "&fromage=30"
)

RSS_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Referer": "https://ca.indeed.com/",
}


def _parse_rss(xml_text: str) -> list[dict]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    jobs = []
    for item in root.findall(".//item"):
        title_el = item.find("title")
        link_el = item.find("link")
        pub_el = item.find("pubDate")
        guid_el = item.find("guid")
        desc_el = item.find("description")

        if title_el is None or link_el is None:
            continue

        raw_title = title_el.text or ""
        parts = raw_title.split(" - ")
        title = parts[0].strip() if parts else raw_title
        company = parts[1].strip() if len(parts) > 1 else "Unknown"
        location = parts[2].strip() if len(parts) > 2 else "Toronto, ON"

        guid = (guid_el.text or link_el.text or "").strip()
        job_id_raw = re.search(r"jk=([a-f0-9]+)", guid)
        job_id = f"indeed_{job_id_raw.group(1)}" if job_id_raw else f"indeed_{abs(hash(guid))}"

        desc = ""
        if desc_el is not None and desc_el.text:
            desc = re.sub(r"<[^>]+>", " ", desc_el.text).strip()

        jobs.append(
            {
                "job_id": job_id,
                "title": title,
                "company": company,
                "location": location,
                "url": link_el.text or guid,
                "posted_date": pub_el.text if pub_el is not None else None,
                "description": desc,
            }
        )
    return jobs


def scrape() -> list[Job]:
    client = RateLimitedSession(requests_per_minute=5)
    client.session.headers.update(RSS_HEADERS)
    seen_ids: set[str] = set()
    all_jobs: list[Job] = []

    for query in RSS_QUERIES:
        url = RSS_URL_TEMPLATE.format(query=quote_plus(query))
        print(f"  [indeed] Scraping RSS: '{query}'")
        try:
            resp = client.get(url)
            raw_jobs = _parse_rss(resp.text)
        except Exception as e:
            print(f"  [indeed] Skipping '{query}': {e}")
            continue

        for rj in raw_jobs:
            if rj["job_id"] in seen_ids:
                continue
            seen_ids.add(rj["job_id"])
            job = Job(
                job_id=rj["job_id"],
                source=JobSource.INDEED,
                title=rj["title"],
                company=rj["company"],
                location=rj["location"],
                url=rj["url"],
                posted_date=rj["posted_date"],
                description=rj["description"],
            )
            all_jobs.append(job)
            print(f"    → Found: {job.title} @ {job.company}")

    print(f"  [indeed] Total: {len(all_jobs)} jobs")
    return all_jobs
