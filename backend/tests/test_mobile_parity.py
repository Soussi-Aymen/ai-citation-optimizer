import pytest

from app.geo.checks.mobile_parity import MobileParityCheck
from app.geo.context import AuditContext
from app.geo.models import CheckStatus


def _page(title: str, h1: str, words: int, viewport: bool = True) -> str:
    meta = '<meta name="viewport" content="width=device-width, initial-scale=1">'
    if not viewport:
        meta = ""
    body = " ".join(f"word{index}" for index in range(words))
    return (
        "<html><head><title>"
        + title
        + "</title>"
        + meta
        + '<script type="application/ld+json">{"@type":"WebPage"}</script>'
        + "</head><body><main><h1>"
        + h1
        + "</h1><p>"
        + body
        + "</p></main></body></html>"
    )


def _ctx(
    desktop: str, mobile: str, mobile_url: str = "https://example.com/page"
) -> AuditContext:
    ctx = AuditContext(
        url="https://example.com/page",
        final_url="https://example.com/page",
        raw_html=desktop,
        mobile_html=mobile,
        mobile_status=200,
        mobile_final_url=mobile_url,
    )

    async def ready():
        return None

    ctx.mobile_page = ready
    return ctx


@pytest.mark.asyncio
async def test_identical_pages_pass():
    html = _page("Widget", "Widget", 40)
    result = await MobileParityCheck().run(_ctx(html, html))
    assert result.status == CheckStatus.PASS
    assert result.evidence["main_text_ratio"] == 1.0


@pytest.mark.asyncio
async def test_thin_mobile_page_fails():
    result = await MobileParityCheck().run(
        _ctx(_page("Widget", "Widget", 40), _page("Widget", "Widget", 5))
    )
    assert result.status == CheckStatus.FAIL
    assert result.evidence["main_text_ratio"] < 0.5


@pytest.mark.asyncio
async def test_different_h1_fails():
    result = await MobileParityCheck().run(
        _ctx(_page("Widget", "Widget", 40), _page("Widget", "Other", 40))
    )
    assert result.status == CheckStatus.FAIL
    assert result.evidence["h1_match"] is False


@pytest.mark.asyncio
async def test_mobile_host_redirect_fails():
    html = _page("Widget", "Widget", 40)
    result = await MobileParityCheck().run(
        _ctx(html, html, mobile_url="https://m.example.com/page")
    )
    assert result.status == CheckStatus.FAIL
    assert result.evidence["final_host_differs"] is True


@pytest.mark.asyncio
async def test_missing_viewport_warns():
    result = await MobileParityCheck().run(
        _ctx(
            _page("Widget", "Widget", 40), _page("Widget", "Widget", 40, viewport=False)
        )
    )
    assert result.status == CheckStatus.WARN
    assert result.evidence["viewport_present"] is False


@pytest.mark.asyncio
async def test_mobile_fetch_timeout_skips():
    ctx = _ctx(_page("Widget", "Widget", 10), "")
    ctx.mobile_status = None
    ctx.mobile_fetch_error = "TimeoutException"
    result = await MobileParityCheck().run(ctx)
    assert result.status == CheckStatus.SKIPPED
