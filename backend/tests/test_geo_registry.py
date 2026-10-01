import asyncio
import time

import pytest
from pydantic import BaseModel

from app.geo.base import GeoCheck
from app.geo.cache import InMemoryTTLCache, normalize_url
from app.geo.context import AuditContext
from app.geo.models import CheckResult, CheckStatus
from app.geo.registry import run_checks


class EmptyEvidence(BaseModel):
    note: str = ""


class SleepCheck(GeoCheck):
    evidence_model = EmptyEvidence

    def __init__(self, check_id: str, delay: float, timeout_s: float = 2):
        self.id = check_id
        self.name = check_id
        self.tier = "fast"
        self.timeout_s = timeout_s
        self.delay = delay

    async def run(self, ctx: AuditContext):
        await asyncio.sleep(self.delay)
        return self.finish(CheckStatus.PASS, EmptyEvidence(note=ctx.url), "ok")


class BoomCheck(GeoCheck):
    id = "boom"
    name = "Boom"
    tier = "fast"
    timeout_s = 2
    evidence_model = EmptyEvidence

    async def run(self, ctx: AuditContext):
        raise RuntimeError("broken")


@pytest.mark.asyncio
async def test_checks_run_in_parallel():
    ctx = AuditContext(url="https://example.com/page")
    started = time.monotonic()
    results = await run_checks(
        [SleepCheck("a", 0.3), SleepCheck("b", 0.3)],
        ctx,
    )
    elapsed = time.monotonic() - started
    assert elapsed < 0.5
    assert [item.status for item in results] == [CheckStatus.PASS, CheckStatus.PASS]


@pytest.mark.asyncio
async def test_timeout_does_not_fail_other_checks():
    ctx = AuditContext(url="https://example.com/page")
    results = await run_checks(
        [SleepCheck("slow", 0.4, timeout_s=0.05), SleepCheck("ok", 0.01)],
        ctx,
    )
    assert results[0].status == CheckStatus.SKIPPED
    assert results[0].evidence["reason"] == "timeout"
    assert results[1].status == CheckStatus.PASS


@pytest.mark.asyncio
async def test_error_does_not_fail_other_checks():
    ctx = AuditContext(url="https://example.com/page")
    results = await run_checks([BoomCheck(), SleepCheck("ok", 0.01)], ctx)
    assert results[0].status == CheckStatus.ERROR
    assert "broken" in results[0].evidence["reason"]
    assert results[1].status == CheckStatus.PASS


def test_cache_hit_miss_and_ttl():
    cache = InMemoryTTLCache(ttl_s=0.05)
    assert cache.get("https://Example.com/a/") is None
    result = CheckResult(
        id="x",
        name="X",
        tier="fast",
        status=CheckStatus.PASS,
        evidence={},
        fix_hint="hint",
    )
    cache.set("https://Example.com/a/", [result])
    cached = cache.get("https://example.com/a")
    assert cached is not None
    assert cached[0].id == "x"
    time.sleep(0.06)
    assert cache.get("https://example.com/a") is None


def test_normalize_url_drops_fragment_and_trailing_slash():
    assert (
        normalize_url("HTTPS://Example.COM/path/#section") == "https://example.com/path"
    )
