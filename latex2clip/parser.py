"""LaTeX fragment extraction from plain text."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Union


class MathMode(Enum):
    INLINE = "inline"    # $...$  or \(...\)
    DISPLAY = "display"  # $$...$$ or \[...\]


@dataclass
class TextSegment:
    content: str


@dataclass
class LatexSegment:
    content: str      # bare LaTeX without delimiters
    mode: MathMode
    original: str     # with delimiters


Segment = Union[TextSegment, LatexSegment]

# Priority order:
#   1. \[...\]  — display math (LaTeX standard)
#   2. \(...\)  — inline math (LaTeX standard)
#   3. $$...$$  — display math (TeX shorthand)
#   4. $...$    — inline math (TeX shorthand)
#
# Must match longer delimiters before shorter ones.
PATTERN = re.compile(
    r'\\\['              # \[ opening
    r'(.*?)'             # content (group 1)
    r'\\\]'              # \] closing
    r'|'
    r'\\\('              # \( opening
    r'(.*?)'             # content (group 2)
    r'\\\)'              # \) closing
    r'|'
    r'(?<!\\)\$\$'       # $$ opening
    r'(.+?)'             # content (group 3)
    r'(?<!\\)\$\$'       # $$ closing
    r'|'
    r'(?<!\\)\$'         # $ opening
    r'([^\$\n]+?)'       # content (group 4, no bare $, no newline)
    r'(?<!\\)\$',        # $ closing
    re.DOTALL,
)


def _preprocess(text: str) -> str:
    """Fix common delimiter issues before parsing."""
    # \][ → \]\[ (missing backslash between consecutive display formulas)
    text = re.sub(r'\\\]\s*\[(?!\\)', r'\\]\n\\[', text)
    # \)( → \)\( (same for inline)
    text = re.sub(r'\\\)\s*\((?!\\)', r'\\)\n\\(', text)
    return text


def _clean_latex(content: str) -> str:
    """Clean up LaTeX content: collapse blank lines (invalid in math mode)."""
    # Replace blank lines (paragraph breaks) with single newlines
    content = re.sub(r'\n\s*\n', '\n', content)
    return content.strip()


def parse(text: str) -> list[Segment]:
    """Split *text* into an ordered list of TextSegment / LatexSegment."""
    if not text:
        return []

    text = _preprocess(text)

    segments: list[Segment] = []
    last_end = 0

    for m in PATTERN.finditer(text):
        if m.start() > last_end:
            segments.append(TextSegment(text[last_end : m.start()]))

        if m.group(1) is not None:
            # \[...\] display math
            segments.append(
                LatexSegment(
                    content=_clean_latex(m.group(1)),
                    mode=MathMode.DISPLAY,
                    original=m.group(0),
                )
            )
        elif m.group(2) is not None:
            # \(...\) inline math
            segments.append(
                LatexSegment(
                    content=_clean_latex(m.group(2)),
                    mode=MathMode.INLINE,
                    original=m.group(0),
                )
            )
        elif m.group(3) is not None:
            # $$...$$ display math
            segments.append(
                LatexSegment(
                    content=_clean_latex(m.group(3)),
                    mode=MathMode.DISPLAY,
                    original=m.group(0),
                )
            )
        else:
            # $...$ inline math
            segments.append(
                LatexSegment(
                    content=_clean_latex(m.group(4)),
                    mode=MathMode.INLINE,
                    original=m.group(0),
                )
            )
        last_end = m.end()

    if last_end < len(text):
        segments.append(TextSegment(text[last_end:]))

    # Replace escaped \$ with literal $
    for i, seg in enumerate(segments):
        if isinstance(seg, TextSegment):
            segments[i] = TextSegment(seg.content.replace("\\$", "$"))

    return segments
