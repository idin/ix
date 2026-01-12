"""
Summarize web page content using LLM.
"""

from typing import Dict, Any, Optional

from ..fetch.fetch_url import fetch_url
from .parse_html import extract_text
from ..utils.constants import BROWSER_USER_AGENT


def summarize_page(
    url: str,
    llm: Any,
    max_length: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Summarize the content of a web page using an LLM.
    
    Fetches the page, extracts text content, and uses the LLM to generate
    a summary of the page.
    
    Args:
        url: The URL of the web page to summarize.
        llm: LLM instance to use for summarization.
        max_length: Optional maximum length for the summary in words.
                   If None, LLM will determine appropriate length. Default: None.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if summarization was successful
            - summary: The generated summary
            - url: The URL that was summarized
            - error: Error message if summarization failed (None if successful)
    """
    try:
        # Fetch the page with browser headers
        headers = {"User-Agent": BROWSER_USER_AGENT}
        page_response = fetch_url(url=url, headers=headers)
        
        if not page_response["success"]:
            return {
                "success": False,
                "summary": None,
                "url": url,
                "error": f"Failed to fetch page: {page_response['error']}",
            }
        
        # Extract text from HTML
        html_content = page_response["content"]
        page_text = extract_text(html_content)
        
        # Truncate if too long (LLMs have token limits)
        if len(page_text) > 8000:
            page_text = page_text[:8000] + "..."
        
        # Create prompt for LLM
        length_instruction = ""
        if max_length:
            length_instruction = f" The summary should be approximately {max_length} words."
        
        prompt = (
            f"Summarize the following web page content.{length_instruction}\n\n"
            f"Web page content:\n"
            f"{page_text}\n\n"
            f"Provide a clear, concise summary of the main points and key information."
        )
        
        llm_response = llm.query(user_prompt=prompt)
        
        # LLM.query can return string or dict (with "content" key when usage tracking is enabled)
        if isinstance(llm_response, dict):
            summary = llm_response.get("content", str(llm_response))
        else:
            summary = str(llm_response)
        
        return {
            "success": True,
            "summary": summary.strip(),
            "url": url,
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "summary": None,
            "url": url,
            "error": f"Error summarizing page: {str(e)}",
        }

