import httpx
from lxml import etree
import io
import asyncio

async def fetch_sitemap_urls(domain_url: str):
    """
    Async sitemap fetcher using httpx to prevent blocking the event loop.
    Supports recursive indexing and multiple sitemap paths.
    Returns a dict with 'urls' list and 'health' metrics.
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
    has_lastmod_count = 0
    found_path = None
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        async def parse_sitemap(url, depth=0):
            nonlocal has_lastmod_count, found_path
            if depth > 3: return
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                tree = etree.parse(io.BytesIO(response.content))
                root = tree.getroot()
                ns = {'ns': root.nsmap[None]} if None in root.nsmap else {}
                
                if 'sitemapindex' in root.tag:
                    sitemap_locs = root.xpath('//ns:sitemap/ns:loc/text()', namespaces=ns)
                    tasks = [parse_sitemap(loc, depth + 1) for loc in sitemap_locs]
                    await asyncio.gather(*tasks)
                else:
                    if found_path is None: found_path = url
                    urls_data = root.xpath('//ns:url', namespaces=ns)
                    for url_node in urls_data:
                        loc = url_node.xpath('./ns:loc/text()', namespaces=ns)
                        if loc:
                            all_urls.append(loc[0])
                            lastmod = url_node.xpath('./ns:lastmod/text()', namespaces=ns)
                            if lastmod:
                                has_lastmod_count += 1
            except Exception as e:
                pass

        for path in paths_to_try:
            await parse_sitemap(path)
            if all_urls: break
        
    unique_urls = list(set(all_urls))
    return {
        "urls": unique_urls,
        "metrics": {
            "total_count": len(unique_urls),
            "lastmod_count": has_lastmod_count,
            "has_lastmod": has_lastmod_count > 0,
            "found_path": found_path
        }
    }

def get_ai_citation_gaps(sitemap_urls, cited_urls):
    """
    Identifies:
    1. Gaps: In sitemap but NOT cited (Pages AI is ignoring).
    2. Orphans: Cited but NOT in sitemap (Sitemap is incomplete).
    """
    sitemap_set = {u.rstrip('/') for u in sitemap_urls}
    cited_set = {u.rstrip('/') for u in cited_urls}
    
    gaps = sitemap_set - cited_set
    orphans = cited_set - sitemap_set
    
    return list(gaps), list(orphans)
