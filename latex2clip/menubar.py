"""macOS menu-bar status icon using pure PyObjC (no rumps)."""

from __future__ import annotations

import subprocess
import sys
from typing import TYPE_CHECKING

import AppKit
import objc
from Foundation import NSObject

if TYPE_CHECKING:
    from latex2clip.daemon import Daemon

from latex2clip.config import CONFIG_PATH


class _MenuDelegate(NSObject):
    """Objective-C delegate that handles menu item clicks."""

    daemon = objc.ivar()

    def convertNow_(self, sender):
        if self.daemon:
            self.daemon.trigger_convert()

    def previewLast_(self, sender):
        if self.daemon and self.daemon.last_preview_path:
            subprocess.run(["open", self.daemon.last_preview_path])

    def editConfig_(self, sender):
        subprocess.run(["open", str(CONFIG_PATH)])

    def quitApp_(self, sender):
        AppKit.NSApplication.sharedApplication().terminate_(None)


class LatexClipMenuBar:
    """Native macOS status-bar icon."""

    def __init__(self, daemon: "Daemon") -> None:
        self.daemon = daemon
        self._delegate = None
        self._status_item = None
        self._last_item = None

    def update_status(self, count: int) -> None:
        if self._last_item:
            self._last_item.setTitle_(f"Last: {count} formula(s)")

    def run(self) -> None:
        """Create the status bar item and enter the NSApplication run loop."""
        # Force-register our bundle ID so macOS treats this Python process
        # as a proper app (required for NSStatusBar to work).
        from Foundation import NSBundle

        bundle = NSBundle.mainBundle()
        info = bundle.infoDictionary()
        info["CFBundleIdentifier"] = "com.latex2clip.app"
        info["CFBundleName"] = "latex2clip"
        info["LSUIElement"] = True

        app = AppKit.NSApplication.sharedApplication()
        app.setActivationPolicy_(
            AppKit.NSApplicationActivationPolicyAccessory
        )

        # --- Status item ---
        bar = AppKit.NSStatusBar.systemStatusBar()
        self._status_item = bar.statusItemWithLength_(-1.0)
        btn = self._status_item.button()
        btn.setTitle_("\u2211")  # ∑

        # --- Delegate for actions ---
        self._delegate = _MenuDelegate.alloc().init()
        self._delegate.daemon = self.daemon

        # --- Menu ---
        cfg = self.daemon.config_manager.config
        mods = "+".join(m.capitalize() for m in cfg.hotkey.modifiers)
        hk = f"{mods}+{cfg.hotkey.key.upper()}"

        menu = AppKit.NSMenu.alloc().init()
        menu.setAutoenablesItems_(False)

        # ● Running
        status = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "\u25cf Running", None, ""
        )
        status.setEnabled_(False)
        menu.addItem_(status)

        # Last: –
        self._last_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Last: \u2013", None, ""
        )
        self._last_item.setEnabled_(False)
        menu.addItem_(self._last_item)

        menu.addItem_(AppKit.NSMenuItem.separatorItem())

        # Convert Now
        convert = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            f"Convert Now  ({hk})", "convertNow:", ""
        )
        convert.setTarget_(self._delegate)
        menu.addItem_(convert)

        # Preview Last
        preview = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Preview Last\u2026", "previewLast:", ""
        )
        preview.setTarget_(self._delegate)
        menu.addItem_(preview)

        menu.addItem_(AppKit.NSMenuItem.separatorItem())

        # Engine info
        eng = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            f"Engine: {cfg.render.engine}", None, ""
        )
        eng.setEnabled_(False)
        menu.addItem_(eng)

        # Hotkey info
        hk_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            f"Hotkey: {hk}", None, ""
        )
        hk_item.setEnabled_(False)
        menu.addItem_(hk_item)

        # Edit Config
        edit = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Edit Config\u2026", "editConfig:", ""
        )
        edit.setTarget_(self._delegate)
        menu.addItem_(edit)

        menu.addItem_(AppKit.NSMenuItem.separatorItem())

        # Quit
        quit_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Quit", "quitApp:", "q"
        )
        quit_item.setTarget_(self._delegate)
        menu.addItem_(quit_item)

        self._status_item.setMenu_(menu)

        # Enter run loop
        app.run()
