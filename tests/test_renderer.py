"""Tests for latex2clip.renderer.matplotlib_."""

from io import BytesIO

from PIL import Image

from latex2clip.parser import MathMode
from latex2clip.renderer.base import RenderConfig
from latex2clip.renderer.matplotlib_ import MatplotlibRenderer


class TestMatplotlibRenderer:
    def test_simple_formula(self):
        r = MatplotlibRenderer()
        result = r.render("x^2", MathMode.INLINE, RenderConfig())
        assert result.png_bytes[:8] == b"\x89PNG\r\n\x1a\n"
        assert result.width_px > 0
        assert result.height_px > 0

    def test_fraction(self):
        r = MatplotlibRenderer()
        result = r.render(r"\frac{1}{2}", MathMode.INLINE, RenderConfig())
        assert len(result.png_bytes) > 100

    def test_display_mode_larger(self):
        r = MatplotlibRenderer()
        cfg = RenderConfig()
        inline = r.render(r"\sum_{i=1}^n", MathMode.INLINE, cfg)
        display = r.render(r"\sum_{i=1}^n", MathMode.DISPLAY, cfg)
        assert display.height_px >= inline.height_px

    def test_transparent_background(self):
        r = MatplotlibRenderer()
        result = r.render("x", MathMode.INLINE, RenderConfig(bg_color="transparent"))
        img = Image.open(BytesIO(result.png_bytes))
        assert img.mode == "RGBA"

    def test_is_available(self):
        assert MatplotlibRenderer.is_available() is True

    def test_greek_letters(self):
        r = MatplotlibRenderer()
        result = r.render(r"\alpha + \beta", MathMode.INLINE, RenderConfig())
        assert result.png_bytes[:4] == b"\x89PNG"

    def test_integral(self):
        r = MatplotlibRenderer()
        result = r.render(r"\int_0^1 f(x)dx", MathMode.INLINE, RenderConfig())
        assert result.width_px > 0
