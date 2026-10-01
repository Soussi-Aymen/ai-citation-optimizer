import asyncio
import time

import pytest

from app.geo.checks.llms_txt import LlmsTxtCheck
from app.geo.context import AuditContext
from app.geo.models import CheckStatus


async def _hang(self):
    await asyncio.sleep(30)
    return {}


@pytest.mark.asyncio
async def test_early_fetches_overlap_the_slow_browser_step(monkeypatch):
    async def slow_llms(self):
        await asyncio.sleep(0.4)
        return {
            "has_llms_txt": False,
            "llms_txt_valid": False,
            "llms_txt_lists_page": False,
            "llms_txt_link_count": 0,
            "llms_txt_url": None,
        }

    async def slow_robots(self):
        await asyncio.sleep(0.3)
        return ""

    monkeypatch.setattr(AuditContext, "_load_llms", slow_llms)
    monkeypatch.setattr(AuditContext, "_load_robots", slow_robots)
    started = time.monotonic()
    ctx = AuditContext(
        url="https://example.com/page", final_url="https://example.com/page"
    )
    async with ctx:
        await asyncio.sleep(0.5)
        await ctx.llms_txt()
        await ctx.robots_txt()
    assert time.monotonic() - started < 0.75


@pytest.mark.asyncio
async def test_failed_audit_closes_tasks_and_the_client(monkeypatch):
    monkeypatch.setattr(AuditContext, "_load_llms", _hang)
    monkeypatch.setattr(AuditContext, "_load_robots", _hang)
    ctx = AuditContext(
        url="https://example.com/page", final_url="https://example.com/page"
    )
    with pytest.raises(RuntimeError, match="mid-audit"):
        async with ctx:
            raise RuntimeError("mid-audit")
    assert ctx._client is not None
    assert ctx._client.is_closed
    assert ctx._early_tasks
    assert all(task.done() for task in ctx._early_tasks)


@pytest.mark.asyncio
async def test_llms_check_uses_the_context_probe():
    ctx = AuditContext(url="https://example.com/page")

    async def fake():
        return {
            "has_llms_txt": True,
            "llms_txt_valid": True,
            "llms_txt_lists_page": False,
            "llms_txt_link_count": 2,
            "llms_txt_url": "https://example.com/llms.txt",
        }

    ctx.llms_txt = fake
    result = await LlmsTxtCheck().run(ctx)
    assert result.status == CheckStatus.WARN
    assert result.evidence["llms_txt_link_count"] == 2
