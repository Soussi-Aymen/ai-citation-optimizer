import os
import sys
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, Mock

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

SAMPLE_SITEMAP = {
    "urls": [
        "https://example.com/page-a",
        "https://example.com/page-b",
        "https://example.com/page-c",
    ],
    "metrics": {"total_count": 3, "has_lastmod": True},
}


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_sitemap(monkeypatch):
    async def _fetch(_domain: str):
        return SAMPLE_SITEMAP

    monkeypatch.setattr("app.main.fetch_sitemap_urls", _fetch)


@pytest.fixture
def mock_peec_unavailable(monkeypatch):
    peec = AsyncMock()
    peec.is_available.return_value = False
    peec.get_cited_urls.return_value = []
    peec.list_brands.return_value = {"data": []}
    peec.get_domain_report.return_value = {"data": []}
    peec.get_actions.return_value = {"data": []}
    monkeypatch.setattr("app.main.peec", peec)
    return peec


@pytest.fixture
def mock_peec_available(monkeypatch):
    peec = AsyncMock()
    peec.is_available.return_value = True
    peec.get_cited_urls.return_value = ["https://example.com/page-a"]
    peec.list_brands.return_value = {
        "data": [
            {
                "name": "Example",
                "domain": "example.com",
                "is_own": True,
            }
        ]
    }
    peec.get_domain_report.return_value = {
        "data": [{"visibility_score": 42, "citation_count": 1}]
    }
    peec.get_actions.return_value = {"data": []}
    monkeypatch.setattr("app.main.peec", peec)
    return peec


@pytest.fixture
def mock_agent(monkeypatch):
    agent = Mock()
    agent.build_fix_instructions.return_value = {
        "problem": "Test problem",
        "checklist": ["Step 1"],
        "json_ld": '{"@type": "Product"}',
        "llms_txt_template": "# Example\n",
    }
    agent.fetch_and_analyze = AsyncMock(
        return_value={
            "signals": {"js_impact": "LOW", "has_llms_txt": False},
            "guidance": [],
        }
    )
    agent.generate_action_content = AsyncMock(return_value="Draft outreach content")
    agent.audit_url = AsyncMock(
        return_value={
            "signals": {"load_time_ms": 1200},
            "guidance": [],
        }
    )
    monkeypatch.setattr("app.main.agent", agent)
    return agent
