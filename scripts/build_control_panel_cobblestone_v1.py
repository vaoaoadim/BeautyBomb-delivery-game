"""Build the seam-safe cobblestone control-panel parallax."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw


OUTPUT = Path("public/assets/game")
REFERENCE = Path("visual-references")
ENVIRONMENT_OUTPUT = OUTPUT / "environment"
COBBLESTONE_MASTER = REFERENCE / "env-010-control-panel-cobblestone-master-v1.png"
COBBLESTONE_RUNTIME = ENVIRONMENT_OUTPUT / "env-010-control-panel-cobblestone-v1.png"
COBBLESTONE_METADATA = COBBLESTONE_RUNTIME.with_suffix(".json")
SEAM_REVIEW = REFERENCE / "qa/env-010-control-panel-cobblestone-v1-seam-review.png"

TEXTURE_SIZE = (512, 128)
PANEL_SIZE = (360, 118)
PALETTE = {
    "curb_highlight": (241, 241, 241, 255),
    "curb_face": (196, 196, 196, 255),
    "curb_mid": (153, 153, 153, 255),
    "curb_shadow": (112, 112, 112, 255),
    "grout": (92, 92, 104, 255),
}


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def draw_cobble(draw: ImageDraw.ImageDraw, left: int, top: int, width: int, height: int, color: tuple[int, int, int, int]) -> None:
    right = left + width - 1
    bottom = top + height - 1
    points = (
        (left + 3, top),
        (right - 3, top),
        (right, top + 3),
        (right, bottom - 3),
        (right - 3, bottom),
        (left + 3, bottom),
        (left, bottom - 3),
        (left, top + 3),
    )
    draw.polygon(points, fill=color)
    draw.line(((left + 3, top), (right - 3, top)), fill=PALETTE["curb_highlight"], width=1)
    draw.line(((left, top + 3), (left, bottom - 3)), fill=PALETTE["curb_highlight"], width=1)
    draw.line(((left + 3, bottom), (right - 3, bottom)), fill=PALETTE["curb_shadow"], width=1)
    draw.line(((right, top + 3), (right, bottom - 3)), fill=PALETTE["curb_shadow"], width=1)


def build_cobblestone() -> Image.Image:
    width, height = TEXTURE_SIZE
    image = Image.new("RGBA", TEXTURE_SIZE, PALETTE["grout"])
    draw = ImageDraw.Draw(image)
    row_heights = (15, 16, 15, 16, 15, 16, 15, 16)
    row_offsets = (-22, -35, -14, -42, -28, -10, -38, -18)
    widths = (56, 48, 62, 50, 58, 46, 64, 52, 76)
    fills = (PALETTE["curb_face"], PALETTE["curb_mid"], PALETTE["curb_face"], PALETTE["curb_mid"])
    y = 1

    for row_index, row_height in enumerate(row_heights):
        pattern = widths[row_index % len(widths) :] + widths[: row_index % len(widths)]
        offset = row_offsets[row_index]
        for cycle in (-1, 0, 1):
            x = cycle * width + offset
            for column_index, stone_width in enumerate(pattern):
                fill = fills[(row_index * 3 + column_index) % len(fills)]
                draw_cobble(draw, x + 2, y + 2, stone_width - 4, row_height - 4, fill)
                x += stone_width
        y += row_height

    if y < height:
        draw.rectangle((0, y, width - 1, height - 1), fill=PALETTE["grout"])

    left_edge = image.crop((0, 0, 1, height))
    right_edge = image.crop((width - 1, 0, width, height))
    if ImageChops.difference(left_edge, right_edge).getbbox() is not None:
        raise ValueError("Cobblestone cycle edges must be pixel-identical.")
    return image


def build_seam_review(cobblestone: Image.Image) -> Image.Image:
    review = Image.new("RGBA", (TEXTURE_SIZE[0] * 3, TEXTURE_SIZE[1]), PALETTE["grout"])
    for index in range(3):
        review.alpha_composite(cobblestone, (index * TEXTURE_SIZE[0], 0))
    return review


def main() -> None:
    ENVIRONMENT_OUTPUT.mkdir(parents=True, exist_ok=True)
    REFERENCE.mkdir(parents=True, exist_ok=True)
    SEAM_REVIEW.parent.mkdir(parents=True, exist_ok=True)

    cobblestone = build_cobblestone()
    cobblestone.save(COBBLESTONE_MASTER, optimize=True)
    cobblestone.save(COBBLESTONE_RUNTIME, optimize=True)
    build_seam_review(cobblestone).save(SEAM_REVIEW, optimize=True)

    write_json(
        COBBLESTONE_METADATA,
        {
            "assetId": "ENV-010",
            "version": "v1",
            "status": "integrated",
            "texture": COBBLESTONE_RUNTIME.name,
            "canvas": {"width": TEXTURE_SIZE[0], "height": TEXTURE_SIZE[1]},
            "paletteSource": {
                "runtime": "public/assets/game/environment/env-006-road-v6.png",
                "sampledRows": [0, 5, 388, 397],
                "role": "neutral white road curb",
            },
            "production": {
                "designMaster": str(COBBLESTONE_MASTER).replace("\\", "/"),
                "designMasterSha256": file_hash(COBBLESTONE_MASTER),
                "buildScript": "scripts/build_control_panel_cobblestone_v1.py",
                "assetMode": "authored-low-resolution-pixel-art",
                "offlineResizeCount": 0,
                "antialiasing": False,
                "paletteQuantization": False,
                "phaserTextureFilter": "nearest",
                "runtimeSha256": file_hash(COBBLESTONE_RUNTIME),
            },
            "seamContract": {
                "mode": "periodic-wrap-aware-cobblestone",
                "loopPeriodTexturePx": TEXTURE_SIZE[0],
                "edgeMismatchRows": {"cycleWrap": 0},
                "mirrored": False,
                "review": str(SEAM_REVIEW).replace("\\", "/"),
                "reviewCopies": 3,
            },
            "runtime": {
                "position": {"x": 0, "y": 520},
                "viewport": {"width": PANEL_SIZE[0], "height": PANEL_SIZE[1] + 2},
                "roadOverlapPx": 2,
                "fixedToCamera": True,
                "displaySpeedPxPerSecond": 92.16,
                "speedMultiplier": 1.28,
                "reducedMotion": "freeze",
                "layering": "below UI-004 controls; directly adjacent to road",
            },
        },
    )
    print(f"cobblestone_master={COBBLESTONE_MASTER} sha256={file_hash(COBBLESTONE_MASTER)}")
    print(f"cobblestone_runtime={COBBLESTONE_RUNTIME} sha256={file_hash(COBBLESTONE_RUNTIME)}")


if __name__ == "__main__":
    main()
