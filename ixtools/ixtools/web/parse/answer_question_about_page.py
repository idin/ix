"""
Answer questions about web page content using LLM.
"""

from typing import Dict, Any, Optional

from ..fetch.fetch_url import fetch_url
from .parse_html import extract_text
from ..utils.constants import BROWSER_USER_AGENT


def answer_question_about_page(
    url: str,
    question: str,
    llm: Any,
) -> Dict[str, Any]:
    """
    Answer a question about the content of a web page using an LLM.
    
    Fetches the page, extracts text content, and uses the LLM to answer
    the question based on the page content.
    
    Args:
        url: The URL of the web page.
        question: The question to answer about the page.
        llm: LLM instance to use for answering.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if operation was successful
            - answer: The answer to the question
            - url: The URL that was queried
            - question: The original question
            - error: Error message if operation failed (None if successful)
    """
    try:
        # Fetch the page with browser headers
        headers = {"User-Agent": BROWSER_USER_AGENT}
        page_response = fetch_url(url=url, headers=headers)
        
        if not page_response["success"]:
            return {
                "success": False,
                "answer": None,
                "url": url,
                "question": question,
                "error": f"Failed to fetch page: {page_response['error']}",
            }
        
        # Extract text from HTML
        html_content = page_response["content"]
        page_text = extract_text(html_content)
        
        # Truncate if too long (LLMs have token limits)
        if len(page_text) > 8000:
            page_text = page_text[:8000] + "..."
        
        # Create prompt for LLM
        prompt = (
            f"Based on the following web page content, answer this question:\n\n"
            f"Question: {question}\n\n"
            f"Web page content:\n"
            f"{page_text}\n\n"
            f"Answer the question based only on the information provided in the web page content. "
            f"If the answer cannot be found in the content, say \"The answer is not found in the page content.\""
        )
        
        llm_response = llm.query(user_prompt=prompt)
        
        # LLM.query can return string or dict (with "content" key when usage tracking is enabled)
        if isinstance(llm_response, dict):
            answer = llm_response.get("content", str(llm_response))
        else:
            answer = str(llm_response)
        
        return {
            "success": True,
            "answer": answer.strip(),
            "url": url,
            "question": question,
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "answer": None,
            "url": url,
            "question": question,
            "error": f"Error answering question: {str(e)}",
        }

