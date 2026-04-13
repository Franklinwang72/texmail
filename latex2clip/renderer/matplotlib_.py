"""Matplotlib-based LaTeX renderer (default, pure-Python)."""

from __future__ import annotations

import re
from io import BytesIO

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["mathtext.fontset"] = "cm"  # Computer Modern — classic LaTeX font
import matplotlib.pyplot as plt
from PIL import Image

from latex2clip.parser import MathMode
from latex2clip.renderer.base import BaseRenderer, RenderedFormula, RenderConfig

# --- amsmath → mathtext shims ---
# matplotlib mathtext doesn't support many amsmath commands.
# We rewrite them into constructs mathtext *does* understand.

def _shim_xrightarrow(m: re.Match) -> str:
    label = m.group(1)
    return rf"\stackrel{{{label}}}{{\rightarrow}}"

def _shim_xleftarrow(m: re.Match) -> str:
    label = m.group(1)
    return rf"\stackrel{{{label}}}{{\leftarrow}}"

def _shim_text(m: re.Match) -> str:
    return rf"\mathrm{{{m.group(1)}}}"

_SHIMS: list[tuple[re.Pattern, object]] = [
    (re.compile(r"\\xrightarrow\s*\{([^}]*)\}"), _shim_xrightarrow),
    (re.compile(r"\\xleftarrow\s*\{([^}]*)\}"),  _shim_xleftarrow),
    (re.compile(r"\\text\s*\{([^}]*)\}"),         _shim_text),
    (re.compile(r"\\operatorname\s*\{([^}]*)\}"), _shim_text),
    (re.compile(r"\\textbf\s*\{([^}]*)\}"),       lambda m: rf"\mathbf{{{m.group(1)}}}"),
    (re.compile(r"\\textit\s*\{([^}]*)\}"),       lambda m: rf"\mathit{{{m.group(1)}}}"),
    (re.compile(r"\\boxed\s*\{([^}]*)\}"),        lambda m: m.group(1)),
    (re.compile(r"\\mathbb\s*\{([^}]*)\}"),       lambda m: rf"\mathcal{{{m.group(1)}}}"),
]


def _preprocess(latex: str) -> str:
    """Rewrite unsupported amsmath commands for mathtext compatibility."""
    for pat, repl in _SHIMS:
        latex = pat.sub(repl, latex)
    return latex


class MatplotlibRenderer(BaseRenderer):
    """Render LaTeX using matplotlib's built-in mathtext engine."""

    def render(self, latex: str, mode: MathMode, config: RenderConfig) -> RenderedFormula:
        latex = _preprocess(latex)
        # Collapse newlines — mathtext silently renders raw code if \n is present
        latex = " ".join(latex.split())

        fontsize = config.font_size_pt
        if mode == MathMode.DISPLAY:
            fontsize *= 1.2

        fig = plt.figure(figsize=(0.01, 0.01))
        is_transparent = config.bg_color == "transparent"
        if is_transparent:
            fig.patch.set_alpha(0.0)
        else:
            fig.patch.set_facecolor(config.bg_color)

        text_obj = fig.text(0, 0, f"${latex}$", fontsize=fontsize,
                            color=config.fg_color, usetex=False)

        # Force render — if mathtext can't parse, this raises immediately
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        _, _, descent = renderer.get_text_width_height_descent(
            f"${latex}$", text_obj.get_fontproperties(), ismath="TeX")
        descent_px = int(descent * config.dpi / 72)

        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=config.dpi,
                    bbox_inches="tight", pad_inches=0.02,
                    transparent=is_transparent)
        plt.close(fig)

        buf.seek(0)
        img = Image.open(buf)
        img.load()  # force decode to catch corrupt PNG early
        img = self._autocrop(img)

        if config.padding_px > 0:
            pad_color = (255, 255, 255, 255) if not is_transparent else (0, 0, 0, 0)
            padded = Image.new("RGBA",
                               (img.width + 2 * config.padding_px,
                                img.height + 2 * config.padding_px),
                               pad_color)
            padded.paste(img, (config.padding_px, config.padding_px))
            img = padded

        out = BytesIO()
        img.save(out, format="PNG")
        return RenderedFormula(
            png_bytes=out.getvalue(),
            width_px=img.width,
            height_px=img.height,
            baseline_px=max(descent_px + config.padding_px, img.height // 4),
        )

    @staticmethod
    def _autocrop(img: Image.Image) -> Image.Image:
        bbox = img.getbbox()
        if bbox:
            return img.crop(bbox)
        return img

    @classmethod
    def is_available(cls) -> bool:
        try:
            import matplotlib  # noqa: F401
            return True
        except ImportError:
            return False
