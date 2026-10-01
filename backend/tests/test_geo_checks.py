import asyncio
from unittest.mock import patch

import pytest

from app.geo.checks.ai_bot_access import AiBotAccessCheck
from app.geo.checks.answer_readiness import AnswerReadinessCheck
from app.geo.checks.canonical_and_redirects import CanonicalAndRedirectsCheck
from app.geo.checks.freshness_consistency import FreshnessConsistencyCheck
from app.geo.checks.schema_validation import SchemaValidationCheck
from app.geo.context import AuditContext
from app.geo.models import CheckStatus
from app.geo.registry import run_checks

PAGE = "https://example.com/guides/topic"


class _Response:
    def __init__(self, status, text):
        self.status_code = status
        self.text = text


class _Client:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def get(self, url, headers=None):
        agent = (headers or {}).get("User-Agent", "")
        if "GPTBot" in agent:
            return _Response(403, "")
        if "ClaudeBot" in agent:
            return _Response(200, "word")
        return _Response(200, "<html><body>" + ("content " * 80) + "</body></html>")


def _ctx(**kwargs) -> AuditContext:
    ctx = AuditContext(url=PAGE, final_url=PAGE, **kwargs)
    ctx._robots_loaded = True
    ctx._sitemap = {"urls": [], "entries": [], "metrics": {}}
    return ctx


@pytest.mark.asyncio
async def test_blocked_bot_fails():
    with patch("app.geo.checks.ai_bot_access.httpx.AsyncClient", _Client):
        result = await AiBotAccessCheck().run(
            _ctx(raw_html="<html></html>", headers={})
        )
    assert result.status == CheckStatus.FAIL
    assert "GPTBot" in result.evidence["blocked_agents"]
    assert "ClaudeBot" in result.evidence["thin_agents"]


@pytest.mark.asyncio
async def test_empty_html_answer_readiness_fails():
    result = await AnswerReadinessCheck().run(_ctx(raw_html="   "))
    assert result.status == CheckStatus.FAIL
    assert result.fix_hint


@pytest.mark.asyncio
async def test_malformed_json_ld_fails():
    html = '<html><script type="application/ld+json">{not json}</script></html>'
    result = await SchemaValidationCheck().run(_ctx(raw_html=html))
    assert result.status == CheckStatus.FAIL
    assert result.evidence["malformed"] is True


@pytest.mark.asyncio
async def test_valid_json_ld_passes_expected_type():
    html = """
    <html><script type="application/ld+json">
    {"@type":"WebPage","author":{"@type":"Person","name":"Ada"},
     "datePublished":"2026-01-01","dateModified":"2026-06-01",
     "sameAs":["https://example.com/about"]}
    </script></html>
    """
    result = await SchemaValidationCheck().run(_ctx(raw_html=html))
    assert result.status == CheckStatus.PASS
    assert result.evidence["has_expected_type"] is True


@pytest.mark.asyncio
async def test_missing_dates_warn():
    result = await FreshnessConsistencyCheck().run(
        _ctx(raw_html="<html></html>", headers={})
    )
    assert result.status == CheckStatus.FAIL
    assert "dateModified" in result.evidence["missing"]


@pytest.mark.asyncio
async def test_canonical_mismatch_fails():
    html = '<html><head><link rel="canonical" href="https://example.com/other"></head></html>'
    result = await CanonicalAndRedirectsCheck().run(
        _ctx(raw_html=html, redirect_chain=[PAGE])
    )
    assert result.status == CheckStatus.FAIL
    assert result.evidence["canonical_mismatch"] is True


@pytest.mark.asyncio
async def test_check_timeout_is_skipped_by_runner():
    check = AiBotAccessCheck()
    check.timeout_s = 0.01

    class _Slow(_Client):
        async def get(self, url, headers=None):
            await asyncio.sleep(0.2)
            return _Response(200, "ok")

    with patch("app.geo.checks.ai_bot_access.httpx.AsyncClient", _Slow):
        results = await run_checks([check], _ctx(raw_html="<html></html>"))
    assert results[0].status == CheckStatus.SKIPPED
    assert results[0].evidence["reason"] == "timeout"
