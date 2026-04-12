"""Configuration management with TOML and auto-reload."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore[no-redef]

CONFIG_DIR = Path.home() / ".config" / "latex2clip"
CONFIG_PATH = CONFIG_DIR / "config.toml"

DEFAULT_CONFIG_TEXT = """\
# latex2clip configuration
# Changes are picked up automatically — no restart needed.

[hotkey]
key = "L"
modifiers = ["cmd", "shift"]

[render]
engine = "auto"
dpi = 300
font_size_pt = 14.0
fg_color = "#000000"
bg_color = "#FFFFFF"

[output]
inline_height_em = 1.4
html_font_size_px = 14

[advanced]
fallback = true
timeout_seconds = 10
max_formulas = 50
preview_dir = "~/Library/Caches/texmail"
"""


@dataclass
class HotkeyConfig:
    key: str = "L"
    modifiers: list[str] = field(default_factory=lambda: ["cmd", "shift"])


@dataclass
class RenderConfigToml:
    engine: str = "auto"
    dpi: int = 300
    font_size_pt: float = 14.0
    fg_color: str = "#000000"
    bg_color: str = "#FFFFFF"


@dataclass
class OutputConfig:
    inline_height_em: float = 1.4
    html_font_size_px: int = 14


@dataclass
class AdvancedConfig:
    fallback: bool = True
    timeout_seconds: int = 10
    max_formulas: int = 50
    preview_dir: str = "/tmp/latex2clip"


@dataclass
class Config:
    hotkey: HotkeyConfig = field(default_factory=HotkeyConfig)
    render: RenderConfigToml = field(default_factory=RenderConfigToml)
    output: OutputConfig = field(default_factory=OutputConfig)
    advanced: AdvancedConfig = field(default_factory=AdvancedConfig)


def _parse_toml(data: dict) -> Config:
    cfg = Config()
    if "hotkey" in data:
        h = data["hotkey"]
        cfg.hotkey = HotkeyConfig(key=h.get("key", "L"),
                                  modifiers=h.get("modifiers", ["cmd", "shift"]))
    if "render" in data:
        r = data["render"]
        cfg.render = RenderConfigToml(
            engine=r.get("engine", "auto"), dpi=r.get("dpi", 300),
            font_size_pt=r.get("font_size_pt", 14.0),
            fg_color=r.get("fg_color", "#000000"),
            bg_color=r.get("bg_color", "#FFFFFF"),
        )
    if "output" in data:
        o = data["output"]
        cfg.output = OutputConfig(
            inline_height_em=o.get("inline_height_em", 1.4),
            html_font_size_px=o.get("html_font_size_px", 14),
        )
    if "advanced" in data:
        a = data["advanced"]
        cfg.advanced = AdvancedConfig(
            fallback=a.get("fallback", True),
            timeout_seconds=a.get("timeout_seconds", 10),
            max_formulas=a.get("max_formulas", 50),
            preview_dir=a.get("preview_dir", "/tmp/latex2clip"),
        )
    return cfg


def ensure_config() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(DEFAULT_CONFIG_TEXT)


def load_config() -> Config:
    ensure_config()
    try:
        with open(CONFIG_PATH, "rb") as f:
            data = tomllib.load(f)
        return _parse_toml(data)
    except (OSError, ValueError, KeyError) as e:
        import logging
        logging.getLogger("texmail").warning("Config load failed, using defaults: %s", e)
        return Config()


import fcntl as _fcntl


def _atomic_config_write(updater):
    """Read-modify-write config.toml with file locking to prevent corruption."""
    ensure_config()
    with open(CONFIG_PATH, "r+") as f:
        _fcntl.flock(f, _fcntl.LOCK_EX)
        text = f.read()
        text = updater(text)
        f.seek(0)
        f.write(text)
        f.truncate()
        _fcntl.flock(f, _fcntl.LOCK_UN)


def save_hotkey(key: str, modifiers: list[str]) -> None:
    """Update key= and modifiers= lines under [hotkey], preserving comments."""
    import re
    mods_str = ", ".join(f'"{m}"' for m in modifiers)

    def updater(text):
        if "[hotkey]" in text:
            text = re.sub(r'key\s*=\s*"[^"]*"', f'key = "{key}"', text, count=1)
            text = re.sub(r'modifiers\s*=\s*\[.*?\]', f'modifiers = [{mods_str}]', text, count=1)
        else:
            text += f'\n[hotkey]\nkey = "{key}"\nmodifiers = [{mods_str}]\n'
        return text

    _atomic_config_write(updater)


class ConfigManager:
    def __init__(self) -> None:
        self.config = load_config()
        self._callbacks: list[Callable[[Config], None]] = []
        self._observer = None

    def on_change(self, callback: Callable[[Config], None]) -> None:
        self._callbacks.append(callback)

    def start_watching(self) -> None:
        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer
            manager = self

            class Handler(FileSystemEventHandler):
                def on_modified(self, event):
                    if Path(event.src_path).name == "config.toml":
                        manager._reload()

            self._observer = Observer()
            self._observer.schedule(Handler(), str(CONFIG_DIR), recursive=False)
            self._observer.daemon = True
            self._observer.start()
        except ImportError:
            pass

    def stop_watching(self) -> None:
        if self._observer:
            self._observer.stop()
            self._observer = None

    def _reload(self) -> None:
        try:
            new = load_config()
            self.config = new
            for cb in self._callbacks:
                cb(new)
        except Exception:
            pass
