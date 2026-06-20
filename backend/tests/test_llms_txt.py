"""Unit tests for llms.txt parsing and template generation."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.llms_txt_analyzer import (
    build_llms_txt_template,
    page_listed_in_llms_txt,
    parse_llms_txt_links,
    validate_llms_txt,
)


def test_parse_llms_txt_links():
    content = """# Nothing

> A phone brand.

## Priority Pages

- [Phone 2](https://nothing.tech/products/phone-2): Flagship device
- [About](https://nothing.tech/pages/about)
"""
    links = parse_llms_txt_links(content)
    assert "https://nothing.tech/products/phone-2" in links
    assert len(links) == 2


def test_page_listed_in_llms_txt():
    links = ["https://nothing.tech/products/phone-2"]
    assert page_listed_in_llms_txt("https://nothing.tech/products/phone-2/", links)
    assert not page_listed_in_llms_txt("https://nothing.tech/products/other", links)


def test_validate_llms_txt():
    assert validate_llms_txt("# Brand\n\n> Summary")
    assert not validate_llms_txt("No heading here")


def test_build_llms_txt_template():
    url = "https://example.com/products/widget"
    template = build_llms_txt_template(url)
    assert "# Example" in template
    assert url in template
    assert "https://example.com/llms.txt" in template
