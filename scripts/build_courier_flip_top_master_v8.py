"""Create a versioned courier master with a closed flip-top cream cap.

The approved v7 master is read-only. This narrowly replaces only its rear
cap region and keeps the vehicle, tube body, mounts, canvas, and alpha matte
unchanged so every runtime variant can derive from the same source.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "visual-references/veh-001-courier-clean-concept-v7.png"
OUTPUT = ROOT / "visual-references/veh-001-courier-clean-concept-v8-flip-top.png"

# This box contains the former rear cap only; roof mounts remain untouched.
CAP_REGION = (248, 132, 384, 380)

OUTLINE = (24, 25, 43, 255)
CREAM = (247, 244, 238, 255)
HIGHLIGHT = (255, 253, 247, 255)
MID = (222, 218, 214, 255)
SHADOW = (179, 176, 179, 255)
NOTCH = (160, 159, 169, 255)


def main() -> None:
    image = Image.open(SOURCE).convert("RGBA")
    clear = Image.new("RGBA", (CAP_REGION[2] - CAP_REGION[0], CAP_REGION[3] - CAP_REGION[1]))
    image.alpha_composite(clear, CAP_REGION[:2])
    draw = ImageDraw.Draw(image)

    # A broad, one-piece cap with a direct tube seam, hinge line, and a small
    # thumb notch: recognisable as a snap-open cosmetic flip top at runtime.
    outer = ((278, 148), (360, 148), (376, 161), (376, 360), (360, 373), (278, 373), (264, 359), (264, 162))
    inner = ((281, 153), (357, 153), (371, 164), (371, 357), (357, 368), (281, 368), (269, 356), (269, 165))
    draw.polygon(outer, fill=OUTLINE)
    draw.polygon(inner, fill=CREAM)
    draw.line(((282, 157), (356, 157)), fill=HIGHLIGHT, width=3)
    draw.line(((270, 167), (270, 354)), fill=HIGHLIGHT, width=2)
    draw.line(((282, 365), (356, 365)), fill=SHADOW, width=3)

    # The seam and hinge are on the tube side, the recess on the outer face.
    # No ribbing or threaded texture is introduced.
    draw.line(((366, 166), (366, 356)), fill=SHADOW, width=3)
    draw.line(((371, 166), (371, 356)), fill=OUTLINE, width=2)
    draw.rounded_rectangle((275, 236, 294, 298), radius=8, fill=NOTCH)
    draw.rounded_rectangle((278, 240, 289, 294), radius=6, fill=MID)
    draw.line(((279, 239), (289, 239)), fill=HIGHLIGHT, width=2)
    draw.line(((298, 361), (350, 361)), fill=SHADOW, width=3)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT)


if __name__ == "__main__":
    main()
