import json
import pathlib
from datetime import datetime
from typing import Optional

from scraper.models import Job

CACHE_FILE = pathlib.Path(".job_cache.json")
CACHE_TTL_HOURS = 24


class JobCache:
    """JSON file cache for scraped and scored jobs. TTL: 24 hours."""

    def __init__(self, cache_path: pathlib.Path = CACHE_FILE):
        self.cache_path = cache_path
        self._data: dict = self._load()

    def _load(self) -> dict:
        if self.cache_path.exists():
            try:
                return json.loads(self.cache_path.read_text())
            except json.JSONDecodeError:
                return {}
        return {}

    def save(self) -> None:
        self.cache_path.write_text(json.dumps(self._data, indent=2, default=str))

    def get(self, job_id: str) -> Optional[Job]:
        entry = self._data.get(job_id)
        if not entry:
            return None
        cached_at_str = entry.get("scraped_at", "2000-01-01T00:00:00")
        try:
            cached_at = datetime.fromisoformat(cached_at_str)
        except ValueError:
            return None
        age_hours = (datetime.utcnow() - cached_at).total_seconds() / 3600
        if age_hours > CACHE_TTL_HOURS:
            del self._data[job_id]
            return None
        return Job.from_dict(entry)

    def set(self, job: Job) -> None:
        self._data[job.job_id] = job.to_dict()

    def get_all(self) -> list[Job]:
        valid = []
        for job_id in list(self._data.keys()):
            job = self.get(job_id)
            if job:
                valid.append(job)
        return valid

    def get_all_scored(self) -> list[Job]:
        return [j for j in self.get_all() if j.match_score is not None]

    def get_all_scored_sorted(self) -> list[Job]:
        return sorted(self.get_all_scored(), key=lambda j: j.match_score or 0, reverse=True)
