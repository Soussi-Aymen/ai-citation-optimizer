import os
import json
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from .peec_client import PeecClient
from .sitemap_analyzer import fetch_sitemap_urls, get_ai_citation_gaps
from .agent import CrawlabilityAgent

app = FastAPI(title="AI Citation Optimizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

peec = PeecClient()
agent = CrawlabilityAgent()

PROJECT_MAP = {
    "nothing.tech": "or_faaa7625-bc84-4f64-a754-a412d423c641",
    "attio.com": "or_47ccb54e-0f32-4c95-b460-6a070499d084"
}

def get_project_id(domain: str):
    for d, pid in PROJECT_MAP.items():
        if d in domain: return pid
    return PROJECT_MAP["nothing.tech"]

class AuditRequest(BaseModel):
    url: str

class FixRequest(BaseModel):
    url: str

class ContentRequest(BaseModel):
    action_type: str
    action_text: str

@app.get("/api/gaps")
async def get_gaps(domain: str = Query(...)):
    try:
        clean_domain = domain.replace("https://", "").replace("http://", "").replace("www.", "").split('/')[0]
        pid = get_project_id(clean_domain)

        sitemap_urls = await fetch_sitemap_urls(clean_domain) or []
        cited_urls = await peec.get_cited_urls(clean_domain)
        gaps = get_ai_citation_gaps(sitemap_urls, cited_urls)

        total = len(sitemap_urls)
        cited = len(cited_urls)
        citation_rate = (cited / total) if total > 0 else 0
        perf_score = min(100, round((citation_rate * 60) + 20 + min(20, max(0, 20 - len(clean_domain)))))

        brands_data = await peec.list_brands(pid)
        brands = brands_data.get('data', [])

        competitors = []
        for b in brands:
            brand_domain = b.get('domain')
            if not brand_domain:
                continue
            comp_report = await peec.get_domain_report(brand_domain)
            comp_data = comp_report.get('data', [{}])[0] if isinstance(comp_report.get('data'), list) else comp_report.get('data', {})
            visibility = comp_data.get('visibility_score', 0)
            if visibility == 0:
                visibility = comp_data.get('retrieved_percentage', 0)
            competitors.append({
                "name": b.get('name', brand_domain),
                "domain": brand_domain,
                "is_own": b.get('is_own', False),
                "citations": comp_data.get('citation_count', 0),
                "visibility": round(visibility, 1)
            })

        return {
            "domain": domain,
            "total_sitemap_pages": total,
            "total_cited_pages": cited,
            "citation_coverage_pct": round(citation_rate * 100, 1),
            "performance_score": perf_score,
            "gaps": gaps[:20],
            "brands": brands,
            "competitors": competitors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-fix")
async def generate_fix(request: FixRequest):
    """Returns structured instruction panel data and live Playwright metrics."""
    try:
        url = request.url
        fix_data = agent.build_fix_instructions(url)
        
        audit_result = await agent.fetch_and_analyze(url)
        if "signals" in audit_result:
            fix_data["metrics"] = audit_result["signals"]
        else:
            fix_data["metrics"] = {}

        return fix_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-content")
async def generate_content(request: ContentRequest):
    try:
        content = await agent.generate_action_content(request.action_type, request.action_text)
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/benchmark")
async def get_benchmark(domain: str = Query(...)):
    try:
        clean_domain = domain.replace("https://", "").replace("http://", "").replace("www.", "").split('/')[0]
        pid = get_project_id(clean_domain)

        report = await peec.get_domain_report(clean_domain)
        report_data = report.get('data', [{}])[0] if isinstance(report.get('data'), list) else report.get('data', {})

        visibility = report_data.get('visibility_score', 0)
        citations = report_data.get('citation_count', 0)
        sitemap_urls = await fetch_sitemap_urls(clean_domain) or []
        total_pages = len(sitemap_urls)

        target_citations = int(citations + (total_pages - citations) * 0.45) if total_pages > 0 else citations + 66
        target_visibility = (target_citations / total_pages) * 100 if total_pages > 0 else 0
        target_visibility = round(target_visibility, 1)
        if target_visibility == 0:
            target_visibility = 15.0

        # --- Fetch actions overview (top 5 by opportunity_score) ---
        actions_overview = await peec.get_actions(pid, scope="overview")
        slices = actions_overview.get('data', [])
        if not isinstance(slices, list):
            slices = []

        top_slices = sorted(slices, key=lambda x: x.get('opportunity_score', 0), reverse=True)[:5]

        roadmap = []
        for s in top_slices:
            slice_id = s.get('id')
            details = await peec.get_actions(pid, scope="slice", slice_id=slice_id)
            action_items = details.get('data', [])[:3]

            priority_score = s.get('relative_opportunity_score', s.get('opportunity_score', 0))
            if priority_score >= 3 or s.get('opportunity_score', 0) > 70:
                priority = "HIGH"
                priority_emoji = "🔴"
            elif priority_score >= 2 or s.get('opportunity_score', 0) > 40:
                priority = "MEDIUM"
                priority_emoji = "🟡"
            else:
                priority = "LOW"
                priority_emoji = "⚪"

            channel = s.get('domain', s.get('action_group_type', 'Web'))
            label = s.get('url_classification', s.get('action_group_type', ''))
            title = f"{channel} — {label}" if label and label != channel else channel

            actions_list = [{"id": item.get('id', f"{slice_id}_{i}"), "text": item.get('text', ''), "url": item.get('url', '')} for i, item in enumerate(action_items)]

            roadmap.append({
                "priority": priority,
                "priority_emoji": priority_emoji,
                "title": title,
                "channel": channel,
                "gap_percentage": s.get('gap_percentage', 0),
                "opportunity_score": s.get('opportunity_score', 0),
                "actions": actions_list,
                "type": s.get('action_group_type', 'General'),
                "slice_id": slice_id
            })

        # --- Competitor advantage breakdown ---
        brands_data = await peec.list_brands(pid)
        brands = brands_data.get('data', [])

        channel_gaps = []
        channel_names = ["YouTube", "Reddit", "Editorial Lists", "Wikipedia"]
        channel_domains = {
            "YouTube": "youtube.com",
            "Reddit": "reddit.com",
            "Editorial Lists": None,
            "Wikipedia": "wikipedia.org"
        }

        own_brand = next((b for b in brands if b.get('is_own')), None)
        own_domain = own_brand.get('domain', clean_domain) if own_brand else clean_domain
        own_name = own_brand.get('name', clean_domain) if own_brand else clean_domain

        competitor_brands = [b for b in brands if not b.get('is_own')][:2]

        for ch_name in channel_names:
            ch_domain = channel_domains[ch_name]
            ch_slice = None
            if ch_domain:
                ch_slice = next((s for s in slices if ch_domain in s.get('domain', '')), None)
            else:
                ch_slice = next((s for s in slices if 'EDITORIAL' in s.get('action_group_type', '').upper() or 'LISTICLE' in s.get('url_classification', '').upper()), None)

            gap_pct = ch_slice.get('gap_percentage', 0) if ch_slice else 0
            opp = ch_slice.get('opportunity_score', 0) if ch_slice else 0
            if opp > 70:
                gap_label = "CRITICAL"
            elif opp > 50:
                gap_label = "HIGH"
            elif opp > 30:
                gap_label = "MEDIUM"
            else:
                gap_label = "LOW"

            comp_data = []
            for cb in competitor_brands:
                cb_report = await peec.get_domain_report(cb.get('domain', ''))
                cb_data = cb_report.get('data', [{}])[0] if isinstance(cb_report.get('data'), list) else cb_report.get('data', {})
                cb_vis = cb_data.get('retrieved_percentage', cb_data.get('visibility_score', 0))
                comp_data.append({"name": cb.get('name', cb.get('domain', '')), "visibility": round(cb_vis, 1)})

            own_report = await peec.get_domain_report(own_domain)
            own_data = own_report.get('data', [{}])[0] if isinstance(own_report.get('data'), list) else own_report.get('data', {})
            own_vis = own_data.get('retrieved_percentage', own_data.get('visibility_score', 0))

            channel_gaps.append({
                "channel": ch_name,
                "competitors": comp_data,
                "own": {"name": own_name, "visibility": round(own_vis, 1)},
                "gap_label": gap_label
            })

        # --- Tab actions (YouTube, Reddit, Editorial) ---
        tab_actions = {}
        tab_map = {
            "YouTube": {"domain": "youtube.com", "scope": "ugc"},
            "Reddit": {"domain": "reddit.com", "scope": "ugc"},
            "Editorial": {"type": "EDITORIAL", "classification": "LISTICLE", "scope": "editorial"}
        }

        for tab, cfg in tab_map.items():
            if "domain" in cfg:
                cat_slice = next((s for s in slices if cfg["domain"] in s.get('domain', '')), None)
            else:
                cat_slice = next((s for s in slices if cfg["type"] in s.get('action_group_type', '').upper() or cfg["classification"] in s.get('url_classification', '').upper()), None)

            if cat_slice:
                if "domain" in cfg:
                    details = await peec.get_actions(pid, scope=cfg["scope"], domain=cfg["domain"])
                else:
                    details = await peec.get_actions(pid, scope=cfg["scope"], url_classification=cfg["classification"])
                items = details.get('data', [])[:3]
                tab_actions[tab] = {
                    "gap_percentage": cat_slice.get('gap_percentage', 0),
                    "opportunity_score": cat_slice.get('opportunity_score', 0),
                    "items": [{"id": item.get('id', f"tab_{tab}_{i}"), "text": item.get('text', ''), "url": item.get('url', '')} for i, item in enumerate(items)],
                    "has_data": len(items) > 0
                }
            else:
                tab_actions[tab] = {"gap_percentage": 0, "opportunity_score": 0, "items": [], "has_data": False}

        return {
            "domain": domain,
            "total_pages": total_pages,
            "current": {"visibility_score": visibility, "citation_count": citations},
            "estimated": {"visibility_score": target_visibility, "citation_count": target_citations},
            "roadmap": roadmap,
            "channel_gaps": channel_gaps,
            "tab_actions": tab_actions,
            "own_brand_name": own_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/audit")
async def audit_page(request: AuditRequest):
    try:
        domain = request.url.replace("https://", "").replace("http://", "").replace("www.", "").split('/')[0]
        report = await peec.get_domain_report(domain)
        comp_context = json.dumps(report.get('data', [])[:3])
        result = await agent.audit_url(request.url, competitor_data=comp_context)
        return {"url": request.url, "analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
