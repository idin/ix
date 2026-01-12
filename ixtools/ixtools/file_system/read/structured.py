"""
File system tools for reading structured data files (CSV, JSON, YAML).
"""

from typing import Dict, Any, List, Optional
import json
import csv
import yaml
from io import StringIO

from ...constants import SUCCESS_KEY, ERROR_KEY, RESULT_KEY, METADATA_KEY
from ..constants import PATH_KEY
from ixutils.file_system import path_exists, path_is_file
from ixutils.file_system.read import read_text_file as _read_text_file


def read_csv(
    path: str,
    encoding: str = "utf-8",
) -> Dict[str, Any]:
    """
    Read data from a CSV file.
    
    Args:
        path: Path to the CSV file to read.
        encoding: Text encoding to use (default: "utf-8").
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - data: List of dictionaries (one per row) if successful, None otherwise.
            - path: Path to the file that was read.
            - error: Error message if operation failed (None if successful).
    """
    try:
        # Check if file exists
        if not path_exists(path):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"File does not exist: {path}",
            }
        
        # Check if it's a file (not a directory)
        if not path_is_file(path):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Path is not a file: {path}",
            }
        
        # Read file content using ixutils
        try:
            content = _read_text_file(path=path, encoding=encoding)
        except FileNotFoundError:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"File does not exist: {path}",
            }
        except IsADirectoryError:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Path is a directory, not a file: {path}",
            }
        except Exception as e:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Error reading file: {str(e)}",
            }
        
        # Parse CSV content
        reader = csv.DictReader(StringIO(content))
        data = list(reader)
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: data,  # Just the file data - what the user needs
            METADATA_KEY: {
                PATH_KEY: path,
            },
            ERROR_KEY: None,
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error reading CSV file: {str(e)}",
        }


def read_json(
    path: str,
    encoding: str = "utf-8",
) -> Dict[str, Any]:
    """
    Read data from a JSON file.
    
    Args:
        path: Path to the JSON file to read.
        encoding: Text encoding to use (default: "utf-8").
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - data: Parsed JSON data (dict, list, etc.) if successful, None otherwise.
            - path: Path to the file that was read.
            - error: Error message if operation failed (None if successful).
    """
    try:
        # Check if file exists
        if not path_exists(path):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"File does not exist: {path}",
            }
        
        # Check if it's a file (not a directory)
        if not path_is_file(path):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Path is not a file: {path}",
            }
        
        # Read file content using ixutils
        try:
            content = _read_text_file(path=path, encoding=encoding)
        except FileNotFoundError:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"File does not exist: {path}",
            }
        except IsADirectoryError:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Path is a directory, not a file: {path}",
            }
        except Exception as e:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Error reading file: {str(e)}",
            }
        
        # Parse JSON content
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Invalid JSON: {str(e)}",
            }
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: data,  # Just the file data - what the user needs
            METADATA_KEY: {
                PATH_KEY: path,
            },
            ERROR_KEY: None,
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error reading JSON file: {str(e)}",
        }


def read_yaml(
    path: str,
    encoding: str = "utf-8",
) -> Dict[str, Any]:
    """
    Read data from a YAML file.
    
    Args:
        path: Path to the YAML file to read.
        encoding: Text encoding to use (default: "utf-8").
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - data: Parsed YAML data (dict, list, etc.) if successful, None otherwise.
            - path: Path to the file that was read.
            - error: Error message if operation failed (None if successful).
    """
    try:
        # Check if file exists
        if not path_exists(path):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"File does not exist: {path}",
            }
        
        # Check if it's a file (not a directory)
        if not path_is_file(path):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Path is not a file: {path}",
            }
        
        # Read file content using ixutils
        try:
            content = _read_text_file(path=path, encoding=encoding)
        except FileNotFoundError:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"File does not exist: {path}",
            }
        except IsADirectoryError:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Path is a directory, not a file: {path}",
            }
        except Exception as e:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Error reading file: {str(e)}",
            }
        
        # Parse YAML content
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Invalid YAML: {str(e)}",
            }
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: data,  # Just the file data - what the user needs
            METADATA_KEY: {
                PATH_KEY: path,
            },
            ERROR_KEY: None,
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error reading YAML file: {str(e)}",
        }

