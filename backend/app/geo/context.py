import asyncio
from dataclasses import dataclass, field

import httpx

from ..llms_txt_analyzer import extract_domain, probe_llms_txt
from ..sitemap_analyzer import fetch_sitemap_urls

_EMPTY_LLMS = {
    "has_llms_txt": False,
    "llms_txt_valid": False,
    "llms_txt_lists_page": False,
    "llms_txt_link_count": 0,
    "llms_txt_url": None,
}

_PAGE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


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
    _client: httpx.AsyncClient | None = None
    _owns_client: bool = False
    _early_tasks: list[asyncio.Task] = field(default_factory=list)
    _llms_task: asyncio.Task | None = None
    _robots_task: asyncio.Task | None = None

    async def __aenter__(self) -> "AuditContext":
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=10.0, follow_redirects=True)
            self._owns_client = True
        self._llms_task = asyncio.create_task(self._load_llms())
        self._robots_task = asyncio.create_task(self._load_robots())
        self._early_tasks = [self._llms_task, self._robots_task]
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        for task in self._early_tasks:
            if not task.done():
                task.cancel()
        if self._early_tasks:
            await asyncio.gather(*self._early_tasks, return_exceptions=True)
        if self._owns_client and self._client is not None:
            await self._client.aclose()
        return False

    async def load_page(self) -> None:
        client = self._client or httpx.AsyncClient(timeout=10.0, follow_redirects=True)
        owns = self._client is None
        try:
            response = await client.get(self.url, headers=_PAGE_HEADERS)
            self.raw_html = response.text
            self.raw_status = response.status_code
            self.headers = {
                key.lower(): value for key, value in response.headers.items()
            }
            self.final_url = str(response.url)
            self.redirect_chain = [str(item.url) for item in response.history] + [
                str(response.url)
            ]
        except Exception:
            self.raw_html = ""
            self.raw_status = None
        finally:
            if owns:
                await client.aclose()

    async def llms_txt(self) -> dict:
        if self._llms_task is None:
            self._llms_task = asyncio.create_task(self._load_llms())
            self._early_tasks.append(self._llms_task)
        return await self._llms_task

    async def _load_llms(self) -> dict:
        domain = extract_domain(self.final_url or self.url)
        try:
            return await probe_llms_txt(domain, self.url, client=self._client)
        except Exception:
            return dict(_EMPTY_LLMS)

    async def robots_txt(self, client: httpx.AsyncClient | None = None) -> str | None:
        if client is not None:
            return await self._fetch_robots(client)
        if self._robots_task is not None:
            return await self._robots_task
        if self._robots_loaded:
            return self._robots
        self._robots_task = asyncio.create_task(self._load_robots())
        self._early_tasks.append(self._robots_task)
        return await self._robots_task

    async def _load_robots(self) -> str | None:
        if self._client is not None:
            return await self._fetch_robots(self._client)
        client = httpx.AsyncClient(timeout=8.0, follow_redirects=True)
        try:
            return await self._fetch_robots(client)
        finally:
            await client.aclose()

    async def _fetch_robots(self, client: httpx.AsyncClient) -> str | None:
        if self._robots_loaded:
            return self._robots
        domain = extract_domain(self.final_url or self.url)
        if not domain:
            self._robots_loaded = True
            return None
        try:
            response = await client.get(f"https://{domain}/robots.txt")
            if response.status_code == 200:
                self._robots = response.text
        except Exception:
            self._robots = None
        self._robots_loaded = True
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
    ctx._client = client
    try:
        await ctx.load_page()
    finally:
        ctx._client = None
        if owns_client:
            await client.aclose()
    return ctx
