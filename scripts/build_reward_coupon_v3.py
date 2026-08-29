"""Build the branded UI-018 v3 coupon without changing its live controls."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter

from build_hud_ui_v1 import PALETTE, TITLE_GLYPHS, colorize_mask


ROOT = Path(__file__).resolve().parents[1]
BASE_RUNTIME = ROOT / "public/assets/game/ui/ui-018-reward-coupon-v2.png"
MASTER = ROOT / "visual-references/ui-018-reward-coupon-master-v3.png"
RUNTIME = ROOT / "public/assets/game/ui/ui-018-reward-coupon-v3.png"
METADATA = RUNTIME.with_suffix(".json")
BASE_RUNTIME_SHA256 = "4630c84db87979cf416a580d5dc93d51ac3c24d21636859a7c67a44a77ced568"
RUNTIME_SIZE = (304, 456)
MASTER_SCALE = 4


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_wordmark() -> Image.Image:
    text = "BEAUTY BOMB"
    scale = 3
    glyph_width = 5 * scale
    gap = 2
    advances = [7 if character == " " else glyph_width for character in text]
    canvas = Image.new("RGBA", (sum(advances) + gap * (len(text) - 1) + 12, 36), (0, 0, 0, 0))
    face = Image.new("L", canvas.size, 0)
    draw = ImageDraw.Draw(face)
    cursor_x = 4
    word_starts: list[int] = []
    at_word_start = True
    for index, character in enumerate(text):
        if character == " ":
            cursor_x += 7
            at_word_start = True
        else:
            if at_word_start:
                word_starts.append(cursor_x)
                at_word_start = False
            for row, bits in enumerate(TITLE_GLYPHS[character]):
                for column, bit in enumerate(bits):
                    if bit == "1":
                        x = cursor_x + column * scale
                        y = 3 + row * scale
                        draw.rectangle((x, y, x + scale - 1, y + scale - 1), fill=255)
            cursor_x += glyph_width
        if index < len(text) - 1:
            cursor_x += gap

    outline = face.filter(ImageFilter.MaxFilter(5))
    extrusion = Image.new("L", canvas.size, 0)
    extrusion.paste(face, (3, 3))
    extrusion_outline = Image.new("L", canvas.size, 0)
    extrusion_outline.paste(outline, (3, 3))
    canvas.alpha_composite(colorize_mask(extrusion_outline, PALETTE["violet"]))
    canvas.alpha_composite(colorize_mask(extrusion, PALETTE["pink"]))
    canvas.alpha_composite(colorize_mask(outline, PALETTE["violet"]))
    canvas.alpha_composite(colorize_mask(face, PALETTE["yellow"]))
    highlights = ImageDraw.Draw(canvas)
    for word_x in word_starts:
        highlights.point((word_x, 3), fill=PALETTE["white"])
        highlights.point((word_x + 1, 3), fill=PALETTE["cyan_light"])
    return canvas


def draw_sparkle(draw: ImageDraw.ImageDraw, x: int, y: int, color: tuple[int, int, int, int]) -> None:
    draw.rectangle((x - 1, y - 7, x + 1, y + 7), fill=PALETTE["violet"])
    draw.rectangle((x - 7, y - 1, x + 7, y + 1), fill=PALETTE["violet"])
    draw.line((x, y - 5, x, y + 5), fill=color, width=1)
    draw.line((x - 5, y, x + 5, y), fill=color, width=1)
    draw.point((x, y), fill=PALETTE["white"])


def draw_heart(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    outline = [
        (x + 2, y), (x + 6, y), (x + 8, y + 2), (x + 10, y), (x + 14, y),
        (x + 16, y + 2), (x + 16, y + 6), (x + 8, y + 14), (x, y + 6), (x, y + 2),
    ]
    inner = [
        (x + 3, y + 3), (x + 6, y + 3), (x + 8, y + 5), (x + 10, y + 3),
        (x + 13, y + 3), (x + 13, y + 6), (x + 8, y + 11), (x + 3, y + 6),
    ]
    draw.polygon(outline, fill=PALETTE["violet"])
    draw.polygon(inner, fill=PALETTE["pink"])
    draw.rectangle((x + 3, y + 3, x + 5, y + 4), fill=PALETTE["yellow"])


def draw_gamepad(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    outline = [
        (x + 5, y), (x + 31, y), (x + 36, y + 5), (x + 36, y + 16),
        (x + 31, y + 21), (x + 25, y + 17), (x + 11, y + 17), (x + 5, y + 21),
        (x, y + 16), (x, y + 5),
    ]
    inner = [
        (x + 6, y + 4), (x + 30, y + 4), (x + 32, y + 6), (x + 32, y + 14),
        (x + 29, y + 16), (x + 24, y + 13), (x + 12, y + 13), (x + 7, y + 16),
        (x + 4, y + 14), (x + 4, y + 6),
    ]
    draw.polygon(outline, fill=PALETTE["violet"])
    draw.polygon(inner, fill=PALETTE["yellow"])
    draw.rectangle((x + 9, y + 7, x + 15, y + 9), fill=PALETTE["violet"])
    draw.rectangle((x + 11, y + 5, x + 13, y + 11), fill=PALETTE["violet"])
    draw.rectangle((x + 24, y + 6, x + 27, y + 9), fill=PALETTE["pink"])
    draw.rectangle((x + 28, y + 10, x + 30, y + 12), fill=PALETTE["cyan"])
    draw.line((x + 7, y + 4, x + 22, y + 4), fill=PALETTE["white"], width=1)


def draw_side_grid(draw: ImageDraw.ImageDraw, mirrored: bool = False) -> None:
    points = [(48, 179), (51, 219), (111, 219), (91, 179)]
    if mirrored:
        points = [(304 - x, y) for x, y in points]
    draw.line(points + [points[0]], fill=PALETTE["purple"], width=1)
    for step in (10, 20, 30):
        segment = [(48 + step // 4, 179 + step), (111 - step // 2, 179 + step)]
        if mirrored:
            segment = [(304 - x, y) for x, y in segment]
        draw.line(segment, fill=PALETTE["cyan"], width=1)
    for x in (60, 75, 90):
        segment = [(x, 179), (x + 5, 219)]
        if mirrored:
            segment = [(304 - px, py) for px, py in segment]
        draw.line(segment, fill=PALETTE["purple"], width=1)


def draw_brand_layer(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image)
    left_ribbon = [(48, 86), (63, 78), (67, 88), (58, 96), (68, 106), (58, 116), (66, 126), (52, 135)]
    right_ribbon = [(304 - x, y) for x, y in reversed(left_ribbon)]
    for points, face in ((left_ribbon, PALETTE["yellow"]), (right_ribbon, PALETTE["pink"])):
        draw.line(points, fill=PALETTE["violet"], width=5, joint="curve")
        draw.line(points, fill=face, width=2, joint="curve")
    draw_heart(draw, 55, 143)
    draw_heart(draw, 233, 143)
    draw_sparkle(draw, 84, 137, PALETTE["yellow"])
    draw_sparkle(draw, 220, 137, PALETTE["pink"])
    draw_sparkle(draw, 70, 174, PALETTE["white"])
    draw_sparkle(draw, 234, 174, PALETTE["yellow"])
    draw_side_grid(draw)
    draw_side_grid(draw, mirrored=True)
    draw_gamepad(draw, 134, 139)
    for x, y, color in (
        (92, 126, "purple"), (103, 153, "pink"), (118, 132, "yellow"),
        (126, 162, "violet"), (178, 162, "yellow"), (186, 132, "violet"),
        (201, 153, "pink"), (212, 126, "purple"),
    ):
        draw.rectangle((x - 1, y - 1, x + 1, y + 1), fill=PALETTE[color])
        draw.point((x, y), fill=PALETTE["white"])
    wordmark = build_wordmark()
    image.alpha_composite(wordmark, ((image.width - wordmark.width) // 2, 76))


def main() -> None:
    if file_hash(BASE_RUNTIME) != BASE_RUNTIME_SHA256:
        raise RuntimeError("UI-018 v2 runtime differs from the approved source")
    with Image.open(BASE_RUNTIME) as source:
        branded_runtime = source.convert("RGBA")
    draw_brand_layer(branded_runtime)
    master = branded_runtime.resize(
        (RUNTIME_SIZE[0] * MASTER_SCALE, RUNTIME_SIZE[1] * MASTER_SCALE),
        Image.Resampling.NEAREST,
    )
    MASTER.parent.mkdir(parents=True, exist_ok=True)
    master.save(MASTER, optimize=True)
    runtime = master.resize(RUNTIME_SIZE, Image.Resampling.NEAREST)
    RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    runtime.save(RUNTIME, optimize=True)
    metadata = {
        "assetId": "UI-018",
        "version": "v3",
        "asset": "Beauty Bomb branded delivery reward coupon background",
        "status": "integrated",
        "canvas": {"width": 304, "height": 456},
        "runtimePlacement": {"x": 180, "y": 320, "originX": 0.5, "originY": 0.5},
        "source": {
            "baseRuntime": "public/assets/game/ui/ui-018-reward-coupon-v2.png",
            "baseRuntimeSha256": BASE_RUNTIME_SHA256,
            "master": "visual-references/ui-018-reward-coupon-master-v3.png",
            "masterSha256": file_hash(MASTER),
            "dimensions": {"width": master.width, "height": master.height},
            "transparentBackground": True,
            "alpha": "binary",
        },
        "runtime": {
            "path": "public/assets/game/ui/ui-018-reward-coupon-v3.png",
            "dimensions": {"width": 304, "height": 456},
            "sha256": file_hash(RUNTIME),
            "phaserTextureFilter": "NEAREST",
            "origin": {"x": 0.5, "y": 0.5},
            "placement": {"x": 180, "y": 320},
        },
        "brandLayer": {
            "wordmark": "BEAUTY BOMB",
            "titleStyle": "UI-009 pixel title at a larger 3px glyph scale",
            "reference": "https://beautybomb.ru/",
            "motifs": ["pixel hearts", "starbursts", "neon ribbons", "cosmic grids", "gamepad sticker"],
            "tearOffAreaDecorated": False,
        },
        "build": {
            "buildScript": "scripts/build_reward_coupon_v3.py",
            "resizeCount": 1,
            "resizeFilter": "nearest-neighbor",
            "paletteQuantization": "none",
        },
        "liveOverlay": {
            "couponCode": "XQZ-20476",
            "codeAndCopyControl": "unchanged Phaser runtime UI",
            "tearOffText": "unchanged Phaser runtime UI",
            "codeField": {"x": 154, "y": 305, "width": 150, "height": 44},
            "copyButton": {"x": 259, "y": 305, "width": 44, "height": 44},
            "tearOffTextCenter": {"x": 180, "y": 468},
        },
    }
    write_json(METADATA, metadata)
    print(f"master={MASTER} sha256={file_hash(MASTER)}")
    print(f"runtime={RUNTIME} sha256={file_hash(RUNTIME)}")


if __name__ == "__main__":
    main()
