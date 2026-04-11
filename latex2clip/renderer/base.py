"""Base renderer interface and shared data structures."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from latex2clip.parser import MathMode


@dataclass
class RenderConfig:
    dpi: int = 300
    font_size_pt: float = 14.0
    fg_color: str = "#000000"
    bg_color: str = "#FFFFFF"
    padding_px: int = 4


@dataclass
class RenderedFormula:
    png_bytes: bytes
    width_px: int
    height_px: int
    baseline_px: int


class BaseRenderer(ABC):
    @abstractmethod
    def render(self, latex: str, mode: MathMode, config: RenderConfig) -> RenderedFormula:
        """Render a LaTeX string to a PNG image."""

    @classmethod
    def is_available(cls) -> bool:
        return False
