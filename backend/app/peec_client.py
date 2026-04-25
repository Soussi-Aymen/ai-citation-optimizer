import os
import httpx
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class PeecClient:
    def __init__(self):
        self.api_key = os.getenv("PEEC_API_KEY")
        self.base_url = "https://api.peec.ai/customer/v1"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        self._cache = {}

    def _get_cache(self, key):
        if key in self._cache:
            data, timestamp = self._cache[key]
            if time.time() - timestamp < 3600: # 1 hour cache
                return data
        return None

    def _set_cache(self, key, data):
        self._cache[key] = (data, time.time())

    async def _post(self, endpoint, payload):
        cache_key = f"{endpoint}:{json.dumps(payload, sort_keys=True)}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/{endpoint}",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                self._set_cache(cache_key, data)
                return data
            except Exception as e:
                print(f"Peec API Error ({endpoint}): {e}")
                return {}

    async def get_domain_report(self, domain: str):
        return await self._post("reports", {"domain": domain})

    async def get_cited_urls(self, domain: str):
        report = await self.get_domain_report(domain)
        items = report.get('data', [])
        if isinstance(items, dict): items = [items]
        cited_urls = []
        for item in items:
            url = item.get('url') or item.get('cited_url') or item.get('source_url')
            if url and domain in url:
                cited_urls.append(url)
            citations = item.get('citations', [])
            if isinstance(citations, list):
                for c in citations:
                    c_url = c.get('url') or c.get('source_url')
                    if c_url and domain in c_url:
                        cited_urls.append(c_url)
        return list(set(u.rstrip('/') for u in cited_urls))

    async def list_brands(self, project_id: str):
        """Lists brands associated with a project."""
        return await self._post("brands", {"project_id": project_id})

    async def get_actions(self, project_id: str, scope: str = "overview", **kwargs):
        """Fetches AI citation actions/gaps."""
        today = datetime.now()
        start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        
        payload = {
            "project_id": project_id,
            "scope": scope,
            "start_date": start_date,
            "end_date": end_date
        }
        for k, v in kwargs.items():
            if v is not None:
                payload[k] = v
            
        return await self._post("actions", payload)
