import pytest

from app.agent import CrawlabilityAgent


@pytest.mark.integration
@pytest.mark.asyncio
async def test_audit_metrics():
    """
    Playwright integration: measures LCP, JS payload, and unused JS on react.dev.
    Run with: pytest -m integration
    """
    agent = CrawlabilityAgent()
    result = await agent.fetch_and_analyze("https://react.dev", skip_ai=True)
    signals = result.get("signals", {})

    assert signals.get("lcp_seconds") is not None
    assert signals.get("unused_js_pct") is not None
