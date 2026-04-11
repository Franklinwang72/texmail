"""LaunchAgent install / uninstall / status."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

PLIST_PATH = Path.home() / "Library/LaunchAgents/com.latex2clip.agent.plist"
PLIST_LABEL = "com.latex2clip.agent"


def install() -> None:
    exe_path = shutil.which("latex2clip")
    if not exe_path:
        raise RuntimeError("latex2clip not found in PATH.")
    PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    plist_content = f"""\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{PLIST_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{exe_path}</string>
        <string>start</string>
        <string>--daemon</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/latex2clip.stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/latex2clip.stderr.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
    </dict>
</dict>
</plist>"""
    PLIST_PATH.write_text(plist_content)
    subprocess.run(["launchctl", "load", "-w", str(PLIST_PATH)], check=True)


def uninstall() -> None:
    if PLIST_PATH.exists():
        subprocess.run(["launchctl", "unload", str(PLIST_PATH)], capture_output=True)
        PLIST_PATH.unlink(missing_ok=True)


def status() -> dict:
    result = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if PLIST_LABEL in line:
            parts = line.split()
            pid = int(parts[0]) if parts[0] != "-" else None
            return {"running": pid is not None, "pid": pid}
    return {"running": False, "pid": None}
