def expected_schema_type(url: str) -> str:
    """Path rule shared with JSON-LD templates. Template bodies stay unchanged."""
    if "/products/" in url:
        return "Product"
    if "/pages/" in url:
        return "Organization"
    if "/collections/" in url:
        return "CollectionPage"
    return "WebPage"
