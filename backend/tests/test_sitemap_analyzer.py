from app.sitemap_analyzer import get_ai_citation_gaps


def test_get_ai_citation_gaps_finds_missing_pages():
    sitemap = [
        "https://example.com/a",
        "https://example.com/b/",
        "https://example.com/c",
    ]
    cited = ["https://example.com/a/"]

    gaps, orphans = get_ai_citation_gaps(sitemap, cited)

    assert "https://example.com/b" in gaps
    assert "https://example.com/c" in gaps
    assert "https://example.com/a" not in gaps
    assert orphans == []


def test_get_ai_citation_gaps_finds_orphans():
    sitemap = ["https://example.com/a"]
    cited = ["https://example.com/a", "https://other.com/cited"]

    gaps, orphans = get_ai_citation_gaps(sitemap, cited)

    assert gaps == []
    assert "https://other.com/cited" in orphans
