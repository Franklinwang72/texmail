"""Tests for latex2clip.composer."""

from latex2clip.composer import compose_html
from latex2clip.parser import LatexSegment, MathMode, TextSegment
from latex2clip.renderer.base import RenderedFormula

_TINY_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
    b"\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _formula(**kw):
    d = dict(png_bytes=_TINY_PNG, width_px=20, height_px=10, baseline_px=5)
    d.update(kw)
    return RenderedFormula(**d)


class TestComposer:
    def test_html_contains_base64_img(self):
        segments = [TextSegment("hello "), LatexSegment("x^2", MathMode.INLINE, "$x^2$")]
        html = compose_html(segments, {1: _formula()})
        assert "data:image/png;base64," in html
        assert "<img" in html

    def test_display_math_has_breaks(self):
        segments = [LatexSegment(r"\int", MathMode.DISPLAY, r"$$\int$$")]
        html = compose_html(segments, {0: _formula()})
        assert "<br/>" in html
        assert "<img" in html

    def test_html_escapes_text(self):
        html = compose_html([TextSegment("a < b & c > d")], {})
        assert "&lt;" in html
        assert "&amp;" in html

    def test_alt_text_contains_latex_source(self):
        segments = [LatexSegment("x^2", MathMode.INLINE, "$x^2$")]
        html = compose_html(segments, {0: _formula()})
        assert 'alt="$x^2$"' in html

    def test_inline_vertical_align(self):
        segments = [LatexSegment("a", MathMode.INLINE, "$a$")]
        html = compose_html(segments, {0: _formula()})
        assert "vertical-align:middle" in html

    def test_newline_becomes_br(self):
        html = compose_html([TextSegment("line1\nline2")], {})
        assert "<br/>" in html

    def test_empty_segments(self):
        assert compose_html([], {}) == ""
