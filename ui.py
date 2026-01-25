"""
Terminal UI Module for TrTReal
Uses curses for a beautiful terminal interface
"""

import curses
import os
import subprocess
import tempfile
from const import Colors, APP_TITLE, APP_SUBTITLE
from parser import TreeParser
from utils import (
    create_file_structure, 
    validate_target_directory, 
    expand_path
)


def get_clipboard_content() -> str:
    """Get content from system clipboard (macOS)"""
    try:
        result = subprocess.run(['pbpaste'], capture_output=True, text=True, timeout=2)
        return result.stdout
    except Exception:
        return ""


class TrTRealUI:
    """Main TUI Application Class"""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        
        # Initialize colors
        self._init_colors()
        
        # Application state
        self.tree_text = ""
        self.target_directory = os.path.expanduser("~/")
        self.parser = TreeParser()
        self.parsed_root = None
        self.message = ""
        self.message_type = "info"  # info, success, error
        
        # UI state
        self.current_menu_item = 0
        self.menu_items = [
            ("1", "📋 Paste from Clipboard", self._paste_from_clipboard),
            ("2", "✏️  Type/Edit Tree", self._edit_tree_external),
            ("3", "📁 Set Target Directory", self._set_target),
            ("4", "👁️  Preview Structure", self._preview),
            ("5", "✨ Create Structure", self._create_structure),
            ("6", "🗑️  Clear Input", self._clear_input),
            ("q", "🚪 Quit", self._quit),
        ]
        
        self.running = True
    
    def _init_colors(self):
        """Initialize color pairs"""
        curses.start_color()
        curses.use_default_colors()
        
        # Initialize color pairs
        curses.init_pair(Colors.HEADER, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(Colors.MENU, curses.COLOR_WHITE, -1)
        curses.init_pair(Colors.SELECTED, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(Colors.SUCCESS, curses.COLOR_GREEN, -1)
        curses.init_pair(Colors.ERROR, curses.COLOR_RED, -1)
        curses.init_pair(Colors.INFO, curses.COLOR_CYAN, -1)
        curses.init_pair(Colors.INPUT, curses.COLOR_YELLOW, -1)
        curses.init_pair(Colors.BORDER, curses.COLOR_WHITE, -1)
        curses.init_pair(Colors.TITLE, curses.COLOR_MAGENTA, -1)
        curses.init_pair(Colors.PREVIEW, curses.COLOR_WHITE, -1)
    
    def run(self):
        """Main application loop"""
        curses.curs_set(0)  # Hide cursor
        self.stdscr.keypad(True)
        
        while self.running:
            self.height, self.width = self.stdscr.getmaxyx()
            self._draw()
            self._handle_input()
    
    def _draw(self):
        """Draw the entire UI"""
        self.stdscr.clear()
        
        try:
            self._draw_header()
            self._draw_menu()
            self._draw_status_panel()
            self._draw_preview_panel()
            self._draw_message()
            self._draw_footer()
        except curses.error:
            pass
        
        self.stdscr.refresh()
    
    def _draw_header(self):
        """Draw the application header"""
        # Title bar
        title_bar = " " * self.width
        self.stdscr.addstr(0, 0, title_bar, curses.color_pair(Colors.HEADER) | curses.A_BOLD)
        
        # Center the title
        title = APP_TITLE
        x = max(0, (self.width - len(title)) // 2)
        self.stdscr.addstr(0, x, title, curses.color_pair(Colors.HEADER) | curses.A_BOLD)
        
        # Subtitle
        subtitle = APP_SUBTITLE
        x = max(0, (self.width - len(subtitle)) // 2)
        self.stdscr.addstr(1, x, subtitle, curses.color_pair(Colors.INFO))
        
        # Separator
        self.stdscr.addstr(2, 0, "─" * min(self.width - 1, self.width), curses.color_pair(Colors.BORDER))
    
    def _draw_menu(self):
        """Draw the menu panel"""
        start_y = 4
        menu_width = 55
        
        # Menu box
        self._draw_box(start_y, 1, 11, menu_width, "Menu", Colors.TITLE)
        
        for i, (key, label, _) in enumerate(self.menu_items):
            y = start_y + 1 + i
            x = 3
            
            if i == self.current_menu_item:
                # Highlighted item
                text = f" [{key}] {label} "
                self.stdscr.addstr(y, x, text.ljust(menu_width - 4), 
                                   curses.color_pair(Colors.SELECTED) | curses.A_BOLD)
            else:
                text = f" [{key}] {label}"
                self.stdscr.addstr(y, x, text, curses.color_pair(Colors.MENU))
    
    def _draw_status_panel(self):
        """Draw the status panel showing current state"""
        start_y = 4
        start_x = 58
        panel_width = min(50, self.width - start_x - 2)
        
        if panel_width < 20:
            return
        
        self._draw_box(start_y, start_x, 11, panel_width, "Status", Colors.TITLE)
        
        y = start_y + 1
        
        # Target directory
        target_label = "📁 Target:"
        self.stdscr.addstr(y, start_x + 2, target_label, curses.color_pair(Colors.INFO))
        target_path = self.target_directory[:panel_width - 14] if len(self.target_directory) > panel_width - 14 else self.target_directory
        self.stdscr.addstr(y, start_x + 13, target_path, curses.color_pair(Colors.MENU))
        
        y += 2
        
        # Tree input status
        if self.tree_text:
            lines = self.tree_text.count('\n') + 1
            self.stdscr.addstr(y, start_x + 2, f"📝 Tree Input: {lines} lines", curses.color_pair(Colors.SUCCESS))
        else:
            self.stdscr.addstr(y, start_x + 2, "📝 Tree Input: Empty", curses.color_pair(Colors.ERROR))
        
        y += 1
        
        # Parsed status
        if self.parsed_root:
            summary = self.parser.get_summary()
            self.stdscr.addstr(y, start_x + 2, 
                               f"📊 Parsed: {summary['directories']} dirs, {summary['files']} files",
                               curses.color_pair(Colors.SUCCESS))
        else:
            self.stdscr.addstr(y, start_x + 2, "📊 Parsed: Not yet", curses.color_pair(Colors.INFO))
    
    def _draw_preview_panel(self):
        """Draw the preview panel showing parsed tree"""
        start_y = 16
        start_x = 1
        panel_width = self.width - 4
        panel_height = self.height - start_y - 4
        
        if panel_height < 5:
            return
        
        self._draw_box(start_y, start_x, panel_height, panel_width, "Preview", Colors.TITLE)
        
        if self.parsed_root:
            # Show parsed structure
            paths = self.parser.get_all_paths("")
            y = start_y + 1
            max_lines = panel_height - 2
            
            for i, (path, is_dir) in enumerate(paths[:max_lines]):
                if y >= start_y + panel_height - 1:
                    break
                
                icon = "📁" if is_dir else "📄"
                text = f" {icon} {path}"
                if len(text) > panel_width - 4:
                    text = text[:panel_width - 7] + "..."
                
                try:
                    self.stdscr.addstr(y, start_x + 2, text, curses.color_pair(Colors.PREVIEW))
                except curses.error:
                    pass
                y += 1
            
            if len(paths) > max_lines:
                try:
                    self.stdscr.addstr(y, start_x + 2, 
                                       f" ... and {len(paths) - max_lines} more items",
                                       curses.color_pair(Colors.INFO))
                except curses.error:
                    pass
        else:
            try:
                self.stdscr.addstr(start_y + 2, start_x + 4, 
                                   "No tree parsed yet. Press [1] to paste from clipboard.",
                                   curses.color_pair(Colors.INFO))
            except curses.error:
                pass
    
    def _draw_message(self):
        """Draw status message"""
        if self.message:
            y = self.height - 3
            color = Colors.INFO
            if self.message_type == "success":
                color = Colors.SUCCESS
            elif self.message_type == "error":
                color = Colors.ERROR
            
            try:
                msg = self.message[:self.width - 4]
                self.stdscr.addstr(y, 2, msg, curses.color_pair(color) | curses.A_BOLD)
            except curses.error:
                pass
    
    def _draw_footer(self):
        """Draw the footer with help"""
        y = self.height - 1
        footer = " ↑↓:Navigate | Enter:Select | q:Quit "
        x = max(0, (self.width - len(footer)) // 2)
        
        try:
            self.stdscr.addstr(y, 0, " " * (self.width - 1), curses.color_pair(Colors.HEADER))
            self.stdscr.addstr(y, x, footer, curses.color_pair(Colors.HEADER))
        except curses.error:
            pass
    
    def _draw_box(self, y: int, x: int, height: int, width: int, title: str, title_color: int):
        """Draw a box with a title"""
        try:
            # Top border with title
            self.stdscr.addstr(y, x, "╭" + "─" * (width - 2) + "╮", curses.color_pair(Colors.BORDER))
            if title:
                title_x = x + 2
                self.stdscr.addstr(y, title_x, f" {title} ", curses.color_pair(title_color) | curses.A_BOLD)
            
            # Sides
            for i in range(1, height - 1):
                self.stdscr.addstr(y + i, x, "│", curses.color_pair(Colors.BORDER))
                self.stdscr.addstr(y + i, x + width - 1, "│", curses.color_pair(Colors.BORDER))
            
            # Bottom border
            self.stdscr.addstr(y + height - 1, x, "╰" + "─" * (width - 2) + "╯", curses.color_pair(Colors.BORDER))
        except curses.error:
            pass
    
    def _handle_input(self):
        """Handle keyboard input"""
        key = self.stdscr.getch()
        
        if key == ord('q') or key == ord('Q'):
            self.running = False
        elif key == curses.KEY_UP:
            self.current_menu_item = (self.current_menu_item - 1) % len(self.menu_items)
        elif key == curses.KEY_DOWN:
            self.current_menu_item = (self.current_menu_item + 1) % len(self.menu_items)
        elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
            # Execute current menu item
            _, _, action = self.menu_items[self.current_menu_item]
            action()
        elif key == ord('1'):
            self._paste_from_clipboard()
        elif key == ord('2'):
            self._edit_tree_external()
        elif key == ord('3'):
            self._set_target()
        elif key == ord('4'):
            self._preview()
        elif key == ord('5'):
            self._create_structure()
        elif key == ord('6'):
            self._clear_input()
    
    def _paste_from_clipboard(self):
        """Paste tree structure directly from system clipboard"""
        clipboard_content = get_clipboard_content()
        
        if not clipboard_content.strip():
            self.message = "✗ Clipboard is empty. Copy a tree structure first!"
            self.message_type = "error"
            return
        
        self.tree_text = clipboard_content.strip()
        self._parse_tree()
        
        if self.parsed_root:
            summary = self.parser.get_summary()
            lines = self.tree_text.count('\n') + 1
            self.message = f"✓ Pasted {lines} lines: {summary['directories']} dirs, {summary['files']} files"
            self.message_type = "success"
        else:
            self.message = "✗ Pasted content but failed to parse as tree"
            self.message_type = "error"
    
    def _edit_tree_external(self):
        """Open external editor to edit tree structure"""
        # Create temp file with current content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.tree_text if self.tree_text else "# Paste or type your tree structure here\n# Example:\n# project/\n# ├── src/\n# │   └── main.py\n# └── README.md\n")
            temp_path = f.name
        
        # Get editor from environment
        editor = os.environ.get('EDITOR', os.environ.get('VISUAL', 'nano'))
        
        # Temporarily leave curses mode
        curses.endwin()
        
        try:
            # Open editor
            subprocess.run([editor, temp_path])
            
            # Read back the content
            with open(temp_path, 'r') as f:
                content = f.read()
            
            # Filter out comment lines and empty lines at the start
            lines = content.split('\n')
            filtered_lines = [line for line in lines if not line.strip().startswith('#')]
            self.tree_text = '\n'.join(filtered_lines).strip()
            
            if self.tree_text:
                self._parse_tree()
                if self.parsed_root:
                    summary = self.parser.get_summary()
                    self.message = f"✓ Loaded: {summary['directories']} dirs, {summary['files']} files"
                    self.message_type = "success"
                else:
                    self.message = "✗ Could not parse tree structure"
                    self.message_type = "error"
            
        except Exception as e:
            self.message = f"✗ Editor error: {e}"
            self.message_type = "error"
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
            
            # Restore curses
            self.stdscr = curses.initscr()
            curses.start_color()
            curses.use_default_colors()
            self._init_colors()
            curses.noecho()
            curses.cbreak()
            self.stdscr.keypad(True)
            curses.curs_set(0)
    
    def _set_target(self):
        """Set target directory"""
        curses.curs_set(1)
        curses.echo()
        
        # Draw input prompt
        y = self.height // 2
        prompt = "Enter target directory: "
        
        try:
            self.stdscr.addstr(y, 2, " " * (self.width - 4))
            self.stdscr.addstr(y, 2, prompt, curses.color_pair(Colors.INPUT))
            self.stdscr.refresh()
            
            # Get input
            curses.curs_set(1)
            input_bytes = self.stdscr.getstr(y, 2 + len(prompt), 200)
            path = input_bytes.decode('utf-8').strip()
            
            if path:
                expanded_path = expand_path(path)
                is_valid, msg = validate_target_directory(expanded_path)
                
                if is_valid:
                    self.target_directory = expanded_path
                    self.message = f"✓ Target set: {self.target_directory}"
                    self.message_type = "success"
                else:
                    self.message = f"✗ {msg}"
                    self.message_type = "error"
            
        except curses.error:
            pass
        
        curses.noecho()
        curses.curs_set(0)
    
    def _preview(self):
        """Parse and preview the tree structure"""
        if not self.tree_text:
            self.message = "✗ No tree input. Press [1] to paste from clipboard."
            self.message_type = "error"
            return
        
        self._parse_tree()
        
        if self.parsed_root:
            summary = self.parser.get_summary()
            self.message = f"✓ Preview ready: {summary['directories']} directories, {summary['files']} files"
            self.message_type = "success"
        else:
            self.message = "✗ Failed to parse tree structure"
            self.message_type = "error"
    
    def _parse_tree(self):
        """Parse the tree text"""
        self.parsed_root = self.parser.parse(self.tree_text)
    
    def _create_structure(self):
        """Create the file structure"""
        if not self.parsed_root:
            self.message = "✗ No tree parsed. Press [4] to preview first."
            self.message_type = "error"
            return
        
        # Confirm dialog
        curses.curs_set(0)
        y = self.height // 2
        
        summary = self.parser.get_summary()
        confirm_msg = f"Create {summary['directories']} dirs and {summary['files']} files in {self.target_directory}? [y/n]"
        
        try:
            self.stdscr.addstr(y, 2, " " * (self.width - 4))
            self.stdscr.addstr(y, 2, confirm_msg[:self.width - 4], curses.color_pair(Colors.INPUT) | curses.A_BOLD)
            self.stdscr.refresh()
        except curses.error:
            pass
        
        key = self.stdscr.getch()
        
        if key == ord('y') or key == ord('Y'):
            # Get paths and create structure
            paths = self.parser.get_all_paths(self.target_directory)
            results = create_file_structure(paths)
            
            created = len(results["created"])
            skipped = len(results["skipped"])
            errors = len(results["errors"])
            
            if errors == 0:
                self.message = f"✓ Created {created} items, skipped {skipped} existing"
                self.message_type = "success"
            else:
                self.message = f"⚠ Created {created}, skipped {skipped}, errors: {errors}"
                self.message_type = "error"
        else:
            self.message = "Operation cancelled"
            self.message_type = "info"
    
    def _clear_input(self):
        """Clear the tree input"""
        self.tree_text = ""
        self.parsed_root = None
        self.message = "✓ Input cleared"
        self.message_type = "success"
    
    def _quit(self):
        """Quit the application"""
        self.running = False


def run_ui():
    """Entry point for the TUI"""
    def main(stdscr):
        app = TrTRealUI(stdscr)
        app.run()
    
    curses.wrapper(main)
