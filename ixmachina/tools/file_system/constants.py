"""
Constants for file system tool return dictionaries.

File system specific return keys.
"""

# File path key
PATH_KEY = "path"

# List operation keys
ITEMS_KEY = "items"
FILES_KEY = "files"
DIRECTORIES_KEY = "directories"

# File status keys
EXISTS_KEY = "exists"
IS_FILE_KEY = "is_file"
IS_DIRECTORY_KEY = "is_directory"
SIZE_KEY = "size"
CREATED_TIME_KEY = "created_time"
MODIFIED_TIME_KEY = "modified_time"
ACCESSED_TIME_KEY = "accessed_time"
PERMISSIONS_KEY = "permissions"

# Delete operation keys
FILE_PATH_KEY = "file_path"
RECYCLE_BIN_PATH_KEY = "recycle_bin_path"

# Recycle bin default name
DEFAULT_RECYCLE_BIN_NAME = ".ix_recycle_bin"

# Compare operation keys
ARE_EQUAL_KEY = "are_equal"
DIFFERENCES_KEY = "differences"

