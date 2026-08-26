"""Build deterministic UI-016/UI-017 delivery-finale runtime assets."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public/assets/game/ui"
REFERENCES = ROOT / "visual-references"
FONT_PATH = REFERENCES / "fonts/press-start-2p/PressStart2P-Regular.ttf"
FONT_LICENSE = REFERENCES / "fonts/press-start-2p/OFL.txt"
APPROVED_FONT_SHA256 = (
    "034c77f1f05ec89421e4a63f0e3a4ca1ecf852cc6d2bf611f126f275728e017d"
)

CALLOUT_FILE = OUTPUT / "ui-016-delivery-callout-v1.png"
CTA_FILE = OUTPUT / "ui-017-claim-v1.png"
CALLOUT_SIZE = (332, 132)
CTA_FRAME_SIZE = (168, 36)

PALETTE = {
    "ink": (29, 29, 27, 255),
    "violet": (30, 29, 62, 255),
    "purple": (152, 42, 221, 255),
    "lavender": (238, 240, 255, 255),
    "white": (255, 255, 255, 255),
    "cyan": (84, 224, 255, 255),
    "pink": (255, 79, 171, 255),
    "yellow": (255, 239, 92, 255),
    "transparent": (0, 0, 0, 0),
}

TEXT_LINES = (
    "БОЛЬШОЕ СПАСИБО!",
    "ТЕПЕРЬ МОЖЕШЬ",
    "ЗАБРАТЬ НАГРАДУ!",
)

CTA_STATES = (
    ("yellow", "pink", "pink", "cyan"),
    ("pink", "purple", "cyan", "yellow"),
    ("cyan", "yellow", "yellow", "pink"),
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


def assert_binary_alpha(image: Image.Image, label: str) -> None:
    histogram = image.getchannel("A").histogram()
    if sum(histogram[1:255]) != 0:
        raise RuntimeError(f"{label} contains antialiased alpha values")


def build_callout(font: ImageFont.FreeTypeFont) -> Image.Image:
    image = Image.new("RGBA", CALLOUT_SIZE, PALETTE["transparent"])
    draw = ImageDraw.Draw(image)
    outer = [(8, 0), (318, 0), (326, 8), (326, 102), (318, 110), (8, 110), (0, 102), (0, 8)]
    inner = [(11, 5), (315, 5), (321, 11), (321, 99), (315, 105), (11, 105), (5, 99), (5, 11)]
    tail_outer = [(214, 106), (250, 106), (244, 118), (229, 131), (229, 112), (214, 112)]
    tail_inner = [(220, 103), (244, 103), (239, 115), (232, 122), (233, 108), (220, 108)]

    draw.polygon([(x + 3, y + 4) for x, y in outer], fill=PALETTE["pink"])
    draw.polygon([(x + 3, y + 4) for x, y in tail_outer], fill=PALETTE["pink"])
    draw.polygon(outer, fill=PALETTE["violet"])
    draw.polygon(tail_outer, fill=PALETTE["violet"])
    draw.polygon(inner, fill=PALETTE["lavender"])
    draw.polygon(tail_inner, fill=PALETTE["lavender"])
    draw.rectangle((16, 9, 302, 11), fill=PALETTE["white"])

    for index, line in enumerate(TEXT_LINES):
        width = round(font.getlength(line))
        x = round(CALLOUT_SIZE[0] / 2 - width / 2)
        y = 24 + index * 25
        mask = Image.new("L", CALLOUT_SIZE, 0)
        ImageDraw.Draw(mask).text((x, y), line, font=font, fill=255)
        image.alpha_composite(colorize(threshold(mask), PALETTE["violet"]))

    assert_binary_alpha(image, "UI-016")
    return image


def draw_chevron(draw: ImageDraw.ImageDraw, x: int, left: bool, color: tuple[int, int, int, int]) -> None:
    direction = 1 if left else -1
    outer = [
        (x, 18),
        (x + direction * 10, 6),
        (x + direction * 18, 6),
        (x + direction * 8, 18),
        (x + direction * 18, 30),
        (x + direction * 10, 30),
    ]
    draw.polygon(outer, fill=PALETTE["violet"])
    inner = [
        (x + direction * 3, 18),
        (x + direction * 11, 10),
        (x + direction * 14, 10),
        (x + direction * 6, 18),
        (x + direction * 14, 26),
        (x + direction * 11, 26),
    ]
    draw.polygon(inner, fill=color)


def build_cta(font: ImageFont.FreeTypeFont) -> Image.Image:
    sheet = Image.new(
        "RGBA",
        (CTA_FRAME_SIZE[0], CTA_FRAME_SIZE[1] * len(CTA_STATES)),
        PALETTE["transparent"],
    )
    for frame_index, (face, extrusion, left, right) in enumerate(CTA_STATES):
        frame = Image.new("RGBA", CTA_FRAME_SIZE, PALETTE["transparent"])
        draw = ImageDraw.Draw(frame)
        draw_chevron(draw, 20, True, PALETTE[left])
        draw_chevron(draw, 148, False, PALETTE[right])

        mask = Image.new("L", CTA_FRAME_SIZE, 0)
        text_width = round(font.getlength("ЗАБРАТЬ"))
        ImageDraw.Draw(mask).text(
            (round(84 - text_width / 2), 9),
            "ЗАБРАТЬ",
            font=font,
            fill=255,
        )
        face_mask = threshold(mask)
        outline = face_mask.filter(ImageFilter.MaxFilter(5))
        extrusion_mask = Image.new("L", CTA_FRAME_SIZE, 0)
        extrusion_mask.paste(outline, (3, 3))
        frame.alpha_composite(colorize(extrusion_mask, PALETTE[extrusion]))
        frame.alpha_composite(colorize(outline, PALETTE["violet"]))
        frame.alpha_composite(colorize(face_mask, PALETTE[face]))
        sheet.alpha_composite(frame, (0, frame_index * CTA_FRAME_SIZE[1]))

    assert_binary_alpha(sheet, "UI-017")
    return sheet


def main() -> None:
    if file_hash(FONT_PATH) != APPROVED_FONT_SHA256 or not FONT_LICENSE.exists():
        raise RuntimeError("Press Start 2P source contract changed")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype(str(FONT_PATH), 10)
    callout = build_callout(font)
    cta = build_cta(font)
    callout.save(CALLOUT_FILE)
    cta.save(CTA_FILE)

    write_json(
        CALLOUT_FILE.with_suffix(".json"),
        {
            "assetId": "UI-016",
            "version": "v1",
            "status": "integrated",
            "texture": CALLOUT_FILE.name,
            "canvas": {"width": CALLOUT_SIZE[0], "height": CALLOUT_SIZE[1]},
            "runtimePosition": {"x": 14, "y": 154, "originX": 0, "originY": 0},
            "copy": "Большое спасибо! Теперь можешь забрать награду!",
            "tailTarget": "CHR-001",
            "production": {
                "buildScript": "scripts/build_delivery_finale_ui_v1.py",
                "fontSource": str(FONT_PATH.relative_to(ROOT)),
                "fontSha256": file_hash(FONT_PATH),
                "offlineResizeCount": 0,
                "antialiasing": False,
                "phaserTextureFilter": "nearest",
                "runtimeSha256": file_hash(CALLOUT_FILE),
            },
        },
    )
    write_json(
        CTA_FILE.with_suffix(".json"),
        {
            "assetId": "UI-017",
            "version": "v1",
            "status": "integrated",
            "texture": CTA_FILE.name,
            "frame": {"width": CTA_FRAME_SIZE[0], "height": CTA_FRAME_SIZE[1], "count": len(CTA_STATES)},
            "runtimeCenter": {"x": 180, "y": 466},
            "input": ["pointer-anywhere", "Enter", "Space"],
            "production": {
                "buildScript": "scripts/build_delivery_finale_ui_v1.py",
                "fontSource": str(FONT_PATH.relative_to(ROOT)),
                "fontSha256": file_hash(FONT_PATH),
                "offlineResizeCount": 0,
                "antialiasing": False,
                "phaserTextureFilter": "nearest",
                "runtimeSha256": file_hash(CTA_FILE),
            },
        },
    )


if __name__ == "__main__":
    main()
