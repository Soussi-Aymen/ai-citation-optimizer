"""In-memory deep-check jobs. Results publish as each check finishes."""

import asyncio
import uuid

from .cache import InMemoryTTLCache, normalize_url
from .context import AuditContext
from .models import CheckResult
from .registry import checks_for_tier, run_check, run_tier

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


async def attach_geo(ctx: AuditContext) -> dict:
    cached = cache.get(ctx.url)
    if cached is not None:
        return {
            "geo_checks": [item.model_dump(mode="json") for item in cached],
            "geo_job_id": None,
        }

    key = normalize_url(ctx.url)
    existing_id = _inflight.get(key)
    if existing_id and existing_id in _jobs:
        fast = _jobs[existing_id]["fast"]
        return {
            "geo_checks": [item.model_dump(mode="json") for item in fast],
            "geo_job_id": existing_id,
        }

    fast = await run_tier(ctx, "fast")
    job_id = schedule_deep(ctx, fast)
    return {
        "geo_checks": [item.model_dump(mode="json") for item in fast],
        "geo_job_id": job_id,
    }


def schedule_deep(ctx: AuditContext, fast: list[CheckResult]) -> str | None:
    deep = checks_for_tier("deep")
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
            if not deep:
                cache.set(ctx.url, list(fast))
                job["status"] = "done"
                return
            tasks = [asyncio.create_task(run_check(check, ctx)) for check in deep]
            for finished in asyncio.as_completed(tasks):
                job["checks"].append(await finished)
            cache.set(ctx.url, list(fast) + list(job["checks"]))
            job["status"] = "done"
        finally:
            if _inflight.get(key) == job_id:
                _inflight.pop(key, None)

    task = asyncio.create_task(runner())
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)
    return job_id
