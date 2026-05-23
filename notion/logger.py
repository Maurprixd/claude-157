"""
Notion database logger using the Notion REST API.
Logs job applications to Mauricio's existing Notion database.
Database ID: fcadfa0f55a54b6f99b5e2fadfdf1ad9
"""
import os
from datetime import datetime
from typing import Optional

import requests

from scraper.models import Job, VerificationStatus

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_API_VERSION = "2022-06-28"
DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "fcadfa0f55a54b6f99b5e2fadfdf1ad9")


class NotionLogger:
    def __init__(self):
        self.token = os.getenv("NOTION_TOKEN")
        if not self.token:
            raise ValueError(
                "NOTION_TOKEN not set. Add it to your .env file.\n"
                "Get it from: https://www.notion.so/my-integrations"
            )
        self.database_id = DATABASE_ID
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_API_VERSION,
        }

    def log_job(self, job: Job, status: str = "Interested") -> str:
        """
        Create a new page in the Notion database for this job.
        Checks for duplicates first using job_id.
        Returns the Notion page ID.
        """
        existing = self._find_existing(job.job_id)
        if existing:
            print(f"  [notion] Job already logged: {job.job_id}")
            job.notion_page_id = existing
            return existing

        payload = self._build_page_payload(job, status)
        resp = requests.post(
            f"{NOTION_API_BASE}/pages",
            headers=self.headers,
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
        page_id = resp.json()["id"]
        job.notion_page_id = page_id
        print(f"  [notion] Logged: {job.title} @ {job.company} (page: {page_id[:8]}...)")
        return page_id

    def mark_applied(self, job: Job) -> None:
        """Update Status to 'Applied' and set Applied Date."""
        if not job.notion_page_id:
            page_id = self._find_existing(job.job_id)
            if not page_id:
                print(f"  [notion] Job not found in Notion, logging first...")
                self.log_job(job, status="Applied")
                return
            job.notion_page_id = page_id

        payload = {
            "properties": {
                "Status": {"select": {"name": "Applied"}},
                "Applied Date": {"date": {"start": datetime.utcnow().date().isoformat()}},
            }
        }
        requests.patch(
            f"{NOTION_API_BASE}/pages/{job.notion_page_id}",
            headers=self.headers,
            json=payload,
            timeout=15,
        ).raise_for_status()
        print(f"  [notion] Marked as Applied: {job.title} @ {job.company}")

    def _find_existing(self, job_id: str) -> Optional[str]:
        payload = {
            "filter": {
                "property": "Job ID",
                "rich_text": {"equals": job_id},
            }
        }
        try:
            resp = requests.post(
                f"{NOTION_API_BASE}/databases/{self.database_id}/query",
                headers=self.headers,
                json=payload,
                timeout=15,
            )
            resp.raise_for_status()
            results = resp.json().get("results", [])
            return results[0]["id"] if results else None
        except Exception:
            return None

    def _build_page_payload(self, job: Job, status: str) -> dict:
        active_str = {
            VerificationStatus.ACTIVE: "Yes",
            VerificationStatus.EXPIRED: "No",
            VerificationStatus.UNKNOWN: "Unknown",
        }.get(job.is_active, "Unknown")

        props: dict = {
            "Job Title": {"title": [{"text": {"content": job.title[:100]}}]},
            "Company": {"rich_text": [{"text": {"content": job.company[:100]}}]},
            "Location": {"rich_text": [{"text": {"content": job.location[:100]}}]},
            "Source": {"select": {"name": job.source.value}},
            "URL": {"url": job.url},
            "Status": {"select": {"name": status}},
            "Job ID": {"rich_text": [{"text": {"content": job.job_id}}]},
            "Scraped Date": {"date": {"start": job.scraped_at[:10]}},
            "Still Active": {"select": {"name": active_str}},
        }

        if job.match_score is not None:
            props["Match Score"] = {"number": job.match_score}

        if job.odds_of_getting:
            props["Odds"] = {
                "rich_text": [{"text": {"content": job.odds_of_getting[:200]}}]
            }

        if job.match_reasoning:
            props["Match Reasoning"] = {
                "rich_text": [{"text": {"content": job.match_reasoning[:2000]}}]
            }

        if job.salary:
            props["Salary"] = {
                "rich_text": [{"text": {"content": job.salary[:100]}}]
            }

        return {
            "parent": {"database_id": self.database_id},
            "properties": props,
        }
