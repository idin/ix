"""
Name registry for tracking and matching names.

Provides a registry that stores canonical names, tracks usage, and enables
fast fuzzy matching organized by first letter for efficiency.

Uses a token-based approach where names are broken into tokens, and matching
happens at both token and name levels for better accuracy.
"""

from typing import Optional
from collections import defaultdict
from rapidfuzz import fuzz
import json
import pickle
from pathlib import Path

from .normalize import normalize_for_matching, normalize_strict, get_first_letter, extract_tokens
from .first_letter_dict import FirstLetterDict


class NameRegistry:
    """
    Registry for tracking and matching names with token-based matching.
    
    Stores canonical names organized by first letter for fast lookup.
    Tracks usage counts for each name for analytics and prioritization.
    Uses token-level indexing to enable intelligent multi-word name matching.
    
    The registry maintains multiple representations:
    - Canonical form (original as provided, preserving exact case)
    - Normalized form (lowercase, for case-insensitive fuzzy matching)
    - Token-level index (which names contain which tokens)
    
    Case handling:
    - When adding: Preserves exact case (e.g., "Chris de Burgh" stays as-is)
    - When matching: Case-insensitive (finds "chris de burgh", "CHRIS DE BURGH", etc.)
    
    Token-based matching enables:
    - Finding "John Smith" when text has "john_smiths" (fuzzy token match)
    - Distinguishing "John Smith" from just "John" or just "Smith"
    - Handling partial matches intelligently
    
    Names are indexed by their first letter for fast filtering before
    fuzzy matching, which dramatically improves performance when matching
    against large name lists.
    
    Example:
        >>> registry = NameRegistry()
        >>> registry.add_name("Chris de Burgh")  # Preserves lowercase "de"
        >>> registry.add_name("John Smith")
        >>> # Matching is case-insensitive
        >>> registry.get_canonical("chris de burgh")
        'Chris de Burgh'
        >>> registry.get_names_containing_token("john")
        ['John Smith']
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
        # Canonical form is exactly as provided
        canonical = name
        
        # Get normalized forms for matching
        normalized = normalize_for_matching(name)
        strict = normalize_strict(name)
        
        # Get first letter
        first_letter = get_first_letter(name)
        if first_letter is None:
            raise ValueError(f"Name '{name}' has no alphabetic characters")
        
        # Check if we already have this name (by normalized form)
        if normalized in self._normalized_to_canonical:
            # Already exists - increment count and return existing canonical
            existing_canonical = self._normalized_to_canonical[normalized]
            existing_first_letter = get_first_letter(existing_canonical)
            if existing_first_letter and existing_first_letter in self._names_by_letter:
                if existing_canonical in self._names_by_letter[existing_first_letter]:
                    self._names_by_letter[existing_first_letter][existing_canonical]['count'] += 1
            return existing_canonical
        
        # Extract tokens from the name
        tokens = extract_tokens(name)
        
        # Store normalized tokens with their positions
        token_data = []
        for i, token in enumerate(tokens):
            token_data.append({
                'token': token,
                'position': i,
                'normalized': normalize_for_matching(token),
                'strict': normalize_strict(token)
            })
        
        # Create concatenated form (all tokens together, no spaces)
        concatenated = ''.join([t['normalized'] for t in token_data])
        
        # New name - add it
        self._names_by_letter[first_letter][canonical] = {
            'normalized': normalized,
            'strict': strict,
            'count': 1,
            'tokens': token_data,
            'num_tokens': len(tokens),
            'concatenated': concatenated  # "johnsmith" for "John Smith"
        }
        
        # Update reverse lookups (using FirstLetterDict)
        self._normalized_to_canonical[normalized] = canonical
        self._strict_to_canonical[strict] = canonical
        self._concatenated_to_canonical[concatenated] = canonical
        
        # Index tokens
        for token_info in token_data:
            token = token_info['token']
            token_normalized = token_info['normalized']
            token_first_letter = get_first_letter(token)
            
            if token_first_letter is None:
                continue
            
            # Add to token index
            if token_normalized not in self._tokens_by_letter[token_first_letter]:
                self._tokens_by_letter[token_first_letter][token_normalized] = {
                    'names': [],
                    'normalized': token_normalized,
                    'strict': token_info['strict']
                }
            
            # Add this name to the token's list (if not already there)
            if canonical not in self._tokens_by_letter[token_first_letter][token_normalized]['names']:
                self._tokens_by_letter[token_first_letter][token_normalized]['names'].append(canonical)
        
        return canonical
    
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
        normalized = normalize_for_matching(name)
        strict = normalize_strict(name)
        
        # Try normalized lookup first (most common)
        canonical = self._normalized_to_canonical.get(normalized)
        if canonical:
            return canonical
        
        # Try strict lookup
        canonical = self._strict_to_canonical.get(strict)
        if canonical:
            return canonical
        
        # Try concatenated lookup (for "johnsmith" -> "John Smith")
        canonical = self._concatenated_to_canonical.get(strict)
        if canonical:
            return canonical
        
        # Try alias lookup
        canonical = self._alias_to_canonical.get(normalized)
        if canonical:
            return canonical
        
        return None
    
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
        # Check if canonical name exists
        first_letter = get_first_letter(canonical_name)
        if first_letter is None or first_letter not in self._names_by_letter:
            return {
                'success': False,
                'error': f"Canonical name '{canonical_name}' not found in registry",
                'canonical_name': canonical_name,
                'alias': alias
            }
        
        if canonical_name not in self._names_by_letter[first_letter]:
            return {
                'success': False,
                'error': f"Canonical name '{canonical_name}' not found in registry",
                'canonical_name': canonical_name,
                'alias': alias
            }
        
        # Normalize the alias
        alias_normalized = normalize_for_matching(alias)
        
        # Check if alias already points to a different canonical name
        existing_canonical = self._alias_to_canonical.get(alias_normalized)
        if existing_canonical and existing_canonical != canonical_name:
            return {
                'success': False,
                'error': f"Alias '{alias}' already points to '{existing_canonical}'",
                'canonical_name': canonical_name,
                'alias': alias,
                'existing_canonical': existing_canonical
            }
        
        # Add the alias
        self._alias_to_canonical[alias_normalized] = canonical_name
        
        # Track aliases in the name's data
        name_data = self._names_by_letter[first_letter][canonical_name]
        if 'aliases' not in name_data:
            name_data['aliases'] = []
        
        if alias not in name_data['aliases']:
            name_data['aliases'].append(alias)
        
        return {
            'success': True,
            'canonical_name': canonical_name,
            'alias': alias,
            'aliases': name_data['aliases']
        }
    
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
        first_letter = get_first_letter(canonical_name)
        if first_letter is None or first_letter not in self._names_by_letter:
            return None
        
        if canonical_name not in self._names_by_letter[first_letter]:
            return None
        
        name_data = self._names_by_letter[first_letter][canonical_name]
        return name_data.get('aliases', [])
    
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
        token_normalized = normalize_for_matching(token)
        token_first_letter = get_first_letter(token)
        
        if token_first_letter is None:
            return []
        
        if token_first_letter not in self._tokens_by_letter:
            return []
        
        if token_normalized not in self._tokens_by_letter[token_first_letter]:
            return []
        
        return self._tokens_by_letter[token_first_letter][token_normalized]['names'].copy()
    
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
        tokens = []
        
        for letter_dict in self._tokens_by_letter.values():
            for token, data in letter_dict.items():
                frequency = len(data['names'])
                tokens.append((token, frequency))
        
        if sort_by_frequency:
            tokens.sort(key=lambda x: x[1], reverse=True)
        else:
            tokens.sort(key=lambda x: x[0])
        
        return tokens
    
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
        first_letter = get_first_letter(canonical_name)
        if first_letter is None:
            return None
        
        if first_letter not in self._names_by_letter:
            return None
        
        if canonical_name not in self._names_by_letter[first_letter]:
            return None
        
        token_data = self._names_by_letter[first_letter][canonical_name]['tokens']
        return [t['token'] for t in token_data]
    
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
        first_letter = get_first_letter(canonical_name)
        if first_letter is None:
            return 0
        
        if first_letter not in self._names_by_letter:
            return 0
        
        if canonical_name not in self._names_by_letter[first_letter]:
            return 0
        
        return self._names_by_letter[first_letter][canonical_name]['count']
    
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
        names = []
        
        for letter_dict in self._names_by_letter.values():
            for canonical, data in letter_dict.items():
                names.append((canonical, data['count']))
        
        if sort_by_usage:
            names.sort(key=lambda x: x[1], reverse=True)
        else:
            names.sort(key=lambda x: x[0])
        
        return names
    
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
        letter = letter.lower()
        if letter not in self._names_by_letter:
            return []
        
        return sorted(self._names_by_letter[letter].keys())
    
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
        total_names = sum(
            len(letter_dict)
            for letter_dict in self._names_by_letter.values()
        )
        
        total_tokens = sum(
            len(letter_dict)
            for letter_dict in self._tokens_by_letter.values()
        )
        
        names_by_letter = {
            letter: len(letter_dict)
            for letter, letter_dict in self._names_by_letter.items()
        }
        
        tokens_by_letter = {
            letter: len(letter_dict)
            for letter, letter_dict in self._tokens_by_letter.items()
        }
        
        # Get most used names
        all_names = self.get_all_names(sort_by_usage=True)
        most_used = all_names[:10]
        
        # Get most common tokens
        all_tokens = self.get_all_tokens(sort_by_frequency=True)
        most_common_tokens = all_tokens[:10]
        
        return {
            'total_names': total_names,
            'total_tokens': total_tokens,
            'total_lookups': self._total_lookups,
            'names_by_letter': dict(sorted(names_by_letter.items())),
            'tokens_by_letter': dict(sorted(tokens_by_letter.items())),
            'most_used': most_used,
            'most_common_tokens': most_common_tokens
        }
    
    def _fuzzy_match_token(
        self,
        token: str,
        threshold: int = 80
    ) -> list[tuple[str, int]]:
        """
        Find fuzzy matches for a single token in the registry.
        
        Uses a two-stage approach for efficiency:
        1. Try exact match first (O(1) hash lookup)
        2. Fall back to fuzzy matching if no exact match
        
        Args:
            token: Token to match.
            threshold: Minimum similarity score.
            
        Returns:
            List of (registered_token, score) tuples for matches above threshold.
        """
        token_normalized = normalize_for_matching(token)
        token_first_letter = get_first_letter(token)
        
        if token_first_letter is None:
            return []
        
        # Get all tokens starting with same letter
        if token_first_letter not in self._tokens_by_letter:
            return []
        
        tokens_dict = self._tokens_by_letter[token_first_letter]
        
        # Stage 1: Try exact match first (O(1) hash lookup)
        if token_normalized in tokens_dict:
            return [(token_normalized, 100)]
        
        # Stage 2: No exact match, do fuzzy matching
        matches = []
        for registered_token, data in tokens_dict.items():
            score = fuzz.ratio(token_normalized, registered_token)
            if score >= threshold:
                matches.append((registered_token, score))
        
        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
    
    def _score_name_match(
        self,
        name_canonical: str,
        text_tokens: list[str],
        token_matches: dict[str, list[tuple[str, int]]]
    ) -> Optional[tuple[int, dict]]:
        """
        Score how well a name matches the text based on its tokens.
        
        Args:
            name_canonical: Canonical name to score.
            text_tokens: Tokens extracted from text.
            token_matches: Dict of text_token -> [(registry_token, score)]
            
        Returns:
            Tuple of (total_score, details) or None if no match.
            Details include: matched_tokens, coverage, average_score, positions
        """
        # Get the tokens that make up this name
        name_tokens = self.get_name_tokens(name_canonical)
        if not name_tokens:
            return None
        
        # Try to match each name token to text tokens
        matched_name_tokens = {}  # name_token -> (text_position, score)
        
        for name_token in name_tokens:
            best_score = 0
            best_position = -1
            
            # Check each text token
            for text_pos, text_token in enumerate(text_tokens):
                if text_token not in token_matches:
                    continue
                
                # Check if any of the matched registry tokens match this name token
                for registry_token, score in token_matches[text_token]:
                    if registry_token == name_token:
                        if score > best_score:
                            best_score = score
                            best_position = text_pos
            
            if best_score > 0:
                matched_name_tokens[name_token] = (best_position, best_score)
        
        # Calculate metrics
        num_name_tokens = len(name_tokens)
        num_matched = len(matched_name_tokens)
        
        if num_matched == 0:
            return None
        
        # Coverage: what fraction of name tokens were found
        coverage = num_matched / num_name_tokens
        
        # Average score of matched tokens
        avg_score = sum(score for _, score in matched_name_tokens.values()) / num_matched
        
        # Check if matched tokens are adjacent in text
        positions = sorted([pos for pos, _ in matched_name_tokens.values()])
        adjacency_bonus = 0
        if len(positions) > 1:
            # Check if positions are consecutive
            is_adjacent = all(
                positions[i + 1] - positions[i] == 1
                for i in range(len(positions) - 1)
            )
            if is_adjacent:
                adjacency_bonus = 20  # Boost score for adjacent matches
        
        # Total score calculation:
        # - Base score: average token score
        # - Coverage multiplier: penalize incomplete matches
        # - Adjacency bonus: reward adjacent tokens
        total_score = int(avg_score * coverage + adjacency_bonus)
        total_score = min(100, total_score)  # Cap at 100
        
        details = {
            'matched_tokens': matched_name_tokens,
            'coverage': coverage,
            'average_score': avg_score,
            'adjacency_bonus': adjacency_bonus,
            'positions': positions
        }
        
        return (total_score, details)
    
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
        # Extract tokens from text
        text_tokens = extract_tokens(text)
        if not text_tokens:
            return None
        
        # Fuzzy match each text token against registry tokens
        token_matches = {}  # text_token -> [(registry_token, score)]
        
        for text_token in text_tokens:
            matches = self._fuzzy_match_token(text_token, threshold=token_threshold)
            if matches:
                token_matches[text_token] = matches
        
        if not token_matches:
            return None
        
        # Get candidate names from matched tokens
        candidate_names = set()
        for text_token, matches in token_matches.items():
            for registry_token, _ in matches:
                # Get all names containing this registry token
                names = self.get_names_containing_token(registry_token)
                candidate_names.update(names)
        
        if not candidate_names:
            return None
        
        # Score each candidate name
        scored_candidates = []
        for candidate_name in candidate_names:
            result = self._score_name_match(
                candidate_name,
                text_tokens,
                token_matches
            )
            if result:
                score, details = result
                if score >= threshold:
                    scored_candidates.append((candidate_name, score, details))
        
        if not scored_candidates:
            return None
        
        # Return best match
        scored_candidates.sort(key=lambda x: (x[1], x[2]['coverage']), reverse=True)
        
        # Increment lookup counter
        self._total_lookups += 1
        
        return scored_candidates[0]
    
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
        # Extract tokens from text
        text_tokens = extract_tokens(text)
        if not text_tokens:
            return []
        
        # Fuzzy match each text token
        token_matches = {}
        for text_token in text_tokens:
            matches = self._fuzzy_match_token(text_token, threshold=token_threshold)
            if matches:
                token_matches[text_token] = matches
        
        if not token_matches:
            return []
        
        # Get candidate names
        candidate_names = set()
        for text_token, matches in token_matches.items():
            for registry_token, _ in matches:
                names = self.get_names_containing_token(registry_token)
                candidate_names.update(names)
        
        if not candidate_names:
            return []
        
        # Score all candidates
        results = []
        for candidate_name in candidate_names:
            result = self._score_name_match(
                candidate_name,
                text_tokens,
                token_matches
            )
            if result:
                score, details = result
                if score >= threshold:
                    results.append((candidate_name, score, details))
        
        # Sort by score and coverage
        results.sort(key=lambda x: (x[1], x[2]['coverage']), reverse=True)
        
        # Increment lookup counter
        self._total_lookups += 1
        
        return results
    
    def standardize_names_in_text(
        self,
        text: str,
        threshold: int = 70,
        token_threshold: int = 80
    ) -> dict:
        """
        Standardize ALL names in text by replacing them with their canonical forms.
        
        Finds all matching names and returns both the standardized text
        and a list of canonical names that were found.
        
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
            'John Smith and Jane Doe_report.pdf'
            >>> result['names_found']
            ['John Smith', 'Jane Doe']
        """
        # Find all names in the text
        matches = self.find_all_names_in_text(text, threshold, token_threshold)
        
        if not matches:
            return {
                'standardized_text': text,
                'original_text': text,
                'names_found': [],
                'num_replacements': 0
            }
        
        # Extract tokens from the original text
        text_tokens = extract_tokens(text)
        if not text_tokens:
            return {
                'standardized_text': text,
                'original_text': text,
                'names_found': [],
                'num_replacements': 0
            }
        
        # Build a map of which text token positions are "claimed" by which name
        # This prevents overlapping replacements
        token_to_name = {}  # position -> (canonical_name, name_match_details)
        
        for canonical_name, score, details in matches:
            # Get positions this name matched
            positions = details['positions']
            
            # Check if any of these positions are already claimed
            conflict = any(pos in token_to_name for pos in positions)
            
            if not conflict:
                # Claim these positions for this name
                for pos in positions:
                    token_to_name[pos] = (canonical_name, details)
        
        # Build result by replacing matched token sequences with canonical names
        result_tokens = []
        i = 0
        found_names = []
        
        while i < len(text_tokens):
            if i in token_to_name:
                # This position starts a name match
                canonical_name, details = token_to_name[i]
                
                # Add the canonical name
                result_tokens.append(canonical_name)
                found_names.append(canonical_name)
                
                # Skip all positions that were part of this name
                positions = sorted(details['positions'])
                # Find the last position in this sequence
                last_pos = positions[-1]
                i = last_pos + 1
            else:
                # Regular token, keep as-is
                result_tokens.append(text_tokens[i])
                i += 1
        
        # Rejoin tokens (this loses original formatting - could be improved)
        standardized = ' '.join(result_tokens)
        
        return {
            'standardized_text': standardized,
            'original_text': text,
            'names_found': found_names,
            'num_replacements': len(found_names)
        }
    
    def __len__(self) -> int:
        """Return total number of unique names in registry."""
        return sum(
            len(letter_dict)
            for letter_dict in self._names_by_letter.values()
        )
    
    def __contains__(self, name: str) -> bool:
        """Check if a name exists in the registry (using normalized form)."""
        return self.get_canonical(name) is not None
    
    def __repr__(self) -> str:
        """String representation of the registry."""
        total_tokens = sum(
            len(letter_dict)
            for letter_dict in self._tokens_by_letter.values()
        )
        return f"NameRegistry(names={len(self)}, tokens={total_tokens}, lookups={self._total_lookups})"
    
    def save_to_json(self, file_path: str) -> dict:
        """
        Save the registry to a JSON file.
        
        JSON format is human-readable and portable across Python versions.
        Good for inspection, debugging, and version control.
        
        Args:
            file_path: Path where the JSON file should be saved.
            
        Returns:
            Dictionary with:
                - success: True if save succeeded, False otherwise
                - file_path: The path where the file was saved
                - error: Error message if any
                
        Example:
            >>> registry = NameRegistry()
            >>> registry.add_name("John Smith")
            >>> result = registry.save_to_json("names.json")
            >>> result['success']
            True
        """
        try:
            path = Path(file_path)
            
            # Convert FirstLetterDict to regular dict for JSON serialization
            def first_letter_dict_to_dict(fld: FirstLetterDict) -> dict:
                """Convert FirstLetterDict to regular dict."""
                return dict(fld.items())
            
            # Prepare data for JSON serialization
            data = {
                'names_by_letter': self._names_by_letter,
                'tokens_by_letter': self._tokens_by_letter,
                'normalized_to_canonical': first_letter_dict_to_dict(self._normalized_to_canonical),
                'strict_to_canonical': first_letter_dict_to_dict(self._strict_to_canonical),
                'concatenated_to_canonical': first_letter_dict_to_dict(self._concatenated_to_canonical),
                'alias_to_canonical': first_letter_dict_to_dict(self._alias_to_canonical),
                'total_lookups': self._total_lookups,
                'version': '1.0'  # For future compatibility
            }
            
            # Save to JSON with pretty formatting
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return {
                'success': True,
                'file_path': str(path.resolve())
            }
            
        except Exception as e:
            return {
                'success': False,
                'file_path': file_path,
                'error': str(e)
            }
    
    @classmethod
    def load_from_json(cls, file_path: str) -> 'NameRegistry':
        """
        Load a registry from a JSON file.
        
        Args:
            file_path: Path to the JSON file to load.
            
        Returns:
            A new NameRegistry instance loaded from the file.
            
        Raises:
            FileNotFoundError: If the file doesn't exist.
            json.JSONDecodeError: If the file is not valid JSON.
            KeyError: If the file is missing required fields.
            
        Example:
            >>> registry = NameRegistry.load_from_json("names.json")
            >>> len(registry)
            5
        """
        path = Path(file_path)
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create new instance
        registry = cls()
        
        # Restore data structures
        registry._names_by_letter = defaultdict(dict, data['names_by_letter'])
        registry._tokens_by_letter = defaultdict(dict, data['tokens_by_letter'])
        registry._total_lookups = data.get('total_lookups', 0)
        
        # Efficiently restore FirstLetterDict instances using from_dict
        registry._normalized_to_canonical = FirstLetterDict.from_dict(data['normalized_to_canonical'])
        registry._strict_to_canonical = FirstLetterDict.from_dict(data['strict_to_canonical'])
        registry._concatenated_to_canonical = FirstLetterDict.from_dict(data['concatenated_to_canonical'])
        registry._alias_to_canonical = FirstLetterDict.from_dict(data['alias_to_canonical'])
        
        return registry
    
    def save_to_pickle(self, file_path: str) -> dict:
        """
        Save the registry to a pickle file.
        
        Pickle format is faster and simpler than JSON, but not human-readable.
        Use this for production when you don't need to inspect the file contents.
        
        Warning: Pickle files are Python version-dependent and can have security
        implications when loading untrusted data.
        
        Args:
            file_path: Path where the pickle file should be saved.
            
        Returns:
            Dictionary with:
                - success: True if save succeeded, False otherwise
                - file_path: The path where the file was saved
                - error: Error message if any
                
        Example:
            >>> registry = NameRegistry()
            >>> registry.add_name("John Smith")
            >>> result = registry.save_to_pickle("names.pkl")
            >>> result['success']
            True
        """
        try:
            path = Path(file_path)
            
            # Save entire instance to pickle
            with open(path, 'wb') as f:
                pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            return {
                'success': True,
                'file_path': str(path.resolve())
            }
            
        except Exception as e:
            return {
                'success': False,
                'file_path': file_path,
                'error': str(e)
            }
    
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
            
        Raises:
            FileNotFoundError: If the file doesn't exist.
            pickle.UnpicklingError: If the file is not a valid pickle.
            
        Example:
            >>> registry = NameRegistry.load_from_pickle("names.pkl")
            >>> len(registry)
            5
        """
        path = Path(file_path)
        
        with open(path, 'rb') as f:
            registry = pickle.load(f)
        
        # Verify it's a NameRegistry instance
        if not isinstance(registry, cls):
            raise TypeError(f"Loaded object is not a {cls.__name__} instance")
        
        return registry

