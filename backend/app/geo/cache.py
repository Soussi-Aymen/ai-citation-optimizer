import time
from typing import Protocol
from urllib.parse import urlsplit, urlunsplit

from .models import CheckResult, CheckStatus

DEFAULT_TTL_S = 600
CACHEABLE_STATUSES = frozenset({CheckStatus.PASS, CheckStatus.WARN, CheckStatus.FAIL})


def normalize_url(url: str) -> str:
    parsed = urlsplit(url.strip())
    host = (parsed.hostname or "").lower()
    if parsed.port:
        host = f"{host}:{parsed.port}"
    path = parsed.path.rstrip("/") or "/"
    scheme = (parsed.scheme or "https").lower()
    return urlunsplit((scheme, host, path, parsed.query, ""))


def _cache_key(url: str, check_id: str) -> tuple[str, str]:
    return (normalize_url(url), check_id)


class CheckResultCache(Protocol):
    def get(self, url: str, check_id: str) -> CheckResult | None: ...

    def put(self, url: str, result: CheckResult) -> None: ...


class InMemoryTTLCache:
    def __init__(self, ttl_s: float = DEFAULT_TTL_S):
        self.ttl_s = ttl_s
        self._store: dict[tuple[str, str], tuple[float, CheckResult]] = {}

    def get(self, url: str, check_id: str) -> CheckResult | None:
        key = _cache_key(url, check_id)
        item = self._store.get(key)
        if item is None:
            return None
        stored_at, result = item
        if time.monotonic() - stored_at > self.ttl_s:
            del self._store[key]
            return None
        return result

    def put(self, url: str, result: CheckResult) -> None:
        if result.status not in CACHEABLE_STATUSES:
            return
        self._store[_cache_key(url, result.id)] = (time.monotonic(), result)
