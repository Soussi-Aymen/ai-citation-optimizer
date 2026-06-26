from app.agent import CrawlabilityAgent


def test_build_fix_instructions_for_product_url():
    agent = CrawlabilityAgent()
    result = agent.build_fix_instructions("https://example.com/products/widget")

    assert "JavaScript" in result["problem"]
    assert any("llms.txt" in item for item in result["checklist"])
    assert '"@type": "Product"' in result["json_ld"]
    assert "https://example.com/products/widget" in result["llms_txt_template"]


def test_build_fix_instructions_includes_json_ld_template():
    agent = CrawlabilityAgent()
    result = agent.build_fix_instructions("https://example.com/about")

    assert result["json_ld"]
    assert result["llms_txt_template"]
    assert len(result["checklist"]) >= 1
