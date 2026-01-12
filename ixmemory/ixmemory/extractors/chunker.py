"""
Text chunking utilities.

Splits large text into smaller overlapping chunks for processing.
"""

from typing import List


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Chunks text by character count, with overlap between consecutive
    chunks to avoid losing information at boundaries.
    
    Args:
        text: The text to chunk.
        chunk_size: Maximum size of each chunk in characters.
        overlap: Number of overlapping characters between chunks.
    
    Returns:
        List of text chunks.
    
    Example:
        >>> chunks = chunk_text("A very long text...", chunk_size=100, overlap=20)
        >>> len(chunks)
        5
    """
    if not text:
        return []
    
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    
    if overlap < 0:
        raise ValueError("overlap cannot be negative")
    
    if overlap >= chunk_size:
        raise ValueError("overlap must be less than chunk_size")
    
    # If text fits in one chunk, return as-is
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    step = chunk_size - overlap
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at a sentence or word boundary
        if end < len(text):
            chunk = _break_at_boundary(chunk)
        
        chunks.append(chunk)
        start += step
        
        # Avoid creating tiny final chunks
        if start + step >= len(text) and start < len(text):
            # Last chunk - include everything remaining
            final_chunk = text[start:]
            if final_chunk and final_chunk != chunks[-1]:
                chunks.append(final_chunk)
            break
    
    return chunks


def _break_at_boundary(chunk: str) -> str:
    """
    Try to break chunk at a natural boundary (sentence or word).
    
    Looks for the last sentence-ending punctuation or whitespace
    near the end of the chunk.
    """
    # Look for sentence boundaries in the last 20% of the chunk
    search_start = int(len(chunk) * 0.8)
    search_region = chunk[search_start:]
    
    # Try sentence boundaries first
    for punct in ['. ', '! ', '? ', '.\n', '!\n', '?\n']:
        idx = search_region.rfind(punct)
        if idx != -1:
            return chunk[:search_start + idx + len(punct)]
    
    # Fall back to word boundary
    idx = search_region.rfind(' ')
    if idx != -1:
        return chunk[:search_start + idx + 1]
    
    # No good boundary found, return as-is
    return chunk
