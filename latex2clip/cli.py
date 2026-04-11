"""Command-line interface for latex2clip."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import click


@click.group()
def main():
    """latex2clip — Convert LaTeX in clipboard to images for email."""


@main.command()
@click.option("--daemon", is_flag=True, help="Run in background (fork)")
def start(daemon: bool):
    """Start the background daemon with hotkey listener and menu bar."""
    if daemon:
        import os
        pid = os.fork()
        if pid > 0:
            click.echo(f"latex2clip daemon started (pid {pid})")
            return
        os.setsid()
    from latex2clip.daemon import Daemon
    Daemon().start()


@main.command()
def stop():
    """Stop the running daemon."""
    r = subprocess.run(["pkill", "-f", "latex2clip start"], capture_output=True)
    click.echo("latex2clip daemon stopped." if r.returncode == 0
               else "No running daemon found.")


@main.command()
@click.option("--engine", default="auto", help="Renderer engine")
def convert(engine: str):
    """One-shot convert: read clipboard, render, write back."""
    from latex2clip.clipboard import read_plaintext, write_html_and_plain
    from latex2clip.composer import compose_html
    from latex2clip.config import load_config
    from latex2clip.parser import LatexSegment, parse
    from latex2clip.renderer import render_with_fallback
    from latex2clip.renderer.base import RenderConfig

    cfg = load_config()
    text = read_plaintext()
    if not text:
        click.echo("Clipboard is empty.", err=True); sys.exit(1)

    segments = parse(text)
    latex_indices = [i for i, s in enumerate(segments) if isinstance(s, LatexSegment)]
    if not latex_indices:
        click.echo("No LaTeX formulas found in clipboard.", err=True); sys.exit(1)

    render_cfg = RenderConfig(
        dpi=cfg.render.dpi, font_size_pt=cfg.render.font_size_pt,
        fg_color=cfg.render.fg_color, bg_color=cfg.render.bg_color)
    rendered = {}
    for idx in latex_indices:
        seg = segments[idx]
        assert isinstance(seg, LatexSegment)
        rendered[idx] = render_with_fallback(
            seg.content, seg.mode, render_cfg,
            engine=engine, fallback=cfg.advanced.fallback)

    html = compose_html(segments, rendered,
                        font_size_px=cfg.output.html_font_size_px,
                        dpi=cfg.render.dpi)

    try:
        from latex2clip.clipboard import build_rtfd, write_rich
        rtfd_data = build_rtfd(segments, rendered, dpi=cfg.render.dpi)
        write_rich(html, rtfd_data, text)
    except Exception:
        write_html_and_plain(html, text)

    click.echo(f"Converted {len(latex_indices)} formula(s). Cmd+V to paste.")


@main.command()
@click.option("--input", "input_text", default=None, help="Text to preview")
def preview(input_text: str | None):
    """Render and open an HTML preview in the browser."""
    from latex2clip.clipboard import read_plaintext
    from latex2clip.composer import compose_html
    from latex2clip.config import load_config
    from latex2clip.parser import LatexSegment, parse
    from latex2clip.renderer import render_with_fallback
    from latex2clip.renderer.base import RenderConfig

    cfg = load_config()
    text = input_text or read_plaintext()
    if not text:
        click.echo("No input text.", err=True); sys.exit(1)

    segments = parse(text)
    render_cfg = RenderConfig(
        dpi=cfg.render.dpi, font_size_pt=cfg.render.font_size_pt,
        fg_color=cfg.render.fg_color, bg_color=cfg.render.bg_color)
    rendered = {}
    for i, seg in enumerate(segments):
        if isinstance(seg, LatexSegment):
            rendered[i] = render_with_fallback(
                seg.content, seg.mode, render_cfg, engine=cfg.render.engine)

    html = compose_html(segments, rendered, dpi=cfg.render.dpi)
    preview_dir = Path(cfg.advanced.preview_dir)
    preview_dir.mkdir(parents=True, exist_ok=True)
    path = preview_dir / "preview.html"
    path.write_text(
        f"<html><body style='padding:20px;font-family:sans-serif;'>{html}</body></html>")
    subprocess.run(["open", str(path)])
    click.echo(f"Preview opened: {path}")


@main.command()
def doctor():
    """Check the runtime environment."""
    v = sys.version.split()[0]
    checks = [("Python " + v, True)]

    for mod, label in [("AppKit", "pyobjc-framework-Cocoa"),
                       ("Quartz", "pyobjc-framework-Quartz"),
                       ("matplotlib", "matplotlib"),
                       ("PIL", "Pillow"),
                       ("rumps", "rumps")]:
        try:
            __import__(mod)
            checks.append((label, True))
        except ImportError:
            checks.append((label, False))

    checks.append(("pdflatex" if shutil.which("pdflatex")
                   else "pdflatex (optional, for local TeX)", bool(shutil.which("pdflatex"))))
    checks.append(("node" if shutil.which("node")
                   else "node (optional, for KaTeX)", bool(shutil.which("node"))))

    try:
        from latex2clip.hotkey import check_accessibility
        checks.append(("Accessibility permission", check_accessibility()))
    except Exception:
        checks.append(("Accessibility permission", False))

    from latex2clip.config import CONFIG_PATH
    checks.append((f"Config file at {CONFIG_PATH}", CONFIG_PATH.exists()))

    for label, ok in checks:
        sym = click.style("✓", fg="green") if ok else click.style("✗", fg="red")
        click.echo(f"  {sym} {label}")


@main.group()
def service():
    """Manage the LaunchAgent (install/uninstall/status)."""


@service.command("install")
def service_install():
    from latex2clip.service import install
    install()
    click.echo("LaunchAgent installed. latex2clip will start at login.")


@service.command("uninstall")
def service_uninstall():
    from latex2clip.service import uninstall
    uninstall()
    click.echo("LaunchAgent removed.")


@service.command("status")
def service_status():
    from latex2clip.service import status
    s = status()
    if s["running"]:
        click.echo(f"latex2clip is running (pid {s['pid']})")
    else:
        click.echo("latex2clip is not running.")


if __name__ == "__main__":
    main()
