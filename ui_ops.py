import os
import shutil
import shlex
import subprocess
import sys
import tempfile
from typing import Callable, List, Optional, Tuple

def select_clipboard_command(
    platform: str,
    which: Callable[[str], Optional[str]],
) -> Optional[list]:
    """Select the clipboard command for the current platform."""
    if platform.startswith("darwin"):
        return ["pbpaste"] if which("pbpaste") else None
    if platform.startswith("win"):
        if which("powershell"):
            return ["powershell", "-command", "Get-Clipboard"]
        if which("pwsh"):
            return ["pwsh", "-command", "Get-Clipboard"]
        return None
    if which("xclip"):
        return ["xclip", "-selection", "clipboard", "-o"]
    if which("xsel"):
        return ["xsel", "--clipboard", "--output"]
    return None


def get_clipboard_unavailable_message(platform: str) -> str:
    """Provide an error message when clipboard access is unavailable."""
    if platform.startswith("win"):
        return "Clipboard utility not found (requires PowerShell)."
    if platform.startswith("darwin"):
        return "Clipboard utility not found (pbpaste unavailable)."
    return "Clipboard utility not found. Install xclip or xsel."


def get_clipboard_content() -> Tuple[str, Optional[str]]:
    """Get content from system clipboard across platforms."""
    command = select_clipboard_command(sys.platform, shutil.which)
    if not command:
        return "", get_clipboard_unavailable_message(sys.platform)

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=2)
    except Exception as exc:
        return "", f"Clipboard error: {exc}"

    if result.returncode != 0:
        error_message = result.stderr.strip() or "Clipboard command failed"
        return "", error_message

    return result.stdout, None


def validate_editor_command(editor_cmd: str) -> List[str]:
    """
    Validate and split the editor command.
    Only allows a set of known safe editors to prevent arbitrary execution.
    """
    if not editor_cmd:
        raise ValueError("Editor command is empty")

    parts = shlex.split(editor_cmd)
    if not parts:
        raise ValueError("Invalid editor command")

    binary = parts[0]
    binary_name = os.path.basename(binary)

    # Allowed editors allowlist
    ALLOWED_EDITORS = {"vim", "vi", "nano", "code", "emacs", "notepad", "edit"}

    if binary_name not in ALLOWED_EDITORS:
        raise ValueError(f"Editor '{binary_name}' is not in the allowlist")

    return parts


def filter_tree_content(content: str) -> str:
    """Filter editor content, removing comment lines."""
    lines = content.splitlines()
    filtered_lines = [line for line in lines if not line.strip().startswith("#")]
    return "\n".join(filtered_lines).strip()
