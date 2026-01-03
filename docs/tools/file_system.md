# File System Tools

This package provides file and directory operations with a focus on safety, clarity, and undo capabilities.

## Core Design Principles

### No Overwriting Allowed

**Overwrite is never allowed.** If a destination already exists, operations will fail with an error. If you need to replace something, you must explicitly delete it first. This prevents accidental data loss and makes operations predictable.

### Recycle Bin System

Deleting files or directories doesn't permanently remove them—they're moved to a recycle bin at `~/.ix_recycle_bin`. This gives you a safety net. You can restore deleted items using `undelete()`, or permanently remove them with `empty_recycle_bin()`.

The recycle bin uses hash-based folder names to avoid name collisions when multiple items with the same name are deleted. Each deleted item stores metadata about its original location, so you can restore it even if you only remember the original path.

### Action Tracking (Optional)

All operations accept an optional `file_system_memory` parameter. If provided, the system tracks actions and their undo operations in a stack. This lets you build undo/redo functionality on top of the file system operations.

## Understanding the Function Names

The naming scheme is designed to be explicit about what each operation does.

### "Change" vs "Clone" vs "Copy"

- **`change_*_path`**: Moves to an exact destination path (the source is moved/renamed)
- **`clone_*_to_path`**: Copies to an exact destination path (the source remains)
- **`copy_*_into`**: Copies into a directory (the source remains)
- **`move_*_into`**: Moves into a directory (the source is moved)

### "To Path" vs "Into"

This is the most important distinction:

- **`*_to_path`** functions: The destination is the **exact final path** where the item will end up.
  - Example: `clone_file_to_path("file.txt", "/tmp/newfile.txt")` creates `/tmp/newfile.txt`
  - Example: `change_dir_path("old_dir", "/tmp/new_dir")` moves `old_dir` to `/tmp/new_dir`

- **`*_into`** functions: The destination is a **directory** that must already exist. The item is placed inside it, keeping its original name.
  - Example: `copy_file_into("file.txt", "/tmp")` creates `/tmp/file.txt`
  - Example: `move_dir_into("my_dir", "/tmp")` moves `my_dir` to `/tmp/my_dir`

### Quick Reference

| Operation | File | Directory |
|-----------|------|-----------|
| Move to exact path | `change_file_path` | `change_dir_path` |
| Move into directory | `move_file_into` | `move_dir_into` |
| Copy to exact path | `clone_file_to_path` | `clone_dir_to_path` |
| Copy into directory | `copy_file_into` | `copy_dir_into` |

## Comparison Functions

`compare_files()` and `compare_dirs()` are optimized for efficiency:

- File comparison checks sizes first (if different, no need to read contents)
- Directory comparison stops at the first difference found
- Both return detailed information about what differs, not just a boolean

## Empty Operations

`empty_dir()` removes all contents from a directory but keeps the directory itself. All removed items go to the recycle bin, so they can be restored.

`empty_recycle_bin()` permanently deletes everything in the recycle bin—this is the only way to permanently delete items.

## Path Utilities

Use `path_exists()`, `path_is_file()`, and `path_is_dir()` instead of direct `os.path` calls. These provide consistent behavior across the codebase.

## List Functions

- `list_dir()`: Returns a simple list of item names in a directory
- `list_dir_contents()`: Returns files and directories as separate lists, with full paths and metadata

Both support an `include_hidden` parameter to control whether hidden files (starting with `.`) are included.

## Tool Output Structure

All file system tools return a standardized dictionary structure:

```python
{
    "success": bool,      # Whether the operation succeeded
    "result": {...},      # Primary output data (nested dict with tool-specific fields)
    "error": str | None   # Error message if operation failed, None if successful
}
```

### Structure Rules

1. **Top-level keys**: Only `success`, `result`, and `error` are allowed at the top level. These are defined as constants in `ixmachina.tools.constants`.

2. **Tool-specific data**: All tool-specific information (like file paths, content, metadata) must be nested inside the `result` dictionary, not at the top level.

3. **Primary output**: The `result` key contains the main output of the operation. For read operations, this typically includes the data read and the file path. For write operations, it includes the written content and path.

### Examples

**Read operation:**
```python
{
    "success": True,
    "result": {
        "data": "file contents here",  # The actual file data
        "metadata": {
            "path": "/path/to/file.txt"  # Metadata nested separately
        }
    },
    "error": None
}
```

**Write operation:**
```python
{
    "success": True,
    "result": {
        "content": "written content",
        "path": "/path/to/file.txt"
    },
    "error": None
}
```

**Error case:**
```python
{
    "success": False,
    "result": None,
    "error": "File does not exist: /path/to/file.txt"
}
```

### Why This Structure?

- **Consistency**: All tools use the same structure, making it predictable for agents and other code
- **Agent extraction**: The agent's `_extract_tool_output_value()` method automatically extracts the `result` key, giving clean output without metadata
- **Tool-specific keys**: By nesting tool-specific data in `result`, we avoid polluting the top-level dictionary with domain-specific keys
- **Error handling**: The `success` and `error` keys provide clear, consistent error information

