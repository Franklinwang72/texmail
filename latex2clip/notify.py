"""macOS native notifications via osascript."""

from __future__ import annotations

import subprocess


def send_notification(title: str, message: str) -> None:
    """Display a macOS notification banner."""
    safe_title = title.replace("\\", "\\\\").replace('"', '\\"')
    safe_msg = message.replace("\\", "\\\\").replace('"', '\\"')
    subprocess.run(
        ["osascript", "-e",
         f'display notification "{safe_msg}" with title "{safe_title}"'],
        capture_output=True,
    )
