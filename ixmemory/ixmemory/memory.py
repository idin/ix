"""
Unified Memory class that provides access to all memory systems.

Memory owns:
- Database connection (shared by all sub-memories)
- ID Registry (tracks all IDs across all systems)
- Sub-memories: SemanticMemory, GraphMemory, ConversationMemory, FileMemory
"""

from typing import Optional, Dict, Any, List, Union

from ixutils import create_database_connection

from .semantic_memory.database import initialize_database as init_semantic_db
from .semantic_memory.id_registry import IdRegistry
from .semantic_memory import SemanticMemory
from .graph_memory.database import initialize_database as init_graph_db
from .graph_memory import GraphMemory
from .conversation_memory import ConversationMemory
from .file_memory.database import initialize_database as init_file_db
from .file_memory import FileMemory


def _initialize_all_tables(connection) -> None:
    """Initialize all database tables."""
    init_semantic_db(connection)  # includes ids and id_tables
    init_graph_db(connection)
    init_file_db(connection)


class Memory:
    """
    Unified memory system with automatic ID tracking.
    
    All IDs are universal - the same ID can exist across different memory
    systems (semantic, graph, files). The ID registry tracks which systems
    contain each ID.
    
    Sub-memories (for direct access when needed):
    - semantic: moments, numbers, texts
    - graph: nodes, edges, traversal
    - conversations: in-memory conversation history
    - files: file storage
    - registry: ID tracking (usually accessed through Memory methods)
    
    Args:
        database_path: Path to SQLite database file. If None, uses in-memory.
        auto_embed: Whether to auto-generate embeddings for text records.
        embedding_model: Sentence-transformers model name.
        files_dir: Directory for file storage.
    
    Example:
        >>> memory = Memory()
        >>> 
        >>> # Save with auto ID tracking
        >>> memory.save_text(id="alice", content="Alice is an engineer")
        >>> memory.save_number(id="alice_age", value=32, record_type="age")
        >>> memory.add_node(node_id="alice", node_type="Person")
        >>> 
        >>> # Check what we know about an ID
        >>> memory.registry.get(id="alice")
        {'id': 'alice', 'tables': ['texts', 'graph_nodes'], ...}
    """
    
    def __init__(
        self,
        database_path: Optional[str] = None,
        auto_embed: bool = True,
        embedding_model: str = 'all-MiniLM-L6-v2',
        files_dir: Optional[str] = None,
    ):
        self.database_path = database_path or ':memory:'
        self.auto_embed = auto_embed
        self.embedding_model = embedding_model
        
        # Create single database connection
        self.connection = create_database_connection(
            database_path=self.database_path,
            initialize_tables=_initialize_all_tables,
        )
        
        # Initialize ID registry
        self.registry = IdRegistry(connection=self.connection)
        
        # Initialize sub-memories (they receive the connection)
        self.semantic = SemanticMemory(
            connection=self.connection,
            auto_embed=auto_embed,
            embedding_model=embedding_model,
        )
        
        self.graph = GraphMemory(
            connection=self.connection,
        )
        
        self.conversations = ConversationMemory()
        
        self.files = FileMemory(
            connection=self.connection,
            files_dir=files_dir,
        )
    
    # =========================================================================
    # ID Management
    # =========================================================================
    
    def create_id(self, prefix: Optional[str] = None) -> str:
        """
        Generate and register a new unique ID.
        
        Args:
            prefix: Optional prefix for human readability.
        
        Returns:
            The newly created ID.
        """
        return self.registry.create_id(prefix=prefix)
    
    def id_exists(self, *, id: str) -> bool:
        """Check if an ID exists in the registry."""
        return self.registry.exists(id=id)
    
    def get_id_info(self, *, id: str) -> Optional[Dict[str, Any]]:
        """Get full info for an ID (creation time, which tables)."""
        return self.registry.get(id=id)
    
    # =========================================================================
    # Moment Operations (with registry tracking)
    # =========================================================================
    
    def save_moment(
        self,
        *,
        id: str,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        hour: Optional[int] = None,
        minute: Optional[int] = None,
        second: Optional[int] = None,
        record_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Save a moment and track in registry."""
        result = self.semantic.moments.save(
            id=id,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
            record_type=record_type,
        )
        self.registry.add_to_table(id=id, table_name="moments")
        return result
    
    def load_moment(self, *, id: str) -> Optional[Dict[str, Any]]:
        """Load a moment by ID."""
        return self.semantic.moments.load(id=id)
    
    def delete_moment(self, *, id: str) -> bool:
        """Delete a moment and update registry."""
        deleted = self.semantic.moments.delete(id=id)
        if deleted:
            self.registry.remove_from_table(id=id, table_name="moments")
        return deleted
    
    def find_nearest_moments(self, **kwargs) -> List[Dict[str, Any]]:
        """Find moments nearest to target values."""
        return self.semantic.moments.find_nearest(**kwargs)
    
    # =========================================================================
    # Number Operations (with registry tracking)
    # =========================================================================
    
    def save_number(
        self,
        *,
        id: str,
        value: Union[int, float],
        record_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Save a number and track in registry."""
        result = self.semantic.numbers.save(
            id=id,
            value=value,
            record_type=record_type,
        )
        self.registry.add_to_table(id=id, table_name="numbers")
        return result
    
    def load_number(self, *, id: str) -> Optional[Dict[str, Any]]:
        """Load a number by ID."""
        return self.semantic.numbers.load(id=id)
    
    def delete_number(self, *, id: str) -> bool:
        """Delete a number and update registry."""
        deleted = self.semantic.numbers.delete(id=id)
        if deleted:
            self.registry.remove_from_table(id=id, table_name="numbers")
        return deleted
    
    def find_nearest_numbers(self, **kwargs) -> List[Dict[str, Any]]:
        """Find numbers nearest to target value."""
        return self.semantic.numbers.find_nearest(**kwargs)
    
    # =========================================================================
    # Text Operations (with registry tracking)
    # =========================================================================
    
    def save_text(
        self,
        *,
        id: str,
        content: str,
        record_type_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        """Save a text and track in registry."""
        result = self.semantic.texts.save(
            id=id,
            content=content,
            record_type_id=record_type_id,
            tags=tags,
            metadata=metadata,
            embedding=embedding,
        )
        self.registry.add_to_table(id=id, table_name="texts")
        return result
    
    def load_text(self, *, id: str) -> Optional[Dict[str, Any]]:
        """Load a text by ID."""
        return self.semantic.texts.load(id=id)
    
    def delete_text(self, *, id: str) -> bool:
        """Delete a text and update registry."""
        deleted = self.semantic.texts.delete(id=id)
        if deleted:
            self.registry.remove_from_table(id=id, table_name="texts")
        return deleted
    
    def search_texts(self, **kwargs) -> List[Dict[str, Any]]:
        """Search texts by semantic similarity."""
        return self.semantic.texts.search(**kwargs)
    
    # =========================================================================
    # Set/Member Operations (with registry tracking)
    # =========================================================================
    
    def add_member(
        self,
        *,
        set_id: str,
        member_id: str,
        member_table: str,
    ) -> Dict[str, Any]:
        """Add a member to a set (text_members table tracks membership)."""
        return self.semantic.texts.add_member(
            text_id=set_id,
            member_id=member_id,
            member_table=member_table,
        )
    
    def remove_member(
        self,
        *,
        set_id: str,
        member_id: str,
        member_table: str,
    ) -> bool:
        """Remove a member from a set."""
        return self.semantic.texts.remove_member(
            text_id=set_id,
            member_id=member_id,
            member_table=member_table,
        )
    
    def get_members(self, *, set_id: str, **kwargs) -> List[Dict[str, Any]]:
        """Get all members of a set."""
        return self.semantic.texts.get_members(text_id=set_id, **kwargs)
    
    # =========================================================================
    # Graph Operations (with registry tracking)
    # =========================================================================
    
    def add_node(
        self,
        *,
        node_id: str,
        node_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Add a graph node and track in registry."""
        result = self.graph.add_node(
            node_id=node_id,
            node_type=node_type,
            properties=properties,
        )
        self.registry.add_to_table(id=node_id, table_name="graph_nodes")
        return result
    
    def get_node(self, *, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a graph node by ID."""
        return self.graph.get_node(node_id=node_id)
    
    def delete_node(self, *, node_id: str) -> bool:
        """Delete a graph node and update registry."""
        deleted = self.graph.delete_node(node_id=node_id)
        if deleted:
            self.registry.remove_from_table(id=node_id, table_name="graph_nodes")
        return deleted
    
    def add_edge(self, **kwargs) -> Dict[str, Any]:
        """Add an edge between nodes."""
        return self.graph.add_edge(**kwargs)
    
    def traverse(self, **kwargs) -> List[Dict[str, Any]]:
        """Traverse the graph from a starting node."""
        return self.graph.traverse(**kwargs)
    
    # =========================================================================
    # File Operations (with registry tracking)
    # =========================================================================
    
    def save_file(
        self,
        *,
        file_id: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Save a file and track in registry."""
        result = self.files.save(file_id=file_id, **kwargs)
        if result.get('success'):
            self.registry.add_to_table(id=file_id, table_name="files")
        return result
    
    def load_file(self, *, file_id: str) -> Optional[Dict[str, Any]]:
        """Load a file by ID."""
        return self.files.load(file_id=file_id)
    
    def delete_file(self, *, file_id: str) -> bool:
        """Delete a file and update registry."""
        deleted = self.files.delete(file_id=file_id)
        if deleted:
            self.registry.remove_from_table(id=file_id, table_name="files")
        return deleted
    
    # =========================================================================
    # Cross-System Queries
    # =========================================================================
    
    def get_all_info(self, *, id: str) -> Dict[str, Any]:
        """
        Get all information about an ID across all memory systems.
        
        Args:
            id: ID to look up.
        
        Returns:
            Dictionary with data from all systems where ID exists.
        """
        result = {
            'id': id,
            'registry': self.registry.get(id=id),
            'moment': self.semantic.moments.load(id=id),
            'number': self.semantic.numbers.load(id=id),
            'text': self.semantic.texts.load(id=id),
            'node': self.graph.get_node(node_id=id),
            'file': self.files.load(file_id=id),
        }
        
        # Remove None values
        result = {k: v for k, v in result.items() if v is not None}
        result['id'] = id  # Always include id
        
        return result
    
    def delete_everywhere(self, *, id: str) -> Dict[str, Any]:
        """
        Delete an ID from all memory systems where it exists.
        
        Args:
            id: ID to delete.
        
        Returns:
            Dictionary with what was deleted.
        """
        deleted_from = []
        
        if self.semantic.moments.delete(id=id):
            deleted_from.append('moments')
        if self.semantic.numbers.delete(id=id):
            deleted_from.append('numbers')
        if self.semantic.texts.delete(id=id):
            deleted_from.append('texts')
        if self.graph.delete_node(node_id=id):
            deleted_from.append('graph_nodes')
        if self.files.delete(file_id=id):
            deleted_from.append('files')
        
        # Clean up registry
        self.registry.delete(id=id)
        
        return {
            'id': id,
            'deleted_from': deleted_from,
            'success': len(deleted_from) > 0,
        }
    
    # =========================================================================
    # Lifecycle
    # =========================================================================
    
    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __repr__(self) -> str:
        return f"Memory(database_path='{self.database_path}')"
