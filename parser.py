"""
Tree Parser Module - Parses tree text into a structured format
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from const import TREE_BRANCH, TREE_LAST, TREE_VERTICAL, TREE_SPACE


@dataclass
class TreeNode:
    """Represents a node in the tree structure"""
    name: str
    is_directory: bool
    depth: int
    children: List['TreeNode'] = field(default_factory=list)
    parent: Optional['TreeNode'] = None
    
    def __repr__(self):
        type_str = "DIR" if self.is_directory else "FILE"
        return f"TreeNode({type_str}: {self.name}, depth={self.depth}, children={len(self.children)})"
    
    def get_full_path(self, base_path: str = "") -> str:
        """Get the full path from root to this node"""
        parts = []
        node = self
        while node is not None:
            parts.append(node.name)
            node = node.parent
        parts.reverse()
        
        if base_path:
            return f"{base_path.rstrip('/')}/{'/'.join(parts)}"
        return "/".join(parts)


class TreeParser:
    """Parses tree-formatted text into TreeNode structure"""
    
    def __init__(self):
        self.root: Optional[TreeNode] = None
        self.all_nodes: List[TreeNode] = []
    
    def parse(self, tree_text: str) -> Optional[TreeNode]:
        """
        Parse tree text and return the root TreeNode
        
        Args:
            tree_text: The tree-formatted text to parse
            
        Returns:
            The root TreeNode or None if parsing fails
        """
        lines = tree_text.strip().split('\n')
        if not lines:
            return None
        
        self.all_nodes = []
        self.root = None
        
        # Stack to keep track of parent nodes at each depth level
        # Index in stack = depth level
        parent_stack: List[TreeNode] = []
        
        for line_num, line in enumerate(lines):
            if not line.strip():
                continue
            
            # Calculate depth and extract name
            depth, name = self._parse_line(line)
            
            if not name:
                continue
            
            # Check if it's a directory. Primary signal: trailing '/'.
            # Fallback: if the next non-empty line is deeper, this node is a parent
            # even without a trailing slash (common in plain `tree` output).
            is_directory = name.endswith('/')
            if is_directory:
                name = name.rstrip('/')
            else:
                # Look ahead to the next meaningful line to infer depth
                next_depth = None
                for look_ahead in lines[line_num + 1:]:
                    if not look_ahead.strip():
                        continue
                    next_depth, _ = self._parse_line(look_ahead)
                    break
                if next_depth is not None and next_depth > depth:
                    is_directory = True
            
            # Create the node
            node = TreeNode(
                name=name,
                is_directory=is_directory,
                depth=depth
            )
            
            self.all_nodes.append(node)
            
            if line_num == 0 or self.root is None:
                # First non-empty line is always the root
                self.root = node
                parent_stack = [node]
            else:
                # Find the correct parent based on depth
                # Parent is at depth - 1 in the stack
                while len(parent_stack) > depth:
                    parent_stack.pop()
                
                if parent_stack:
                    parent = parent_stack[-1]
                    node.parent = parent
                    parent.children.append(node)
                
                # Add this node to the stack at its depth level
                if len(parent_stack) <= depth:
                    parent_stack.append(node)
                else:
                    parent_stack[depth] = node
        
        return self.root
    
    def _parse_line(self, line: str) -> Tuple[int, str]:
        """
        Parse a single line to extract depth and name
        
        Returns:
            Tuple of (depth, name)
        """
        # Count the indentation level by looking for tree characters
        depth = 0
        pos = 0
        
        while pos < len(line):
            remaining = line[pos:]
            
            # Check for item markers - these indicate we found the actual item
            if remaining.startswith(TREE_BRANCH):
                name = remaining[len(TREE_BRANCH):].strip()
                return (depth + 1, name)  # +1 because this item is a child
            
            if remaining.startswith(TREE_LAST):
                name = remaining[len(TREE_LAST):].strip()
                return (depth + 1, name)  # +1 because this item is a child
            
            # Check for continuation characters - these add to depth
            if remaining.startswith(TREE_VERTICAL):
                depth += 1
                pos += len(TREE_VERTICAL)
                continue
            
            if remaining.startswith(TREE_SPACE):
                depth += 1
                pos += len(TREE_SPACE)
                continue
            
            # Handle single space or tab
            if remaining[0] == ' ':
                pos += 1
                continue
            
            if remaining[0] == '\t':
                depth += 1
                pos += 1
                continue
            
            # No tree prefix found - this is the root or plain text
            name = remaining.strip()
            if name:
                return (0, name)
            break
        
        return (0, "")
    
    def get_all_paths(self, base_path: str = "") -> List[Tuple[str, bool]]:
        """
        Get all paths that will be created
        
        Args:
            base_path: The base directory path
            
        Returns:
            List of tuples (path, is_directory)
        """
        if not self.root:
            return []
        
        paths: List[Tuple[str, bool]] = []
        self._collect_paths(self.root, base_path, paths)
        return paths
    
    def _collect_paths(self, node: TreeNode, base_path: str, paths: List[Tuple[str, bool]]):
        """Recursively collect all paths"""
        full_path = node.get_full_path(base_path)
        paths.append((full_path, node.is_directory))
        
        for child in node.children:
            self._collect_paths(child, base_path, paths)
    
    def get_summary(self) -> dict:
        """Get a summary of the parsed tree"""
        if not self.all_nodes:
            return {"total": 0, "directories": 0, "files": 0}
        
        directories = sum(1 for node in self.all_nodes if node.is_directory)
        files = sum(1 for node in self.all_nodes if not node.is_directory)
        
        return {
            "total": len(self.all_nodes),
            "directories": directories,
            "files": files
        }


def parse_tree(tree_text: str) -> Optional[TreeNode]:
    """
    Convenience function to parse tree text
    
    Args:
        tree_text: The tree-formatted text
        
    Returns:
        Root TreeNode or None
    """
    parser = TreeParser()
    return parser.parse(tree_text)
