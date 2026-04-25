import asyncio
import sys
import os

# Add the backend directory to sys.path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent import CrawlabilityAgent

async def test_audit_metrics():
    """
    Tests the Playwright browser metrics logic (LCP, JS payload, Unused JS, Console Errors)
    without hitting the live Gemini API to keep the test fast.
    """
    print("Testing CrawlabilityAgent Performance Metrics on react.dev...")
    agent = CrawlabilityAgent()
    
    # Mock the Gemini call to return a stubbed JSON response
    original_generate = agent.model.generate_content
    agent.model.generate_content = lambda prompt: type('obj', (object,), {
        'text': '{"performance_report":{"score":0,"issues":[],"fixes":[]},"sitemap_audit":{"score":0,"analysis":"","improvements":[]},"competitive_analysis":{"competitor_edge":"","gap_to_close":""},"ai_readiness":{"overall_score":0,"estimated_impact":""}}'
    })()

    try:
        res = await agent.fetch_and_analyze("https://react.dev")
        signals = res.get("signals", {})
        
        print("\n--- Audit Metrics Retrieved ---")
        print(f"LCP (Seconds):      {signals.get('lcp_seconds')}")
        print(f"Console Errors:     {signals.get('console_errors')}")
        print(f"JS Payload (MB):    {signals.get('js_payload_mb')}")
        print(f"Unused JS (%):      {signals.get('unused_js_pct')}")
        print("-------------------------------")
        
        assert signals.get('lcp_seconds') is not None, "LCP was not measured"
        assert signals.get('unused_js_pct') is not None, "Unused JS was not measured"
        print("\n✅ Test Passed")
        
    finally:
        # Restore the original method
        agent.model.generate_content = original_generate

if __name__ == "__main__":
    asyncio.run(test_audit_metrics())
