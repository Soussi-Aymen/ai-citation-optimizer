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
    assert result.evidence["reason"] == "missing_api_key"
    assert result.evidence["questions"]


@pytest.mark.asyncio
async def test_citability_skips_on_rate_limit_without_retry(monkeypatch):
    calls = {"n": 0}

    class RateLimited:
        def with_structured_output(self, _schema):
            return self

        async def ainvoke(self, _prompt):
            calls["n"] += 1
            error = Exception("429")
            error.status_code = 429
            raise error

    monkeypatch.setattr(
        "app.geo.checks.llm_citability_review.make_chat_model",
        lambda _temperature: RateLimited(),
    )
    ctx = AuditContext(url="https://example.com/page", raw_html="<h1>Widget</h1>")
    result = await LlmCitabilityReviewCheck().run(ctx)
    assert result.status == CheckStatus.SKIPPED
    assert result.evidence["reason"] == "rate_limited"
    assert calls["n"] == 1


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
