#!/usr/bin/env python3
"""
TrTReal - Tree to Real File Structure
A TUI tool to convert tree text input into actual file/directory structures

Usage:
    python main.py              # Launch the TUI
    python main.py --help       # Show help
    python main.py --cli <file> # CLI mode with tree file
"""

import argparse
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parser import TreeParser
from utils import create_file_structure, validate_target_directory, expand_path


def print_banner():
    """Print the application banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║   🌳 TrTReal - Tree to Real File Structure                    ║
║   Convert tree text to actual files and directories           ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def cli_mode(tree_file: str, target_dir: str, dry_run: bool = False):
    """Run in CLI mode without TUI"""
    print_banner()
    
    # Read tree file
    try:
        with open(tree_file, 'r') as f:
            tree_text = f.read()
        print(f"✓ Read tree from: {tree_file}")
    except FileNotFoundError:
        print(f"✗ File not found: {tree_file}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error reading file: {e}")
        sys.exit(1)
    
    # Validate target
    target_dir = expand_path(target_dir)
    is_valid, msg = validate_target_directory(target_dir)
    if not is_valid:
        print(f"✗ Invalid target: {msg}")
        sys.exit(1)
    print(f"✓ Target directory: {target_dir}")
    
    # Parse tree
    parser = TreeParser()
    root = parser.parse(tree_text)
    
    if not root:
        print("✗ Failed to parse tree structure")
        sys.exit(1)
    
    summary = parser.get_summary()
    print(f"✓ Parsed: {summary['directories']} directories, {summary['files']} files")
    
    # Preview
    print("\n📋 Preview:")
    paths = parser.get_all_paths(target_dir)
    for path, is_dir in paths[:20]:
        icon = "📁" if is_dir else "📄"
        print(f"  {icon} {path}")
    
    if len(paths) > 20:
        print(f"  ... and {len(paths) - 20} more items")
    
    # Create structure
    if dry_run:
        print("\n⚠ Dry run mode - no files created")
        return
    
    print("\n🔨 Creating structure...")
    results = create_file_structure(paths)
    
    print("\n📊 Results:")
    print(f"  ✓ Created: {len(results['created'])} items")
    print(f"  ⏭ Skipped: {len(results['skipped'])} items")
    if results['errors']:
        print(f"  ✗ Errors: {len(results['errors'])} items")
        for path, error in results['errors']:
            print(f"    - {path}: {error}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="TrTReal - Convert tree text to real file structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Launch TUI mode
  python main.py --cli tree.txt -t ./out   # CLI mode with tree file
  python main.py --cli tree.txt -t ./out --dry-run  # Preview only
        """
    )
    
    parser.add_argument(
        '--cli',
        metavar='FILE',
        help='Run in CLI mode with the specified tree file'
    )
    
    parser.add_argument(
        '-t', '--target',
        default='.',
        help='Target directory (default: current directory)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview only, do not create files'
    )
    
    args = parser.parse_args()
    
    if args.cli:
        # CLI mode
        cli_mode(args.cli, args.target, args.dry_run)
    else:
        # TUI mode
        try:
            from ui import run_ui
            run_ui()
        except ImportError as e:
            print(f"Error: Could not import UI module: {e}")
            print("Make sure all dependencies are installed.")
            sys.exit(1)
        except Exception as e:
            print(f"Error running TUI: {e}")
            print("Try running with --cli option for command-line mode.")
            sys.exit(1)


if __name__ == "__main__":
    main()
