"""
Semantic memory for storing and searching records with embeddings.

Contains three sub-memories:
- MomentMemory: Temporal values (dates, times, partial dates)
- NumberMemory: Numeric values
- TextMemory: Text records with embeddings
"""

import sqlite3

from .moment_memory import MomentMemory
from .number_memory import NumberMemory
from .text_memory import TextMemory


class SemanticMemory:
    """
    Semantic memory for storing and searching various types of records.
    
    Provides three specialized sub-memories:
    - moments: Temporal values (dates, times, partial dates)
    - numbers: Numeric values
    - texts: Text records with embeddings for semantic search
    
    Note: This class receives a database connection from the parent Memory class.
    It does NOT manage database connections or ID registration.
    
    Args:
        connection: SQLite database connection (managed by parent).
        auto_embed: Whether to automatically generate embeddings for text records.
        embedding_model: Name of the sentence-transformers model to use.
    """
    
    def __init__(
        self,
        connection: sqlite3.Connection,
        auto_embed: bool = True,
        embedding_model: str = 'all-MiniLM-L6-v2',
    ):
        self.connection = connection
        self.auto_embed = auto_embed
        self.embedding_model = embedding_model
        
        # Initialize sub-memories
        self.moments = MomentMemory(connection=self.connection)
        self.numbers = NumberMemory(connection=self.connection)
        self.texts = TextMemory(
            connection=self.connection,
            auto_embed=auto_embed,
            embedding_model=embedding_model,
        )
    
    def __repr__(self) -> str:
        return f"SemanticMemory()"
