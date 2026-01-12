"""
Document storage system with filesystem backend.
"""

from typing import Optional, Dict, Any
import sqlite3
from pathlib import Path

from ixutils import create_database_connection
from .database import initialize_database
from .storage import (
    save_document,
    load_document,
    delete_document,
    list_documents,
    cleanup_orphaned_files,
    cleanup_missing_files,
)


class DocumentMemory:
    """
    Document storage system using filesystem for content and database for metadata.
    
    Uses SQLite for persistent storage of document metadata and paths, with actual
    document content stored on the filesystem. Each document has a summary stored
    as a record in the records table (via semantic memory).
    
    Args:
        database_path: Path to SQLite database file. If None, uses in-memory database.
                      Can share the same database_path as other memory systems.
        documents_dir: Base directory for storing documents. Defaults to "documents" 
                     in the current working directory.
    """
    
    def __init__(
        self,
        database_path: Optional[str] = None,
        documents_dir: Optional[str] = None,
    ):
        self.database_path = database_path or ':memory:'
        self.documents_dir = documents_dir or str(Path.cwd() / 'documents')
        
        # Ensure documents directory exists
        Path(self.documents_dir).mkdir(parents=True, exist_ok=True)
        
        self.connection = create_database_connection(
            database_path=self.database_path,
            initialize_tables=initialize_database,
        )
    
    def save_document(
        self,
        summary_record_id: str,
        content: str,
        id: Optional[str] = None,
        file_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Save a document to the filesystem and database.
        
        Args:
            summary_record_id: ID of the summary record in records table.
            content: Document content to save.
            id: Universal ID for the document. If None, generates a new UUID.
            file_path: Optional custom file path. If None, generates one based on ID.
            metadata: Optional metadata dictionary.
            
        Returns:
            Dictionary with success status and document ID.
        """
        return save_document(
            connection=self.connection,
            id=id,
            summary_record_id=summary_record_id,
            content=content,
            file_path=file_path,
            documents_dir=self.documents_dir,
            metadata=metadata,
        )
    
    def load_document(
        self,
        id: str,
    ) -> Dict[str, Any]:
        """
        Load a document from the filesystem.
        
        Args:
            id: Universal ID of the document to load.
            
        Returns:
            Dictionary with success status and document data.
        """
        return load_document(
            connection=self.connection,
            id=id,
            documents_dir=self.documents_dir,
        )
    
    def delete_document(
        self,
        id: str,
    ) -> Dict[str, Any]:
        """
        Delete a document from both database and filesystem.
        
        Args:
            id: Universal ID of the document to delete.
            
        Returns:
            Dictionary with success status.
        """
        return delete_document(
            connection=self.connection,
            id=id,
            documents_dir=self.documents_dir,
        )
    
    def list_documents(
        self,
    ) -> Dict[str, Any]:
        """
        List all documents with basic info.
        
        Returns:
            Dictionary with success status and list of documents.
        """
        return list_documents(
            connection=self.connection,
            documents_dir=self.documents_dir,
        )
    
    def cleanup_orphaned_files(
        self,
    ) -> Dict[str, Any]:
        """
        Remove files from filesystem that are not in the database.
        
        Returns:
            Dictionary with success status and cleanup results.
        """
        return cleanup_orphaned_files(
            connection=self.connection,
            documents_dir=self.documents_dir,
        )
    
    def cleanup_missing_files(
        self,
    ) -> Dict[str, Any]:
        """
        Remove database entries for documents whose files no longer exist.
        
        Returns:
            Dictionary with success status and cleanup results.
        """
        return cleanup_missing_files(
            connection=self.connection,
            documents_dir=self.documents_dir,
        )
    
    def cleanup(
        self,
    ) -> Dict[str, Any]:
        """
        Perform both cleanup operations: remove orphaned files and missing file entries.
        
        Returns:
            Dictionary with success status and cleanup results from both operations.
        """
        orphaned_result = self.cleanup_orphaned_files()
        missing_result = self.cleanup_missing_files()
        
        return {
            'success': orphaned_result.get('success') and missing_result.get('success'),
            'orphaned_files': orphaned_result.get('deleted_files', []),
            'orphaned_count': orphaned_result.get('count', 0),
            'missing_files': missing_result.get('deleted_ids', []),
            'missing_count': missing_result.get('count', 0),
        }
    
    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __repr__(self) -> str:
        return f"DocumentMemory(database_path='{self.database_path}', documents_dir='{self.documents_dir}')"

