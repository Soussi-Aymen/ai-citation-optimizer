from dataclasses import dataclass, field

import httpx

from ..llms_txt_analyzer import extract_domain
from ..sitemap_analyzer import fetch_sitemap_urls


@dataclass
class AuditContext:
    """One fetch per audit. Checks read this object and do not repeat it."""

    url: str
    raw_html: str = ""
    raw_status: int | None = None
    headers: dict[str, str] = field(default_factory=dict)
    redirect_chain: list[str] = field(default_factory=list)
    final_url: str = ""
    rendered_html: str | None = None
    rendered_text: str | None = None
    uncited_prompts: list[str] | None = None
    _robots: str | None = None
    _robots_loaded: bool = False
    _sitemap: dict | None = None

    async def robots_txt(self, client: httpx.AsyncClient | None = None) -> str | None:
        if self._robots_loaded:
            return self._robots
        self._robots_loaded = True
        domain = extract_domain(self.final_url or self.url)
        if not domain:
            return None
        owns_client = client is None
        client = client or httpx.AsyncClient(timeout=8.0, follow_redirects=True)
        try:
            response = await client.get(f"https://{domain}/robots.txt")
            if response.status_code == 200:
                self._robots = response.text
        except Exception:
            self._robots = None
        finally:
            if owns_client:
                await client.aclose()
        return self._robots

    async def sitemap(self) -> dict:
        if self._sitemap is not None:
            return self._sitemap
        domain = extract_domain(self.final_url or self.url)
        try:
            self._sitemap = await fetch_sitemap_urls(domain or self.url)
        except Exception:
            self._sitemap = {"urls": [], "metrics": {}, "entries": []}
        return self._sitemap


async def load_raw_context(
    url: str, client: httpx.AsyncClient | None = None
) -> AuditContext:
    ctx = AuditContext(url=url, final_url=url)
    owns_client = client is None
    client = client or httpx.AsyncClient(timeout=10.0, follow_redirects=True)
    try:
        response = await client.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )
        ctx.raw_html = response.text
        ctx.raw_status = response.status_code
        ctx.headers = {k.lower(): v for k, v in response.headers.items()}
        ctx.final_url = str(response.url)
        ctx.redirect_chain = [str(item.url) for item in response.history] + [
            str(response.url)
        ]
    except Exception:
        ctx.raw_html = ""
        ctx.raw_status = None
    finally:
        if owns_client:
            await client.aclose()
    return ctx
