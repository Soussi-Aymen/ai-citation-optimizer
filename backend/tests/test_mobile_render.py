import asyncio
import time

import pytest
from playwright.async_api import async_playwright

from app.agent import CrawlabilityAgent
from app.geo.checks.mobile_parity import MobileParityCheck
from app.geo.checks.mobile_render import MobileRenderCheck, _drop_heavy
from app.geo.config import assert_browser_hold
from app.geo.context import AuditContext
from app.geo.models import CheckResult, CheckStatus


def _words(count: int) -> str:
    return " ".join(f"word{index}" for index in range(count))


class _Route:
    def __init__(self, resource_type: str):
        self.request = type("Req", (), {"resource_type": resource_type})()
        self.aborted = False
        self.continued = False

    async def abort(self):
        self.aborted = True

    async def continue_(self):
        self.continued = True


class _Page:
    def __init__(self, html: str, overlay: dict):
        self.html = html
        self.overlay = overlay
        self.handler = None

    async def route(self, pattern, handler):
        self.handler = handler

    async def goto(self, url, **kwargs):
        return None

    async def content(self):
        return self.html

    async def evaluate(self, script):
        return self.overlay


class _Context:
    def __init__(self, page: _Page):
        self.page = page
        self.closed = False

    async def new_page(self):
        return self.page

    async def close(self):
        self.closed = True


class _Browser:
    def __init__(self, page: _Page | None = None):
        self.page = page or _Page("<html><body></body></html>", {})
        self.kwargs = None
        self.closed = False
        self.launch_calls = 0

    async def new_context(self, **kwargs):
        self.kwargs = kwargs
        return _Context(self.page)

    async def close(self):
        self.closed = True

    async def launch(self):
        self.launch_calls += 1


def _ctx(desktop_words: int, browser=None) -> AuditContext:
    return AuditContext(
        url="https://example.com/page",
        final_url="https://example.com/page",
        rendered_text=_words(desktop_words),
        browser=browser,
    )


@pytest.mark.asyncio
async def test_overlay_fail_records_tag_and_selector():
    page = _Page(
        f"<html><body><p>{_words(40)}</p></body></html>",
        {"overlay": True, "tag": "div", "selector": "div.modal"},
    )
    browser = _Browser(page)
    result = await MobileRenderCheck().run(_ctx(40, browser))
    assert result.status == CheckStatus.FAIL
    assert result.evidence["overlay"] is True
    assert result.evidence["overlay_tag"] == "div"
    assert result.evidence["overlay_selector"] == "div.modal"
    assert browser.launch_calls == 0
    assert browser.kwargs["viewport"]["width"] == 390


@pytest.mark.asyncio
async def test_thin_rendered_text_fails_on_ratio():
    page = _Page(f"<html><body><p>{_words(5)}</p></body></html>", {"overlay": False})
    result = await MobileRenderCheck().run(_ctx(40, _Browser(page)))
    assert result.status == CheckStatus.FAIL
    assert result.evidence["main_text_ratio"] < 0.5


@pytest.mark.asyncio
async def test_missing_browser_skips():
    result = await MobileRenderCheck().run(_ctx(10, None))
    assert result.status == CheckStatus.SKIPPED


@pytest.mark.asyncio
async def test_image_requests_are_aborted():
    image = _Route("image")
    document = _Route("document")
    await _drop_heavy(image)
    await _drop_heavy(document)
    assert image.aborted is True
    assert document.continued is True


def test_short_browser_hold_is_rejected():
    with pytest.raises(ValueError):
        assert_browser_hold(10, 12, 8)
    assert_browser_hold()


@pytest.mark.asyncio
async def test_stuck_render_closes_the_browser_and_returns(monkeypatch):
    async def fail_parity(self, ctx):
        return CheckResult(
            id="mobile_parity",
            name="Mobile content parity",
            tier="fast",
            status=CheckStatus.FAIL,
            evidence={},
            fix_hint="",
        )

    async def stuck(self, ctx):
        await asyncio.sleep(30)

    monkeypatch.setattr(MobileParityCheck, "run", fail_parity)
    monkeypatch.setattr(MobileRenderCheck, "run", stuck)
    monkeypatch.setattr("app.agent.BROWSER_MAX_HOLD_S", 0.2)
    browser = _Browser()
    started = time.monotonic()
    await CrawlabilityAgent()._maybe_mobile_render(browser, _ctx(10, None))
    assert browser.closed is True
    assert time.monotonic() - started < 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_phone_context_uses_the_open_browser():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        try:
            ctx = AuditContext(
                url="about:blank",
                final_url="about:blank",
                rendered_text="about blank",
                browser=browser,
            )
            result = await MobileRenderCheck().run(ctx)
            assert result.status in {
                CheckStatus.PASS,
                CheckStatus.WARN,
                CheckStatus.FAIL,
            }
        finally:
            await browser.close()
