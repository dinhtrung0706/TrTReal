"""
Constants for Tree to Real File Structure (TrTReal) Tool
"""
# Minimum terminal dimensions for usability
MIN_WIDTH = 40
MIN_HEIGHT = 15
# Threshold for side-by-side layout (menu + status panels)
WIDE_LAYOUT_MIN_WIDTH = 90

# Tree prefixes used in tree output
TREE_BRANCH = "├── "      # Branch connector
TREE_LAST = "└── "        # Last item connector
TREE_VERTICAL = "│   "    # Vertical line for continuing
TREE_SPACE = "    "       # Empty space for indentation

# All possible prefixes for parsing
TREE_PREFIXES = [TREE_BRANCH, TREE_LAST, TREE_VERTICAL, TREE_SPACE]

# UI Colors (curses color pair indices)
class Colors:
    HEADER = 1
    MENU = 2
    SELECTED = 3
    SUCCESS = 4
    ERROR = 5
    INFO = 6
    INPUT = 7
    BORDER = 8
    TITLE = 9
    PREVIEW = 10

# UI Symbols
SYMBOLS = {
    "folder": "📁",
    "file": "📄",
    "arrow_right": "→",
    "check": "✓",
    "cross": "✗",
    "warning": "⚠",
    "info": "ℹ",
}

# Application title
APP_TITLE = "🌳 TrTReal - Tree to Real File Structure"
APP_SUBTITLE = "Convert tree text to actual files and directories"

# Help text
HELP_TEXT = [
    "Commands:",
    "  [1] Paste Tree    - Enter/paste your tree structure",
    "  [2] Set Target    - Set the target directory",
    "  [3] Preview       - Preview what will be created",
    "  [4] Create        - Create the file structure",
    "  [5] Clear         - Clear the current tree input",
    "  [q] Quit          - Exit the application",
    "",
    "Navigation:",
    "  ↑/↓               - Move selection",
    "  Enter             - Select/Confirm",
    "  Esc               - Cancel/Back",
]
