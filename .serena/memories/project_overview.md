Project: TrTReal (Tree to Real File Structure)
Purpose: TUI/CLI tool that parses tree-formatted text and creates corresponding directories/files on disk.
Tech stack: Python 3.7+; standard library only (argparse, curses, pathlib, subprocess).
Entry points: `main.py` (TUI or CLI modes), `ui.py` for curses UI, `parser.py` for tree parsing, `utils.py` for filesystem ops.
Structure: main.py (CLI/TUI dispatcher), ui.py (curses UI), parser.py (TreeParser), utils.py (path validation + file creation), const.py (constants).