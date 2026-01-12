"""
First-letter-indexed dictionary for efficient name/token lookups.

This module provides a dictionary-like class that automatically organizes
entries by their first letter, enabling O(1) lookups within smaller buckets
instead of searching the entire dataset.
"""

from typing import Optional, Iterator
from collections import defaultdict
from .normalize import get_first_letter


class FirstLetterDict:
    """
    Dictionary that automatically indexes entries by their first letter.
    
    Instead of storing all entries in a flat dictionary, this class organizes
    entries into buckets based on their first letter, enabling faster lookups
    when dealing with large datasets.
    
    For example, with 10,000 entries, each letter bucket contains ~400 entries
    instead of searching all 10,000.
    
    Example:
        >>> fld = FirstLetterDict()
        >>> fld['john'] = 'John Smith'
        >>> fld['jane'] = 'Jane Doe'
        >>> fld['john']
        'John Smith'
        >>> 'jane' in fld
        True
        >>> len(fld)
        2
    """
    
    def __init__(self):
        """Initialize an empty first-letter-indexed dictionary."""
        # Structure: {'j': {'john': 'John Smith', 'jane': 'Jane Doe'}, ...}
        self._buckets: dict[str, dict[str, str]] = defaultdict(dict)
        self._size: int = 0
    
    @classmethod
    def from_dict(cls, data: dict[str, str]) -> 'FirstLetterDict':
        """
        Create a FirstLetterDict from a regular dictionary efficiently.
        
        This is much faster than adding items one by one because it
        organizes all items into buckets in a single pass.
        
        Args:
            data: Dictionary mapping keys to values.
            
        Returns:
            New FirstLetterDict instance with all items organized by first letter.
            
        Example:
            >>> data = {'john': 'John Smith', 'jane': 'Jane Doe'}
            >>> fld = FirstLetterDict.from_dict(data)
            >>> fld['john']
            'John Smith'
        """
        instance = cls()
        
        # Organize items by first letter in a single pass
        for key, value in data.items():
            first_letter = get_first_letter(key)
            if first_letter is None:
                first_letter = ''
            
            instance._buckets[first_letter][key] = value
            instance._size += 1
        
        return instance
    
    def __setitem__(self, key: str, value: str) -> None:
        """
        Set an item in the dictionary.
        
        Args:
            key: Key to store (will be indexed by its first letter).
            value: Value to store.
        """
        first_letter = get_first_letter(key)
        if first_letter is None:
            # Keys with no valid first letter are stored in a special bucket
            first_letter = ''
        
        # Check if this is a new key
        if key not in self._buckets[first_letter]:
            self._size += 1
        
        self._buckets[first_letter][key] = value
    
    def __getitem__(self, key: str) -> str:
        """
        Get an item from the dictionary.
        
        Args:
            key: Key to look up.
            
        Returns:
            Value associated with the key.
            
        Raises:
            KeyError: If key is not found.
        """
        first_letter = get_first_letter(key)
        if first_letter is None:
            first_letter = ''
        
        if first_letter not in self._buckets:
            raise KeyError(key)
        
        return self._buckets[first_letter][key]
    
    def __contains__(self, key: str) -> bool:
        """
        Check if a key exists in the dictionary.
        
        Args:
            key: Key to check.
            
        Returns:
            True if key exists, False otherwise.
        """
        first_letter = get_first_letter(key)
        if first_letter is None:
            first_letter = ''
        
        if first_letter not in self._buckets:
            return False
        
        return key in self._buckets[first_letter]
    
    def __delitem__(self, key: str) -> None:
        """
        Delete an item from the dictionary.
        
        Args:
            key: Key to delete.
            
        Raises:
            KeyError: If key is not found.
        """
        first_letter = get_first_letter(key)
        if first_letter is None:
            first_letter = ''
        
        if first_letter not in self._buckets:
            raise KeyError(key)
        
        if key not in self._buckets[first_letter]:
            raise KeyError(key)
        
        del self._buckets[first_letter][key]
        self._size -= 1
        
        # Clean up empty bucket
        if not self._buckets[first_letter]:
            del self._buckets[first_letter]
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get an item with a default value if not found.
        
        Args:
            key: Key to look up.
            default: Value to return if key is not found.
            
        Returns:
            Value associated with the key, or default if not found.
        """
        try:
            return self[key]
        except KeyError:
            return default
    
    def __len__(self) -> int:
        """
        Get the number of entries in the dictionary.
        
        Returns:
            Total number of key-value pairs.
        """
        return self._size
    
    def __iter__(self) -> Iterator[str]:
        """
        Iterate over all keys in the dictionary.
        
        Yields:
            Keys in the dictionary.
        """
        for bucket in self._buckets.values():
            yield from bucket.keys()
    
    def items(self) -> Iterator[tuple[str, str]]:
        """
        Iterate over all key-value pairs.
        
        Yields:
            Tuples of (key, value).
        """
        for bucket in self._buckets.values():
            yield from bucket.items()
    
    def keys(self) -> Iterator[str]:
        """
        Iterate over all keys.
        
        Yields:
            Keys in the dictionary.
        """
        return iter(self)
    
    def values(self) -> Iterator[str]:
        """
        Iterate over all values.
        
        Yields:
            Values in the dictionary.
        """
        for bucket in self._buckets.values():
            yield from bucket.values()
    
    def get_bucket(self, first_letter: str) -> dict[str, str]:
        """
        Get all entries for a specific first letter.
        
        This is useful for fuzzy matching within a specific letter bucket.
        
        Args:
            first_letter: First letter to get entries for.
            
        Returns:
            Dictionary of all entries starting with that letter.
            
        Example:
            >>> fld = FirstLetterDict()
            >>> fld['john'] = 'John Smith'
            >>> fld['jane'] = 'Jane Doe'
            >>> fld.get_bucket('j')
            {'john': 'John Smith', 'jane': 'Jane Doe'}
        """
        return self._buckets.get(first_letter, {})
    
    def clear(self) -> None:
        """Clear all entries from the dictionary."""
        self._buckets.clear()
        self._size = 0
    
    def __repr__(self) -> str:
        """
        Return string representation of the dictionary.
        
        Returns:
            String representation showing the structure.
        """
        if self._size == 0:
            return "FirstLetterDict()"
        
        # Show first few entries and count
        entries = list(self.items())[:3]
        entries_str = ', '.join(f'{k!r}: {v!r}' for k, v in entries)
        
        if self._size > 3:
            return f"FirstLetterDict({{{entries_str}, ... ({self._size} total)}})"
        else:
            return f"FirstLetterDict({{{entries_str}}})"

