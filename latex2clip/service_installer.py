"""Install a macOS Automator Quick Action for latex2clip.

Creates ~/Library/Services/latex2clip.workflow which:
1. Copies selected text (Cmd+C via AppleScript)
2. Runs Python to convert LaTeX → rendered images in clipboard
3. Pastes back (Cmd+V via AppleScript), replacing the selection

First run: macOS auto-prompts to allow controlling System Events (one-time).
Also programmatically sets the keyboard shortcut via `defaults write pbs`.
"""

from __future__ import annotations

import plistlib
import subprocess
import shutil
from pathlib import Path

WORKFLOW_NAME = "latex2clip"
SERVICES_DIR = Path.home() / "Library" / "Services"
WORKFLOW_PATH = SERVICES_DIR / f"{WORKFLOW_NAME}.workflow"

_MOD_PBS = {"cmd": "@", "shift": "$", "alt": "~", "ctrl": "^"}


def _find_project_dir() -> str:
    return str(Path(__file__).resolve().parent.parent)


def _find_venv_python() -> str:
    p = Path(_find_project_dir()) / ".venv" / "bin" / "python"
    return str(p) if p.exists() else "python3"


def install_service() -> str:
    """Create and install the Automator Quick Action."""
    SERVICES_DIR.mkdir(parents=True, exist_ok=True)
    # Remove old version
    if WORKFLOW_PATH.exists():
        shutil.rmtree(WORKFLOW_PATH)

    contents = WORKFLOW_PATH / "Contents"
    contents.mkdir(parents=True)

    venv_python = _find_venv_python()
    project_dir = _find_project_dir()

    # The shell script that does: copy → convert clipboard → paste
    script = f'''export PATH="/Library/TeX/texbin:/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin:$PATH"

# 1. Copy selection to clipboard
osascript -e 'tell application "System Events" to keystroke "c" using command down'
sleep 0.3

# 2. Convert clipboard (LaTeX → rendered images)
"{venv_python}" << 'PYTHON_EOF'
import sys
sys.path.insert(0, "{project_dir}")
from latex2clip.clipboard import read_plaintext, write_html_and_plain
from latex2clip.composer import compose_html
from latex2clip.config import load_config
from latex2clip.parser import LatexSegment, parse
from latex2clip.renderer import render_with_fallback
from latex2clip.renderer.base import RenderConfig

text = read_plaintext()
if not text:
    sys.exit(0)
cfg = load_config()
segments = parse(text)
indices = [i for i, s in enumerate(segments) if isinstance(s, LatexSegment)]
if not indices:
    sys.exit(0)
rc = RenderConfig(dpi=cfg.render.dpi, font_size_pt=cfg.render.font_size_pt,
                  fg_color=cfg.render.fg_color, bg_color=cfg.render.bg_color)
rendered = {{}}
for idx in indices:
    seg = segments[idx]
    rendered[idx] = render_with_fallback(seg.content, seg.mode, rc,
        engine=cfg.render.engine, fallback=cfg.advanced.fallback)
html = compose_html(segments, rendered, font_size_px=int(cfg.render.font_size_pt),
                    dpi=cfg.render.dpi)
try:
    from latex2clip.clipboard import build_rtfd, write_rich
    rtfd = build_rtfd(segments, rendered, dpi=cfg.render.dpi)
    write_rich(html, rtfd, text)
except Exception:
    write_html_and_plain(html, text)
print(f"Converted {{len(indices)}} formulas")
PYTHON_EOF

# 3. Paste back (replaces selection)
sleep 0.2
osascript -e 'tell application "System Events" to keystroke "v" using command down'

# 4. Notify
osascript -e 'display notification "Formulas rendered and replaced" with title "Taxmail"'
'''

    # Build the Automator workflow plist
    wflow = {
        "AMApplicationBuild": "523",
        "AMApplicationVersion": "2.10",
        "AMDocumentVersion": "2",
        "actions": [
            {
                "action": {
                    "AMAccepts": {"Container": "List", "Optional": True,
                                  "Types": ["com.apple.cocoa.string"]},
                    "AMActionVersion": "2.0.3",
                    "AMApplication": ["Automator"],
                    "AMBundleIdentifier": "com.apple.RunShellScript",
                    "AMCategory": "AMCategoryUtilities",
                    "AMIconName": "Automator",
                    "AMName": "Run Shell Script",
                    "AMProvides": {"Container": "List",
                                   "Types": ["com.apple.cocoa.string"]},
                    "ActionBundlePath": "/System/Library/Automator/Run Shell Script.action",
                    "ActionName": "Run Shell Script",
                    "ActionParameters": {
                        "COMMAND_STRING": script,
                        "CheckedForUserDefaultShell": True,
                        "inputMethod": 1,  # 1 = as arguments (we ignore input, use clipboard)
                        "shell": "/bin/bash",
                        "source": "",
                    },
                    "BundleIdentifier": "com.apple.RunShellScript",
                    "CFBundleVersion": "2.0.3",
                    "CanShowSelectedItemsWhenRun": False,
                    "CanShowWhenRun": False,
                    "Class Name": "RunShellScriptAction",
                    "InputUUID": "00000000-0000-0000-0000-000000000000",
                    "Keywords": ["Shell", "Script"],
                    "OutputUUID": "11111111-1111-1111-1111-111111111111",
                    "UUID": "22222222-2222-2222-2222-222222222222",
                    "UnlocalizedApplications": ["Automator"],
                    "arguments": {
                        "0": {"default value": "/bin/bash", "name": "shell",
                              "required": "0", "type": "0", "uuid": "0"},
                        "2": {"default value": script, "name": "COMMAND_STRING",
                              "required": "0", "type": "0", "uuid": "2"},
                        "3": {"default value": "1", "name": "inputMethod",
                              "required": "0", "type": "0", "uuid": "3"},
                        "4": {"default value": "", "name": "CheckedForUserDefaultShell",
                              "required": "0", "type": "0", "uuid": "4"},
                    },
                    "isViewVisible": True,
                    "location": "300:600",
                    "nibPath": "/System/Library/Automator/Run Shell Script.action/Contents/Resources/Base.lproj/main.nib",
                },
                "class": "AMBundleAction",
                "isViewVisible": True,
            }
        ],
        "connectors": {},
        "workflowMetaData": {
            "serviceInputTypeIdentifier": "com.apple.Automator.text",
            "serviceOutputTypeIdentifier": "com.apple.Automator.nothing",
            "serviceProcessesInput": 0,
            "workflowTypeIdentifier": "com.apple.Automator.servicesMenu",
        },
    }

    with open(contents / "document.wflow", "wb") as f:
        plistlib.dump(wflow, f)

    info = {
        "CFBundleName": WORKFLOW_NAME,
        "CFBundleIdentifier": f"com.apple.Automator.{WORKFLOW_NAME}",
        "NSServices": [{
            "NSMenuItem": {"default": WORKFLOW_NAME},
            "NSMessage": "runWorkflowAsService",
            "NSRequiredContext": {"NSTextContent": "Text"},
            "NSSendTypes": ["NSStringPboardType"],
            "NSReturnTypes": [],
        }],
    }
    with open(contents / "Info.plist", "wb") as f:
        plistlib.dump(info, f)

    subprocess.run(["/System/Library/CoreServices/pbs", "-flush"],
                   capture_output=True)
    return str(WORKFLOW_PATH)


def set_shortcut(key: str, modifiers: list[str]) -> None:
    """Set keyboard shortcut by directly modifying ~/Library/Preferences/pbs.plist."""
    import plistlib as _plistlib

    pbs_mods = "".join(_MOD_PBS.get(m, "") for m in modifiers)
    pbs_equiv = pbs_mods + key.lower()
    plist_path = Path.home() / "Library" / "Preferences" / "pbs.plist"

    # Read
    try:
        with open(plist_path, "rb") as f:
            data = _plistlib.load(f)
    except Exception:
        data = {}

    status = data.get("NSServicesStatus", {})
    entry = {"enabled": True, "key_equivalent": pbs_equiv}

    # Update ALL latex2clip service keys
    for k in list(status.keys()):
        if "latex2clip" in k.lower():
            status[k] = entry

    # Also ensure the standard Automator keys exist
    for prefix in [f"com.apple.Automator.{WORKFLOW_NAME}", WORKFLOW_NAME]:
        svc_key = f"{prefix} - {WORKFLOW_NAME} - runWorkflowAsService"
        status[svc_key] = entry

    data["NSServicesStatus"] = status

    # Write back
    with open(plist_path, "wb") as f:
        _plistlib.dump(data, f)

    # Force pbs to reload
    subprocess.run(["killall", "pbs"], capture_output=True)
    import time
    time.sleep(1)


def uninstall_service() -> None:
    if WORKFLOW_PATH.exists():
        shutil.rmtree(WORKFLOW_PATH)
    subprocess.run(["/System/Library/CoreServices/pbs", "-flush"],
                   capture_output=True)
