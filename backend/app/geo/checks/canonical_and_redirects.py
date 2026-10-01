from urllib.parse import urljoin

from bs4 import BeautifulSoup
from pydantic import BaseModel

from ..base import GeoCheck
from ..config import REDIRECT_CHAIN_FAIL, REDIRECT_CHAIN_WARN
from ..context import AuditContext
from ..models import CheckStatus


class CanonicalEvidence(BaseModel):
    redirect_count: int = 0
    canonical: str = ""
    canonical_mismatch: bool = False
    noindex: bool = False


class CanonicalAndRedirectsCheck(GeoCheck):
    id = "canonical_and_redirects"
    name = "Canonical and redirects"
    tier = "fast"
    timeout_s = 2
    evidence_model = CanonicalEvidence

    async def run(self, ctx: AuditContext):
        soup = BeautifulSoup(ctx.raw_html or "", "html.parser")
        link = soup.find(
            "link", attrs={"rel": lambda value: value and "canonical" in value}
        )
        canonical = ""
        if link and link.get("href"):
            canonical = urljoin(ctx.final_url or ctx.url, link["href"])
        final = (ctx.final_url or ctx.url).rstrip("/")
        mismatch = bool(canonical) and canonical.rstrip("/") != final
        robots = " ".join(
            [
                ctx.headers.get("x-robots-tag", ""),
                _meta(soup),
            ]
        ).lower()
        evidence = CanonicalEvidence(
            redirect_count=max(len(ctx.redirect_chain) - 1, 0),
            canonical=canonical,
            canonical_mismatch=mismatch,
            noindex="noindex" in robots,
        )
        if (
            evidence.noindex
            or evidence.canonical_mismatch
            or evidence.redirect_count >= REDIRECT_CHAIN_FAIL
        ):
            status = CheckStatus.FAIL
            hint = "Point canonical at the final URL, remove noindex, and shorten the redirect chain."
        elif evidence.redirect_count >= REDIRECT_CHAIN_WARN:
            status = CheckStatus.WARN
            hint = "Collapse extra redirects so crawlers reach the canonical URL in one hop."
        else:
            status = CheckStatus.PASS
            hint = "Canonical and redirects are consistent."
        return self.finish(status, evidence, hint)


def _meta(soup: BeautifulSoup) -> str:
    tag = soup.find(
        "meta", attrs={"name": lambda value: value and value.lower() == "robots"}
    )
    if tag is None:
        return ""
    return str(tag.get("content") or "")
