"""Probe and template generation for analyzed domains' /llms.txt files."""

import re
from urllib.parse import urlparse

import httpx

LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def extract_domain(url: str) -> str:
    if not url.startswith("http"):
        url = f"https://{url}"
    return urlparse(url).netloc.replace("www.", "")


def _infer_page_name(url: str) -> str:
    slug = url.rstrip("/").split("/")[-1].replace("-", " ").replace("_", " ")
    return slug.title() if slug else "Homepage"


def normalize_url(u: str) -> str:
    return u.rstrip("/").split("#")[0].split("?")[0]


def parse_llms_txt_links(content: str) -> list[str]:
    return [m.group(2).strip() for m in LINK_PATTERN.finditer(content)]


def page_listed_in_llms_txt(page_url: str, links: list[str]) -> bool:
    page_norm = normalize_url(page_url)
    page_path = urlparse(page_norm).path.rstrip("/") or "/"

    for link in links:
        if link.startswith("/"):
            if normalize_url(page_path) == normalize_url(link.rstrip("/") or "/"):
                return True
            continue
        if not link.startswith("http"):
            continue
        link_norm = normalize_url(link)
        if link_norm == page_norm:
            return True
        if urlparse(link_norm).path.rstrip("/") == page_path.rstrip("/"):
            return True
    return False


def validate_llms_txt(content: str) -> bool:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            return True
    return False


def build_llms_txt_template(url: str) -> str:
    domain = extract_domain(url)
    brand = domain.split(".")[0].replace("-", " ").title()
    page_name = _infer_page_name(url)
    return (
        f"# {brand}\n\n"
        f"> Official content from {domain} curated for AI assistants and LLM crawlers.\n\n"
        f"Publish this file at `https://{domain}/llms.txt` so AI search bots can discover "
        f"your most important pages without crawling the entire site.\n\n"
        f"## Priority Pages\n\n"
        f"- [{page_name}]({url}): Key page that should be cited by AI search engines.\n\n"
        f"## Optional\n\n"
        f"- [Homepage](https://{domain}/): Brand overview and site navigation\n"
    )


async def probe_llms_txt(
    domain: str, page_url: str, client: httpx.AsyncClient | None = None
) -> dict:
    """Fetch analyzed domain's /llms.txt (or /llm.txt) and check if page_url is listed."""
    clean_domain = extract_domain(domain if "://" in domain else f"https://{domain}")
    probe_urls = [
        f"https://{clean_domain}/llms.txt",
        f"https://{clean_domain}/llm.txt",
    ]

    result = {
        "has_llms_txt": False,
        "llms_txt_valid": False,
        "llms_txt_lists_page": False,
        "llms_txt_link_count": 0,
        "llms_txt_url": None,
    }

    own_client = client is None
    if own_client:
        client = httpx.AsyncClient(timeout=10.0, follow_redirects=True)

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; AICitationOptimizer/1.0)"
    }

    try:
        for llms_url in probe_urls:
            try:
                resp = await client.get(llms_url, headers=headers)
                if resp.status_code != 200:
                    continue
                content = resp.text.strip()
                if not content:
                    continue

                links = parse_llms_txt_links(content)
                result.update(
                    {
                        "has_llms_txt": True,
                        "llms_txt_valid": validate_llms_txt(content),
                        "llms_txt_lists_page": page_listed_in_llms_txt(page_url, links),
                        "llms_txt_link_count": len(links),
                        "llms_txt_url": llms_url,
                    }
                )
                break
            except Exception:
                continue
    finally:
        if own_client:
            await client.aclose()

    return result
