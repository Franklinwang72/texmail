"""Local TeX renderer — uses xelatex for full Unicode + package support."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from io import BytesIO
from pathlib import Path

from PIL import Image

from latex2clip.parser import MathMode
from latex2clip.renderer.base import BaseRenderer, RenderedFormula, RenderConfig

TEX_TEMPLATE = r"""\documentclass[preview,border=2pt]{{standalone}}
\usepackage{{amsmath,amssymb,amsfonts,mathrsfs}}
\usepackage{{tikz-cd}}
\usepackage{{xcolor}}
\usepackage{{fontspec}}
\definecolor{{fgcolor}}{{HTML}}{{{fg_hex}}}
\definecolor{{bgcolor}}{{HTML}}{{{bg_hex}}}
\pagecolor{{bgcolor}}
\color{{fgcolor}}
\AtBeginDocument{{\fontsize{{{fontsize}pt}}{{{lineheight}pt}}\selectfont}}
\begin{{document}}
{content}
\end{{document}}
"""


# Common macOS TeX paths — covers MacTeX, Homebrew, manual TeX Live
_TEX_SEARCH_PATHS = [
    "/Library/TeX/texbin",                              # MacTeX (symlink, most common)
    "/opt/homebrew/bin",                                # Homebrew Apple Silicon
    "/usr/local/bin",                                   # Homebrew Intel
]
# Also glob TeX Live year directories (2020–2030)
_TEXLIVE_GLOBS = [
    "/usr/local/texlive/*/bin/universal-darwin",
    "/usr/local/texlive/*/bin/x86_64-darwin",
    "/usr/local/texlive/*/bin/aarch64-darwin",
]


def _find_tex_engine() -> str | None:
    """Find xelatex (preferred) or pdflatex, searching common macOS locations."""
    # Prefer xelatex for Unicode/CJK support
    for engine in ["xelatex", "pdflatex"]:
        found = shutil.which(engine)
        if found:
            return found
        for d in _TEX_SEARCH_PATHS:
            p = Path(d) / engine
            if p.is_file():
                return str(p)
        import glob
        for pattern in _TEXLIVE_GLOBS:
            for d in sorted(glob.glob(pattern), reverse=True):
                p = Path(d) / engine
                if p.is_file():
                    return str(p)
    return None


# Keep old name as alias for compatibility
_find_pdflatex = _find_tex_engine


class LocalTeXRenderer(BaseRenderer):
    """Render using xelatex/pdflatex + pdftoppm."""

    def render(self, latex: str, mode: MathMode, config: RenderConfig) -> RenderedFormula:
        engine = _find_tex_engine()
        if not engine:
            raise RuntimeError("No TeX engine found (xelatex or pdflatex)")

        fg_hex = config.fg_color.lstrip("#")
        bg_hex = "FFFFFF" if config.bg_color in ("transparent", "#FFFFFF") else config.bg_color.lstrip("#")
        content = f"${latex}$" if mode == MathMode.INLINE else f"\\[ {latex} \\]"
        fontsize = config.font_size_pt
        lineheight = fontsize * 1.2
        tex_source = TEX_TEMPLATE.format(
            fg_hex=fg_hex, bg_hex=bg_hex, content=content,
            fontsize=fontsize, lineheight=lineheight)

        tex_bin_dir = str(Path(engine).parent)
        import os
        env = os.environ.copy()
        env["PATH"] = tex_bin_dir + ":" + env.get("PATH", "")

        with tempfile.TemporaryDirectory(prefix="latex2clip_") as tmpdir:
            tmp = Path(tmpdir)
            (tmp / "input.tex").write_text(tex_source, encoding="utf-8")

            result = subprocess.run(
                [engine, "-interaction=nonstopmode", "-halt-on-error", "input.tex"],
                cwd=tmpdir, capture_output=True, timeout=15,
                env=env,
            )
            if result.returncode != 0:
                raw = (result.stdout or result.stderr or b"").decode("utf-8", errors="replace")
                # Extract actual TeX error lines (start with !)
                error_lines = [l for l in raw.splitlines() if l.startswith("!")]
                if error_lines:
                    err_msg = "; ".join(error_lines[:3])
                else:
                    # Fallback: skip the version banner, find useful info
                    lines = raw.splitlines()
                    useful = [l for l in lines if l.strip() and not l.startswith("This is")
                              and not l.startswith("restricted") and not l.startswith("entering")]
                    err_msg = " ".join(useful[:5])
                raise RuntimeError(f"TeX error: {err_msg[:300]}")

            # Convert PDF → PNG at the requested DPI.
            # pdftoppm gives much sharper results than sips.
            pdftoppm = shutil.which("pdftoppm")
            gs = shutil.which("gs")

            if pdftoppm:
                subprocess.run(
                    [pdftoppm, "-png", "-r", str(config.dpi), "-singlefile",
                     str(tmp / "input.pdf"), str(tmp / "output")],
                    capture_output=True, check=True, timeout=10,
                )
                # pdftoppm writes output.png
            elif gs:
                subprocess.run(
                    [gs, "-q", "-dNOPAUSE", "-dBATCH",
                     "-sDEVICE=pngalpha",
                     f"-r{config.dpi}",
                     f"-sOutputFile={tmp / 'output.png'}",
                     str(tmp / "input.pdf")],
                    capture_output=True, check=True, timeout=10,
                )
            else:
                # Fallback to sips (lower quality)
                subprocess.run(
                    ["sips", "-s", "format", "png",
                     "-s", "dpiWidth", str(config.dpi),
                     "-s", "dpiHeight", str(config.dpi),
                     str(tmp / "input.pdf"), "--out", str(tmp / "output.png")],
                    capture_output=True, check=True, timeout=10,
                )

            img = Image.open(tmp / "output.png")
            img = self._autocrop(img)
            if config.padding_px > 0:
                padded = Image.new("RGBA",
                                   (img.width + 2 * config.padding_px,
                                    img.height + 2 * config.padding_px),
                                   (0, 0, 0, 0))
                padded.paste(img, (config.padding_px, config.padding_px))
                img = padded

            buf = BytesIO()
            img.save(buf, format="PNG")
            return RenderedFormula(
                png_bytes=buf.getvalue(), width_px=img.width,
                height_px=img.height, baseline_px=img.height // 2,
            )

    @staticmethod
    def _autocrop(img: Image.Image) -> Image.Image:
        bbox = img.getbbox()
        return img.crop(bbox) if bbox else img

    @classmethod
    def is_available(cls) -> bool:
        return _find_pdflatex() is not None
