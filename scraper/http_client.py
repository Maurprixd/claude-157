import time
import random
from urllib.parse import urlparse

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

SESSION_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
    ),
    "Accept-Language": "en-CA,en;q=0.9,fr;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


class RateLimitedSession:
    """HTTP session with per-domain rate limiting and exponential backoff."""

    def __init__(self, requests_per_minute: int = 8):
        self.session = requests.Session()
        self.session.headers.update(SESSION_HEADERS)
        self._min_delay = 60.0 / requests_per_minute
        self._last_request_time: dict[str, float] = {}

    def _wait_for_rate(self, domain: str) -> None:
        last = self._last_request_time.get(domain, 0)
        elapsed = time.monotonic() - last
        wait = self._min_delay - elapsed
        if wait > 0:
            time.sleep(wait + random.uniform(0.1, 0.5))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=30),
        retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout)),
    )
    def get(self, url: str, **kwargs) -> requests.Response:
        domain = urlparse(url).netloc
        self._wait_for_rate(domain)
        resp = self.session.get(url, timeout=15, **kwargs)
        self._last_request_time[domain] = time.monotonic()
        resp.raise_for_status()
        return resp

    def head(self, url: str, **kwargs) -> requests.Response:
        domain = urlparse(url).netloc
        self._wait_for_rate(domain)
        try:
            resp = self.session.head(url, timeout=10, allow_redirects=True, **kwargs)
            self._last_request_time[domain] = time.monotonic()
            return resp
        except Exception:
            return self.session.head(url, timeout=10, **kwargs)
