
import curses
from const import Colors

def calculate_status_panel_layout(
    width: int,
    height: int,
    menu_height: int,
    is_wide_layout: bool,
):
    """Calculate layout for the status panel."""
    status_height = 6

    if is_wide_layout:
        start_y = 4
        menu_width = min(55, int(width * 0.55) - 2)
        menu_width = max(30, menu_width)
        start_x = menu_width + 3
        panel_width = width - start_x - 2
    else:
        start_y = 4 + menu_height + 1
        start_x = 1
        panel_width = width - 4

    if panel_width < 25 or start_y + status_height > height - 5:
        return None

    return start_y, start_x, panel_width, status_height


def calculate_preview_panel_layout(
    width: int,
    height: int,
    menu_height: int,
    status_height: int,
    is_wide_layout: bool,
):
    """Calculate layout for the preview panel."""
    if is_wide_layout:
        start_y = 4 + max(menu_height, status_height) + 1
    else:
        start_y = 4 + menu_height + 1 + status_height + 1

    panel_width = width - 4
    panel_height = height - start_y - 4

    if panel_height < 4 or panel_width < 20:
        return None

    return start_y, panel_width, panel_height

def draw_box(stdscr, y: int, x: int, height: int, width: int, title: str, title_color: int):
    """Draw a box with a title"""
    try:
        # Top border with title
        stdscr.addstr(y, x, "╭" + "─" * (width - 2) + "╮", curses.color_pair(Colors.BORDER))
        if title:
            title_x = x + 2
            stdscr.addstr(y, title_x, f" {title} ", curses.color_pair(title_color) | curses.A_BOLD)
        
        # Sides
        for i in range(1, height - 1):
            stdscr.addstr(y + i, x, "│", curses.color_pair(Colors.BORDER))
            stdscr.addstr(y + i, x + width - 1, "│", curses.color_pair(Colors.BORDER))
        
        # Bottom border
        stdscr.addstr(y + height - 1, x, "╰" + "─" * (width - 2) + "╯", curses.color_pair(Colors.BORDER))
    except curses.error:
        pass
