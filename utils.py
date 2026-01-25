"""
Utility functions for TrTReal
"""

import os
from typing import List, Tuple
from pathlib import Path


def create_file_structure(paths: List[Tuple[str, bool]], dry_run: bool = False) -> dict:
    """
    Create files and directories from the parsed paths
    
    Args:
        paths: List of tuples (path, is_directory)
        dry_run: If True, don't actually create anything, just validate
        
    Returns:
        Dictionary with results: created, skipped, errors
    """
    results = {
        "created": [],
        "skipped": [],
        "errors": []
    }
    
    for path, is_directory in paths:
        try:
            path_obj = Path(path)
            
            if path_obj.exists():
                results["skipped"].append((path, "Already exists"))
                continue
            
            if not dry_run:
                if is_directory:
                    path_obj.mkdir(parents=True, exist_ok=True)
                else:
                    # Ensure parent directory exists
                    path_obj.parent.mkdir(parents=True, exist_ok=True)
                    # Create empty file
                    path_obj.touch()
            
            results["created"].append(path)
            
        except PermissionError:
            results["errors"].append((path, "Permission denied"))
        except OSError as e:
            results["errors"].append((path, str(e)))
        except Exception as e:
            results["errors"].append((path, f"Unexpected error: {e}"))
    
    return results


def validate_target_directory(path: str) -> Tuple[bool, str]:
    """
    Validate that the target directory is valid and writable
    
    Args:
        path: The target directory path
        
    Returns:
        Tuple of (is_valid, message)
    """
    if not path:
        return False, "Path is empty"
    
    path_obj = Path(path).expanduser().resolve()
    
    # Check if parent exists or can be created
    if not path_obj.exists():
        # Check if parent directory exists
        if not path_obj.parent.exists():
            return False, f"Parent directory does not exist: {path_obj.parent}"
        
        # Check if we can write to parent
        if not os.access(path_obj.parent, os.W_OK):
            return False, f"No write permission for: {path_obj.parent}"
        
        return True, f"Directory will be created: {path_obj}"
    
    # Directory exists
    if not path_obj.is_dir():
        return False, f"Path exists but is not a directory: {path_obj}"
    
    if not os.access(path_obj, os.W_OK):
        return False, f"No write permission for: {path_obj}"
    
    return True, f"Valid directory: {path_obj}"


def expand_path(path: str) -> str:
    """Expand user home and resolve the path"""
    return str(Path(path).expanduser().resolve())


def get_directory_tree(path: str, max_depth: int = 3) -> str:
    """
    Generate a tree view of an existing directory
    
    Args:
        path: Directory path
        max_depth: Maximum depth to traverse
        
    Returns:
        Tree-formatted string
    """
    path_obj = Path(path)
    if not path_obj.is_dir():
        return f"Not a directory: {path}"
    
    lines = [f"{path_obj.name}/"]
    _build_tree(path_obj, "", lines, max_depth, 0)
    return "\n".join(lines)


def _build_tree(directory: Path, prefix: str, lines: List[str], max_depth: int, current_depth: int):
    """Recursively build tree lines"""
    if current_depth >= max_depth:
        return
    
    try:
        entries = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
    except PermissionError:
        lines.append(f"{prefix}└── [Permission Denied]")
        return
    
    entries = list(entries)
    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        
        if entry.is_dir():
            lines.append(f"{prefix}{connector}{entry.name}/")
            extension = "    " if is_last else "│   "
            _build_tree(entry, prefix + extension, lines, max_depth, current_depth + 1)
        else:
            lines.append(f"{prefix}{connector}{entry.name}")


def format_size(size: int) -> str:
    """Format byte size to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def count_items_in_directory(path: str) -> Tuple[int, int]:
    """
    Count files and directories in a path
    
    Returns:
        Tuple of (file_count, directory_count)
    """
    path_obj = Path(path)
    if not path_obj.exists():
        return 0, 0
    
    files = 0
    directories = 0
    
    try:
        for item in path_obj.rglob("*"):
            if item.is_file():
                files += 1
            elif item.is_dir():
                directories += 1
    except PermissionError:
        pass
    
    return files, directories
