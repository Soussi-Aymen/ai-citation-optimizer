"""Sitemap URLs that a bounded crawl never links to."""

import time
from urllib.parse import urljoin, urlsplit

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from ...llms_txt_analyzer import extract_domain
from ..base import GeoCheck
from ..cache import normalize_url
from ..config import MAX_CRAWL_PAGES, MAX_CRAWL_SECONDS, MAX_DEPTH
from ..context import AuditContext
from ..models import CheckResult, CheckStatus


class OrphanEvidence(BaseModel):
    pages_crawled: int = 0
    in_sitemap: bool = False
    linked_internally: bool = False
    orphan_urls: list[str] = Field(default_factory=list)


class OrphanPageCheck(GeoCheck):
    id = "orphan_page_check"
    name = "Orphan page"
    tier = "deep"
    timeout_s = MAX_CRAWL_SECONDS + 2
    evidence_model = OrphanEvidence

    async def run(self, ctx: AuditContext) -> CheckResult:
        sitemap = await ctx.sitemap()
        sitemap_urls = [normalize_url(url) for url in sitemap.get("urls") or []]
        if not sitemap_urls:
            return self.finish(
                CheckStatus.SKIPPED,
                OrphanEvidence(),
                "Publish a sitemap so internal links can be compared with listed URLs.",
            )

        domain = extract_domain(ctx.final_url or ctx.url)
        host = (urlsplit(ctx.final_url or ctx.url).hostname or "").lower()
        origin = f"https://{domain}" if domain else ""
        target = normalize_url(ctx.final_url or ctx.url)
        linked = _links_from(ctx.raw_html or "", ctx.final_url or ctx.url, host)
        crawled = 0
        seen_pages: set[str] = set()
        queue: list[tuple[str, int]] = []
        if origin:
            queue.append((origin + "/", 0))

        started = time.monotonic()
        async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
            while queue and crawled < MAX_CRAWL_PAGES:
                if time.monotonic() - started >= MAX_CRAWL_SECONDS:
                    break
                url, depth = queue.pop(0)
                key = normalize_url(url)
                if key in seen_pages or depth > MAX_DEPTH:
                    continue
                seen_pages.add(key)
                if key == target and ctx.raw_html:
                    html = ctx.raw_html
                else:
                    html = await _fetch(client, url)
                crawled += 1
                if depth >= MAX_DEPTH:
                    continue
                for href in _links_from(html, url, host):
                    linked.add(href)
                    if normalize_url(href) not in seen_pages:
                        queue.append((href, depth + 1))

        root = normalize_url(origin) if origin else ""
        orphans = [url for url in sitemap_urls if url not in linked and url != root]
        in_sitemap = target in sitemap_urls
        linked_internally = target in linked or target == root
        evidence = OrphanEvidence(
            pages_crawled=crawled,
            in_sitemap=in_sitemap,
            linked_internally=linked_internally,
            orphan_urls=orphans[:10],
        )
        if in_sitemap and not linked_internally:
            return self.finish(
                CheckStatus.FAIL,
                evidence,
                "Add an internal link to this page from the homepage or a section index.",
            )
        if orphans:
            return self.finish(
                CheckStatus.WARN,
                evidence,
                "Link sitemap URLs that the crawl never reached from an index page.",
            )
        return self.finish(CheckStatus.PASS, evidence, "")


def _links_from(html: str, base: str, host: str) -> set[str]:
    soup = BeautifulSoup(html or "", "html.parser")
    found: set[str] = set()
    for anchor in soup.find_all("a", href=True):
        href = urljoin(base, anchor["href"]).split("#", maxsplit=1)[0]
        parsed = urlsplit(href)
        if (parsed.hostname or "").lower() != host or parsed.scheme not in (
            "http",
            "https",
        ):
            continue
        found.add(normalize_url(href))
    return found


async def _fetch(client: httpx.AsyncClient, url: str) -> str:
    try:
        response = await client.get(url)
    except Exception:
        return ""
    if response.status_code >= 400:
        return ""
    return response.text
