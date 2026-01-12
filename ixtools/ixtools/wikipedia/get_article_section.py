"""
Get a specific section from a Wikipedia article.
"""

from typing import Dict, Any
import re

from .normalize_article_title import normalize_article_title


def get_article_section(
    title: str,
    section_name: str,
    language: str = "en",
) -> Dict[str, Any]:
    """
    Get a specific section from a Wikipedia article.
    
    Args:
        title: Article title (will be normalized automatically).
        section_name: Name of the section to retrieve (e.g., "History", "See also").
        language: Wikipedia language code (e.g., "en", "fr", "de"). Default: "en".
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if retrieval was successful
            - title: The canonical article title
            - section_name: The requested section name
            - content: Content of the section
            - found: Boolean indicating if the section was found
            - language: The language code used
            - error: Error message if retrieval failed (None if successful)
    """
    # First normalize the title to get canonical form
    normalize_result = normalize_article_title(title=title, language=language)
    
    if not normalize_result.get("success"):
        return {
            "success": False,
            "title": None,
            "section_name": section_name,
            "content": None,
            "found": False,
            "language": language,
            "error": normalize_result.get("error"),
        }
    
    canonical_title = normalize_result["canonical_title"]
    
    # Get full article first
    # Lazy import to avoid circular dependencies
    from .get_wikipedia_article import get_wikipedia_article
    
    article_result = get_wikipedia_article(
        title=canonical_title,
        language=language,
        summary_only=False,
    )
    
    if not article_result.get("success"):
        return {
            "success": False,
            "title": canonical_title,
            "section_name": section_name,
            "content": None,
            "found": False,
            "language": language,
            "error": article_result.get("error"),
        }
    
    full_content = article_result.get("content", "")
    
    # Parse sections from content
    # Wikipedia API's explaintext returns sections where headers are on their own lines
    # Sections are typically capitalized and followed by content
    lines = full_content.split("\n")
    
    sections = {}
    current_section = None
    current_content = []
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # Check if this line is a section header
        # Section headers are typically:
        # - On their own line
        # - Capitalized (first letter uppercase)
        # - Followed by a blank line or content
        # - Not too long (reasonable section name length)
        is_section_header = (
            line_stripped and
            len(line_stripped) < 100 and  # Reasonable section name length
            line_stripped[0].isupper() and  # Starts with capital letter
            (i == 0 or not lines[i-1].strip()) and  # Preceded by blank line or is first line
            (i + 1 < len(lines)) and  # Not the last line
            (not lines[i+1].strip() or lines[i+1][0].isupper() or lines[i+1][0].isdigit())  # Followed by blank or content
        )
        
        # Additional check: if line is all caps or has specific patterns, it might be a header
        if not is_section_header and line_stripped:
            # Check if it looks like a section header (short, capitalized words)
            words = line_stripped.split()
            if len(words) <= 10 and all(word[0].isupper() if word else False for word in words if word):
                # Could be a section header, but be more conservative
                # Only treat as header if it's followed by content that doesn't start with capital
                if i + 1 < len(lines) and lines[i+1].strip():
                    next_line = lines[i+1].strip()
                    if next_line and not next_line[0].isupper():
                        is_section_header = True
        
        if is_section_header:
            # Save previous section
            if current_section:
                sections[current_section] = "\n".join(current_content).strip()
            # Start new section
            current_section = line_stripped
            current_content = []
        else:
            if current_section:
                current_content.append(line)
            elif not current_section:
                # Content before first section (intro)
                if "intro" not in sections:
                    sections["intro"] = []
                sections["intro"].append(line)
    
    # Save last section
    if current_section:
        sections[current_section] = "\n".join(current_content).strip()
    
    # Normalize section name for matching (case-insensitive)
    section_name_lower = section_name.lower().strip()
    found_section = None
    found_content = None
    
    for section_title, section_content in sections.items():
        if section_title.lower() == section_name_lower:
            found_section = section_title
            found_content = section_content
            break
    
    if not found_section:
        return {
            "success": True,
            "title": article_result.get("title", canonical_title),
            "section_name": section_name,
            "content": None,
            "found": False,
            "language": language,
            "error": None,
        }
    
    return {
        "success": True,
        "title": article_result.get("title", canonical_title),
        "section_name": found_section,
        "content": found_content,
        "found": True,
        "language": language,
        "error": None,
    }

