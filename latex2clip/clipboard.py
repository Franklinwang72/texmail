"""macOS clipboard read/write via PyObjC.

Writes three formats simultaneously:
1. public.html       -> Gmail, Thunderbird
2. RTFD              -> Apple Mail
3. public.utf8-plain-text -> universal fallback
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from AppKit import (
    NSAttributedString,
    NSFileWrapper,
    NSMutableAttributedString,
    NSPasteboard,
    NSPasteboardTypeHTML,
    NSPasteboardTypeString,
    NSRTFDPboardType,
    NSTextAttachment,
)
from Foundation import NSData, NSDictionary

if TYPE_CHECKING:
    from latex2clip.renderer.base import RenderedFormula

from latex2clip.parser import LatexSegment, Segment, TextSegment


def read_plaintext() -> str | None:
    """Read plain text from the macOS system clipboard."""
    pb = NSPasteboard.generalPasteboard()
    return pb.stringForType_(NSPasteboardTypeString)


def write_rich(html: str, rtfd_data: bytes, plaintext: str) -> None:
    """Write HTML + RTFD + plain text to the clipboard."""
    pb = NSPasteboard.generalPasteboard()
    pb.clearContents()
    pb.setString_forType_(html, NSPasteboardTypeHTML)
    pb.setData_forType_(
        NSData.dataWithBytes_length_(rtfd_data, len(rtfd_data)),
        NSRTFDPboardType,
    )
    pb.setString_forType_(plaintext, NSPasteboardTypeString)


def write_html_and_plain(html: str, plaintext: str) -> None:
    """Write HTML + plain text to the clipboard (no RTFD)."""
    pb = NSPasteboard.generalPasteboard()
    pb.clearContents()
    pb.setString_forType_(html, NSPasteboardTypeHTML)
    pb.setString_forType_(plaintext, NSPasteboardTypeString)


def build_rtfd(
    segments: list[Segment],
    rendered: dict[int, "RenderedFormula"],
    dpi: int = 300,
) -> bytes:
    """Build RTFD NSData with inline images for Apple Mail."""
    result = NSMutableAttributedString.alloc().init()

    for i, seg in enumerate(segments):
        if isinstance(seg, TextSegment):
            attr_str = NSAttributedString.alloc().initWithString_(seg.content)
            result.appendAttributedString_(attr_str)
        elif isinstance(seg, LatexSegment):
            if i not in rendered:
                # Render failed — insert source text as fallback
                attr_str = NSAttributedString.alloc().initWithString_(seg.original)
                result.appendAttributedString_(attr_str)
                continue
            formula = rendered[i]
            attachment = NSTextAttachment.alloc().init()
            image_data = NSData.dataWithBytes_length_(
                formula.png_bytes, len(formula.png_bytes)
            )
            file_wrapper = NSFileWrapper.alloc().initRegularFileWithContents_(image_data)
            file_wrapper.setPreferredFilename_(f"formula_{i}.png")
            attachment.setFileWrapper_(file_wrapper)

            # Set display size: convert pixels to points (px / dpi * 72)
            display_width = formula.width_px / dpi * 72
            display_height = formula.height_px / dpi * 72
            # Use NSTextAttachmentCell to set the image size
            # (attachment.bounds is read-only in newer PyObjC)
            from AppKit import NSImage, NSSize
            ns_image = NSImage.alloc().initWithData_(image_data)
            ns_image.setSize_(NSSize(display_width, display_height))
            attachment.setImage_(ns_image)

            img_str = NSAttributedString.attributedStringWithAttachment_(attachment)
            result.appendAttributedString_(img_str)

    full_range = (0, result.length())
    rtfd_data = result.RTFDFromRange_documentAttributes_(
        full_range,
        NSDictionary.dictionaryWithObject_forKey_("NSRTFD", "DocumentType"),
    )
    if rtfd_data is None:
        raise RuntimeError("Failed to generate RTFD data")
    return bytes(rtfd_data)
