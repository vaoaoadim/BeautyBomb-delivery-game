"""Build UI-015 v2 as the tail-free, enlarged sibling of the intro cloud.

The previous v1 candidate remains immutable.  This new native-grid version
copies UI-013's stepped front face and its offset pink extrusion exactly, but
extends the body vertically to hold the existing pause controls inside it.
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
TARGET = OUTPUT / "ui-015-pause-callout-v2.png"
METADATA = TARGET.with_suffix(".json")

FONT_SHA256 = "034c77f1f05ec89421e4a63f0e3a4ca1ecf852cc6d2bf611f126f275728e017d"
WIDTH = 332
HEIGHT = 272
FONT_SIZE = 15
TEXT_LINES = ("НЕ ТОРМОЗИ!", "НУЖНО УСПЕТЬ", "ВОВРЕМЯ :)")
PALETTE = {
    "violet": (30, 29, 62, 255),
    "lavender": (238, 240, 255, 255),
    "pink": (255, 79, 171, 255),
    "transparent": (0, 0, 0, 0),
}


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def pixel_hash(image: Image.Image) -> str:
    return sha256(image.convert("RGBA").tobytes()).hexdigest()


def threshold_mask(mask: Image.Image) -> Image.Image:
    return mask.point(lambda value: 255 if value >= 128 else 0)


def assert_binary_alpha(image: Image.Image) -> None:
    histogram = image.convert("RGBA").getchannel("A").histogram()
    if sum(histogram[1:255]):
        raise RuntimeError("UI-015 v2 contains antialiased alpha values.")


def offset(points: list[tuple[int, int]], x: int, y: int) -> list[tuple[int, int]]:
    return [(point_x + x, point_y + y) for point_x, point_y in points]


def draw_callout(font: ImageFont.FreeTypeFont) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), PALETTE["transparent"])
    draw = ImageDraw.Draw(image)

    # UI-013 outer body translated to this asset's local coordinates and
    # extended downward. The pink form is the same +3,+4 sticker extrusion.
    outer = [(8, 2), (320, 2), (326, 8), (326, 258), (320, 264), (8, 264), (2, 258), (2, 8)]
    inner = [(11, 7), (317, 7), (321, 11), (321, 255), (316, 259), (12, 259), (7, 254), (7, 12)]
    draw.polygon(offset(outer, 3, 4), fill=PALETTE["pink"])
    draw.polygon(outer, fill=PALETTE["violet"])
    draw.polygon(inner, fill=PALETTE["lavender"])

    for index, line in enumerate(TEXT_LINES):
        line_width = round(font.getlength(line))
        x = round((WIDTH - line_width) / 2)
        y = 38 + index * 23
        mask = Image.new("L", image.size, 0)
        ImageDraw.Draw(mask).text((x, y), line, font=font, fill=255)
        text_layer = Image.new("RGBA", image.size, PALETTE["violet"])
        text_layer.putalpha(threshold_mask(mask))
        image.alpha_composite(text_layer)

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
                "version": "v2",
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
                    "buildScript": "scripts/build_pause_callout_v2.py",
                    "assetMode": "authored-low-resolution-pixel-art",
                    "styleSource": "UI-013 v3 stepped comic body and +3,+4 pink extrusion; tail omitted",
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
                    "center": {"x": 180, "y": 318},
                    "origin": {"x": 0.5, "y": 0.5},
                    "fixedToCamera": True,
                    "tail": "none",
                    "visibleBounds": {"x": 16, "y": 184, "width": 328, "height": 267},
                    "continueButtonCenter": {"x": 180, "y": 334},
                    "restartButtonCenter": {"x": 180, "y": 394},
                    "buttonContainment": "both existing 168 x 44 buttons remain inside the lavender inner body",
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
