"""
Tests for FileMemory operations.
"""

import os
import json
from pathlib import Path

from ixmemory.file_memory.file_memory import FileMemory


def test_save_text_file():
    """Test saving a text file."""
    files_dir = "test_files_save_text"
    Path(files_dir).mkdir(exist_ok=True)
    
    try:
        memory = FileMemory(files_dir=files_dir)
        
        result = memory.save_file(
            summary_record_id="summary_1",
            content="This is a test document",
            id="file_1",
        )
        
        assert result['success'] is True
        assert result['id'] == "file_1"
        assert result['file_type'] == "text"
        
        # Check file exists
        assert os.path.exists(result['file_path'])
        
        memory.close()
    finally:
        # Cleanup
        if Path(files_dir).exists():
            for file in Path(files_dir).rglob('*'):
                if file.is_file():
                    file.unlink()
            Path(files_dir).rmdir()


def test_load_text_file():
    """Test loading a text file."""
    files_dir = "test_files_load_text"
    Path(files_dir).mkdir(exist_ok=True)
    
    try:
        memory = FileMemory(files_dir=files_dir)
        
        memory.save_file(
            summary_record_id="summary_1",
            content="This is test content",
            id="file_1",
        )
        
        result = memory.load_file(id="file_1")
        
        assert result['success'] is True
        assert result['id'] == "file_1"
        assert result['file_type'] == "text"
        assert result['content'] == "This is test content"
        
        memory.close()
    finally:
        # Cleanup
        if Path(files_dir).exists():
            for file in Path(files_dir).rglob('*'):
                if file.is_file():
                    file.unlink()
            Path(files_dir).rmdir()


def test_save_binary_file_from_content():
    """Test saving a binary file from bytes content."""
    files_dir = "test_files_save_binary"
    Path(files_dir).mkdir(exist_ok=True)
    
    try:
        memory = FileMemory(files_dir=files_dir)
        
        binary_content = b"\x00\x01\x02\x03"
        
        result = memory.save_file(
            summary_record_id="summary_1",
            content=binary_content,
            id="file_1",
            file_path="file_1.bin",
        )
        
        assert result['success'] is True
        assert result['file_type'] == "binary"
        
        # Binary files don't return content in load
        result = memory.load_file(id="file_1")
        assert result['success'] is True
        assert 'content' not in result  # Binary files don't have content
        
        memory.close()
    finally:
        # Cleanup
        if Path(files_dir).exists():
            for file in Path(files_dir).rglob('*'):
                if file.is_file():
                    file.unlink()
            Path(files_dir).rmdir()


def test_save_file_from_source_path():
    """Test saving a file by copying from source path."""
    files_dir = "test_files_source_path"
    Path(files_dir).mkdir(exist_ok=True)
    source_file = Path(files_dir) / "source.txt"
    
    try:
        # Create source file
        source_file.write_text("Source content")
        
        memory = FileMemory(files_dir=files_dir)
        
        result = memory.save_file(
            summary_record_id="summary_1",
            source_file_path=str(source_file),
            id="file_1",
        )
        
        assert result['success'] is True
        
        # Verify content was copied
        result = memory.load_file(id="file_1")
        assert result['content'] == "Source content"
        
        memory.close()
    finally:
        # Cleanup
        if Path(files_dir).exists():
            for file in Path(files_dir).rglob('*'):
                if file.is_file():
                    file.unlink()
            Path(files_dir).rmdir()


def test_delete_file():
    """Test deleting a file."""
    files_dir = "test_files_delete"
    Path(files_dir).mkdir(exist_ok=True)
    
    try:
        memory = FileMemory(files_dir=files_dir)
        
        memory.save_file(
            summary_record_id="summary_1",
            content="Test content",
            id="file_1",
        )
        
        # Verify file exists
        result = memory.load_file(id="file_1")
        assert result['success'] is True
        
        # Delete file
        result = memory.delete_file(id="file_1")
        assert result['success'] is True
        
        # Verify file is gone
        result = memory.load_file(id="file_1")
        assert result['success'] is False
        
        memory.close()
    finally:
        # Cleanup
        if Path(files_dir).exists():
            for file in Path(files_dir).rglob('*'):
                if file.is_file():
                    file.unlink()
            Path(files_dir).rmdir()


def test_list_files():
    """Test listing all files."""
    files_dir = "test_files_list"
    Path(files_dir).mkdir(exist_ok=True)
    
    try:
        memory = FileMemory(files_dir=files_dir)
        
        memory.save_file(summary_record_id="s1", content="Text 1", id="file_1")
        memory.save_file(summary_record_id="s2", content="Text 2", id="file_2")
        memory.save_file(summary_record_id="s3", content=b"Binary", id="file_3", file_path="file_3.bin")
        
        result = memory.list_files()
        
        assert result['success'] is True
        assert result['count'] == 3
        
        file_ids = [f['id'] for f in result['files']]
        assert "file_1" in file_ids
        assert "file_2" in file_ids
        assert "file_3" in file_ids
        
        memory.close()
    finally:
        # Cleanup
        if Path(files_dir).exists():
            for file in Path(files_dir).rglob('*'):
                if file.is_file():
                    file.unlink()
            Path(files_dir).rmdir()


def test_list_files_filtered_by_type():
    """Test listing files filtered by type."""
    files_dir = "test_files_filter"
    Path(files_dir).mkdir(exist_ok=True)
    
    try:
        memory = FileMemory(files_dir=files_dir)
        
        memory.save_file(summary_record_id="s1", content="Text 1", id="file_1")
        memory.save_file(summary_record_id="s2", content="Text 2", id="file_2")
        memory.save_file(summary_record_id="s3", content=b"Binary", id="file_3", file_path="file_3.bin")
        
        result = memory.list_files(file_type="text")
        
        assert result['success'] is True
        assert result['count'] == 2
        assert all(f['file_type'] == "text" for f in result['files'])
        
        memory.close()
    finally:
        # Cleanup
        if Path(files_dir).exists():
            for file in Path(files_dir).rglob('*'):
                if file.is_file():
                    file.unlink()
            Path(files_dir).rmdir()


def test_cleanup_orphaned_files():
    """Test cleaning up orphaned files."""
    files_dir = "test_files_orphaned"
    Path(files_dir).mkdir(exist_ok=True)
    
    try:
        memory = FileMemory(files_dir=files_dir)
        
        # Save a file
        memory.save_file(summary_record_id="s1", content="Text 1", id="file_1")
        
        # Create an orphaned file manually
        orphaned_file = Path(files_dir) / "orphaned.txt"
        orphaned_file.write_text("Orphaned content")
        
        result = memory.cleanup_orphaned_files()
        
        assert result['success'] is True
        assert result['count'] == 1
        assert not orphaned_file.exists()  # Orphaned file should be deleted
        
        memory.close()
    finally:
        # Cleanup
        if Path(files_dir).exists():
            for file in Path(files_dir).rglob('*'):
                if file.is_file():
                    file.unlink()
            Path(files_dir).rmdir()


def test_cleanup_missing_files():
    """Test cleaning up database entries for missing files."""
    files_dir = "test_files_missing"
    Path(files_dir).mkdir(exist_ok=True)
    
    try:
        memory = FileMemory(files_dir=files_dir)
        
        # Save a file
        memory.save_file(summary_record_id="s1", content="Text 1", id="file_1")
        
        # Verify it exists
        result = memory.list_files()
        assert result['count'] == 1
        
        # Manually delete the file
        file_path = Path(files_dir) / "file_1.txt"
        file_path.unlink()
        
        # Cleanup should remove database entry
        result = memory.cleanup_missing_files()
        
        assert result['success'] is True
        assert result['count'] == 1
        
        # Verify entry is gone
        result = memory.list_files()
        assert result['count'] == 0
        
        memory.close()
    finally:
        # Cleanup
        if Path(files_dir).exists():
            for file in Path(files_dir).rglob('*'):
                if file.is_file():
                    file.unlink()
            Path(files_dir).rmdir()


def test_database_record_created():
    """Test that database records are actually created when saving files."""
    files_dir = "test_files_db_check"
    Path(files_dir).mkdir(exist_ok=True)
    
    try:
        memory = FileMemory(files_dir=files_dir)
        
        # Save a file
        memory.save_file(
            summary_record_id="summary_1",
            content="Test content",
            id="file_1",
            metadata={"test_key": "test_value"},
        )
        
        # Directly query the database to verify record exists
        cursor = memory.connection.cursor()
        cursor.execute("""
            SELECT id, summary_record_id, file_path, file_type, metadata, created_at, updated_at
            FROM files
            WHERE id = ?
        """, ("file_1",))
        
        row = cursor.fetchone()
        assert row is not None
        assert row['id'] == "file_1"
        assert row['summary_record_id'] == "summary_1"
        assert row['file_type'] == "text"
        assert row['file_path'] == "file_1.txt"
        
        # Verify metadata
        metadata = json.loads(row['metadata'])
        assert metadata['test_key'] == "test_value"
        assert 'file_size' in metadata
        
        # Verify timestamps exist
        assert row['created_at'] is not None
        assert row['updated_at'] is not None
        
        memory.close()
    finally:
        # Cleanup
        if Path(files_dir).exists():
            for file in Path(files_dir).rglob('*'):
                if file.is_file():
                    file.unlink()
            Path(files_dir).rmdir()


def test_database_record_deleted():
    """Test that database records are actually deleted when deleting files."""
    files_dir = "test_files_db_delete"
    Path(files_dir).mkdir(exist_ok=True)
    
    try:
        memory = FileMemory(files_dir=files_dir)
        
        # Save a file
        memory.save_file(
            summary_record_id="summary_1",
            content="Test content",
            id="file_1",
        )
        
        # Verify record exists in database
        cursor = memory.connection.cursor()
        cursor.execute("SELECT id FROM files WHERE id = ?", ("file_1",))
        assert cursor.fetchone() is not None
        
        # Delete file
        memory.delete_file(id="file_1")
        
        # Verify record is gone from database
        cursor.execute("SELECT id FROM files WHERE id = ?", ("file_1",))
        assert cursor.fetchone() is None
        
        memory.close()
    finally:
        # Cleanup
        if Path(files_dir).exists():
            for file in Path(files_dir).rglob('*'):
                if file.is_file():
                    file.unlink()
            Path(files_dir).rmdir()
