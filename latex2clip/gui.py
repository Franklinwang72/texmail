"""latex2clip — macOS app with Automator Quick Action.

On first launch, installs a macOS Service (Automator workflow) that lets users:
1. Select text containing LaTeX in ANY app
2. Press shortcut (default Cmd+Shift+L, configurable in-app)
3. Selected text is replaced with rendered formulas
"""

from __future__ import annotations

import AppKit
import objc
from Foundation import NSObject, NSBundle, NSMakeRect

_MOD_SYMBOLS = {"cmd": "\u2318", "ctrl": "\u2303", "alt": "\u2325", "shift": "\u21e7"}

_NS_MODS = {
    "cmd": AppKit.NSEventModifierFlagCommand,
    "ctrl": AppKit.NSEventModifierFlagControl,
    "alt": AppKit.NSEventModifierFlagOption,
    "shift": AppKit.NSEventModifierFlagShift,
}
_ALL_MOD_MASK = 0
for _v in _NS_MODS.values():
    _ALL_MOD_MASK |= _v

_KEY_CODES = {
    0x00: "A", 0x01: "S", 0x02: "D", 0x03: "F",
    0x04: "H", 0x05: "G", 0x06: "Z", 0x07: "X",
    0x08: "C", 0x09: "V", 0x0B: "B", 0x0C: "Q",
    0x0D: "W", 0x0E: "E", 0x0F: "R", 0x10: "Y",
    0x11: "T", 0x12: "1", 0x13: "2", 0x14: "3",
    0x15: "4", 0x16: "6", 0x17: "5", 0x19: "9",
    0x1A: "7", 0x1C: "8", 0x1D: "0", 0x1F: "O",
    0x20: "U", 0x22: "I", 0x23: "P", 0x25: "L",
    0x26: "J", 0x28: "K", 0x2D: "N", 0x2E: "M",
}


def _display(key, mods):
    return "".join(_MOD_SYMBOLS.get(m, m) for m in mods) + key.upper()


class _AppDelegate(NSObject):
    window = objc.ivar()
    status_label = objc.ivar()
    font_size_field = objc.ivar()
    shortcut_label = objc.ivar()
    record_btn = objc.ivar()
    _recording = objc.ivar()
    _monitor = objc.ivar()
    _key = objc.ivar()
    _mods = objc.ivar()

    def applicationDidFinishLaunching_(self, notification):
        from latex2clip.config import load_config
        cfg = load_config()
        self._key = cfg.hotkey.key
        self._mods = cfg.hotkey.modifiers
        self._recording = False

        # Install the Automator Quick Action + set shortcut
        from latex2clip.service_installer import install_service, set_shortcut
        install_service()
        set_shortcut(self._key, self._mods)

        self._build_window(cfg)

    def _build_window(self, cfg):
        style = (AppKit.NSTitledWindowMask | AppKit.NSClosableWindowMask
                 | AppKit.NSMiniaturizableWindowMask)
        self.window = AppKit.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(200, 300, 420, 330), style,
            AppKit.NSBackingStoreBuffered, False)
        self.window.setTitle_("latex2clip")
        self.window.setLevel_(AppKit.NSFloatingWindowLevel)
        c = self.window.contentView()
        y = 280  # top

        # Title
        t = AppKit.NSTextField.labelWithString_("\u2211 latex2clip")
        t.setFont_(AppKit.NSFont.boldSystemFontOfSize_(22))
        t.setFrame_(NSMakeRect(20, y, 380, 35))
        c.addSubview_(t)
        y -= 60

        # Instructions
        instr = AppKit.NSTextField.labelWithString_(
            "\u9009\u4e2d\u542b LaTeX \u7684\u6587\u5b57 \u2192 "
            "\u6309\u5feb\u6377\u952e \u2192 \u516c\u5f0f\u81ea\u52a8\u6e32\u67d3\u66ff\u6362\n"
            "\u4e5f\u53ef\u4ee5\u53f3\u952e \u2192 \u670d\u52a1 \u2192 latex2clip"
        )
        instr.setFrame_(NSMakeRect(20, y, 390, 40))
        c.addSubview_(instr)
        y -= 50

        # ── Shortcut ──
        hl = AppKit.NSTextField.labelWithString_("\u5feb\u6377\u952e\uff1a")
        hl.setFrame_(NSMakeRect(20, y, 70, 28))
        c.addSubview_(hl)

        self.shortcut_label = AppKit.NSTextField.labelWithString_(
            _display(self._key, self._mods))
        self.shortcut_label.setFont_(
            AppKit.NSFont.monospacedSystemFontOfSize_weight_(20, 0.5))
        self.shortcut_label.setFrame_(NSMakeRect(90, y, 130, 28))
        c.addSubview_(self.shortcut_label)

        self.record_btn = AppKit.NSButton.alloc().initWithFrame_(
            NSMakeRect(230, y + 2, 80, 24))
        self.record_btn.setTitle_("\u66f4\u6539")
        self.record_btn.setBezelStyle_(AppKit.NSBezelStyleRounded)
        self.record_btn.setTarget_(self)
        self.record_btn.setAction_("onRecord:")
        c.addSubview_(self.record_btn)

        hint = AppKit.NSTextField.labelWithString_(
            "\u70b9\u201c\u66f4\u6539\u201d\u540e\u6309\u65b0\u7ec4\u5408\u952e")
        hint.setFont_(AppKit.NSFont.systemFontOfSize_(10))
        hint.setTextColor_(AppKit.NSColor.tertiaryLabelColor())
        hint.setFrame_(NSMakeRect(315, y + 2, 100, 24))
        c.addSubview_(hint)
        y -= 45

        # ── Font size ──
        sl = AppKit.NSTextField.labelWithString_("\u516c\u5f0f\u5b57\u53f7\uff1a")
        sl.setFrame_(NSMakeRect(20, y, 70, 24))
        c.addSubview_(sl)

        self.font_size_field = AppKit.NSTextField.alloc().initWithFrame_(
            NSMakeRect(90, y, 50, 24))
        self.font_size_field.setStringValue_(str(int(cfg.render.font_size_pt)))
        self.font_size_field.setAlignment_(AppKit.NSTextAlignmentCenter)
        c.addSubview_(self.font_size_field)

        pt = AppKit.NSTextField.labelWithString_("pt")
        pt.setFrame_(NSMakeRect(143, y, 25, 24))
        pt.setTextColor_(AppKit.NSColor.secondaryLabelColor())
        c.addSubview_(pt)

        for i, sz in enumerate([10, 12, 14, 16]):
            b = AppKit.NSButton.alloc().initWithFrame_(
                NSMakeRect(180 + i * 55, y, 48, 24))
            b.setTitle_(str(sz))
            b.setBezelStyle_(AppKit.NSBezelStyleRounded)
            b.setFont_(AppKit.NSFont.systemFontOfSize_(12))
            b.setTag_(sz)
            b.setTarget_(self)
            b.setAction_("onPresetSize:")
            c.addSubview_(b)
        y -= 40

        # Separator
        sep = AppKit.NSBox.alloc().initWithFrame_(NSMakeRect(20, y, 380, 1))
        sep.setBoxType_(AppKit.NSBoxSeparator)
        c.addSubview_(sep)
        y -= 10

        # Manual clipboard convert section
        ml = AppKit.NSTextField.labelWithString_(
            "\u6216\uff1a\u590d\u5236\u6587\u5b57 \u2192 \u70b9\u6309\u94ae \u2192 Cmd+V \u7c98\u8d34")
        ml.setFont_(AppKit.NSFont.systemFontOfSize_(11))
        ml.setTextColor_(AppKit.NSColor.secondaryLabelColor())
        ml.setFrame_(NSMakeRect(20, y, 380, 20))
        c.addSubview_(ml)
        y -= 45

        cb = AppKit.NSButton.alloc().initWithFrame_(NSMakeRect(20, y, 240, 40))
        cb.setTitle_("\u8f6c\u6362\u526a\u8d34\u677f\u4e2d\u7684\u516c\u5f0f")
        cb.setBezelStyle_(AppKit.NSBezelStyleRounded)
        cb.setFont_(AppKit.NSFont.systemFontOfSize_(14))
        cb.setTarget_(self)
        cb.setAction_("onConvert:")
        c.addSubview_(cb)

        self.status_label = AppKit.NSTextField.labelWithString_("")
        self.status_label.setFrame_(NSMakeRect(268, y + 5, 145, 30))
        self.status_label.setTextColor_(AppKit.NSColor.secondaryLabelColor())
        c.addSubview_(self.status_label)

        self.window.center()
        self.window.makeKeyAndOrderFront_(None)

    # ── Shortcut recording ──

    def onRecord_(self, sender):
        if self._recording:
            return
        self._recording = True
        self.record_btn.setTitle_("\u6309\u4e0b\u5feb\u6377\u952e\u2026")
        self.record_btn.setEnabled_(False)
        self.shortcut_label.setStringValue_("...")
        self._monitor = AppKit.NSEvent.addLocalMonitorForEventsMatchingMask_handler_(
            AppKit.NSEventMaskKeyDown, self._on_key)

    def _on_key(self, event):
        flags = event.modifierFlags() & _ALL_MOD_MASK
        if not flags:
            return event
        key_name = _KEY_CODES.get(event.keyCode())
        if not key_name:
            return event

        mods = [n for n, m in _NS_MODS.items() if flags & m]

        if self._monitor:
            AppKit.NSEvent.removeMonitor_(self._monitor)
            self._monitor = None

        self._key = key_name
        self._mods = mods
        self._recording = False
        self.shortcut_label.setStringValue_(_display(key_name, mods))
        self.record_btn.setTitle_("\u66f4\u6539")
        self.record_btn.setEnabled_(True)

        # Save and apply
        from latex2clip.config import save_hotkey
        from latex2clip.service_installer import set_shortcut
        save_hotkey(key_name, mods)
        set_shortcut(key_name, mods)
        self.status_label.setStringValue_(
            f"\u5feb\u6377\u952e\u5df2\u8bbe\u4e3a {_display(key_name, mods)}")
        return None

    # ── Font size ──

    def onPresetSize_(self, sender):
        self.font_size_field.setStringValue_(str(sender.tag()))

    def _get_font_size(self):
        try:
            return max(6.0, min(72.0, float(self.font_size_field.stringValue())))
        except ValueError:
            return 12.0

    # ── Manual clipboard convert ──

    def onConvert_(self, sender):
        self.status_label.setStringValue_("\u8f6c\u6362\u4e2d\u2026")
        self.status_label.display()
        try:
            from latex2clip.clipboard import read_plaintext, write_html_and_plain
            from latex2clip.composer import compose_html
            from latex2clip.config import load_config
            from latex2clip.parser import LatexSegment, parse
            from latex2clip.renderer import render_with_fallback
            from latex2clip.renderer.base import RenderConfig

            cfg = load_config()
            fs = self._get_font_size()
            text = read_plaintext()
            if not text:
                self.status_label.setStringValue_("\u274c \u526a\u8d34\u677f\u4e3a\u7a7a"); return
            segments = parse(text)
            indices = [i for i, s in enumerate(segments) if isinstance(s, LatexSegment)]
            if not indices:
                self.status_label.setStringValue_("\u274c \u672a\u68c0\u6d4b\u5230\u516c\u5f0f"); return
            rc = RenderConfig(dpi=cfg.render.dpi, font_size_pt=fs,
                              fg_color=cfg.render.fg_color, bg_color=cfg.render.bg_color)
            rendered = {}
            for idx in indices:
                seg = segments[idx]
                rendered[idx] = render_with_fallback(seg.content, seg.mode, rc,
                    engine=cfg.render.engine, fallback=cfg.advanced.fallback)
            html = compose_html(segments, rendered, font_size_px=int(fs),
                                inline_height_em=cfg.output.inline_height_em)
            try:
                from latex2clip.clipboard import build_rtfd, write_rich
                rtfd = build_rtfd(segments, rendered, dpi=cfg.render.dpi)
                write_rich(html, rtfd, text)
            except Exception:
                write_html_and_plain(html, text)
            self.status_label.setStringValue_(f"\u2705 {len(indices)}\u4e2a\u516c\u5f0f Cmd+V")
        except Exception as e:
            self.status_label.setStringValue_(f"\u274c {e}")

    def applicationShouldTerminateAfterLastWindowClosed_(self, app):
        return True


def run_gui():
    info = NSBundle.mainBundle().infoDictionary()
    info["CFBundleIdentifier"] = "com.latex2clip.app"
    info["CFBundleName"] = "latex2clip"
    app = AppKit.NSApplication.sharedApplication()
    app.setActivationPolicy_(AppKit.NSApplicationActivationPolicyRegular)
    delegate = _AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    app.activateIgnoringOtherApps_(True)
    app.run()
