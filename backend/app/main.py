import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from .peec_client import PeecClient
from .sitemap_analyzer import fetch_sitemap_urls, get_ai_citation_gaps
from .agent import CrawlabilityAgent

app = FastAPI(title="AI Citation Optimizer API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

peec = PeecClient()
agent = CrawlabilityAgent()

class AuditRequest(BaseModel):
    url: str

@app.get("/api/gaps")
async def get_gaps(domain: str = Query(..., description="The domain to analyze (e.g. example.com)")):
    """
    Returns pages that exist in the sitemap but are NOT cited by AI search engines.
    """
    try:
        # 1. Fetch Sitemap URLs
        sitemap_urls = fetch_sitemap_urls(domain)
        if not sitemap_urls:
            # Try with www if first attempt fails
            sitemap_urls = fetch_sitemap_urls(f"www.{domain}")
            
        if not sitemap_urls:
             return {"domain": domain, "gaps": [], "message": "No sitemap found. Please ensure /sitemap.xml exists."}

        # 2. Fetch Cited URLs from Peec
        cited_urls = peec.get_cited_urls(domain)

        # 3. Find Gaps
        gaps = get_ai_citation_gaps(sitemap_urls, cited_urls)
        
        return {
            "domain": domain,
            "total_sitemap_pages": len(sitemap_urls),
            "total_cited_pages": len(cited_urls),
            "gaps": gaps[:20] 
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/audit")
async def audit_page(request: AuditRequest):
    """
    Runs the AI crawlability agent on a specific URL.
    """
    try:
        # The agent now returns real logs and signals
        result = await agent.audit_url(request.url)
        return {
            "url": request.url,
            "analysis": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/benchmark")
async def get_benchmark(domain: str = Query(...)):
    """
    Returns before vs after visibility metrics using a gap-weighted calculation.
    """
    try:
        report = peec.get_domain_report(domain)
        data = report.get('data', [{}])[0]
        
        visibility = data.get('visibility_score', 0)
        citations = data.get('citation_count', 0)
        
        # Real-ish calculation:
        # If we have 100 pages and 2 cited, we have a huge potential.
        # If we have 100 pages and 80 cited, potential is lower.
        sitemap_urls = fetch_sitemap_urls(domain) or []
        total_pages = len(sitemap_urls)
        
        if total_pages > 0:
            citation_rate = citations / total_pages
            # Potential boost is proportional to the gap
            potential_boost = (1 - citation_rate) * 0.4 # Max 40% boost from current
            estimated_visibility = min(100, int(visibility * (1 + potential_boost)))
            estimated_citations = int(citations + (total_pages - citations) * 0.3) # Assume 30% of gap can be recovered
        else:
            estimated_visibility = visibility
            estimated_citations = citations

        return {
            "domain": domain,
            "total_pages": total_pages,
            "current": {
                "visibility_score": visibility,
                "citation_count": citations
            },
            "estimated": {
                "visibility_score": estimated_visibility,
                "citation_count": estimated_citations
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
