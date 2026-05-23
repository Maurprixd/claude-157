from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import json


class JobSource(str, Enum):
    JOBBANK = "jobbank"
    INDEED = "indeed"
    GLASSDOOR = "glassdoor"
    LINKEDIN = "linkedin"


class VerificationStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    UNKNOWN = "unknown"


@dataclass
class Job:
    job_id: str
    source: JobSource
    title: str
    company: str
    location: str
    url: str

    description: str = ""
    salary: Optional[str] = None
    posted_date: Optional[str] = None

    match_score: Optional[int] = None
    match_reasoning: Optional[str] = None
    key_strengths: list = field(default_factory=list)
    key_gaps: list = field(default_factory=list)
    odds_of_getting: Optional[str] = None

    is_active: VerificationStatus = VerificationStatus.UNKNOWN

    notion_page_id: Optional[str] = None
    applied: bool = False
    applied_at: Optional[str] = None

    scraped_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        d = {k: v for k, v in self.__dict__.items()}
        d["source"] = self.source.value
        d["is_active"] = self.is_active.value
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Job":
        d = dict(d)
        d["source"] = JobSource(d["source"])
        d["is_active"] = VerificationStatus(d.get("is_active", "unknown"))
        return cls(**d)

    def short_summary(self) -> str:
        score_str = f"  SCORE: {self.match_score}/100" if self.match_score else ""
        active_str = {
            VerificationStatus.ACTIVE: "✓ ACTIVE",
            VerificationStatus.EXPIRED: "✗ EXPIRED",
            VerificationStatus.UNKNOWN: "? UNKNOWN",
        }[self.is_active]
        return (
            f"{score_str}  {active_str}\n"
            f"    {self.title} — {self.company}\n"
            f"    Location: {self.location}\n"
            f"    Salary: {self.salary or 'Not specified'}\n"
            f"    Source: {self.source.value} | ID: {self.job_id}\n"
            f"    URL: {self.url}\n"
            f"    Odds: {self.odds_of_getting or 'N/A'}\n"
            f"    Gaps: {', '.join(self.key_gaps) if self.key_gaps else 'None identified'}\n"
            f"    Strengths: {', '.join(self.key_strengths) if self.key_strengths else 'N/A'}"
        )
