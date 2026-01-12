"""
File storage system with filesystem backend for all file types.
"""

from typing import Optional, Dict, Any, Union
from pathlib import Path
import sqlite3

from .storage import (
    save_file,
    load_file,
    delete_file,
    list_files,
    cleanup_orphaned_files,
    cleanup_missing_files,
)


class FileMemory:
    """
    File storage system using filesystem for content and database for metadata.
    
    Supports all file types: text documents, images, videos, audio, PDFs, binary files, etc.
    Uses SQLite for persistent storage of file metadata and paths, with actual
    file content stored on the filesystem.
    
    For text files, content can be read directly. For binary files, only the
    file path and metadata are stored.
    
    Args:
        connection: SQLite database connection (managed by parent Memory class).
        files_dir: Base directory for storing files. Defaults to "files" 
                  in the current working directory.
    """
    
    def __init__(
        self,
        connection: sqlite3.Connection,
        files_dir: Optional[str] = None,
    ):
        self.connection = connection
        self.files_dir = files_dir or str(Path.cwd() / 'files')
        
        # Ensure files directory exists
        Path(self.files_dir).mkdir(parents=True, exist_ok=True)
    
    def save_file(
        self,
        summary_record_id: str,
        content: Optional[Union[str, bytes]] = None,
        source_file_path: Optional[str] = None,
        id: Optional[str] = None,
        file_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Save a file to the filesystem and database.
        
        Supports both text and binary files. For text files, provide content as string.
        For binary files, use source_file_path to copy from existing file.
        
        Args:
            summary_record_id: ID of the summary record in records table.
            content: File content (string for text, bytes for binary). If None, uses source_file_path.
            source_file_path: Optional path to existing file to copy (for binary files).
            id: Universal ID for the file. If None, generates a new UUID.
            file_path: Optional custom file path. If None, generates one based on ID and file type.
            metadata: Optional metadata dictionary.
            
        Returns:
            Dictionary with success status and file ID.
        """
        return save_file(
            connection=self.connection,
            id=id,
            summary_record_id=summary_record_id,
            content=content,
            file_path=file_path,
            source_file_path=source_file_path,
            files_dir=self.files_dir,
            metadata=metadata,
        )
    
    def load_file(
        self,
        id: str,
    ) -> Dict[str, Any]:
        """
        Load a file from the filesystem.
        
        For text files, returns content. For binary files, returns file path only.
        
        Args:
            id: Universal ID of the file to load.
            
        Returns:
            Dictionary with success status and file data.
        """
        return load_file(
            connection=self.connection,
            id=id,
            files_dir=self.files_dir,
        )
    
    def delete_file(
        self,
        id: str,
    ) -> Dict[str, Any]:
        """
        Delete a file from both database and filesystem.
        
        Args:
            id: Universal ID of the file to delete.
            
        Returns:
            Dictionary with success status.
        """
        return delete_file(
            connection=self.connection,
            id=id,
            files_dir=self.files_dir,
        )
    
    def list_files(
        self,
        file_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List all files with basic info.
        
        Args:
            file_type: Optional filter by file type (e.g., 'text', 'image', 'binary').
        
        Returns:
            Dictionary with success status and list of files.
        """
        return list_files(
            connection=self.connection,
            files_dir=self.files_dir,
            file_type=file_type,
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
            files_dir=self.files_dir,
        )
    
    def cleanup_missing_files(
        self,
    ) -> Dict[str, Any]:
        """
        Remove database entries for files whose files no longer exist.
        
        Returns:
            Dictionary with success status and cleanup results.
        """
        return cleanup_missing_files(
            connection=self.connection,
            files_dir=self.files_dir,
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
    
    def __repr__(self) -> str:
        return f"FileMemory(files_dir='{self.files_dir}')"

