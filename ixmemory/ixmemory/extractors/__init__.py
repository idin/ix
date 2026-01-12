"""
Text extraction utilities.
"""

from .chunker import chunk_text

from .entities import extract_entities, ENTITIES_SPEC
from .numbers import extract_numbers, NUMBERS_SPEC
from .moments import extract_moments, MOMENTS_SPEC
from .attributes import extract_attributes, ATTRIBUTES_SPEC
from .relationships import extract_relationships, RELATIONSHIPS_SPEC
from .number_ranges import extract_number_ranges, NUMBER_RANGES_SPEC
from .moment_ranges import extract_moment_ranges, MOMENT_RANGES_SPEC

from .extract import extract, SPECS
from .detect import detect, detect_and_extract

__all__ = [
    'chunk_text',
    # Detection
    'detect',
    'detect_and_extract',
    # Individual extractors
    'extract_entities',
    'extract_numbers',
    'extract_moments',
    'extract_attributes',
    'extract_relationships',
    'extract_number_ranges',
    'extract_moment_ranges',
    # Combined extractor
    'extract',
    # Specs (for building custom prompts)
    'ENTITIES_SPEC',
    'NUMBERS_SPEC',
    'MOMENTS_SPEC',
    'ATTRIBUTES_SPEC',
    'RELATIONSHIPS_SPEC',
    'NUMBER_RANGES_SPEC',
    'MOMENT_RANGES_SPEC',
    'SPECS',
]
