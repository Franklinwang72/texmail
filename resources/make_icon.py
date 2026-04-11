"""Generate latex2clip.icns icon with a ∑ symbol."""

import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SIZES = [16, 32, 64, 128, 256, 512, 1024]
OUT_DIR = Path(__file__).parent


def make_png(size: int) -> Image.Image:
    """Create a single icon PNG at the given size."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded-rect background: deep blue gradient feel
    margin = int(size * 0.08)
    radius = int(size * 0.18)
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=radius,
        fill=(41, 98, 255, 255),  # vibrant blue
    )

    # Draw ∑ symbol in white
    font_size = int(size * 0.58)
    try:
        # Try system fonts that render ∑ well
        for font_name in [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/SFNSMono.ttf",
            "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        ]:
            try:
                font = ImageFont.truetype(font_name, font_size)
                break
            except OSError:
                continue
        else:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    text = "∑"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size - tw) / 2 - bbox[0]
    y = (size - th) / 2 - bbox[1] - size * 0.02  # nudge up slightly
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

    return img


def build_icns():
    with tempfile.TemporaryDirectory() as tmpdir:
        iconset = Path(tmpdir) / "latex2clip.iconset"
        iconset.mkdir()

        for s in SIZES:
            img = make_png(s)
            img.save(iconset / f"icon_{s}x{s}.png")
            # @2x versions
            if s <= 512:
                img2x = make_png(s * 2)
                img2x.save(iconset / f"icon_{s}x{s}@2x.png")

        out = OUT_DIR / "latex2clip.icns"
        subprocess.run(
            ["iconutil", "-c", "icns", str(iconset), "-o", str(out)],
            check=True,
        )
        print(f"Created {out}")


if __name__ == "__main__":
    build_icns()
