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

    async def mock_ainvoke(*_args, **_kwargs):
        return type(
            "obj",
            (object,),
            {
                "content": (
                    '{"performance_report":{"score":0,"issues":[],"fixes":[]},'
                    '"sitemap_audit":{"score":0,"analysis":"","improvements":[]},'
                    '"competitive_analysis":{"competitor_edge":"","gap_to_close":""},'
                    '"ai_readiness":{"overall_score":0,"estimated_impact":""}}'
                )
            },
        )()

    agent.model.ainvoke = mock_ainvoke

    result = await agent.fetch_and_analyze("https://react.dev")
    signals = result.get("signals", {})

    assert signals.get("lcp_seconds") is not None
    assert signals.get("unused_js_pct") is not None
