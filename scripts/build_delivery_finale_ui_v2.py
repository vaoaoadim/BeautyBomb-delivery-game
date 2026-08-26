"""Build the lower, upward-pointing UI-016 v2 delivery callout."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public/assets/game/ui"
FONT_PATH = ROOT / "visual-references/fonts/press-start-2p/PressStart2P-Regular.ttf"
FONT_LICENSE = ROOT / "visual-references/fonts/press-start-2p/OFL.txt"
APPROVED_FONT_SHA256 = (
    "034c77f1f05ec89421e4a63f0e3a4ca1ecf852cc6d2bf611f126f275728e017d"
)

CALLOUT_FILE = OUTPUT / "ui-016-delivery-callout-v2.png"
CALLOUT_SIZE = (332, 112)
RUNTIME_POSITION = {"x": 14, "y": 378, "originX": 0, "originY": 0}

PALETTE = {
    "violet": (30, 29, 62, 255),
    "lavender": (238, 240, 255, 255),
    "white": (255, 255, 255, 255),
    "pink": (255, 79, 171, 255),
    "transparent": (0, 0, 0, 0),
}

TEXT_LINES = (
    "БОЛЬШОЕ СПАСИБО!",
    "ТЕПЕРЬ МОЖЕШЬ",
    "ЗАБРАТЬ НАГРАДУ!",
)


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def threshold(mask: Image.Image) -> Image.Image:
    return mask.point(lambda value: 255 if value >= 128 else 0)


def colorize(mask: Image.Image, color: tuple[int, int, int, int]) -> Image.Image:
    layer = Image.new("RGBA", mask.size, color)
    layer.putalpha(mask)
    return layer


def assert_binary_alpha(image: Image.Image) -> None:
    histogram = image.getchannel("A").histogram()
    if sum(histogram[1:255]) != 0:
        raise RuntimeError("UI-016 v2 contains antialiased alpha values")


def build_callout(font: ImageFont.FreeTypeFont) -> Image.Image:
    image = Image.new("RGBA", CALLOUT_SIZE, PALETTE["transparent"])
    draw = ImageDraw.Draw(image)

    outer = [
        (8, 16),
        (318, 16),
        (326, 24),
        (326, 98),
        (318, 106),
        (8, 106),
        (0, 98),
        (0, 24),
    ]
    inner = [
        (11, 21),
        (315, 21),
        (321, 27),
        (321, 95),
        (315, 101),
        (11, 101),
        (5, 95),
        (5, 27),
    ]
    tail_outer = [(206, 0), (220, 20), (192, 20)]
    tail_inner = [(206, 6), (214, 19), (198, 19)]

    draw.polygon([(x + 3, y + 4) for x, y in tail_outer], fill=PALETTE["pink"])
    draw.polygon([(x + 3, y + 4) for x, y in outer], fill=PALETTE["pink"])
    draw.polygon(tail_outer, fill=PALETTE["violet"])
    draw.polygon(outer, fill=PALETTE["violet"])
    draw.polygon(inner, fill=PALETTE["lavender"])
    draw.polygon(tail_inner, fill=PALETTE["lavender"])
    draw.rectangle((16, 25, 302, 27), fill=PALETTE["white"])

    for index, line in enumerate(TEXT_LINES):
        width = round(font.getlength(line))
        x = round(CALLOUT_SIZE[0] / 2 - width / 2)
        y = 36 + index * 23
        mask = Image.new("L", CALLOUT_SIZE, 0)
        ImageDraw.Draw(mask).text((x, y), line, font=font, fill=255)
        image.alpha_composite(colorize(threshold(mask), PALETTE["violet"]))

    assert_binary_alpha(image)
    return image


def main() -> None:
    if file_hash(FONT_PATH) != APPROVED_FONT_SHA256 or not FONT_LICENSE.exists():
        raise RuntimeError("Press Start 2P source contract changed")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype(str(FONT_PATH), 10)
    callout = build_callout(font)
    callout.save(CALLOUT_FILE)

    write_json(
        CALLOUT_FILE.with_suffix(".json"),
        {
            "assetId": "UI-016",
            "version": "v2",
            "status": "integrated",
            "texture": CALLOUT_FILE.name,
            "canvas": {"width": CALLOUT_SIZE[0], "height": CALLOUT_SIZE[1]},
            "runtimePosition": RUNTIME_POSITION,
            "copy": "Большое спасибо! Теперь можешь забрать награду!",
            "tailTarget": "CHR-001",
            "tailPlacement": "top edge; points upward to the recipient",
            "production": {
                "buildScript": "scripts/build_delivery_finale_ui_v2.py",
                "fontSource": FONT_PATH.relative_to(ROOT).as_posix(),
                "fontSha256": file_hash(FONT_PATH),
                "offlineResizeCount": 0,
                "antialiasing": False,
                "phaserTextureFilter": "nearest",
                "runtimeSha256": file_hash(CALLOUT_FILE),
            },
        },
    )


if __name__ == "__main__":
    main()
