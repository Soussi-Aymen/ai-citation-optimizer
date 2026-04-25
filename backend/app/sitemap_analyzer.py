import httpx
from lxml import etree
import io
import asyncio

async def fetch_sitemap_urls(domain_url: str):
    """
    Async sitemap fetcher using httpx to prevent blocking the event loop.
    Supports recursive indexing and multiple sitemap paths.
    """
    if not domain_url.startswith('http'):
        domain_url = f"https://{domain_url}"
    
    clean_base = domain_url.rstrip('/')
    paths_to_try = [
        f"{clean_base}/sitemap.xml",
        f"{clean_base}/sitemap_index.xml",
        f"{clean_base}/en/sitemap.xml"
    ]
    
    all_urls = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        async def parse_sitemap(url, depth=0):
            if depth > 3: return
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                tree = etree.parse(io.BytesIO(response.content))
                root = tree.getroot()
                ns = {'ns': root.nsmap[None]} if None in root.nsmap else {}
                
                if 'sitemapindex' in root.tag:
                    sitemap_locs = root.xpath('//ns:sitemap/ns:loc/text()', namespaces=ns)
                    # Run nested sitemap parses in parallel
                    tasks = [parse_sitemap(loc, depth + 1) for loc in sitemap_locs]
                    await asyncio.gather(*tasks)
                else:
                    locs = root.xpath('//ns:url/ns:loc/text()', namespaces=ns)
                    all_urls.extend(locs)
            except Exception as e:
                pass # Silently ignore parse errors for fallback paths

        for path in paths_to_try:
            await parse_sitemap(path)
            if all_urls: break
        
    return list(set(all_urls))

def get_ai_citation_gaps(sitemap_urls, cited_urls):
    """
    Identifies URLs that are in the sitemap but NOT in the cited_urls list.
    """
    sitemap_set = {u.rstrip('/') for u in sitemap_urls}
    cited_set = {u.rstrip('/') for u in cited_urls}
    
    gaps = sitemap_set - cited_set
    return list(gaps)
