"""Build UI-018 v5 from the owner-provided coupon artwork.

Only the exterior connected white JPEG background is removed. The coupon
surface and all enclosed light details remain opaque. A deterministic
``beautybomb`` wordmark is then added in the existing UI-009 title treatment
before the master is resized once with nearest-neighbor for Phaser.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "visual-references/ui-018-reward-coupon-source-v5.jpeg"
MASTER = ROOT / "visual-references/ui-018-reward-coupon-master-v5.png"
RUNTIME = ROOT / "public/assets/game/ui/ui-018-reward-coupon-v5.png"
METADATA = RUNTIME.with_suffix(".json")
FONT_PATH = ROOT / "visual-references/fonts/press-start-2p/PressStart2P-Regular.ttf"
FONT_LICENSE = FONT_PATH.with_name("OFL.txt")

SOURCE_SHA256 = "af2e2f28dac3415865454f633ba9ed1ba52c057cf3fa21a13951215523dfa47d"
FONT_SHA256 = "034c77f1f05ec89421e4a63f0e3a4ca1ecf852cc6d2bf611f126f275728e017d"
SOURCE_SIZE = (1024, 1536)
RUNTIME_SIZE = (304, 456)
TITLE_TEXT = "beautybomb"
TITLE_TOP_LOGICAL_PX = 100

PALETTE = {
    "violet": (30, 29, 62, 255),
    "pink": (255, 79, 171, 255),
    "yellow": (255, 239, 92, 255),
    "cyan_light": (84, 224, 255, 255),
    "white": (255, 255, 255, 255),
}


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def pixel_hash(image: Image.Image) -> str:
    return sha256(image.convert("RGBA").tobytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def connected_exterior_mask(source: Image.Image) -> Image.Image:
    """Return a binary mask for the border-connected near-white background."""

    rgb = source.convert("RGB")
    candidate = Image.new("L", rgb.size, 0)
    candidate.putdata(
        [
            255
            if min(red, green, blue) >= 205 and max(red, green, blue) - min(red, green, blue) <= 35
            else 0
            for red, green, blue in rgb.get_flattened_data()
        ]
    )
    # The exterior is a single connected component in the supplied artwork.
    # Flood-filling the candidate from the top-left keeps enclosed white and
    # pale-yellow coupon pixels opaque.
    ImageDraw.floodfill(candidate, (0, 0), 128, thresh=0)
    return candidate.point(lambda value: 255 if value == 128 else 0)


def threshold_mask(mask: Image.Image) -> Image.Image:
    return mask.point(lambda value: 255 if value >= 128 else 0)


def colorize(mask: Image.Image, color: tuple[int, int, int, int]) -> Image.Image:
    layer = Image.new("RGBA", mask.size, color)
    layer.putalpha(mask)
    return layer


def add_wordmark(master: Image.Image) -> dict[str, int]:
    scale = master.width / RUNTIME_SIZE[0]
    font_size = round(15 * scale)
    font = ImageFont.truetype(FONT_PATH, font_size)
    probe = ImageDraw.Draw(Image.new("L", (1, 1), 0))
    bbox = probe.textbbox((0, 0), TITLE_TEXT, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    face = Image.new("L", master.size, 0)
    x = round((master.width - text_width) / 2 - bbox[0])
    y = round(TITLE_TOP_LOGICAL_PX * scale - bbox[1])
    ImageDraw.Draw(face).text((x, y), TITLE_TEXT, font=font, fill=255)
    face = threshold_mask(face)

    outline_radius = max(1, round(2 * scale))
    if outline_radius % 2 == 0:
        outline_radius += 1
    outline = face.filter(ImageFilter.MaxFilter(outline_radius))
    offset = round(3 * scale)
    extrusion = Image.new("L", master.size, 0)
    extrusion.paste(face, (offset, offset))
    extrusion_outline = Image.new("L", master.size, 0)
    extrusion_outline.paste(outline, (offset, offset))

    master.alpha_composite(colorize(extrusion_outline, PALETTE["violet"]))
    master.alpha_composite(colorize(extrusion, PALETTE["pink"]))
    master.alpha_composite(colorize(outline, PALETTE["violet"]))
    master.alpha_composite(colorize(face, PALETTE["yellow"]))

    highlight = ImageDraw.Draw(master)
    highlight.rectangle(
        (x + round(scale), round(TITLE_TOP_LOGICAL_PX * scale), x + round(2 * scale), round((TITLE_TOP_LOGICAL_PX + 1) * scale)),
        fill=PALETTE["white"],
    )
    highlight.point((x + round(3 * scale), round(TITLE_TOP_LOGICAL_PX * scale)), fill=PALETTE["cyan_light"])
    return {
        "x": round(x / scale),
        "y": TITLE_TOP_LOGICAL_PX,
        "width": round(text_width / scale),
        "height": round(text_height / scale),
    }


def assert_binary_alpha(image: Image.Image) -> None:
    alpha = image.getchannel("A").histogram()
    if sum(alpha[1:255]):
        raise RuntimeError("UI-018 v5 contains non-binary alpha values")


def main() -> None:
    if file_hash(SOURCE) != SOURCE_SHA256:
        raise RuntimeError("UI-018 v5 source differs from the owner-provided artwork")
    if not FONT_PATH.exists() or not FONT_LICENSE.exists() or file_hash(FONT_PATH) != FONT_SHA256:
        raise RuntimeError("The approved local Press Start 2P source is required")

    with Image.open(SOURCE) as supplied:
        if supplied.size != SOURCE_SIZE:
            raise RuntimeError(f"Unexpected UI-018 v5 source size: {supplied.size}")
        master = supplied.convert("RGBA")
    exterior = connected_exterior_mask(master)
    alpha = Image.new("L", master.size, 255)
    alpha.paste(0, mask=exterior)
    master.putalpha(alpha)
    title_bounds = add_wordmark(master)
    assert_binary_alpha(master)

    MASTER.parent.mkdir(parents=True, exist_ok=True)
    master.save(MASTER, optimize=True)
    runtime = master.resize(RUNTIME_SIZE, Image.Resampling.NEAREST)
    assert_binary_alpha(runtime)
    RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    runtime.save(RUNTIME, optimize=True)

    metadata = {
        "assetId": "UI-018",
        "version": "v5",
        "asset": "Owner-provided BeautyBomb delivery reward coupon",
        "status": "integrated",
        "canvas": {"width": 304, "height": 456},
        "runtimePlacement": {"x": 180, "y": 320, "originX": 0.5, "originY": 0.5},
        "source": {
            "path": "visual-references/ui-018-reward-coupon-source-v5.jpeg",
            "sha256": SOURCE_SHA256,
            "dimensions": {"width": 1024, "height": 1536},
            "role": "sole visual source supplied by the owner",
        },
        "master": {
            "path": "visual-references/ui-018-reward-coupon-master-v5.png",
            "sha256": file_hash(MASTER),
            "pixelSha256": pixel_hash(master),
            "dimensions": {"width": 1024, "height": 1536},
            "transparentBackground": True,
            "alpha": "binary; exterior border-connected near-white component only",
        },
        "runtime": {
            "path": "public/assets/game/ui/ui-018-reward-coupon-v5.png",
            "sha256": file_hash(RUNTIME),
            "pixelSha256": pixel_hash(runtime),
            "dimensions": {"width": 304, "height": 456},
            "phaserTextureFilter": "nearest",
            "origin": {"x": 0.5, "y": 0.5},
            "placement": {"x": 180, "y": 320},
        },
        "wordmark": {
            "text": TITLE_TEXT,
            "logicalBounds": title_bounds,
            "logicalTop": TITLE_TOP_LOGICAL_PX,
            "style": "UI-009 yellow face, violet outline, pink lower-right extrusion, cyan-white highlight",
            "font": "Press Start 2P",
        },
        "build": {
            "buildScript": "scripts/build_reward_coupon_v5.py",
            "exteriorRemoval": "border-connected near-white flood fill; enclosed light pixels preserved",
            "resizeCount": 1,
            "resizeFilter": "nearest-neighbor",
            "paletteQuantization": "none",
            "antialiasing": False,
        },
        "liveOverlay": {
            "couponCode": "XQZ-20476",
            "codeAndCopyControl": "unchanged live Phaser and DOM accessibility UI",
            "tearOffArea": "empty",
            "codeField": {"x": 154, "y": 305, "width": 150, "height": 44},
            "copyButton": {"x": 259, "y": 305, "width": 44, "height": 44},
        },
    }
    write_json(METADATA, metadata)
    print(f"master={MASTER} sha256={file_hash(MASTER)}")
    print(f"runtime={RUNTIME} sha256={file_hash(RUNTIME)}")


if __name__ == "__main__":
    main()
