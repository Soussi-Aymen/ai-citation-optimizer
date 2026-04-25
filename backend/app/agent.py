import os
import json
import asyncio
import time
from playwright.async_api import async_playwright
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

class CrawlabilityAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def fetch_and_analyze(self, url: str):
        """
        Performs a real browser audit using Playwright and extracts technical signals.
        """
        logs = []
        start_time = time.time()

        logs.append("Initiating raw HTML fetch...")
        try:
            raw_response = requests.get(url, timeout=10)
            raw_html = raw_response.text
            raw_soup = BeautifulSoup(raw_html, 'html.parser')
            raw_text_len = len(raw_soup.get_text())
        except Exception:
            raw_html = ""
            raw_text_len = 0

        logs.append("Launching headless browser for rendered audit...")
        rendered_html = ""
        signals = {}
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                logs.append(f"Navigating to {url} (waiting for network idle)...")
                nav_start = time.time()
                await page.goto(url, wait_until="networkidle", timeout=30000)
                load_time = time.time() - nav_start
                
                logs.append("Extracting DOM signals and JS impact...")
                rendered_html = await page.content()
                rendered_soup = BeautifulSoup(rendered_html, 'html.parser')
                rendered_text_len = len(rendered_soup.get_text())
                
                # Signals
                signals['load_time_ms'] = int(load_time * 1000)
                signals['raw_text_length'] = raw_text_len
                signals['rendered_text_length'] = rendered_text_len
                signals['js_text_gain_ratio'] = (rendered_text_len - raw_text_len) / raw_text_len if raw_text_len > 0 else 1.0
                signals['has_json_ld'] = bool(rendered_soup.find('script', type='application/ld+json'))
                signals['dom_nodes'] = await page.evaluate("document.querySelectorAll('*').length")
                
                # Check for meta tags
                signals['has_meta_description'] = bool(rendered_soup.find('meta', attrs={'name': 'description'}))
                signals['has_og_tags'] = bool(rendered_soup.find('meta', attrs={'property': 'og:title'}))

            except Exception as e:
                logs.append(f"Browser Error: {str(e)}")
            finally:
                await browser.close()

        logs.append("Sending technical signals to Gemini for AI Citation Audit...")
        
        # Determine JS Dependency label
        js_dep = "low"
        if signals.get('js_text_gain_ratio', 0) > 0.5:
            js_dep = "high"
        elif signals.get('js_text_gain_ratio', 0) > 0.1:
            js_dep = "medium"

        # Prepare content for Gemini
        content_snippet = rendered_html[:20000] # Increased limit for better context

        prompt = f"""
        You are an AI Citation Auditor. Analyze the technical signals and content of this webpage.
        The goal is to explain WHY an AI search engine (like ChatGPT or Gemini) might NOT cite this page.

        URL: {url}
        Technical Signals:
        - JS Dependency: {js_dep} (Text gain after rendering: {signals.get('js_text_gain_ratio', 0):.2f})
        - Load Time: {signals.get('load_time_ms', 0)}ms
        - Has Structured Data (JSON-LD): {signals.get('has_json_ld', False)}
        - Meta Description: {signals.get('has_meta_description', False)}
        - DOM Nodes: {signals.get('dom_nodes', 0)}
        - Content Length (Rendered): {signals.get('rendered_text_length', 0)} chars

        Content Snippet (First 20k chars):
        {content_snippet}

        Provide a structured JSON response. Ensure "estimated_impact" is a meaningful percentage (e.g., "+35% Visibility") based on the severity of issues.
        Return ONLY valid JSON:
        {{
            "ai_readiness_score": number (0-100),
            "js_dependency": "{js_dep}",
            "signals": {json.dumps(signals)},
            "issues": ["list of specific technical or content issues"],
            "fixes": ["actionable steps to fix"],
            "estimated_impact": "string like '+X% Visibility'"
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(text)
            result['logs'] = logs
            result['execution_time_ms'] = int((time.time() - start_time) * 1000)
            return result
        except Exception as e:
            print(f"Gemini error: {e}")
            return {
                "ai_readiness_score": 0,
                "js_dependency": js_dep,
                "issues": [f"AI Analysis Failed: {str(e)}"],
                "fixes": ["Check API credentials and retry"],
                "estimated_impact": "0%",
                "logs": logs,
                "signals": signals
            }

    async def audit_url(self, url: str):
        # Wrapper for compatibility
        return await self.fetch_and_analyze(url)
