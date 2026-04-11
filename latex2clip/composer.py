"""Compose HTML from parsed segments and rendered formulas."""

from __future__ import annotations

import base64
import html as html_mod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from latex2clip.renderer.base import RenderedFormula

from latex2clip.parser import LatexSegment, MathMode, Segment, TextSegment


def compose_html(
    segments: list[Segment],
    rendered: dict[int, RenderedFormula],
    font_size_px: int = 14,
    inline_height_em: float = 1.4,
    dpi: int = 300,
) -> str:
    """Build a self-contained HTML fragment (no <html>/<body>).

    Image display size is calculated from the actual rendered dimensions,
    converted from pixels at *dpi* to CSS px (≈ 72 dpi).
    """
    parts: list[str] = []

    for i, seg in enumerate(segments):
        if isinstance(seg, TextSegment):
            escaped = html_mod.escape(seg.content).replace("\n", "<br/>")
            parts.append(f'<span style="font-size:{font_size_px}px;">{escaped}</span>')

        elif isinstance(seg, LatexSegment):
            if i not in rendered:
                # Render failed for this formula — show source as fallback
                escaped = html_mod.escape(seg.original).replace("\n", "<br/>")
                parts.append(f'<span style="font-size:{font_size_px}px;color:#cc0000;">{escaped}</span>')
                continue
            formula = rendered[i]
            b64 = base64.b64encode(formula.png_bytes).decode("ascii")
            alt = html_mod.escape(seg.original)

            # Convert rendered pixel size to CSS display size
            # 72 CSS-px per inch / rendered DPI
            scale = 72.0 / dpi
            display_w = round(formula.width_px * scale)
            display_h = round(formula.height_px * scale)

            if seg.mode == MathMode.INLINE:
                parts.append(
                    f'<img src="data:image/png;base64,{b64}" '
                    f'alt="{alt}" '
                    f'style="vertical-align:middle; '
                    f'width:{display_w}px; height:{display_h}px; '
                    f'display:inline;" />'
                )
            else:
                # Display formula: use <br> + centered image (no <div>, Apple Mail strips it)
                parts.append(
                    f'<br/><img src="data:image/png;base64,{b64}" '
                    f'alt="{alt}" '
                    f'style="width:{display_w}px; height:{display_h}px;" /><br/>'
                )

    return "".join(parts)
