"""
Tests for parse_html, extract_text, and find_elements tools.
"""

import pytest

from ixmachina.tools.web import parse_html, extract_text, find_elements


def test_parse_html_basic():
    """Test parse_html parses basic HTML."""
    html = "<html><head><title>Test Page</title></head><body><p>Hello World</p></body></html>"
    result = parse_html(html)
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert result["title"] == "Test Page"
    assert "text" in result
    assert "Hello World" in result["text"]
    assert result["elements"] is None
    assert result["error"] is None


def test_parse_html_with_selector():
    """Test parse_html extracts elements by CSS selector."""
    html = "<html><body><div class='price'>$99.99</div><div class='price'>$149.99</div></body></html>"
    result = parse_html(html, selector=".price")
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert result["elements"] is not None
    assert len(result["elements"]) == 2
    assert result["count"] == 2
    assert result["elements"][0]["text"] == "$99.99"
    assert result["elements"][1]["text"] == "$149.99"


def test_parse_html_selector_not_found():
    """Test parse_html handles selector that finds nothing."""
    html = "<html><body><p>No prices here</p></body></html>"
    result = parse_html(html, selector=".price")
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert result["elements"] == []
    assert result["count"] == 0


def test_parse_html_element_structure():
    """Test parse_html returns proper element structure."""
    html = '<html><body><a href="/link" class="test">Link Text</a></body></html>'
    result = parse_html(html, selector="a")
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert len(result["elements"]) == 1
    element = result["elements"][0]
    assert element["text"] == "Link Text"
    assert element["tag"] == "a"
    assert "href" in element["attributes"]
    assert element["attributes"]["href"] == "/link"
    assert "class" in element["attributes"]
    assert "html" in element


def test_parse_html_invalid_html():
    """Test parse_html handles invalid HTML gracefully."""
    html = "<html><body><p>Unclosed tag</body>"
    result = parse_html(html)
    
    # BeautifulSoup is lenient, so it should still parse
    assert isinstance(result, dict)
    assert result["success"] is True


def test_extract_text_basic():
    """Test extract_text extracts plain text from HTML."""
    html = "<html><head><title>Title</title></head><body><h1>Heading</h1><p>Paragraph text</p></body></html>"
    text = extract_text(html)
    
    assert isinstance(text, str)
    assert "Title" in text
    assert "Heading" in text
    assert "Paragraph text" in text
    assert "<" not in text  # No HTML tags


def test_extract_text_empty():
    """Test extract_text handles empty HTML."""
    text = extract_text("")
    
    assert isinstance(text, str)
    assert len(text) == 0 or text.strip() == ""


def test_extract_text_with_whitespace():
    """Test extract_text handles whitespace properly."""
    html = "<p>Line 1</p><p>Line 2</p>"
    text = extract_text(html)
    
    assert "Line 1" in text
    assert "Line 2" in text


def test_find_elements_by_class():
    """Test find_elements finds elements by class selector."""
    html = '<div class="price">$10</div><div class="price">$20</div><div class="other">Not a price</div>'
    elements = find_elements(html, ".price")
    
    assert isinstance(elements, list)
    assert len(elements) == 2
    assert elements[0]["text"] == "$10"
    assert elements[1]["text"] == "$20"


def test_find_elements_by_tag():
    """Test find_elements finds elements by tag name."""
    html = "<p>First paragraph</p><p>Second paragraph</p>"
    elements = find_elements(html, "p")
    
    assert isinstance(elements, list)
    assert len(elements) == 2
    assert elements[0]["text"] == "First paragraph"
    assert elements[1]["text"] == "Second paragraph"
    assert all(elem["tag"] == "p" for elem in elements)


def test_find_elements_by_id():
    """Test find_elements finds element by ID."""
    html = '<div id="main">Main content</div><div>Other content</div>'
    elements = find_elements(html, "#main")
    
    assert isinstance(elements, list)
    assert len(elements) == 1
    assert elements[0]["text"] == "Main content"
    assert elements[0]["attributes"]["id"] == "main"


def test_find_elements_not_found():
    """Test find_elements returns empty list when nothing found."""
    html = "<p>No prices here</p>"
    elements = find_elements(html, ".price")
    
    assert isinstance(elements, list)
    assert len(elements) == 0


def test_find_elements_complex_selector():
    """Test find_elements with complex CSS selector."""
    html = '<div class="product"><span class="price">$99</span></div><div class="product"><span class="price">$149</span></div>'
    elements = find_elements(html, "div.product span.price")
    
    assert isinstance(elements, list)
    assert len(elements) == 2
    assert elements[0]["text"] == "$99"
    assert elements[1]["text"] == "$149"

