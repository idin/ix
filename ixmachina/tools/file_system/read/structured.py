"""
File system tools for reading structured data files (CSV, JSON, YAML).
"""

from typing import Dict, Any, List, Optional
import os
import json
import csv

from ...constants import SUCCESS_KEY, ERROR_KEY, RESULT_KEY, METADATA_KEY
from ..constants import PATH_KEY
from ..path_utils import path_exists


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
        if not os.path.isfile(path):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Path is not a file: {path}",
            }
        
        # Read CSV file
        data = []
        with open(path, "r", encoding=encoding, newline="") as f:
            reader = csv.DictReader(f)
            data = list(reader)
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: data,  # Just the file data - what the user needs
            METADATA_KEY: {
                PATH_KEY: path,
            },
            ERROR_KEY: None,
        }
    except UnicodeDecodeError as e:
        return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Encoding error: {str(e)}. Try a different encoding.",
        }
    except PermissionError as e:
        return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Permission denied: {str(e)}",
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
        if not os.path.isfile(path):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Path is not a file: {path}",
            }
        
        # Read JSON file
        with open(path, "r", encoding=encoding) as f:
            data = json.load(f)
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: data,  # Just the file data - what the user needs
            METADATA_KEY: {
                PATH_KEY: path,
            },
            ERROR_KEY: None,
        }
    except json.JSONDecodeError as e:
        return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Invalid JSON: {str(e)}",
        }
    except UnicodeDecodeError as e:
        return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Encoding error: {str(e)}. Try a different encoding.",
        }
    except PermissionError as e:
        return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Permission denied: {str(e)}",
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
        # Try to import yaml
        try:
            import yaml
        except ImportError:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: "PyYAML is required for YAML operations. Install it with: pip install pyyaml",
            }
        
        # Check if file exists
        if not path_exists(path):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"File does not exist: {path}",
            }
        
        # Check if it's a file (not a directory)
        if not os.path.isfile(path):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Path is not a file: {path}",
            }
        
        # Read YAML file
        with open(path, "r", encoding=encoding) as f:
            data = yaml.safe_load(f)
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: data,  # Just the file data - what the user needs
            METADATA_KEY: {
                PATH_KEY: path,
            },
            ERROR_KEY: None,
        }
    except yaml.YAMLError as e:
        return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Invalid YAML: {str(e)}",
        }
    except UnicodeDecodeError as e:
        return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Encoding error: {str(e)}. Try a different encoding.",
        }
    except PermissionError as e:
        return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Permission denied: {str(e)}",
        }
    except Exception as e:
        return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Error reading YAML file: {str(e)}",
        }

