"""
File storage operations for FileMemory.
"""

import os
import json
import uuid
import mimetypes
import shutil
from pathlib import Path
from typing import Any, Optional, Dict, Union
from ixutils import utc_now


# Text file extensions that can be read as content
TEXT_EXTENSIONS = {'.txt', '.md', '.py', '.js', '.json', '.xml', '.html', '.css', '.csv', '.log', '.yaml', '.yml'}


def _detect_file_type(file_path: str) -> str:
    """
    Detect file type from file path/extension.
    
    Args:
        file_path: Path to the file.
        
    Returns:
        File type string (e.g., 'text', 'image', 'video', 'audio', 'binary', 'pdf').
    """
    path = Path(file_path)
    ext = path.suffix.lower()
    
    if ext in TEXT_EXTENSIONS:
        return 'text'
    elif ext == '.pdf':
        return 'pdf'
    elif ext in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'}:
        return 'image'
    elif ext in {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'}:
        return 'video'
    elif ext in {'.mp3', '.wav', '.flac', '.ogg', '.aac', '.m4a'}:
        return 'audio'
    elif ext in {'.pickle', '.pkl'}:
        return 'pickle'
    else:
        # Try mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            if mime_type.startswith('text/'):
                return 'text'
            elif mime_type.startswith('image/'):
                return 'image'
            elif mime_type.startswith('video/'):
                return 'video'
            elif mime_type.startswith('audio/'):
                return 'audio'
        
        return 'binary'


def save_file(
    *,
    connection: Any,
    id: Optional[str],
    summary_record_id: str,
    content: Optional[Union[str, bytes]] = None,
    file_path: Optional[str] = None,
    source_file_path: Optional[str] = None,
    files_dir: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Save a file to the filesystem and database.
    
    Supports both text and binary files. For text files, content can be provided.
    For binary files, use source_file_path to copy from existing file.
    
    Args:
        connection: Database connection.
        id: Universal ID for the file. If None, generates a new UUID.
        summary_record_id: ID of the summary record in records table.
        content: File content (string for text, bytes for binary). If None, uses source_file_path.
        file_path: Optional custom file path. If None, generates one based on ID and file type.
        source_file_path: Optional path to existing file to copy (for binary files).
        files_dir: Base directory for storing files.
        metadata: Optional metadata dictionary.
        
    Returns:
        Dictionary with success status and file ID.
    """
    try:
        file_id = id or str(uuid.uuid4())
        
        # Create files directory if it doesn't exist
        files_path = Path(files_dir)
        files_path.mkdir(parents=True, exist_ok=True)
        
        # Determine file type and extension
        if source_file_path:
            # Copy from existing file
            source_path = Path(source_file_path)
            if not source_path.exists():
                return {
                    'success': False,
                    'error': f"Source file not found: {source_file_path}",
                }
            
            file_type = _detect_file_type(str(source_path))
            ext = source_path.suffix or '.bin'
            
            if file_path is None:
                relative_path = f"{file_id}{ext}"
            else:
                relative_path = file_path.lstrip('/').lstrip('\\')
            
            full_path = files_path / relative_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_path, full_path)
            
        elif content is not None:
            # Save content directly
            if isinstance(content, str):
                file_type = 'text'
                ext = '.txt'
            else:
                file_type = 'binary'
                ext = '.bin'
            
            if file_path is None:
                relative_path = f"{file_id}{ext}"
            else:
                relative_path = file_path.lstrip('/').lstrip('\\')
                file_type = _detect_file_type(relative_path)
            
            full_path = files_path / relative_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            if isinstance(content, str):
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                with open(full_path, 'wb') as f:
                    f.write(content)
        else:
            return {
                'success': False,
                'error': "Either content or source_file_path must be provided",
            }
        
        # Get file size for metadata
        file_size = os.path.getsize(full_path)
        
        # Prepare metadata
        file_metadata = metadata or {}
        file_metadata['file_size'] = file_size
        file_metadata['extension'] = Path(relative_path).suffix
        
        # Save to database
        cursor = connection.cursor()
        now = utc_now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO files 
            (id, summary_record_id, file_path, file_type, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 
                    COALESCE((SELECT created_at FROM files WHERE id = ?), ?),
                    ?)
        """, (
            file_id,
            summary_record_id,
            relative_path,
            file_type,
            json.dumps(file_metadata),
            file_id,
            now,
            now,
        ))
        
        connection.commit()
        
        return {
            'success': True,
            'id': file_id,
            'file_path': str(full_path),
            'relative_path': relative_path,
            'file_type': file_type,
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }


def load_file(
    *,
    connection: Any,
    id: str,
    files_dir: str,
) -> Dict[str, Any]:
    """
    Load a file from the filesystem.
    
    For text files, returns content. For binary files, returns file path only.
    
    Args:
        connection: Database connection.
        id: Universal ID of the file to load.
        files_dir: Base directory for storing files.
        
    Returns:
        Dictionary with success status and file data.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id, summary_record_id, file_path, file_type, metadata, created_at, updated_at
            FROM files
            WHERE id = ?
        """, (id,))
        
        row = cursor.fetchone()
        if not row:
            return {
                'success': False,
                'error': f"File with ID '{id}' not found",
            }
        
        # Convert relative path to absolute path
        relative_path = row['file_path']
        files_path = Path(files_dir)
        full_path = files_path / relative_path
        
        if not full_path.exists():
            return {
                'success': False,
                'error': f"File not found at path '{full_path}'",
            }
        
        result = {
            'success': True,
            'id': row['id'],
            'summary_record_id': row['summary_record_id'],
            'file_path': str(full_path),
            'relative_path': relative_path,
            'file_type': row['file_type'],
            'metadata': json.loads(row['metadata']) if row['metadata'] else {},
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
        }
        
        # For text files, read and return content
        if row['file_type'] == 'text':
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    result['content'] = f.read()
            except UnicodeDecodeError:
                # Fallback to binary read if UTF-8 fails
                with open(full_path, 'rb') as f:
                    result['content'] = f.read()
        
        return result
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }


def delete_file(
    *,
    connection: Any,
    id: str,
    files_dir: str,
) -> Dict[str, Any]:
    """
    Delete a file from both database and filesystem.
    
    Args:
        connection: Database connection.
        id: Universal ID of the file to delete.
        files_dir: Base directory for storing files.
        
    Returns:
        Dictionary with success status.
    """
    try:
        cursor = connection.cursor()
        
        # Get file path before deleting from database
        cursor.execute("""
            SELECT file_path FROM files WHERE id = ?
        """, (id,))
        
        row = cursor.fetchone()
        if not row:
            return {
                'success': False,
                'error': f"File with ID '{id}' not found",
            }
        
        # Convert relative path to absolute path
        relative_path = row['file_path']
        files_path = Path(files_dir)
        full_path = files_path / relative_path
        
        # Delete from database
        cursor.execute("""
            DELETE FROM files WHERE id = ?
        """, (id,))
        
        connection.commit()
        
        # Delete file from filesystem
        if full_path.exists():
            full_path.unlink()
        
        return {
            'success': True,
            'id': id,
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }


def list_files(
    *,
    connection: Any,
    files_dir: str,
    file_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List all files with basic info.
    
    Args:
        connection: Database connection.
        files_dir: Base directory for storing files.
        file_type: Optional filter by file type (e.g., 'text', 'image', 'binary').
        
    Returns:
        Dictionary with success status and list of files.
    """
    try:
        cursor = connection.cursor()
        if file_type:
            cursor.execute("""
                SELECT id, summary_record_id, file_path, file_type, metadata, created_at, updated_at
                FROM files
                WHERE file_type = ?
            """, (file_type,))
        else:
            cursor.execute("""
                SELECT id, summary_record_id, file_path, file_type, metadata, created_at, updated_at
                FROM files
            """)
        
        files_path = Path(files_dir)
        files = []
        for row in cursor.fetchall():
            metadata = json.loads(row['metadata']) if row['metadata'] else {}
            relative_path = row['file_path']
            full_path = files_path / relative_path
            file_exists = full_path.exists()
            
            files.append({
                'id': row['id'],
                'summary_record_id': row['summary_record_id'],
                'file_path': str(full_path),
                'relative_path': relative_path,
                'file_type': row['file_type'],
                'file_exists': file_exists,
                'file_size': metadata.get('file_size'),
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
            })
        
        return {
            'success': True,
            'files': files,
            'count': len(files),
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }


def cleanup_orphaned_files(
    *,
    connection: Any,
    files_dir: str,
) -> Dict[str, Any]:
    """
    Remove files from filesystem that are not in the database.
    
    Args:
        connection: Database connection.
        files_dir: Base directory for storing files.
        
    Returns:
        Dictionary with success status and cleanup results.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT file_path FROM files")
        registered_paths = {row['file_path'] for row in cursor.fetchall()}
        
        files_path = Path(files_dir)
        if not files_path.exists():
            return {
                'success': True,
                'deleted_files': [],
                'count': 0,
            }
        
        deleted_files = []
        for file_path in files_path.rglob('*'):
            if file_path.is_file():
                # Get relative path from files_dir
                try:
                    relative_path = str(file_path.relative_to(files_path))
                    if relative_path not in registered_paths:
                        file_path.unlink()
                        deleted_files.append(str(file_path))
                except ValueError:
                    # File is outside files_dir, skip it
                    pass
        
        return {
            'success': True,
            'deleted_files': deleted_files,
            'count': len(deleted_files),
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }


def cleanup_missing_files(
    *,
    connection: Any,
    files_dir: str,
) -> Dict[str, Any]:
    """
    Remove database entries for files whose files no longer exist.
    
    Args:
        connection: Database connection.
        files_dir: Base directory for storing files.
        
    Returns:
        Dictionary with success status and cleanup results.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, file_path FROM files")
        
        files_path = Path(files_dir)
        deleted_ids = []
        for row in cursor.fetchall():
            relative_path = row['file_path']
            full_path = files_path / relative_path
            if not full_path.exists():
                cursor.execute("DELETE FROM files WHERE id = ?", (row['id'],))
                deleted_ids.append(row['id'])
        
        connection.commit()
        
        return {
            'success': True,
            'deleted_ids': deleted_ids,
            'count': len(deleted_ids),
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }
