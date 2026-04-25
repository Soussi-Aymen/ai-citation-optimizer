import os
import json
import asyncio
from playwright.async_api import async_playwright
import google.generativeai as genai
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

class CrawlabilityAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def fetch_html(self, url: str):
        """
        Fetches both raw HTML and rendered HTML (via Playwright).
        """
        # Raw HTML
        try:
            raw_response = requests.get(url, timeout=10)
            raw_html = raw_response.text
        except Exception:
            raw_html = ""

        # Rendered HTML
        rendered_html = ""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                rendered_html = await page.content()
            except Exception as e:
                print(f"Playwright error for {url}: {e}")
            finally:
                await browser.close()

        return raw_html, rendered_html

    def analyze_js_dependency(self, raw_html, rendered_html):
        """
        Compares raw and rendered HTML to detect JS dependency.
        """
        raw_len = len(raw_html)
        rendered_len = len(rendered_html)
        
        if raw_len == 0: return "high" # Couldn't even get raw
        
        diff_ratio = (rendered_len - raw_len) / raw_len if raw_len > 0 else 0
        
        if diff_ratio > 0.5:
            return "high"
        elif diff_ratio > 0.1:
            return "medium"
        else:
            return "low"

    async def audit_url(self, url: str):
        raw_html, rendered_html = await self.fetch_html(url)
        js_dependency = self.analyze_js_dependency(raw_html, rendered_html)
        
        # Extract main text content for Gemini (simplified)
        # In a real app, we'd use a better cleaner
        content_to_analyze = rendered_html[:15000] # Limit to 15k chars for prompt efficiency

        prompt = f"""
        You are an AI Search Optimization Expert. Analyze the following webpage content and determine its "AI Citation Readiness".
        Webpages are cited by AI search engines (ChatGPT, Gemini, Perplexity) if they are clear, authoritative, and easily parsable.

        URL: {url}
        JS Dependency: {js_dependency}
        Content Snippet:
        {content_to_analyze}

        Provide a structured JSON response with the following fields:
        {{
            "ai_readiness_score": number (0-100),
            "js_dependency": "{js_dependency}",
            "issues": ["list of strings explaining why an AI might ignore this page"],
            "fixes": ["list of strings with actionable steps to improve citation likelihood"],
            "estimated_impact": "string (e.g. +20% visibility)"
        }}
        Return ONLY the JSON.
        """

        try:
            response = self.model.generate_content(prompt)
            # Clean JSON from response if needed (sometimes Gemini wraps in ```json)
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:-3].strip()
            
            result = json.loads(text)
            return result
        except Exception as e:
            print(f"Gemini error: {e}")
            return {
                "ai_readiness_score": 50,
                "js_dependency": js_dependency,
                "issues": ["Error during AI analysis"],
                "fixes": ["Try again later"],
                "estimated_impact": "Unknown"
            }
