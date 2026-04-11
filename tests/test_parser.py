"""Tests for latex2clip.parser."""

from latex2clip.parser import LatexSegment, MathMode, TextSegment, parse


class TestParser:
    # --- $...$ inline ---

    def test_single_inline(self):
        result = parse("hello $x^2$ world")
        assert result == [
            TextSegment("hello "),
            LatexSegment("x^2", MathMode.INLINE, "$x^2$"),
            TextSegment(" world"),
        ]

    def test_multiple_inline(self):
        result = parse("$a$ and $b$")
        latex_segs = [s for s in result if isinstance(s, LatexSegment)]
        assert len(latex_segs) == 2
        assert latex_segs[0].content == "a"
        assert latex_segs[1].content == "b"

    def test_adjacent_inline(self):
        result = parse("$a$$b$")
        latex_segs = [s for s in result if isinstance(s, LatexSegment)]
        assert len(latex_segs) == 2
        assert all(s.mode == MathMode.INLINE for s in latex_segs)

    # --- $$...$$ display ---

    def test_single_display(self):
        result = parse("before $$\\int_0^1 f(x)dx$$ after")
        assert len(result) == 3
        assert result[1].mode == MathMode.DISPLAY
        assert result[1].content == "\\int_0^1 f(x)dx"

    def test_display_multiline(self):
        result = parse("$$\n\\frac{1}{2}\n$$")
        assert len(result) == 1
        assert isinstance(result[0], LatexSegment)
        assert result[0].mode == MathMode.DISPLAY

    def test_display_math_content(self):
        result = parse("$$\\int_0^1$$")
        assert len(result) == 1
        assert result[0].mode == MathMode.DISPLAY

    # --- \[...\] display (LaTeX standard) ---

    def test_bracket_display(self):
        result = parse("before \\[\n\\frac{1}{2}\n\\] after")
        assert len(result) == 3
        assert result[1].mode == MathMode.DISPLAY
        assert result[1].content == "\\frac{1}{2}"

    def test_bracket_display_single_line(self):
        result = parse("\\[x^2\\]")
        assert len(result) == 1
        assert result[0].mode == MathMode.DISPLAY
        assert result[0].content == "x^2"

    def test_bracket_display_with_blank_lines(self):
        """Blank lines inside \\[...\\] should be collapsed."""
        result = parse("\\[\n\nx^2\n\n\\]")
        latex_segs = [s for s in result if isinstance(s, LatexSegment)]
        assert len(latex_segs) == 1
        assert "\n\n" not in latex_segs[0].content

    def test_multiple_bracket_display(self):
        result = parse("\\[a\\]\n\\[b\\]")
        latex_segs = [s for s in result if isinstance(s, LatexSegment)]
        assert len(latex_segs) == 2
        assert all(s.mode == MathMode.DISPLAY for s in latex_segs)

    # --- \(...\) inline (LaTeX standard) ---

    def test_paren_inline(self):
        result = parse("see \\(x^2\\) here")
        assert len(result) == 3
        assert result[1].mode == MathMode.INLINE
        assert result[1].content == "x^2"

    def test_paren_inline_preserves_original(self):
        result = parse("\\(x^2\\)")
        assert result[0].original == "\\(x^2\\)"

    # --- Mixed delimiters ---

    def test_mixed_dollar_and_bracket(self):
        result = parse("$a$ then \\[b\\]")
        segs = [s for s in result if isinstance(s, LatexSegment)]
        assert len(segs) == 2
        assert segs[0].mode == MathMode.INLINE
        assert segs[1].mode == MathMode.DISPLAY

    def test_mixed_inline_and_display(self):
        result = parse("inline $x$ and display $$y$$")
        segs = [s for s in result if isinstance(s, LatexSegment)]
        assert segs[0].mode == MathMode.INLINE
        assert segs[1].mode == MathMode.DISPLAY

    # --- Preprocessing / edge cases ---

    def test_missing_backslash_between_displays(self):
        """\\][ should be auto-fixed to \\]\\[."""
        result = parse("\\[a\\][\nb\n\\]")
        latex_segs = [s for s in result if isinstance(s, LatexSegment)]
        assert len(latex_segs) == 2

    def test_escaped_dollar(self):
        result = parse("price is \\$5")
        assert len(result) == 1
        assert isinstance(result[0], TextSegment)
        assert result[0].content == "price is $5"

    def test_unclosed_dollar(self):
        result = parse("just a $ sign")
        assert all(isinstance(s, TextSegment) for s in result)

    def test_no_latex(self):
        result = parse("just plain text")
        assert result == [TextSegment("just plain text")]

    def test_empty_string(self):
        assert parse("") == []

    def test_chinese_text_with_latex(self):
        result = parse("由 $f(x)=x^2$ 可知")
        assert isinstance(result[0], TextSegment)
        assert result[0].content == "由 "
        assert isinstance(result[1], LatexSegment)
        assert result[1].content == "f(x)=x^2"

    def test_original_preserved(self):
        result = parse("see $x^2$ here")
        seg = [s for s in result if isinstance(s, LatexSegment)][0]
        assert seg.original == "$x^2$"
