# 🌳 TrTReal - Tree to Real File Structure

A powerful TUI (Text User Interface) tool that converts tree-formatted text into actual file and directory structures.

## Features

- **Beautiful TUI**: Interactive terminal interface with colors and emojis
- **Smart Parser**: Handles standard tree output format (`├──`, `└──`, `│`)
- **Preview Mode**: See what will be created before executing
- **CLI Support**: Command-line mode for scripting
- **Safe Execution**: Validates paths and handles errors gracefully
- **No Dependencies**: Uses only Python standard library

## Installation

No installation required! Just clone or copy the files:

```bash
cd TrTReal
python main.py
```

## Usage

### TUI Mode (Interactive)

```bash
python main.py
```

Navigate with:
- **↑/↓**: Move selection
- **Enter**: Select menu item
- **1-5**: Quick action keys
- **q**: Quit

### CLI Mode

```bash
# From a tree file
python main.py --cli tree.txt -t ./output

# Dry run (preview only)
python main.py --cli tree.txt -t ./output --dry-run
```

## Input Format

The tool accepts standard `tree` command output:

```
project-name/
├── folder1/
│   ├── subfolder/
│   │   └── file.txt
│   └── another.py
├── folder2/
│   └── script.py
└── README.md
```

### Rules:
- **Directories**: End with `/` (e.g., `data/`)
- **Files**: No trailing slash (e.g., `README.md`)
- **Indentation**: Uses `├──`, `└──`, `│` characters

## Workflow

1. **Paste Tree**: Enter or paste your tree structure
2. **Set Target**: Choose where to create the structure
3. **Preview**: Review what will be created
4. **Create**: Execute and create the files/directories

## Project Structure

```
TrTReal/
├── main.py         # Entry point
├── ui.py           # TUI implementation
├── parser.py       # Tree text parser
├── utils.py        # File operations utilities
├── const.py        # Constants and configuration
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.7+
- `curses` module (included in standard library on Unix/macOS)

> **Note for Windows**: The `curses` module is not included by default. Install `windows-curses`:
> ```bash
> pip install windows-curses
> ```

## License

MIT License - Feel free to use and modify!
