"""
Name registry for tracking and matching names.

Provides a registry that stores canonical names, tracks usage, and enables
fast fuzzy matching organized by first letter for efficiency.

Uses a token-based approach where names are broken into tokens, and matching
happens at both token and name levels for better accuracy.
"""

from typing import Optional
from collections import defaultdict

from .utils.normalize import normalize_for_matching, normalize_strict, get_first_letter, extract_tokens
from .utils.first_letter_dict import FirstLetterDict
from .utils.name_finding import find_name_in_text as _find_name_in_text, find_all_names_in_text as _find_all_names_in_text
from .utils.standardize_names_in_text import standardize_names_in_text as _standardize_names_in_text
from .utils.save_load import save_to_json as _save_to_json, load_from_json as _load_from_json, save_to_pickle as _save_to_pickle, load_from_pickle as _load_from_pickle
from .utils.registry_core import (
    add_name_to_registry,
    get_canonical_from_registry,
    add_alias_to_registry,
    get_all_tokens_from_registry,
    get_name_tokens_from_registry,
    get_usage_count_from_registry,
    get_all_names_from_registry,
    get_statistics_from_registry,
    get_names_containing_token_from_registry,
    get_aliases_from_registry,
    get_names_by_letter_from_registry,
    get_registry_length,
    registry_contains_name,
    get_registry_repr,
)
class NameRegistry:
    """
    Registry for tracking and matching names with token-based matching.
    
    Stores canonical names organized by first letter for fast lookup.
    Tracks usage counts and uses token-level indexing for intelligent matching.
    
    The registry maintains multiple representations:
    - Canonical form (original as provided, preserving exact case)
    - Normalized form (lowercase, for case-insensitive fuzzy matching)
    - Token-level index (which names contain which tokens)
    
    Case handling:
    - When adding: Preserves exact case (e.g., "Chris de Burgh" stays as-is)
    - When matching: Case-insensitive (finds "chris de burgh", "CHRIS DE BURGH", etc.)
    
    Token-based matching enables finding "John Smith" when text has "john_smiths"
    and distinguishing "John Smith" from just "John" or just "Smith".
    
    Names are indexed by their first letter for fast filtering before
    fuzzy matching, which dramatically improves performance when matching
    against large name lists.
    """
    
    def __init__(self):
        """
        Initialize the name registry.
        
        Names are stored exactly as provided, but matching is case-insensitive.
        Aliases can be added to point multiple name variations to the same canonical name.
        """
        # Canonical names organized by first letter
        # Structure: {'a': {'canonical_name': {...}}}
        self._names_by_letter: dict[str, dict[str, dict]] = defaultdict(dict)
        
        # Token registry organized by first letter
        # Structure: {'j': {'john': {'names': ['John Smith', 'John Doe'], 'normalized': 'john'}}}
        self._tokens_by_letter: dict[str, dict[str, dict]] = defaultdict(dict)
        
        # Reverse lookups using FirstLetterDict for automatic first-letter indexing
        self._normalized_to_canonical = FirstLetterDict()  # 'john smith' -> 'John Smith'
        self._strict_to_canonical = FirstLetterDict()       # 'johnsmith' -> 'John Smith'
        self._concatenated_to_canonical = FirstLetterDict() # 'johnsmith' -> 'John Smith'
        self._alias_to_canonical = FirstLetterDict()        # 'johnny' -> 'John Smith'
        
        # Total name lookups (for statistics)
        self._total_lookups = 0
    
    def add_name(self, name: str) -> str:
        """
        Add a name to the registry.
        
        The name is stored exactly as provided, preserving case (e.g., "Chris de Burgh").
        If the name already exists (in normalized form), increments its usage count.
        If it's new, adds it with count 1 and indexes all its tokens.
        
        Args:
            name: Name to add (will be stored exactly as provided).
            
        Returns:
            The canonical name as stored in the registry.
            
        Example:
            >>> registry = NameRegistry()
            >>> registry.add_name("Chris de Burgh")  # Lowercase "de" preserved
            'Chris de Burgh'
            >>> registry.add_name("chris de burgh")  # Same name, different case
            'Chris de Burgh'  # Returns existing canonical form, increments count
        """
        return add_name_to_registry(self, name)
    
    def get_canonical(self, name: str) -> Optional[str]:
        """
        Get the canonical form of a name if it exists.
        
        Checks normalized, strict, concatenated forms, and aliases to find an exact match.
        Does not perform fuzzy matching.
        
        Args:
            name: Name to look up.
            
        Returns:
            Canonical name if found, None otherwise.
            
        Example:
            >>> registry = NameRegistry()
            >>> registry.add_name("John Smith")
            >>> registry.get_canonical("john_smith")
            'John Smith'
            >>> registry.get_canonical("johnsmith")
            'John Smith'
            >>> registry.add_alias(canonical_name="John Smith", alias="Johnny")
            >>> registry.get_canonical("Johnny")
            'John Smith'
            >>> registry.get_canonical("Unknown Person")
            None
        """
        self._total_lookups += 1
        return get_canonical_from_registry(self, name)
    
    def add_alias(self, canonical_name: str, alias: str) -> dict:
        """
        Add an alias for a canonical name.
        
        Aliases are alternative names that resolve to the same canonical name.
        For example, "Johnny" and "Jon" might be aliases for "John Smith".
        
        Args:
            canonical_name: The canonical name that must already exist in the registry.
            alias: The alias to add (will be normalized for matching).
            
        Returns:
            Dictionary with:
                - success: True if alias was added, False otherwise
                - error: Error message if any
                - canonical_name: The canonical name
                - alias: The alias that was added
                - aliases: List of all aliases for this canonical name
                
        Example:
            >>> registry = NameRegistry()
            >>> registry.add_name("John Smith")
            >>> registry.add_alias(canonical_name="John Smith", alias="Johnny")
            {'success': True, 'canonical_name': 'John Smith', 'alias': 'Johnny', 'aliases': ['Johnny']}
            >>> registry.get_canonical("Johnny")
            'John Smith'
        """
        return add_alias_to_registry(self, canonical_name, alias)
    
    def get_aliases(self, canonical_name: str) -> Optional[list[str]]:
        """
        Get all aliases for a canonical name.
        
        Args:
            canonical_name: The canonical name to get aliases for.
            
        Returns:
            List of aliases if the name exists, None otherwise.
            
        Example:
            >>> registry = NameRegistry()
            >>> registry.add_name("John Smith")
            >>> registry.add_alias(canonical_name="John Smith", alias="Johnny")
            >>> registry.add_alias(canonical_name="John Smith", alias="Jon")
            >>> registry.get_aliases("John Smith")
            ['Johnny', 'Jon']
        """
        return get_aliases_from_registry(self, canonical_name)
    
    def get_names_containing_token(
        self,
        token: str
    ) -> list[str]:
        """
        Get all canonical names that contain a specific token.
        
        Args:
            token: Token to search for (will be normalized).
                  
        Returns:
            List of canonical names containing this token.
            
        Example:
            >>> registry = NameRegistry()
            >>> registry.add_name("John Smith")
            >>> registry.add_name("John Doe")
            >>> registry.get_names_containing_token("john")
            ['John Smith', 'John Doe']
            >>> registry.get_names_containing_token("smith")
            ['John Smith']
        """
        return get_names_containing_token_from_registry(self, token)
    
    def get_all_tokens(self, sort_by_frequency: bool = False) -> list[tuple[str, int]]:
        """
        Get all tokens in the registry with their frequency.
        
        Args:
            sort_by_frequency: If True, sort by frequency (descending).
                              If False, sort alphabetically.
                              
        Returns:
            List of (token, frequency) tuples where frequency is the
            number of different names containing this token.
            
        Example:
            >>> registry = NameRegistry()
            >>> registry.add_name("John Smith")
            >>> registry.add_name("John Doe")
            >>> registry.get_all_tokens(sort_by_frequency=True)
            [('john', 2), ('doe', 1), ('smith', 1)]
        """
        return get_all_tokens_from_registry(self, sort_by_frequency)
    
    def get_name_tokens(self, canonical_name: str) -> Optional[list[str]]:
        """
        Get the tokens that make up a canonical name.
        
        Args:
            canonical_name: The canonical name to look up.
            
        Returns:
            List of tokens (normalized) or None if name not found.
            
        Example:
            >>> registry = NameRegistry()
            >>> registry.add_name("John Smith")
            >>> registry.get_name_tokens("John Smith")
            ['john', 'smith']
        """
        return get_name_tokens_from_registry(self, canonical_name)
    
    def get_usage_count(self, canonical_name: str) -> int:
        """
        Get the usage count for a canonical name.
        
        Args:
            canonical_name: The canonical name to check.
            
        Returns:
            Usage count, or 0 if name not found.
            
        Example:
            >>> registry = NameRegistry()
            >>> registry.add_name("John Smith")
            >>> registry.add_name("john smith")  # Increments count
            >>> registry.get_usage_count("John Smith")
            2
        """
        return get_usage_count_from_registry(self, canonical_name)
    
    def get_all_names(self, sort_by_usage: bool = False) -> list[tuple[str, int]]:
        """
        Get all names in the registry with their usage counts.
        
        Args:
            sort_by_usage: If True, sort by usage count (descending).
                          If False, sort alphabetically.
                          
        Returns:
            List of (canonical_name, usage_count) tuples.
            
        Example:
            >>> registry = NameRegistry()
            >>> registry.add_name("John Smith")
            >>> registry.add_name("Jane Doe")
            >>> registry.add_name("john smith")
            >>> registry.get_all_names(sort_by_usage=True)
            [('John Smith', 2), ('Jane Doe', 1)]
        """
        return get_all_names_from_registry(self, sort_by_usage)
    
    def get_names_by_letter(self, letter: str) -> list[str]:
        """
        Get all canonical names starting with a specific letter.
        
        Args:
            letter: First letter (case-insensitive).
            
        Returns:
            List of canonical names starting with that letter.
            
        Example:
            >>> registry = NameRegistry()
            >>> registry.add_name("John Smith")
            >>> registry.add_name("Jane Doe")
            >>> registry.get_names_by_letter('j')
            ['Jane Doe', 'John Smith']
        """
        return get_names_by_letter_from_registry(self, letter)
    
    def get_statistics(self) -> dict:
        """
        Get statistics about the registry.
        
        Returns:
            Dictionary with statistics:
            - total_names: Total number of unique canonical names
            - total_tokens: Total number of unique tokens
            - total_lookups: Total number of times names were looked up
            - names_by_letter: Count of names per first letter
            - tokens_by_letter: Count of tokens per first letter
            - most_used: Top 10 most-used names
            - most_common_tokens: Top 10 most common tokens
            
        Example:
            >>> registry = NameRegistry()
            >>> registry.add_name("John Smith")
            >>> stats = registry.get_statistics()
            >>> stats['total_names']
            1
            >>> stats['total_tokens']
            2
        """
        return get_statistics_from_registry(self)
    
    def find_name_in_text(
        self,
        text: str,
        threshold: int = 70,
        token_threshold: int = 80
    ) -> Optional[tuple[str, int, dict]]:
        """
        Find a name from the registry in the given text using token-based fuzzy matching.
        
        This function uses an intelligent multi-step process:
        1. Extract tokens from the text
        2. Fuzzy match each token against the token registry
        3. Find candidate names that contain matched tokens
        4. Score each candidate based on token coverage and proximity
        5. Return the best-scoring candidate
        
        Example: Finding "John Smith" in "john_smiths_report.pdf"
        - Tokens: ["john", "smiths", "report", "pdf"]
        - Token "john" matches "john" (100%)
        - Token "smiths" matches "smith" (95%)
        - Candidate "John Smith" has tokens ["john", "smith"]
        - Score: 95% (both tokens found, adjacent, high similarity)
        
        Args:
            text: Text to search in (file name, sentence, etc.).
            threshold: Minimum score (0-100) for name match.
                      Default: 70 (allows some flexibility).
            token_threshold: Minimum score for individual token matches.
                            Default: 80 (fairly strict per token).
                            
        Returns:
            Tuple of (canonical_name, score, details) if match found, None otherwise.
            Details include information about which tokens matched and how.
            
        Example:
            >>> registry = NameRegistry()
            >>> registry.add_name("John Smith")
            >>> registry.find_name_in_text("john_smiths_report.pdf")
            ('John Smith', 95, {...})
        """
        return _find_name_in_text(self, text, threshold, token_threshold)
    
    def find_all_names_in_text(
        self,
        text: str,
        threshold: int = 70,
        token_threshold: int = 80
    ) -> list[tuple[str, int, dict]]:
        """
        Find all names from the registry in the given text.
        
        Unlike find_name_in_text which returns the best match, this function
        returns ALL names that match above the threshold.
        
        Args:
            text: Text to search in.
            threshold: Minimum score for name match.
            token_threshold: Minimum score for individual token matches.
            
        Returns:
            List of (canonical_name, score, details) tuples, sorted by score descending.
            
        Example:
            >>> registry = NameRegistry()
            >>> registry.add_name("John Smith")
            >>> registry.add_name("Jane Doe")
            >>> registry.find_all_names_in_text("john_smith_and_jane_doe.txt")
            [('John Smith', 95, {...}), ('Jane Doe', 90, {...})]
        """
        return _find_all_names_in_text(self, text, threshold, token_threshold)
    
    def standardize_names_in_text(
        self,
        text: str,
        threshold: int = 70,
        token_threshold: int = 80
    ) -> dict:
        """
        Standardize ALL names in text by replacing them with their canonical forms.
        
        Finds all matching names and replaces them in the original text,
        preserving formatting and non-name portions.
        
        Args:
            text: Text to standardize (often a file name).
            threshold: Minimum score for name match.
            token_threshold: Minimum score for token matches.
            
        Returns:
            Dictionary with keys:
            - standardized_text: Text with names replaced by canonical forms
            - original_text: Original input text
            - names_found: List of canonical names that were found and replaced
            - num_replacements: Number of names replaced
            
        Example:
            >>> registry = NameRegistry()
            >>> registry.add_name("John Smith")
            >>> registry.add_name("Jane Doe")
            >>> result = registry.standardize_names_in_text("john_smith_and_jane_doe_report.pdf")
            >>> result['standardized_text']
            'John Smith and Jane Doe report.pdf'
            >>> result['names_found']
            ['John Smith', 'Jane Doe']
        """
        return _standardize_names_in_text(self, text, threshold, token_threshold)
    
    def __len__(self) -> int:
        """Return total number of unique names in registry."""
        return get_registry_length(self)
    
    def __contains__(self, name: str) -> bool:
        """Check if a name exists in the registry (using normalized form)."""
        return registry_contains_name(self, name)
    
    def __repr__(self) -> str:
        """String representation of the registry."""
        return get_registry_repr(self)
    
    def save_to_json(self, file_path: str) -> dict:
        """
        Save the registry to a JSON file.
        
        Args:
            file_path: Path where the JSON file should be saved.
            
        Returns:
            Dictionary with success, file_path, and error keys.
        """
        return _save_to_json(self, file_path)
    
    @classmethod
    def load_from_json(cls, file_path: str) -> 'NameRegistry':
        """
        Load a registry from a JSON file.
        
        Args:
            file_path: Path to the JSON file to load.
            
        Returns:
            A new NameRegistry instance loaded from the file.
        """
        return _load_from_json(file_path)
    
    def save_to_pickle(self, file_path: str) -> dict:
        """
        Save the registry to a pickle file.
        
        Warning: Pickle files are Python version-dependent and can have security
        implications when loading untrusted data.
        
        Args:
            file_path: Path where the pickle file should be saved.
            
        Returns:
            Dictionary with success, file_path, and error keys.
        """
        return _save_to_pickle(self, file_path)
    
    @classmethod
    def load_from_pickle(cls, file_path: str) -> 'NameRegistry':
        """
        Load a registry from a pickle file.
        
        Warning: Only load pickle files from trusted sources, as pickle can
        execute arbitrary code during deserialization.
        
        Args:
            file_path: Path to the pickle file to load.
            
        Returns:
            A NameRegistry instance loaded from the file.
        """
        return _load_from_pickle(file_path)
