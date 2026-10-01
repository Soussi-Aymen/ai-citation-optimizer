import asyncio

import pytest
from pydantic import BaseModel

from app.geo import jobs as jobs_module
from app.geo.base import GeoCheck
from app.geo.context import AuditContext
from app.geo.jobs import attach_geo, cache, get_job, reset_jobs, schedule_deep
from app.geo.models import CheckResult, CheckStatus
from app.geo.prompts import extract_uncited_prompts


class _Evidence(BaseModel):
    n: int = 1


class QuickCheck(GeoCheck):
    id = "quick"
    name = "Quick"
    tier = "deep"
    timeout_s = 1
    evidence_model = _Evidence

    async def run(self, ctx: AuditContext):
        return self.finish(CheckStatus.PASS, _Evidence(), "")


class SlowCheck(GeoCheck):
    id = "slow"
    name = "Slow"
    tier = "deep"
    timeout_s = 2
    evidence_model = _Evidence

    async def run(self, ctx: AuditContext):
        await asyncio.sleep(0.3)
        return self.finish(CheckStatus.PASS, _Evidence(), "")


def test_extract_uncited_prompts_ignores_cited_and_empty():
    assert extract_uncited_prompts(None) is None
    assert extract_uncited_prompts({"data": []}) is None
    prompts = extract_uncited_prompts(
        {
            "data": [
                {"prompt": "cited question", "cited": True},
                {"prompt": "missing citation", "cited": False},
                {"uncited_prompts": ["plain prompt"]},
            ]
        }
    )
    assert prompts == ["missing citation", "plain prompt"]


class CountingCheck(GeoCheck):
    evidence_model = _Evidence

    def __init__(self, check_id: str, tier: str, status: CheckStatus):
        self.id = check_id
        self.name = check_id
        self.tier = tier
        self.timeout_s = 1
        self.status = status
        self.calls = 0

    async def run(self, ctx: AuditContext):
        self.calls += 1
        return self.finish(self.status, _Evidence(), "")


def _tiers(fast: list, deep: list):
    def checks_for_tier(tier: str):
        return fast if tier == "fast" else deep

    return checks_for_tier


@pytest.mark.asyncio
async def test_cache_hit_returns_fast_and_deep_without_a_job(monkeypatch):
    reset_jobs()
    fast = CountingCheck("fast_ok", "fast", CheckStatus.PASS)
    deep = CountingCheck("deep_ok", "deep", CheckStatus.PASS)
    monkeypatch.setattr("app.geo.jobs.checks_for_tier", _tiers([fast], [deep]))
    cache.put(
        "https://example.com/page",
        CheckResult(id="fast_ok", name="fast_ok", tier="fast", status=CheckStatus.PASS),
    )
    cache.put(
        "https://example.com/page",
        CheckResult(id="deep_ok", name="deep_ok", tier="deep", status=CheckStatus.PASS),
    )
    payload = await attach_geo(AuditContext(url="https://example.com/page"))
    assert payload["geo_job_id"] is None
    assert {item["id"] for item in payload["geo_checks"]} == {"fast_ok", "deep_ok"}
    assert fast.calls == 0
    assert deep.calls == 0


@pytest.mark.asyncio
async def test_skipped_deep_check_is_rerun_and_pass_fast_is_not(monkeypatch):
    reset_jobs()
    fast = CountingCheck("fast_ok", "fast", CheckStatus.PASS)
    cite = CountingCheck("llm_citability_review", "deep", CheckStatus.SKIPPED)
    monkeypatch.setattr("app.geo.jobs.checks_for_tier", _tiers([fast], [cite]))
    first = await attach_geo(AuditContext(url="https://example.com/page"))
    assert first["geo_job_id"] is not None
    for _ in range(30):
        job = get_job(first["geo_job_id"])
        if job and job["status"] == "done":
            break
        await asyncio.sleep(0.02)
    assert cite.calls == 1
    assert cache.get("https://example.com/page", "fast_ok") is not None
    assert cache.get("https://example.com/page", "llm_citability_review") is None

    second = await attach_geo(AuditContext(url="https://example.com/page"))
    assert second["geo_job_id"] is not None
    for _ in range(30):
        job = get_job(second["geo_job_id"])
        if job and job["status"] == "done":
            break
        await asyncio.sleep(0.02)
    assert fast.calls == 1
    assert cite.calls == 2


@pytest.mark.asyncio
async def test_missing_deep_check_is_the_only_job(monkeypatch):
    reset_jobs()
    fast = CountingCheck("fast_ok", "fast", CheckStatus.PASS)
    deep = CountingCheck("deep_ok", "deep", CheckStatus.PASS)
    monkeypatch.setattr("app.geo.jobs.checks_for_tier", _tiers([fast], [deep]))
    cache.put(
        "https://example.com/page",
        CheckResult(id="fast_ok", name="fast_ok", tier="fast", status=CheckStatus.PASS),
    )
    payload = await attach_geo(AuditContext(url="https://example.com/page"))
    assert payload["geo_job_id"] is not None
    assert fast.calls == 0
    assert {item["id"] for item in payload["geo_checks"]} == {"fast_ok"}
    for _ in range(30):
        job = get_job(payload["geo_job_id"])
        if job and job["status"] == "done":
            break
        await asyncio.sleep(0.02)
    assert deep.calls == 1
    assert {item["id"] for item in job["checks"]} == {"deep_ok"}


@pytest.mark.asyncio
async def test_deep_job_publishes_the_fast_check_before_the_slow_one(monkeypatch):
    reset_jobs()
    monkeypatch.setattr(
        "app.geo.jobs.checks_for_tier",
        lambda tier: [QuickCheck(), SlowCheck()] if tier == "deep" else [],
    )
    job_id = schedule_deep(AuditContext(url="https://example.com/deep"), [])
    assert job_id is not None

    partial = None
    for _ in range(20):
        job = get_job(job_id)
        assert job is not None
        if job["checks"] and job["status"] == "running":
            partial = job
            break
        await asyncio.sleep(0.02)
    assert partial is not None
    assert partial["checks"][0]["id"] == "quick"

    for _ in range(30):
        job = get_job(job_id)
        if job and job["status"] == "done":
            break
        await asyncio.sleep(0.05)
    assert job is not None
    assert job["status"] == "done"
    assert {item["id"] for item in job["checks"]} == {"quick", "slow"}


@pytest.mark.asyncio
async def test_audit_response_includes_geo_fields(
    client, mock_peec_unavailable, mock_agent
):
    mock_agent.audit_url.return_value = {
        "signals": {},
        "geo_checks": [{"id": "ai_bot_access", "status": "pass"}],
        "geo_job_id": "job-1",
    }
    response = await client.post("/api/audit", json={"url": "https://example.com/page"})
    assert response.status_code == 200
    body = response.json()
    assert body["geo_job_id"] == "job-1"
    assert body["geo_checks"][0]["id"] == "ai_bot_access"
    assert body["analysis"]["signals"] == {}


@pytest.mark.asyncio
async def test_generate_fix_appends_fail_and_warn_hints(
    client, mock_peec_unavailable, mock_agent
):
    mock_agent.fetch_and_analyze.return_value = {
        "signals": {"js_impact": "LOW"},
        "guidance": [],
        "geo_job_id": "job-2",
        "geo_checks": [
            {"status": "fail", "fix_hint": "Allow GPTBot in robots.txt"},
            {"status": "warn", "fix_hint": "Shorten the redirect chain"},
            {"status": "pass", "fix_hint": "Already fine"},
        ],
    }
    response = await client.post(
        "/api/generate-fix",
        json={"url": "https://example.com/products/widget"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["checklist"] == [
        "Step 1",
        "Allow GPTBot in robots.txt",
        "Shorten the redirect chain",
    ]
    assert data["geo_job_id"] == "job-2"


@pytest.mark.asyncio
async def test_geo_job_missing_is_404(client):
    response = await client.get("/api/geo-jobs/does-not-exist")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_geo_job_returns_stored_partial_results(client):
    reset_jobs()
    jobs_module._jobs["abc"] = {
        "id": "abc",
        "status": "running",
        "checks": [],
        "fast": [],
    }
    response = await client.get("/api/geo-jobs/abc")
    assert response.status_code == 200
    assert response.json() == {"id": "abc", "status": "running", "checks": []}
