"""
Verifies whether a job listing is still active.
Uses source-specific heuristics.
"""
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from scraper.models import Job, JobSource, VerificationStatus
from scraper.http_client import RateLimitedSession

EXPIRED_PHRASES = [
    "no longer available",
    "job has expired",
    "no longer accepting applications",
    "position has been filled",
    "this job is closed",
    "listing has expired",
    "job not found",
    "offre expirée",
]


def _check_jobbank(raw_id: str, client: RateLimitedSession) -> VerificationStatus:
    url = f"https://www.jobbank.gc.ca/jobsearch/jobposting/{raw_id}"
    try:
        resp = client.get(url)
        if resp.status_code == 410:
            return VerificationStatus.EXPIRED
        text_lower = resp.text.lower()
        if any(p in text_lower for p in EXPIRED_PHRASES):
            return VerificationStatus.EXPIRED
        if "how to apply" in text_lower or "apply now" in text_lower:
            return VerificationStatus.ACTIVE
        return VerificationStatus.UNKNOWN
    except Exception as e:
        status = getattr(getattr(e, "response", None), "status_code", None)
        if status == 410:
            return VerificationStatus.EXPIRED
        return VerificationStatus.UNKNOWN


def _check_generic(url: str, client: RateLimitedSession) -> VerificationStatus:
    try:
        resp = client.get(url)
        if resp.status_code == 404:
            return VerificationStatus.EXPIRED
        text_lower = resp.text.lower()
        if any(p in text_lower for p in EXPIRED_PHRASES):
            return VerificationStatus.EXPIRED
        return VerificationStatus.ACTIVE
    except Exception as e:
        status = getattr(getattr(e, "response", None), "status_code", None)
        if status in (404, 410):
            return VerificationStatus.EXPIRED
        return VerificationStatus.UNKNOWN


def verify_job(job: Job, client: RateLimitedSession) -> VerificationStatus:
    if job.source == JobSource.JOBBANK:
        raw_id = job.job_id.replace("jobbank_", "")
        return _check_jobbank(raw_id, client)
    return _check_generic(job.url, client)


def verify_jobs_batch(
    jobs: list[Job], max_workers: int = 3
) -> list[Job]:
    client = RateLimitedSession(requests_per_minute=6)
    results = list(jobs)

    def _check(i: int, job: Job):
        status = verify_job(job, client)
        return i, status

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_check, i, job): i for i, job in enumerate(results)}
        for future in as_completed(futures):
            try:
                i, status = future.result()
                results[i].is_active = status
                label = {
                    VerificationStatus.ACTIVE: "✓ active",
                    VerificationStatus.EXPIRED: "✗ expired",
                    VerificationStatus.UNKNOWN: "? unknown",
                }[status]
                print(f"  [verify] {results[i].title[:50]} → {label}")
            except Exception as e:
                print(f"  [verify] Error: {e}")

    return results
