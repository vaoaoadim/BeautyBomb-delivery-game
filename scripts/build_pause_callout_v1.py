"""Build the native pixel-art pause callout used by the existing pause flow.

The artwork deliberately follows the integrated intro callout's palette and
stepped comic outline, but omits its courier-facing tail.  It is authored on
the final logical pixel grid: no master resize, smoothing, or browser font
loading is involved.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public/assets/game/ui"
FONT_PATH = ROOT / "visual-references/fonts/press-start-2p/PressStart2P-Regular.ttf"
FONT_LICENSE = FONT_PATH.with_name("OFL.txt")
TARGET = OUTPUT / "ui-015-pause-callout-v1.png"
METADATA = TARGET.with_suffix(".json")

FONT_SHA256 = "034c77f1f05ec89421e4a63f0e3a4ca1ecf852cc6d2bf611f126f275728e017d"
WIDTH = 304
HEIGHT = 232
FONT_SIZE = 15
TEXT_LINES = ("НЕ ТОРМОЗИ!", "НУЖНО УСПЕТЬ", "ВОВРЕМЯ :)")
PALETTE = {
    "violet": (30, 29, 62, 255),
    "lavender": (238, 240, 255, 255),
    "pink": (255, 79, 171, 255),
    "white": (255, 255, 255, 255),
    "transparent": (0, 0, 0, 0),
}


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def pixel_hash(image: Image.Image) -> str:
    return sha256(image.convert("RGBA").tobytes()).hexdigest()


def assert_binary_alpha(image: Image.Image) -> None:
    histogram = image.convert("RGBA").getchannel("A").histogram()
    if sum(histogram[1:255]):
        raise RuntimeError("UI-015 contains antialiased alpha values.")


def threshold_mask(mask: Image.Image) -> Image.Image:
    return mask.point(lambda value: 255 if value >= 128 else 0)


def polygon_offset(points: list[tuple[int, int]], x: int, y: int) -> list[tuple[int, int]]:
    return [(point_x + x, point_y + y) for point_x, point_y in points]


def draw_callout(font: ImageFont.FreeTypeFont) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), PALETTE["transparent"])
    draw = ImageDraw.Draw(image)

    # Same stepped-body language as UI-013, intentionally without a tail.
    outer = [(7, 1), (297, 1), (303, 7), (303, 225), (297, 231), (7, 231), (1, 225), (1, 7)]
    inner = [(11, 6), (293, 6), (298, 11), (298, 221), (293, 226), (11, 226), (6, 221), (6, 11)]
    draw.polygon(polygon_offset(outer, 1, 0), fill=PALETTE["pink"])
    draw.polygon(outer, fill=PALETTE["violet"])
    draw.polygon(inner, fill=PALETTE["lavender"])

    # A restrained white edge keeps the bubble aligned with the intro sticker
    # treatment without adding a separate decoration or tail.
    draw.rectangle((15, 10, 289, 12), fill=PALETTE["white"])
    draw.rectangle((10, 15, 12, 62), fill=PALETTE["white"])

    for index, line in enumerate(TEXT_LINES):
        width = round(font.getlength(line))
        x = round((WIDTH - width) / 2)
        y = 42 + index * 25
        mask = Image.new("L", image.size, 0)
        ImageDraw.Draw(mask).text((x, y), line, font=font, fill=255)
        text = Image.new("RGBA", image.size, PALETTE["violet"])
        text.putalpha(threshold_mask(mask))
        image.alpha_composite(text)

    assert_binary_alpha(image)
    return image


def main() -> None:
    if not FONT_PATH.exists() or not FONT_LICENSE.exists():
        raise RuntimeError("Press Start 2P and its local OFL license are required.")
    if file_hash(FONT_PATH) != FONT_SHA256:
        raise RuntimeError("Press Start 2P source hash changed.")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    asset = draw_callout(ImageFont.truetype(FONT_PATH, FONT_SIZE))
    asset.save(TARGET, optimize=True)
    METADATA.write_text(
        json.dumps(
            {
                "assetId": "UI-015",
                "version": "v1",
                "status": "integrated",
                "texture": TARGET.name,
                "canvas": {"width": WIDTH, "height": HEIGHT},
                "frame": {"width": WIDTH, "height": HEIGHT, "count": 1},
                "copy": "Не тормози! Нужно успеть вовремя :)",
                "renderedCopy": list(TEXT_LINES),
                "font": {"family": "Press Start 2P", "sizePx": FONT_SIZE},
                "palette": {
                    name: "#" + "".join(f"{channel:02x}" for channel in color[:3])
                    for name, color in PALETTE.items()
                    if name != "transparent"
                },
                "production": {
                    "buildScript": "scripts/build_pause_callout_v1.py",
                    "assetMode": "authored-low-resolution-pixel-art",
                    "fontSource": "visual-references/fonts/press-start-2p/PressStart2P-Regular.ttf",
                    "fontSha256": FONT_SHA256,
                    "fontLicense": "visual-references/fonts/press-start-2p/OFL.txt",
                    "fontLicenseId": "SIL-OFL-1.1",
                    "offlineResizeCount": 0,
                    "antialiasing": False,
                    "paletteQuantization": False,
                    "phaserTextureFilter": "nearest",
                    "runtimeSha256": file_hash(TARGET),
                    "runtimePixelSha256": pixel_hash(asset),
                },
                "runtime": {
                    "center": {"x": 180, "y": 312},
                    "origin": {"x": 0.5, "y": 0.5},
                    "fixedToCamera": True,
                    "tail": "none",
                    "continueButtonCenter": {"x": 180, "y": 350},
                    "restartButtonCenter": {"x": 180, "y": 404},
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
