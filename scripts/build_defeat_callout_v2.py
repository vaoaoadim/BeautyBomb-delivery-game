"""Build UI-006 v2 as an exact pause-popup visual sibling."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public/assets/game/ui"
FONT_PATH = ROOT / "visual-references/fonts/press-start-2p/PressStart2P-Regular.ttf"
FONT_LICENSE = FONT_PATH.with_name("OFL.txt")
TARGET = OUTPUT / "ui-006-defeat-callout-v2.png"
METADATA = TARGET.with_suffix(".json")

FONT_SHA256 = "034c77f1f05ec89421e4a63f0e3a4ca1ecf852cc6d2bf611f126f275728e017d"
WIDTH = 332
HEIGHT = 272
TITLE_FONT_SIZE = 15
BODY_FONT_SIZE = 15
TITLE_LINES = ("ДТП!", "Давай еще раз!")
BODY_LINES = ("Внимательно следи", "за дорогой и", "не врезайся.")
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


def offset(points: list[tuple[int, int]], x: int, y: int) -> list[tuple[int, int]]:
    return [(point_x + x, point_y + y) for point_x, point_y in points]


def draw_text_line(
    image: Image.Image,
    line: str,
    y: int,
    font: ImageFont.FreeTypeFont,
) -> None:
    line_width = round(font.getlength(line))
    x = round((WIDTH - line_width) / 2)
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).text((x, y), line, font=font, fill=255)
    layer = Image.new("RGBA", image.size, PALETTE["violet"])
    layer.putalpha(threshold_mask(mask))
    image.alpha_composite(layer)


def draw_callout(
    title_font: ImageFont.FreeTypeFont,
    body_font: ImageFont.FreeTypeFont,
) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), PALETTE["transparent"])
    draw = ImageDraw.Draw(image)
    outer = [(8, 2), (320, 2), (326, 8), (326, 258), (320, 264), (8, 264), (2, 258), (2, 8)]
    inner = [(11, 7), (317, 7), (321, 11), (321, 255), (316, 259), (12, 259), (7, 254), (7, 12)]
    draw.polygon(offset(outer, 3, 4), fill=PALETTE["pink"])
    draw.polygon(outer, fill=PALETTE["violet"])
    draw.polygon(inner, fill=PALETTE["lavender"])

    for index, line in enumerate(TITLE_LINES):
        draw_text_line(image, line, 28 + index * 28, title_font)
    for index, line in enumerate(BODY_LINES):
        draw_text_line(image, line, 94 + index * 28, body_font)

    if sum(image.getchannel("A").histogram()[1:255]):
        raise RuntimeError("UI-006 v2 contains antialiased alpha values")
    return image


def main() -> None:
    if not FONT_PATH.exists() or not FONT_LICENSE.exists() or file_hash(FONT_PATH) != FONT_SHA256:
        raise RuntimeError("The approved local Press Start 2P source is required")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    asset = draw_callout(
        ImageFont.truetype(FONT_PATH, TITLE_FONT_SIZE),
        ImageFont.truetype(FONT_PATH, BODY_FONT_SIZE),
    )
    asset.save(TARGET, optimize=True)
    METADATA.write_text(
        json.dumps(
            {
                "assetId": "UI-006",
                "version": "v2",
                "status": "integrated",
                "texture": TARGET.name,
                "canvas": {"width": WIDTH, "height": HEIGHT},
                "copy": "ДТП!\nДавай еще раз!\nВнимательно следи за дорогой и не врезайся.",
                "renderedCopy": list(TITLE_LINES + BODY_LINES),
                "font": {
                    "family": "Press Start 2P",
                    "titleSizePx": TITLE_FONT_SIZE,
                    "bodySizePx": BODY_FONT_SIZE,
                },
                "production": {
                    "buildScript": "scripts/build_defeat_callout_v2.py",
                    "styleSource": "UI-015 v2 exact panel geometry and palette",
                    "fontSource": "visual-references/fonts/press-start-2p/PressStart2P-Regular.ttf",
                    "fontSha256": FONT_SHA256,
                    "offlineResizeCount": 0,
                    "antialiasing": False,
                    "phaserTextureFilter": "nearest",
                    "runtimeSha256": file_hash(TARGET),
                    "runtimePixelSha256": pixel_hash(asset),
                },
                "runtime": {
                    "center": {"x": 180, "y": 318},
                    "origin": {"x": 0.5, "y": 0.5},
                    "depth": "RENDER_DEPTH.overlay + 10",
                    "dimOverlay": {"color": "#17162f", "alpha": 0.78},
                    "restartButtonCenter": {"x": 180, "y": 394},
                    "restartButtonLabel": "заново",
                    "restartFlow": "existing resetRun",
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
