"""Main daemon process — coordinates all modules."""

from __future__ import annotations

import logging
from pathlib import Path

from latex2clip.clipboard import build_rtfd, read_plaintext, write_html_and_plain, write_rich
from latex2clip.composer import compose_html
from latex2clip.config import ConfigManager
from latex2clip.notify import send_notification
from latex2clip.parser import LatexSegment, parse
from latex2clip.renderer import render_with_fallback
from latex2clip.renderer.base import RenderConfig

log = logging.getLogger("taxmail")


class Daemon:
    def __init__(self) -> None:
        self.config_manager = ConfigManager()
        self.last_preview_path: str | None = None

    def trigger_convert(self) -> None:
        cfg = self.config_manager.config
        text = read_plaintext()
        if not text:
            send_notification("Taxmail", "Clipboard is empty")
            return

        segments = parse(text)
        latex_indices = [i for i, s in enumerate(segments) if isinstance(s, LatexSegment)]
        if not latex_indices:
            send_notification("Taxmail", "No LaTeX formulas found")
            return

        if len(latex_indices) > cfg.advanced.max_formulas:
            send_notification("Taxmail",
                              f"Too many formulas ({len(latex_indices)} > {cfg.advanced.max_formulas})")
            return

        render_cfg = RenderConfig(
            dpi=cfg.render.dpi, font_size_pt=cfg.render.font_size_pt,
            fg_color=cfg.render.fg_color, bg_color=cfg.render.bg_color,
        )
        rendered: dict[int, object] = {}
        for idx in latex_indices:
            seg = segments[idx]
            assert isinstance(seg, LatexSegment)
            rendered[idx] = render_with_fallback(
                seg.content, seg.mode, render_cfg,
                engine=cfg.render.engine, fallback=cfg.advanced.fallback)

        html = compose_html(segments, rendered,
                            font_size_px=cfg.output.html_font_size_px,
                            dpi=cfg.render.dpi)

        try:
            rtfd_data = build_rtfd(segments, rendered, dpi=cfg.render.dpi)
            write_rich(html, rtfd_data, text)
        except Exception:
            log.warning("RTFD build failed, writing HTML + plain only")
            write_html_and_plain(html, text)

        preview_dir = Path(cfg.advanced.preview_dir)
        preview_dir.mkdir(parents=True, exist_ok=True)
        preview_path = preview_dir / "preview.html"
        preview_path.write_text(
            f"<html><body style='padding:20px;font-family:sans-serif;'>{html}</body></html>")
        self.last_preview_path = str(preview_path)

        send_notification("Taxmail", f"Converted {len(rendered)} formula(s). Cmd+V to paste.")

    def start(self) -> None:
        from latex2clip.hotkey import HotkeyListener
        from latex2clip.menubar import LatexClipMenuBar

        cfg = self.config_manager.config

        # Hotkey may fail without Accessibility permission — non-fatal
        try:
            hotkey = HotkeyListener(
                key=cfg.hotkey.key, modifiers=cfg.hotkey.modifiers,
                callback=self.trigger_convert)
            hotkey.start()
            self.config_manager.on_change(
                lambda c: hotkey.update_hotkey(c.hotkey.key, c.hotkey.modifiers))
        except PermissionError:
            log.warning("Accessibility permission not granted — hotkey disabled. "
                        "Use menu bar Convert Now instead.")
            send_notification("Taxmail",
                              "Grant Accessibility permission for hotkey support")

        self.config_manager.start_watching()
        menubar = LatexClipMenuBar(self)
        menubar.run()
