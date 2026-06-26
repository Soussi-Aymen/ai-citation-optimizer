from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.peec_client import PeecClient


def test_is_configured_rejects_empty_and_placeholders(monkeypatch):
    monkeypatch.delenv("PEEC_API_KEY", raising=False)
    assert PeecClient().is_configured is False

    monkeypatch.setenv("PEEC_API_KEY", "your_peec_api_key")
    assert PeecClient().is_configured is False

    monkeypatch.setenv("PEEC_API_KEY", "sk-live-real-key")
    assert PeecClient().is_configured is True


@pytest.mark.asyncio
async def test_is_available_false_when_not_configured(monkeypatch):
    monkeypatch.delenv("PEEC_API_KEY", raising=False)
    client = PeecClient()
    assert await client.is_available() is False


@pytest.mark.asyncio
async def test_is_available_false_on_auth_error(monkeypatch):
    monkeypatch.setenv("PEEC_API_KEY", "invalid-key")

    response = httpx.Response(401, request=httpx.Request("POST", "http://test"))
    mock_client = AsyncMock()
    mock_client.post.return_value = response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("app.peec_client.httpx.AsyncClient", return_value=mock_client):
        client = PeecClient()
        assert await client.is_available() is False


@pytest.mark.asyncio
async def test_post_returns_empty_when_unconfigured(monkeypatch):
    monkeypatch.delenv("PEEC_API_KEY", raising=False)
    client = PeecClient()
    result = await client.get_domain_report("example.com")
    assert result == {}
