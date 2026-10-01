"""In-memory deep-check jobs. Results publish as each check finishes."""

import asyncio
import uuid

from .cache import InMemoryTTLCache, normalize_url
from .context import AuditContext
from .models import CheckResult
from .registry import checks_for_tier, run_check, run_checks

cache = InMemoryTTLCache()
_jobs: dict[str, dict] = {}
_inflight: dict[str, str] = {}
_tasks: set[asyncio.Task] = set()


def get_job(job_id: str) -> dict | None:
    job = _jobs.get(job_id)
    if job is None:
        return None
    return {
        "id": job["id"],
        "status": job["status"],
        "checks": [item.model_dump(mode="json") for item in job["checks"]],
    }


def reset_jobs() -> None:
    _jobs.clear()
    _inflight.clear()
    cache._store.clear()


def _dump(results: list[CheckResult]) -> list[dict]:
    return [item.model_dump(mode="json") for item in results]


async def attach_geo(ctx: AuditContext) -> dict:
    key = normalize_url(ctx.url)
    existing_id = _inflight.get(key)
    if existing_id and existing_id in _jobs:
        fast = _jobs[existing_id]["fast"]
        return {
            "geo_checks": _dump(fast),
            "geo_job_id": existing_id,
        }

    fast_checks = checks_for_tier("fast")
    deep_checks = checks_for_tier("deep")
    cached_fast = _take_cached(ctx.url, fast_checks)
    cached_deep = _take_cached(ctx.url, deep_checks)
    missing_fast = [check for check in fast_checks if check.id not in cached_fast]
    missing_deep = [check for check in deep_checks if check.id not in cached_deep]

    fresh_fast = await run_checks(missing_fast, ctx)
    for result in fresh_fast:
        cache.put(ctx.url, result)
    fresh_by_id = {result.id: result for result in fresh_fast}
    ordered_fast = [
        cached_fast[check.id] if check.id in cached_fast else fresh_by_id[check.id]
        for check in fast_checks
    ]
    ordered_deep = [
        cached_deep[check.id] for check in deep_checks if check.id in cached_deep
    ]

    if not missing_deep:
        return {
            "geo_checks": _dump(ordered_fast + ordered_deep),
            "geo_job_id": None,
        }

    job_id = schedule_deep(ctx, ordered_fast, missing_deep)
    return {
        "geo_checks": _dump(ordered_fast + ordered_deep),
        "geo_job_id": job_id,
    }


def _take_cached(url: str, checks: list) -> dict[str, CheckResult]:
    found: dict[str, CheckResult] = {}
    for check in checks:
        hit = cache.get(url, check.id)
        if hit is not None:
            found[check.id] = hit
    return found


def schedule_deep(
    ctx: AuditContext,
    fast: list[CheckResult],
    deep: list | None = None,
) -> str | None:
    if deep is None:
        deep = checks_for_tier("deep")
    if not deep:
        return None
    job_id = str(uuid.uuid4())
    job = {
        "id": job_id,
        "status": "running",
        "checks": [],
        "fast": list(fast),
    }
    _jobs[job_id] = job
    key = normalize_url(ctx.url)
    _inflight[key] = job_id

    async def runner() -> None:
        try:
            tasks = [asyncio.create_task(run_check(check, ctx)) for check in deep]
            for finished in asyncio.as_completed(tasks):
                result = await finished
                job["checks"].append(result)
                cache.put(ctx.url, result)
            job["status"] = "done"
        finally:
            if _inflight.get(key) == job_id:
                _inflight.pop(key, None)

    task = asyncio.create_task(runner())
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)
    return job_id
