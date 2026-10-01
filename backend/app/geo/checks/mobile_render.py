"""Optional phone render in the audit's existing browser."""

import asyncio

from bs4 import BeautifulSoup
from pydantic import BaseModel

from ..base import GeoCheck
from ..config import (
    MOBILE_MAIN_TEXT_RATIO_FAIL,
    MOBILE_MAIN_TEXT_RATIO_WARN,
    MOBILE_RENDER_CONCURRENCY,
    MOBILE_RENDER_TIMEOUT_S,
    MOBILE_USER_AGENT,
)
from ..context import AuditContext
from ..models import CheckStatus
from .bot_view_diff import _words

_slots = asyncio.Semaphore(MOBILE_RENDER_CONCURRENCY)
_VIEWPORT = {"width": 390, "height": 844}
_HEAVY = {"image", "font", "media"}
_OVERLAY_JS = """
() => {
  const el = document.elementFromPoint(window.innerWidth / 2, window.innerHeight / 2);
  if (!el || el === document.body || el === document.documentElement) {
    return { overlay: false, tag: "", selector: "" };
  }
  const style = getComputedStyle(el);
  const rect = el.getBoundingClientRect();
  const area = Math.max(window.innerWidth * window.innerHeight, 1);
  const cover = (rect.width * rect.height) / area;
  const sticky = style.position === "fixed" || style.position === "sticky";
  let selector = el.tagName.toLowerCase();
  if (el.id) selector += "#" + String(el.id).slice(0, 40);
  else if (typeof el.className === "string" && el.className.trim()) {
    selector += "." + el.className.trim().split(/\\s+/).slice(0, 2).join(".");
  }
  return {
    overlay: sticky && cover >= 0.5,
    tag: el.tagName.toLowerCase(),
    selector: selector.slice(0, 80),
  };
}
"""


class MobileRenderEvidence(BaseModel):
    main_text_ratio: float | None = None
    overlay: bool = False
    overlay_tag: str = ""
    overlay_selector: str = ""


class MobileRenderCheck(GeoCheck):
    id = "mobile_render"
    name = "Mobile rendered content"
    tier = "deep"
    timeout_s = MOBILE_RENDER_TIMEOUT_S
    evidence_model = MobileRenderEvidence
    needs_browser = True

    async def run(self, ctx: AuditContext):
        if ctx.browser is None:
            return self.finish(
                CheckStatus.SKIPPED,
                MobileRenderEvidence(),
                "Mobile rendering was skipped because the audit browser was already closed.",
            )
        async with _slots:
            context = await ctx.browser.new_context(
                user_agent=MOBILE_USER_AGENT,
                viewport=_VIEWPORT,
            )
            try:
                page = await context.new_page()
                await page.route("**/*", _drop_heavy)
                await page.goto(
                    ctx.final_url or ctx.url,
                    wait_until="load",
                    timeout=int(self.timeout_s * 1000),
                )
                rendered = BeautifulSoup(await page.content(), "html.parser").get_text()
                overlay = await page.evaluate(_OVERLAY_JS) or {}
            finally:
                await context.close()
        evidence = _evidence(ctx.rendered_text or "", rendered, overlay)
        if evidence.overlay or _ratio_below(evidence, MOBILE_MAIN_TEXT_RATIO_FAIL):
            hint = (
                "Remove or delay interstitials that cover the page."
                if evidence.overlay
                else "Serve the same main content to mobile visitors."
            )
            return self.finish(CheckStatus.FAIL, evidence, hint)
        if _ratio_below(evidence, MOBILE_MAIN_TEXT_RATIO_WARN):
            return self.finish(
                CheckStatus.WARN,
                evidence,
                "Serve the same main content to mobile visitors.",
            )
        return self.finish(CheckStatus.PASS, evidence, "")


def _ratio_below(evidence: MobileRenderEvidence, limit: float) -> bool:
    return evidence.main_text_ratio is not None and evidence.main_text_ratio < limit


def _evidence(
    desktop_text: str, mobile_text: str, overlay: dict
) -> MobileRenderEvidence:
    desktop_words = len(_words(desktop_text))
    ratio = None
    if desktop_words:
        ratio = round(len(_words(mobile_text)) / desktop_words, 3)
    return MobileRenderEvidence(
        main_text_ratio=ratio,
        overlay=bool(overlay.get("overlay")),
        overlay_tag=str(overlay.get("tag") or ""),
        overlay_selector=str(overlay.get("selector") or ""),
    )


async def _drop_heavy(route) -> None:
    if route.request.resource_type in _HEAVY:
        await route.abort()
        return
    await route.continue_()
