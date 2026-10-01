import pytest

from app.geo.checks.llm_citability_review import (
    CitabilityReview,
    LlmCitabilityReviewCheck,
)
from app.geo.checks.orphan_page_check import OrphanPageCheck
from app.geo.context import AuditContext
from app.geo.models import CheckStatus


class _Pages:
    def __init__(self, pages: dict[str, str]):
        self.pages = pages

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def get(self, url: str):
        class Response:
            status_code = 200
            text = ""

        response = Response()
        response.text = self.pages.get(url, "")
        return response


def _client_factory(pages: dict[str, str]):
    def factory(*args, **kwargs):
        return _Pages(pages)

    return factory


@pytest.mark.asyncio
async def test_orphan_fails_when_the_audited_page_is_not_linked(monkeypatch):
    monkeypatch.setattr(
        "app.geo.checks.orphan_page_check.httpx.AsyncClient",
        _client_factory({"https://example.com/": "<a href='/about'>About</a>"}),
    )
    ctx = AuditContext(
        url="https://example.com/products/widget",
        final_url="https://example.com/products/widget",
        raw_html="<h1>Widget</h1>",
    )

    async def sitemap():
        return {
            "urls": [
                "https://example.com/products/widget",
                "https://example.com/about",
            ]
        }

    ctx.sitemap = sitemap
    result = await OrphanPageCheck().run(ctx)
    assert result.status == CheckStatus.FAIL
    assert result.evidence["linked_internally"] is False
    assert "https://example.com/products/widget" in result.evidence["orphan_urls"]
    assert result.fix_hint


@pytest.mark.asyncio
async def test_orphan_passes_when_the_page_is_linked(monkeypatch):
    monkeypatch.setattr(
        "app.geo.checks.orphan_page_check.httpx.AsyncClient",
        _client_factory(
            {"https://example.com/": "<a href='/products/widget'>Widget</a>"}
        ),
    )
    ctx = AuditContext(
        url="https://example.com/products/widget",
        final_url="https://example.com/products/widget",
        raw_html="<h1>Widget</h1>",
    )

    async def sitemap():
        return {"urls": ["https://example.com/products/widget"]}

    ctx.sitemap = sitemap
    result = await OrphanPageCheck().run(ctx)
    assert result.status == CheckStatus.PASS
    assert result.evidence["linked_internally"] is True


@pytest.mark.asyncio
async def test_orphan_skips_when_the_sitemap_is_empty():
    ctx = AuditContext(
        url="https://example.com/page", final_url="https://example.com/page"
    )

    async def sitemap():
        return {"urls": []}

    ctx.sitemap = sitemap
    result = await OrphanPageCheck().run(ctx)
    assert result.status == CheckStatus.SKIPPED


@pytest.mark.asyncio
async def test_citability_skips_when_the_api_key_is_missing(monkeypatch):
    monkeypatch.setattr(
        "app.geo.checks.llm_citability_review.make_chat_model",
        lambda _temperature: None,
    )
    ctx = AuditContext(
        url="https://example.com/page",
        raw_html="<title>Widget</title><h1>Widget</h1><p>A short page.</p>",
    )
    result = await LlmCitabilityReviewCheck().run(ctx)
    assert result.status == CheckStatus.SKIPPED
    assert result.evidence["reason"] == "API key not configured"
    assert result.evidence["questions"]


def _rate_limit(retry_after: str | None = None):
    error = Exception("429")
    error.status_code = 429
    if retry_after is not None:
        error.headers = {"retry-after": retry_after}
    return error


class _ScriptedModel:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0

    def with_structured_output(self, _schema):
        return self

    async def ainvoke(self, _prompt):
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def _patch_model(monkeypatch, model):
    monkeypatch.setattr(
        "app.geo.checks.llm_citability_review.make_chat_model",
        lambda temperature: model if temperature == 0 else None,
    )


@pytest.mark.asyncio
async def test_citability_retries_429_then_succeeds(monkeypatch):
    model = _ScriptedModel(
        [
            _rate_limit("0"),
            CitabilityReview(answerable=True, missing_points=[], fix_hint=""),
        ]
    )
    _patch_model(monkeypatch, model)
    result = await LlmCitabilityReviewCheck().run(
        AuditContext(url="https://example.com/page", raw_html="<h1>Widget</h1>")
    )
    assert result.status == CheckStatus.PASS
    assert model.calls == 2


@pytest.mark.asyncio
async def test_citability_skips_when_429_persists(monkeypatch):
    model = _ScriptedModel([_rate_limit("0"), _rate_limit("0")])
    _patch_model(monkeypatch, model)
    result = await LlmCitabilityReviewCheck().run(
        AuditContext(url="https://example.com/page", raw_html="<h1>Widget</h1>")
    )
    assert result.status == CheckStatus.SKIPPED
    assert result.evidence["reason"] == "model rate limited, retry later"
    assert model.calls == 2


@pytest.mark.asyncio
async def test_citability_does_not_retry_when_retry_after_exceeds_timeout(monkeypatch):
    model = _ScriptedModel([_rate_limit("30")])
    _patch_model(monkeypatch, model)
    result = await LlmCitabilityReviewCheck().run(
        AuditContext(url="https://example.com/page", raw_html="<h1>Widget</h1>")
    )
    assert result.status == CheckStatus.SKIPPED
    assert result.evidence["reason"] == "model rate limited, retry later"
    assert model.calls == 1


@pytest.mark.asyncio
async def test_citability_passes_structured_output(monkeypatch):
    class Model:
        def with_structured_output(self, _schema):
            return self

        async def ainvoke(self, _prompt):
            return CitabilityReview(answerable=True, missing_points=[], fix_hint="")

    monkeypatch.setattr(
        "app.geo.checks.llm_citability_review.make_chat_model",
        lambda _temperature: Model(),
    )
    ctx = AuditContext(
        url="https://example.com/page",
        uncited_prompts=["What is Widget?"],
        rendered_text="Widget is a product for teams.",
    )
    result = await LlmCitabilityReviewCheck().run(ctx)
    assert result.status == CheckStatus.PASS
    assert result.evidence["questions"] == ["What is Widget?"]
