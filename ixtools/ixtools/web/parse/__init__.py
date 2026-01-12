"""
HTML parsing and content extraction tools.
"""

from .parse_html import parse_html, extract_text, find_elements
from .extract_from_page import extract_from_page
from .answer_question_about_page import answer_question_about_page
from .summarize_page import summarize_page

__all__ = [
    "parse_html",
    "extract_text",
    "find_elements",
    "extract_from_page",
    "answer_question_about_page",
    "summarize_page",
]

