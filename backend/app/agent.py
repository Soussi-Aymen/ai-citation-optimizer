import asyncio
import json
import os
import time

import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from playwright.async_api import async_playwright

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def _infer_product_name(url: str) -> str:
    slug = url.rstrip("/").split("/")[-1].replace("-", " ").replace("_", " ")
    return slug.title() if slug else "Phone (2)"


class CrawlabilityAgent:
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", google_api_key=GEMINI_API_KEY, temperature=0.7
        )

    def build_fix_instructions(self, url: str) -> dict:
        """Returns structured instruction panel data — user-facing action plan, no automated fixes."""
        product_name = _infer_product_name(url)

        if "/products/" in url:
            problem = "This product page is likely rendered in JavaScript. AI crawlers cannot read JS-rendered content — they only see an empty shell."
            checklist = [
                "Add JSON-LD structured data to this page's <head> (copy the template below)",
                "Ensure the product name and description appear in plain HTML <h1> and <p> tags, not rendered by JavaScript",
                f"Add a one-paragraph plain-text description of '{product_name}' that includes: what it is, who it's for, and how it differs from competitors like Apple and Samsung",
            ]
            schema_type = "Product"
            json_ld = {
                "@context": "https://schema.org",
                "@type": "Product",
                "name": product_name,
                "brand": {"@type": "Brand", "name": "Nothing"},
                "description": f"Nothing {product_name} — a minimalist, design-forward smartphone for people who want a phone that stands out from Apple and Samsung.",
                "url": url,
                "image": f"https://nothing.tech/cdn/shop/products/{url.rstrip('/').split('/')[-1]}.jpg",
                "offers": {
                    "@type": "Offer",
                    "priceCurrency": "GBP",
                    "availability": "https://schema.org/InStock",
                    "seller": {
                        "@type": "Organization",
                        "name": "Nothing Technology Limited",
                    },
                },
            }
        elif "/pages/" in url:
            problem = "This page lacks structured entity information that AI engines use to understand your brand and surface it in responses."
            checklist = [
                "Add JSON-LD Organization schema to this page's <head> (copy the template below)",
                "Verify all key brand information (founding year, products, mission) is written in plain HTML — not loaded via JS",
                "Structure the page with proper heading hierarchy: one <h1> with the brand name, <h2> for each major section",
            ]
            schema_type = "Organization"
            json_ld = {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": "Nothing Technology Limited",
                "url": "https://nothing.tech",
                "logo": "https://nothing.tech/logo.png",
                "description": "Nothing Technology Limited makes consumer electronics with a focus on transparency, design, and openness — competing with Apple and Samsung.",
                "sameAs": [
                    "https://twitter.com/nothing",
                    "https://instagram.com/nothing",
                    "https://en.wikipedia.org/wiki/Nothing_(company)",
                ],
                "foundingDate": "2020",
                "founder": {"@type": "Person", "name": "Carl Pei"},
            }
        elif "/collections/" in url:
            problem = "Collection pages typically have thin content with no clear topic — AI engines skip them because there's nothing substantive to cite."
            checklist = [
                "Add a 200–300 word plain-text introductory paragraph above the product grid explaining what this collection is and who it's for",
                "Add JSON-LD CollectionPage schema to this page's <head> (copy the template below)",
                "Link each product in this collection to its own product page with descriptive anchor text (not just 'View' or 'Shop Now')",
            ]
            schema_type = "CollectionPage"
            collection_name = _infer_product_name(url)
            json_ld = {
                "@context": "https://schema.org",
                "@type": "CollectionPage",
                "name": f"Nothing {collection_name} Collection",
                "description": f"Explore the Nothing {collection_name} collection — minimalist, transparent design phones and accessories that challenge Apple and Samsung.",
                "url": url,
                "publisher": {
                    "@type": "Organization",
                    "name": "Nothing Technology Limited",
                },
            }
        else:
            problem = "This page has no structured data and may not have enough plain-text content for AI engines to index and cite it."
            checklist = [
                "Add JSON-LD WebPage schema to this page's <head> (copy the template below)",
                "Ensure all key content is in plain HTML — not loaded via JavaScript frameworks",
                "Add at least one paragraph of descriptive text that clearly explains what this page is about",
            ]
            schema_type = "WebPage"
            json_ld = {
                "@context": "https://schema.org",
                "@type": "WebPage",
                "name": f"Nothing Technology — {_infer_product_name(url)}",
                "url": url,
                "description": "Nothing Technology Limited makes transparent, minimalist consumer electronics.",
                "publisher": {
                    "@type": "Organization",
                    "name": "Nothing Technology Limited",
                },
            }

        return {
            "url": url,
            "problem": problem,
            "checklist": checklist,
            "schema_type": schema_type,
            "json_ld": f'<script type="application/ld+json">\n{json.dumps(json_ld, indent=2)}\n</script>',
        }

    def _generate_guidance(self, signals: dict) -> list:
        """Generates technical guidance only for metrics that are Medium or Bad."""
        guidance = []

        # Load Time (ms)
        load_time = signals.get("load_time_ms", 0)
        if load_time >= 2000:
            score = "Bad" if load_time >= 4000 else "Medium"
            guidance.append(
                {
                    "id": "load_time",
                    "metric": "Load Time",
                    "score": score,
                    "advice": f"Page load is {'too slow' if score == 'Bad' else 'moderate'} ({load_time}ms).",
                    "steps": [
                        "Implement a Content Delivery Network (CDN) like Cloudflare or Akamai to serve assets closer to the user.",
                        "Optimize and compress all images using modern formats like WebP or AVIF.",
                        "Minimize the number of render-blocking resources (CSS and JS) in the <head>.",
                        "Enable Gzip or Brotli compression on your origin server.",
                    ],
                }
            )

        # JS Impact / Hydration (text_delta)
        text_delta = signals.get("text_delta", 0)
        if text_delta > 500:
            score = "Bad" if text_delta > 2000 else "Medium"
            guidance.append(
                {
                    "id": "js_hydration",
                    "metric": "JS Dependency",
                    "score": score,
                    "advice": f"{'Heavy' if score == 'Bad' else 'Moderate'} reliance on client-side rendering ({text_delta} chars injected).",
                    "steps": [
                        "Switch to Server-Side Rendering (SSR) or Static Site Generation (SSG) to ensure content is in the initial HTML.",
                        "Use 'Pre-rendering' to capture the state of the page at build time.",
                        "Avoid using 'loading' states or skeletons for critical SEO content.",
                        "Ensure your framework (Next.js/Nuxt/Astro) is configured for optimal SEO crawlability.",
                    ],
                }
            )

        # JS Payload (MB)
        js_payload = signals.get("js_payload_mb")
        if js_payload is not None and js_payload > 1:
            score = "Bad" if js_payload > 3 else "Medium"
            guidance.append(
                {
                    "id": "js_payload",
                    "metric": "JS Bundle Size",
                    "score": score,
                    "advice": f"JavaScript payload is {'extremely heavy' if score == 'Bad' else 'large'} ({js_payload}MB).",
                    "steps": [
                        "Analyze your bundle using tools like Webpack Bundle Analyzer to identify large dependencies.",
                        "Implement Route-Based Code Splitting to only load the JS needed for the current page.",
                        "Audit third-party scripts (Tag Managers, Analytics, Chatbots) and remove any that aren't critical.",
                        "Use smaller alternatives for heavy libraries (e.g., replace Moment.js with Day.js).",
                    ],
                }
            )

        # Console Errors
        errors = signals.get("console_errors")
        if errors is not None and errors > 0:
            score = "Bad" if errors > 3 else "Medium"
            guidance.append(
                {
                    "id": "console_errors",
                    "metric": "Console Errors",
                    "score": score,
                    "advice": f"Found {errors} console errors that may disrupt AI rendering.",
                    "steps": [
                        "Check for failed API requests (404/500) in the Network tab that might be breaking the UI.",
                        "Ensure all external scripts are loading correctly and don't have CORS issues.",
                        "Wrap risky components in Error Boundaries to prevent the entire page from crashing.",
                        "Fix null/undefined reference errors that occur during the initial page hydration.",
                    ],
                }
            )

        # LCP (Seconds)
        lcp = signals.get("lcp_seconds")
        if lcp is not None and lcp > 2.5:
            score = "Bad" if lcp > 4 else "Medium"
            guidance.append(
                {
                    "id": "lcp",
                    "metric": "Largest Contentful Paint",
                    "score": score,
                    "advice": f"Main content visibility is {'too slow' if score == 'Bad' else 'delayed'} ({lcp}s).",
                    "steps": [
                        "Prioritize loading the LCP image by adding <link rel='preload'> to your HTML <head>.",
                        "Ensure the LCP element (usually a hero image or H1) is part of the initial HTML response, not injected via JS.",
                        "Reduce Server Response Time (TTFB) by caching database queries or using Edge Functions.",
                        "Use the 'fetchpriority=\"high\"' attribute on your most important above-the-fold images.",
                    ],
                }
            )

        # Unused JS (%)
        unused_js = signals.get("unused_js_pct")
        if unused_js is not None and unused_js >= 30:
            score = "Bad" if unused_js > 60 else "Medium"
            guidance.append(
                {
                    "id": "unused_js",
                    "metric": "Unused JavaScript",
                    "score": score,
                    "advice": f"{unused_js}% of your JS is never executed but blocks the crawler.",
                    "steps": [
                        "Enable Tree Shaking in your build tool (Webpack/Vite/Rollup) to remove dead code.",
                        "Remove unused legacy libraries or polyfills that are no longer needed for modern browsers.",
                        "Move non-critical JS (like tracking pixels) to the bottom of the page or load them with 'defer'.",
                        "Audit your CSS-in-JS implementation to ensure it isn't generating excessive runtime overhead.",
                    ],
                }
            )

        # Structured Data
        if not signals.get("has_json_ld"):
            guidance.append(
                {
                    "id": "structured_data",
                    "metric": "Structured Data",
                    "score": "Bad",
                    "advice": "Missing JSON-LD structured data.",
                    "steps": [
                        "Generate a Schema.org JSON-LD snippet for your page type (Product, Article, or Organization).",
                        "Place the <script type='application/ld+json'> tag inside the <head> of your document.",
                        "Use the Google Rich Results Test tool to validate that your markup is readable by bots.",
                        "Ensure the data in your JSON-LD matches the visible content on the page to avoid manual penalties.",
                    ],
                }
            )

        return guidance

    async def generate_action_content(self, action_type: str, action_text: str):
        """Generates content (pitches, scripts, comments) for Peec actions."""
        if "YouTube" in action_type or "youtube" in action_type.lower():
            role = "brand partnerships manager"
            task = "write a concise, professional YouTube collaboration pitch email (under 200 words). Sign off as the Nothing Brand Partnerships team. Be specific, not generic."
        elif "Reddit" in action_type or "reddit" in action_type.lower():
            role = "community manager"
            task = "draft a helpful, non-promotional Reddit comment (under 150 words) that naturally mentions Nothing Phone as a genuine alternative to Apple/Samsung. Do NOT use marketing language. Sound like a real community member."
        elif "Editorial" in action_type or "editorial" in action_type.lower():
            role = "PR manager"
            task = "write a short pitch email (under 200 words) to an article author/editor suggesting Nothing Phone as a relevant inclusion in their list or review. Be specific about what makes Nothing Phone worth including."
        else:
            role = "content strategist"
            task = "generate a specific, ready-to-use content piece (under 250 words) that addresses this AI citation gap. Focus on clarity and actionability."

        prompt = ChatPromptTemplate.from_template("""You are a {role} at Nothing Technology (the phone brand by Carl Pei, competing with Apple and Samsung).
Based on this recommendation: '{action_text}', {task}""")

        chain = prompt | self.model
        response = await chain.ainvoke(
            {"role": role, "action_text": action_text, "task": task}
        )
        return response.content.strip()

    async def fetch_and_analyze(
        self, url: str, competitor_data: str = "", skip_ai: bool = False
    ):
        """Deep technical audit using Playwright and Gemini."""
        logs = []
        start_time = time.time()
        signals = {}

        async with httpx.AsyncClient() as client:
            try:
                logs.append("Phase 1: Deep Content Probe...")
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                raw_response = await client.get(
                    url, timeout=10.0, headers=headers, follow_redirects=True
                )
                raw_soup = BeautifulSoup(raw_response.text, "html.parser")
                signals["raw_text_length"] = len(raw_soup.get_text())
                logs.append(f"Probe successful ({signals['raw_text_length']} chars).")
            except Exception as e:
                logs.append(f"Probe Warning: {str(e)}")
                signals["raw_text_length"] = 0

        logs.append("Phase 2: Initializing Browser Render...")
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    viewport={"width": 1280, "height": 800},
                )
                page = await context.new_page()

                # Metric 1: Console Errors
                console_errors = []
                page.on("pageerror", lambda err: console_errors.append(str(err)))

                # Metric 2: Total JS Payload Size
                js_bytes = []

                def on_response(r):
                    try:
                        ctype = r.headers.get("content-type", "")
                        if "javascript" in ctype:
                            length = r.headers.get("content-length")
                            if length and length.isdigit():
                                js_bytes.append(int(length))
                    except Exception:
                        pass

                page.on("response", on_response)

                # Metric 3: Unused JS Coverage via CDP
                cdp = None
                try:
                    cdp = await context.new_cdp_session(page)
                    await cdp.send("Profiler.enable")
                    await cdp.send(
                        "Profiler.startPreciseCoverage",
                        {"callCount": False, "detailed": True},
                    )
                except Exception:
                    cdp = None

                await page.goto(url, wait_until="load", timeout=20000)
                await asyncio.sleep(0.5)

                try:
                    if cdp:
                        res = await cdp.send("Profiler.takePreciseCoverage")
                        js_coverage = res.get("result", [])
                    else:
                        js_coverage = []
                except Exception:
                    js_coverage = []

                try:
                    total_funcs = 0
                    used_funcs = 0
                    for script in js_coverage:
                        funcs = script.get("functions", [])
                        total_funcs += len(funcs)
                        for f in funcs:
                            ranges = f.get("ranges", [])
                            if ranges and ranges[0].get("count", 0) > 0:
                                used_funcs += 1

                    signals["unused_js_pct"] = (
                        round((1 - used_funcs / total_funcs) * 100)
                        if total_funcs > 0
                        else 0
                    )
                except Exception:
                    signals["unused_js_pct"] = None

                try:
                    signals["console_errors"] = len(console_errors)
                    signals["console_error_details"] = console_errors[:3]
                except Exception:
                    signals["console_errors"] = None
                    signals["console_error_details"] = []

                try:
                    signals["js_payload_mb"] = round(
                        sum(b for b in js_bytes if b) / (1024 * 1024), 2
                    )
                except Exception:
                    signals["js_payload_mb"] = None

                rendered_html = await page.content()
                rendered_soup = BeautifulSoup(rendered_html, "html.parser")
                rendered_text = rendered_soup.get_text()

                # Metric 4: Largest Contentful Paint (LCP)
                try:
                    lcp_ms = await page.evaluate("""
                        () => new Promise(resolve => {
                            let lcp = 0;
                            new PerformanceObserver(list => {
                                const entries = list.getEntries();
                                if (entries.length > 0) {
                                    lcp = entries[entries.length - 1].startTime;
                                }
                            }).observe({ type: 'largest-contentful-paint', buffered: true });
                            setTimeout(() => resolve(lcp), 500);
                        })
                    """)
                    signals["lcp_seconds"] = round(float(lcp_ms) / 1000, 2)
                except Exception:
                    signals["lcp_seconds"] = None

                signals["load_time_ms"] = int((time.time() - start_time) * 1000)
                signals["text_delta"] = len(rendered_text) - signals["raw_text_length"]

                # JS Impact thresholds
                if signals["text_delta"] > 2000:
                    signals["js_impact"] = "CRITICAL"
                elif signals["text_delta"] > 500:
                    signals["js_impact"] = "MODERATE"
                else:
                    signals["js_impact"] = "LOW"

                signals["has_json_ld"] = bool(
                    rendered_soup.find("script", type="application/ld+json")
                )
                signals["dom_depth"] = await page.evaluate(
                    "const getDepth = (node) => node.children.length > 0 ? 1 + Math.max(...Array.from(node.children).map(getDepth)) : 1; getDepth(document.body)"
                )
            except Exception as e:
                logs.append(f"BROWSER_ERROR: {str(e)}")
                return {
                    "error": True,
                    "logs": logs,
                    "message": f"Rendering failed: {str(e)}",
                }
            finally:
                if "browser" in locals():
                    await browser.close()

        if skip_ai:
            return {
                "performance_report": {"score": 0, "issues": [], "fixes": []},
                "sitemap_audit": {"score": 0, "analysis": "", "improvements": []},
                "competitive_analysis": {"competitor_edge": "", "gap_to_close": ""},
                "ai_readiness": {"overall_score": 0, "estimated_impact": ""},
                "logs": logs,
                "signals": signals,
                "guidance": self._generate_guidance(signals),
                "execution_time_ms": int((time.time() - start_time) * 1000),
            }

        logs.append("Phase 3: AI Audit Reasoning...")
        prompt = ChatPromptTemplate.from_template("""Perform a triple-track AI Citation Audit for: {url}.
Technical: {signals}. Content Sample: {content_sample}.
Competitors: {competitor_data}.
Return ONLY valid JSON: {{
    "performance_report": {{"score": 0, "issues": [], "fixes": []}},
    "sitemap_audit": {{"score": 0, "analysis": "", "improvements": []}},
    "competitive_analysis": {{"competitor_edge": "", "gap_to_close": ""}},
    "ai_readiness": {{"overall_score": 0, "estimated_impact": ""}}
}}
Ensure the JSON is properly formatted and includes all keys.""")

        try:
            chain = prompt | self.model
            response = await chain.ainvoke(
                {
                    "url": url,
                    "signals": json.dumps(signals),
                    "content_sample": rendered_text[:10000],
                    "competitor_data": competitor_data,
                }
            )
            res_text = response.content.strip()
            if "```json" in res_text:
                res_text = res_text.split("```json")[1].split("```")[0].strip()
            result = json.loads(res_text)
            result["logs"] = logs
            result["signals"] = signals
            result["guidance"] = self._generate_guidance(signals)
            result["execution_time_ms"] = int((time.time() - start_time) * 1000)
            return result
        except Exception as e:
            logs.append(f"Phase 3 Failed: {str(e)}")
            return {
                "error": True,
                "logs": logs,
                "message": str(e),
                "signals": signals if "signals" in locals() else {},
            }

    async def audit_url(self, url: str, competitor_data: str = ""):
        return await self.fetch_and_analyze(url, competitor_data)
