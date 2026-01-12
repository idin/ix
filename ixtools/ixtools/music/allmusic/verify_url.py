"""
Verify that an AllMusic URL matches a search query.
"""

from typing import Dict, Any
from ...web.fetch.fetch_url import fetch_url
from ...constants import SUCCESS_KEY, RESULT_KEY, ERROR_KEY, METADATA_KEY
from ...web.utils.constants import BROWSER_USER_AGENT
from ...web.parse.parse_html import extract_text, parse_html
from ...string.smart_truncate import smart_truncate_text
from ixutils import persist
from .constants import DEFAULT_TIMEOUT


@persist(expire_seconds=60 * 60 * 24 * 365)  # Cache for 1 year
def verify_allmusic_url(
    url: str,
    query: str,
    llm: Any,
) -> Dict[str, Any]:
    """
    Verify that an AllMusic URL matches the search query.
    
    Fetches the AllMusic page and uses an LLM to verify that the page
    content matches the query (e.g., correct artist, album, or song).
    
    Args:
        url: AllMusic URL to verify (artist, album, or song page).
        query: Original search query that should match this URL.
        llm: LLM instance to use for verification.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if verification was successful
            - result: Dictionary containing:
                - matches: Boolean indicating if URL matches the query
                - title: Page title from AllMusic
                - confidence: Confidence level ("high", "medium", "low") if matches is True
                - reason: Explanation of why it matches or doesn't match
            - metadata: Dictionary with:
                - url: The AllMusic URL verified
                - query: The search query
            - error: Error message if verification failed (None if successful)
    """
    try:
        # Fetch the page
        headers = {"User-Agent": BROWSER_USER_AGENT}
        page_response = fetch_url(url=url, headers=headers, timeout=DEFAULT_TIMEOUT)
        
        if not page_response["success"]:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                METADATA_KEY: {
                    "url": url,
                    "query": query,
                },
                ERROR_KEY: f"Failed to fetch AllMusic page: {page_response.get('error', 'Unknown error')}",
            }
        
        html_content = page_response.get("content", "")
        page_text = extract_text(html_content)
        
        # Extract title from page
        parsed = parse_html(html_content)
        title = parsed.get("title", "").split("|")[0].strip() if parsed.get("title") else ""
        
        # Smart truncation focusing on title and key information
        limited_text = smart_truncate_text(
            text=page_text,
            search_terms=query.split(),
            max_length=6000,
        )
        
        # Use LLM to verify if the page matches the query
        prompt = (
            f"Verify if this AllMusic page matches the search query: '{query}'\n\n"
            f"Page title: {title}\n\n"
            f"Page content (truncated):\n{limited_text[:4000]}\n\n"
            "Determine if this page is the correct result for the query. Consider:\n"
            "- Does the artist name match?\n"
            "- Does the album/song name match?\n"
            "- Is this the right version/release?\n\n"
            "Return in this exact format: 'Matches: yes/no | Confidence: high/medium/low | Reason: brief explanation'\n"
            "If the page clearly matches the query, use 'yes' and 'high' confidence.\n"
            "If it's likely but not certain, use 'yes' and 'medium' confidence.\n"
            "If it's unclear or doesn't match, use 'no' and explain why.\n\n"
            "Return only the formatted result, nothing else."
        )
        
        llm_response = llm.query(user_prompt=prompt)
        
        # Parse LLM response
        if isinstance(llm_response, dict):
            extracted_text = llm_response.get("content", str(llm_response))
        else:
            extracted_text = str(llm_response)
        
        extracted_text = extracted_text.strip()
        
        # Parse the response
        matches = False
        confidence = "low"
        reason = "Could not parse verification response"
        
        if "Matches:" in extracted_text:
            matches_part = extracted_text.split("Matches:")[1].split("|")[0].strip().lower()
            matches = matches_part in ["yes", "true", "1"]
        
        if "Confidence:" in extracted_text:
            confidence_part = extracted_text.split("Confidence:")[1].split("|")[0].strip().lower()
            if confidence_part in ["high", "medium", "low"]:
                confidence = confidence_part
        
        if "Reason:" in extracted_text:
            reason_part = extracted_text.split("Reason:")[1].strip()
            if reason_part:
                reason = reason_part
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: {
                "matches": matches,
                "title": title,
                "confidence": confidence if matches else "low",
                "reason": reason,
            },
            METADATA_KEY: {
                "url": url,
                "query": query,
            },
            ERROR_KEY: None,
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            METADATA_KEY: {
                "url": url,
                "query": query,
            },
            ERROR_KEY: f"Error verifying AllMusic URL: {str(e)}",
        }

