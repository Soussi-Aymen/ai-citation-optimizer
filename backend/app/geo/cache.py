import time
from typing import Protocol
from urllib.parse import urlsplit, urlunsplit

from .models import CheckResult

DEFAULT_TTL_S = 600


def normalize_url(url: str) -> str:
    parsed = urlsplit(url.strip())
    host = (parsed.hostname or "").lower()
    if parsed.port:
        host = f"{host}:{parsed.port}"
    path = parsed.path.rstrip("/") or "/"
    scheme = (parsed.scheme or "https").lower()
    return urlunsplit((scheme, host, path, parsed.query, ""))


class CheckResultCache(Protocol):
    def get(self, url: str) -> list[CheckResult] | None: ...

    def set(self, url: str, results: list[CheckResult]) -> None: ...


class InMemoryTTLCache:
    def __init__(self, ttl_s: float = DEFAULT_TTL_S):
        self.ttl_s = ttl_s
        self._store: dict[str, tuple[float, list[CheckResult]]] = {}

    def get(self, url: str) -> list[CheckResult] | None:
        key = normalize_url(url)
        item = self._store.get(key)
        if item is None:
            return None
        stored_at, results = item
        if time.monotonic() - stored_at > self.ttl_s:
            del self._store[key]
            return None
        return results

    def set(self, url: str, results: list[CheckResult]) -> None:
        self._store[normalize_url(url)] = (time.monotonic(), results)
