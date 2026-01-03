"""
Web-related tools for fetching URLs, scraping, etc.
"""

from .fetch import (
    fetch_url,
    fetch_json,
    post_request,
    check_url_status,
)
from .parse import (
    parse_html,
    extract_text,
    find_elements,
    extract_from_page,
    answer_question_about_page,
    summarize_page,
)
from .search import search_web, search_web_simple, search_brave
from .username_search import (
    discover_username_url_pattern,
    discover_username_signature,
    generate_non_existing_username,
    KNOWN_EXISTING_USERNAMES,
    check_username_availability,
    check_single_username_exists,
)
from .utils import extract_domain, filter_by_domain, BROWSER_USER_AGENT

__all__ = [
    "fetch_url",
    "fetch_json",
    "post_request",
    "check_url_status",
    "parse_html",
    "extract_text",
    "find_elements",
    "extract_from_page",
    "answer_question_about_page",
    "summarize_page",
    "search_web",
    "search_web_simple",
    "search_brave",
    "discover_username_url_pattern",
    "discover_username_signature",
    "generate_non_existing_username",
    "KNOWN_EXISTING_USERNAMES",
    "check_username_availability",
    "check_single_username_exists",
    "extract_domain",
    "filter_by_domain",
    "BROWSER_USER_AGENT",
]
