"""
Web-related tools for fetching URLs, scraping, etc.
"""

from .fetch_url import fetch_url, fetch_json, post_request
from .parse_html import parse_html, extract_text, find_elements
from .search import search_web, search_web_simple
from .extract_from_page import extract_from_page
from .check_url_status import check_url_status
from .username_search import (
    discover_username_url_pattern,
    discover_username_signature,
    generate_non_existing_username,
    KNOWN_EXISTING_USERNAMES,
)
from .extract_domain import extract_domain

__all__ = [
    "fetch_url",
    "fetch_json",
    "post_request",
    "parse_html",
    "extract_text",
    "find_elements",
    "search_web",
    "search_web_simple",
    "extract_from_page",
    "check_url_status",
    "discover_username_url_pattern",
    "discover_username_signature",
    "generate_non_existing_username",
    "KNOWN_EXISTING_USERNAMES",
    "extract_domain",
]
