"""Extend UI-018 patterns through the full main ticket body."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from PIL import Image, ImageDraw

from build_hud_ui_v1 import PALETTE

ROOT = Path(__file__).resolve().parents[1]
BASE_RUNTIME = ROOT / "public/assets/game/ui/ui-018-reward-coupon-v3.png"
MASTER = ROOT / "visual-references/ui-018-reward-coupon-master-v4.png"
RUNTIME = ROOT / "public/assets/game/ui/ui-018-reward-coupon-v4.png"
METADATA = RUNTIME.with_suffix(".json")
BASE_RUNTIME_SHA256 = "12e8feb8afd2adc65b7e911c81a50e5a4adb3f503952dc5305455e22e2afdae6"
RUNTIME_SIZE = (304, 456)
TEAR_LINE_TOP = 328


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def draw_diamond(draw: ImageDraw.ImageDraw, x: int, y: int, color: tuple[int, int, int, int]) -> None:
    draw.polygon(((x, y - 4), (x + 4, y), (x, y + 4), (x - 4, y)), fill=PALETTE["violet"])
    draw.polygon(((x, y - 2), (x + 2, y), (x, y + 2), (x - 2, y)), fill=color)
    draw.point((x, y - 1), fill=PALETTE["white"])


def draw_pixel_wave(draw: ImageDraw.ImageDraw, mirrored: bool = False) -> None:
    points = [(48, 255), (57, 247), (66, 255), (75, 247), (84, 255)]
    if mirrored:
        points = [(304 - x, y) for x, y in points]
    draw.line(points, fill=PALETTE["violet"], width=4)
    draw.line(points, fill=PALETTE["pink" if mirrored else "cyan"], width=2)


def draw_lower_pattern(image: Image.Image) -> None:
    """Decorate below the code, ending before the existing dotted line."""
    draw = ImageDraw.Draw(image)
    draw_pixel_wave(draw)
    draw_pixel_wave(draw, mirrored=True)
    for x, y, color in (
        (55, 278, "pink"), (76, 292, "yellow"), (97, 272, "cyan"),
        (207, 272, "cyan"), (228, 292, "yellow"), (249, 278, "pink"),
        (57, 310, "cyan"), (86, 316, "pink"), (218, 316, "pink"), (247, 310, "cyan"),
    ):
        draw_diamond(draw, x, y, PALETTE[color])
    draw.line([(115, 286), (127, 278), (152, 274), (177, 278), (189, 286)], fill=PALETTE["purple"])
    draw.line([(115, 304), (128, 312), (152, 316), (176, 312), (189, 304)], fill=PALETTE["cyan"])
    draw.ellipse((139, 283, 165, 309), outline=PALETTE["violet"], width=3)
    draw.ellipse((143, 287, 161, 305), fill=PALETTE["pink"])
    draw.rectangle((148, 285, 156, 307), fill=PALETTE["yellow"])
    draw.rectangle((141, 292, 163, 300), fill=PALETTE["yellow"])
    draw.rectangle((149, 291, 155, 301), fill=PALETTE["white"])
    for x, y, color in ((111, 301, "yellow"), (123, 317, "pink"), (181, 317, "pink"), (193, 301, "yellow")):
        draw.rectangle((x - 1, y - 1, x + 1, y + 1), fill=PALETTE[color])
        draw.point((x, y), fill=PALETTE["white"])
    for index, x in enumerate(range(48, 261, 12)):
        color = ("cyan", "pink", "yellow")[index % 3]
        draw.rectangle((x, 322, x + 4, 324), fill=PALETTE[color])


def main() -> None:
    if file_hash(BASE_RUNTIME) != BASE_RUNTIME_SHA256:
        raise RuntimeError("UI-018 v3 runtime differs from the approved source")
    with Image.open(BASE_RUNTIME) as source:
        runtime = source.convert("RGBA")
    draw_lower_pattern(runtime)
    master = runtime.resize((1216, 1824), Image.Resampling.NEAREST)
    MASTER.parent.mkdir(parents=True, exist_ok=True)
    master.save(MASTER, optimize=True)
    final_runtime = master.resize(RUNTIME_SIZE, Image.Resampling.NEAREST)
    RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    final_runtime.save(RUNTIME, optimize=True)
    metadata = {
        "assetId": "UI-018", "version": "v4", "status": "integrated",
        "asset": "Beauty Bomb reward coupon with full main-body pattern",
        "canvas": {"width": 304, "height": 456},
        "source": {"baseRuntime": str(BASE_RUNTIME.relative_to(ROOT)), "baseRuntimeSha256": BASE_RUNTIME_SHA256, "master": str(MASTER.relative_to(ROOT)), "masterSha256": file_hash(MASTER), "dimensions": {"width": 1216, "height": 1824}, "transparentBackground": True, "alpha": "binary"},
        "runtime": {"path": str(RUNTIME.relative_to(ROOT)), "dimensions": {"width": 304, "height": 456}, "sha256": file_hash(RUNTIME), "phaserTextureFilter": "NEAREST", "origin": {"x": 0.5, "y": 0.5}, "placement": {"x": 180, "y": 320}},
        "brandLayer": {"wordmark": "BEAUTY BOMB", "motifs": ["pixel hearts", "starbursts", "neon ribbons", "cosmic grids", "gamepad sticker", "pixel constellation", "mini-confetti band"], "patternCoverage": "entire main body, including below the code, stopping above the dotted tear line", "tearLineTop": TEAR_LINE_TOP, "tearOffAreaDecorated": False},
        "build": {"buildScript": "scripts/build_reward_coupon_v4.py", "resizeCount": 1, "resizeFilter": "nearest-neighbor"},
        "liveOverlay": {"couponCode": "XQZ-20476", "codeAndCopyControl": "unchanged", "tearOffText": "unchanged"},
    }
    METADATA.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"master={MASTER} sha256={file_hash(MASTER)}")
    print(f"runtime={RUNTIME} sha256={file_hash(RUNTIME)}")


if __name__ == "__main__":
    main()
