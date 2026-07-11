"""Renderer selection and fallback logic."""

from __future__ import annotations

import subprocess
from io import BytesIO
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont

if TYPE_CHECKING:
    from latex2clip.parser import MathMode

from latex2clip.renderer.base import BaseRenderer, RenderedFormula, RenderConfig


def get_renderer(engine: str = "auto") -> BaseRenderer:
    """Return a renderer instance based on engine name."""
    if engine == "matplotlib":
        from latex2clip.renderer.matplotlib_ import MatplotlibRenderer
        return MatplotlibRenderer()
    if engine == "latex":
        from latex2clip.renderer.local_tex import LocalTeXRenderer
        if not LocalTeXRenderer.is_available():
            raise RuntimeError("pdflatex not found in PATH")
        return LocalTeXRenderer()
    if engine == "katex":
        raise NotImplementedError("KaTeX renderer not yet implemented")
    # auto
    from latex2clip.renderer.matplotlib_ import MatplotlibRenderer
    return MatplotlibRenderer()


def _make_error_image(latex: str, error_msg: str, dpi: int = 300) -> RenderedFormula:
    """Generate a red error-placeholder image when all renderers fail."""
    # Draw at the output DPI: the composer scales every image by 72/dpi,
    # so a 72dpi-sized placeholder would display as an illegible sliver
    scale = max(dpi / 72.0, 1.0)
    text = f"Render error: {error_msg}\n{latex[:80]}"
    img = Image.new("RGBA", (int(400 * scale), int(60 * scale)), (255, 230, 230, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", int(12 * scale))
    except OSError:
        font = ImageFont.load_default()
    draw.text((int(4 * scale), int(4 * scale)), text, fill=(200, 0, 0, 255), font=font)
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return RenderedFormula(
        png_bytes=buf.getvalue(), width_px=img.width,
        height_px=img.height, baseline_px=img.height // 2, ok=False,
    )


def render_with_fallback(
    latex: str, mode: "MathMode", config: RenderConfig,
    engine: str = "auto", fallback: bool = True,
) -> RenderedFormula:
    """Render with primary engine, falling back on failure."""
    import logging
    log = logging.getLogger("texmail.renderer")

    try:
        primary = get_renderer(engine)
    except (RuntimeError, NotImplementedError) as engine_err:
        # e.g. engine="latex" without TeX, or the unimplemented "katex"
        log.warning("Renderer %r unavailable (%s), using default", engine, engine_err)
        primary = get_renderer("auto")
    try:
        return primary.render(latex, mode, config)
    except (ValueError, RuntimeError, OSError) as primary_err:
        log.debug("Primary renderer failed: %s", primary_err)
        if fallback:
            from latex2clip.renderer.local_tex import LocalTeXRenderer
            if LocalTeXRenderer.is_available():
                try:
                    return LocalTeXRenderer().render(latex, mode, config)
                except (RuntimeError, OSError, subprocess.SubprocessError) as fallback_err:
                    log.debug("Fallback renderer failed: %s", fallback_err)
                    return _make_error_image(latex, str(fallback_err), config.dpi)
        return _make_error_image(latex, str(primary_err), config.dpi)
    except Exception as unexpected:
        log.warning("Unexpected render error: %s", unexpected)
        return _make_error_image(latex, str(unexpected), config.dpi)
