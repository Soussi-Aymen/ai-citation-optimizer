import requests
from bs4 import BeautifulSoup

def fetch_sitemap_urls(domain_url: str):
    """
    Fetches and parses sitemap.xml from the given domain.
    Returns a list of URLs.
    """
    if not domain_url.startswith('http'):
        domain_url = f"https://{domain_url}"
    
    sitemap_url = f"{domain_url.rstrip('/')}/sitemap.xml"
    
    try:
        response = requests.get(sitemap_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'xml')
        urls = [loc.text for loc in soup.find_all('loc')]
        return urls
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        # Fallback to robots.txt to find sitemap if direct access fails?
        # For now, just return empty list or handle in main
        return []

def get_ai_citation_gaps(sitemap_urls, cited_urls):
    """
    Identifies URLs that are in the sitemap but NOT in the cited_urls list.
    """
    sitemap_set = set(sitemap_urls)
    cited_set = set(cited_urls)
    
    gaps = sitemap_set - cited_set
    return list(gaps)
