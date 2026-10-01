"""Compare the desktop raw fetch with one smartphone fetch."""

from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup
from pydantic import BaseModel

from ..base import GeoCheck
from ..config import MOBILE_MAIN_TEXT_RATIO_FAIL, MOBILE_MAIN_TEXT_RATIO_WARN
from ..context import AuditContext
from ..models import CheckStatus
from .bot_view_diff import _text, _words


class MobileParityEvidence(BaseModel):
    title_match: bool = True
    h1_match: bool = True
    main_text_ratio: float | None = None
    json_ld_match: bool = True
    final_host_differs: bool = False
    viewport_present: bool = True
    alternate_mismatch: bool = False


class MobileParityCheck(GeoCheck):
    id = "mobile_parity"
    name = "Mobile content parity"
    tier = "fast"
    timeout_s = 8
    evidence_model = MobileParityEvidence

    async def run(self, ctx: AuditContext):
        await ctx.mobile_page()
        if ctx.mobile_fetch_error or ctx.mobile_status is None:
            return self.finish(
                CheckStatus.SKIPPED,
                MobileParityEvidence(),
                "The smartphone fetch did not finish, so mobile parity was skipped.",
            )
        desktop = BeautifulSoup(ctx.raw_html or "", "html.parser")
        mobile = BeautifulSoup(ctx.mobile_html or "", "html.parser")
        evidence = _compare(ctx, desktop, mobile)
        if (
            evidence.final_host_differs
            or not evidence.h1_match
            or _below_fail(evidence)
        ):
            return self.finish(
                CheckStatus.FAIL,
                evidence,
                "Serve the same main content to mobile visitors, including the H1.",
            )
        if (
            not evidence.title_match
            or not evidence.json_ld_match
            or not evidence.viewport_present
            or evidence.alternate_mismatch
            or _below_warn(evidence)
        ):
            return self.finish(
                CheckStatus.WARN,
                evidence,
                "Serve the same main content to mobile and add a viewport meta tag.",
            )
        return self.finish(CheckStatus.PASS, evidence, "")


def _below_fail(evidence: MobileParityEvidence) -> bool:
    return (
        evidence.main_text_ratio is not None
        and evidence.main_text_ratio < MOBILE_MAIN_TEXT_RATIO_FAIL
    )


def _below_warn(evidence: MobileParityEvidence) -> bool:
    return (
        evidence.main_text_ratio is not None
        and evidence.main_text_ratio < MOBILE_MAIN_TEXT_RATIO_WARN
    )


def _compare(ctx: AuditContext, desktop: BeautifulSoup, mobile: BeautifulSoup):
    desktop_main = _main_words(desktop)
    mobile_main = _main_words(mobile)
    ratio = None
    if desktop_main:
        ratio = round(mobile_main / desktop_main, 3)
    desktop_host = urlsplit(ctx.final_url or ctx.url).hostname or ""
    mobile_host = urlsplit(ctx.mobile_final_url or ctx.url).hostname or ""
    return MobileParityEvidence(
        title_match=_norm(_text(desktop.find("title")))
        == _norm(_text(mobile.find("title"))),
        h1_match=_norm(_text(desktop.find("h1"))) == _norm(_text(mobile.find("h1"))),
        main_text_ratio=ratio,
        json_ld_match=_has_json_ld(desktop) == _has_json_ld(mobile),
        final_host_differs=bool(
            desktop_host and mobile_host and desktop_host != mobile_host
        ),
        viewport_present=_has_viewport(desktop) and _has_viewport(mobile),
        alternate_mismatch=_alternate_mismatch(desktop, ctx),
    )


def _main_words(soup: BeautifulSoup) -> int:
    main = soup.find("main") or soup.find("article") or soup.body
    return len(_words(_text(main)))


def _norm(value: str) -> str:
    return value.casefold().strip()


def _has_json_ld(soup: BeautifulSoup) -> bool:
    return soup.find("script", attrs={"type": "application/ld+json"}) is not None


def _has_viewport(soup: BeautifulSoup) -> bool:
    for tag in soup.find_all("meta"):
        if (tag.get("name") or "").lower() == "viewport" and tag.get("content"):
            return True
    return False


def _alternate_mismatch(soup: BeautifulSoup, ctx: AuditContext) -> bool:
    canonical = _canonical(soup, ctx)
    for tag in soup.find_all("link"):
        rel = " ".join(tag.get("rel") or []).lower()
        if "alternate" not in rel or not tag.get("media"):
            continue
        href = urljoin(ctx.final_url or ctx.url, tag.get("href") or "")
        if _norm(href.rstrip("/")) != _norm(canonical.rstrip("/")):
            return True
    return False


def _canonical(soup: BeautifulSoup, ctx: AuditContext) -> str:
    tag = soup.find("link", rel=lambda value: value and "canonical" in value)
    if tag and tag.get("href"):
        return urljoin(ctx.final_url or ctx.url, tag["href"])
    return ctx.final_url or ctx.url
