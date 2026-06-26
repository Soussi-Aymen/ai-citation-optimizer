import pytest

from app.main import get_project_id


def test_get_project_id_maps_known_domains():
    assert get_project_id("nothing.tech") == get_project_id("www.nothing.tech")
    assert get_project_id("attio.com") != get_project_id("nothing.tech")


@pytest.mark.asyncio
async def test_health_reports_peec_availability(client, mock_peec_unavailable):
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"peec_available": False}


@pytest.mark.asyncio
async def test_gaps_without_peec_returns_sitemap_pages(
    client, mock_sitemap, mock_peec_unavailable
):
    response = await client.get("/api/gaps", params={"domain": "example.com"})
    assert response.status_code == 200

    data = response.json()
    assert data["peec_available"] is False
    assert data["total_sitemap_pages"] == 3
    assert data["total_cited_pages"] is None
    assert data["citation_coverage_pct"] is None
    assert data["performance_score"] is None
    assert len(data["gaps"]) == 3
    assert data["competitors"] == []


@pytest.mark.asyncio
async def test_gaps_with_peec_returns_citation_metrics(
    client, mock_sitemap, mock_peec_available
):
    response = await client.get("/api/gaps", params={"domain": "example.com"})
    assert response.status_code == 200

    data = response.json()
    assert data["peec_available"] is True
    assert data["total_cited_pages"] == 1
    assert data["citation_coverage_pct"] is not None
    assert data["performance_score"] is not None
    assert len(data["gaps"]) == 2


@pytest.mark.asyncio
async def test_benchmark_without_peec(client, mock_peec_unavailable):
    response = await client.get("/api/benchmark", params={"domain": "example.com"})
    assert response.status_code == 200
    assert response.json() == {"peec_available": False}


@pytest.mark.asyncio
async def test_generate_fix_returns_instruction_panel(client, mock_agent):
    response = await client.post(
        "/api/generate-fix",
        json={"url": "https://example.com/products/widget"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["problem"] == "Test problem"
    assert data["checklist"] == ["Step 1"]
    assert "metrics" in data
    assert data["llms_txt_template"].startswith("# Example")


@pytest.mark.asyncio
async def test_generate_content_returns_draft(client, mock_agent):
    response = await client.post(
        "/api/generate-content",
        json={"action_type": "email", "action_text": "Reach out to editors"},
    )
    assert response.status_code == 200
    assert response.json() == {"content": "Draft outreach content"}


@pytest.mark.asyncio
async def test_audit_skips_peec_when_unavailable(
    client, mock_peec_unavailable, mock_agent
):
    response = await client.post(
        "/api/audit",
        json={"url": "https://example.com/page"},
    )
    assert response.status_code == 200
    assert response.json()["url"] == "https://example.com/page"
    mock_agent.audit_url.assert_awaited_once()
    assert mock_agent.audit_url.await_args.kwargs.get("competitor_data") == ""
