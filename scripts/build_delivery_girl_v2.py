"""Build the smaller CHR-001 v2 from the immutable generated master."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "visual-references/chr-001-waiting-girl-master-v1.png"
OUTPUT = ROOT / "public/assets/game/characters/chr-001-waiting-girl-v2.png"

APPROVED_MASTER_SHA256 = "c687fc7019c6a7af2662bc66e3094d9e71ae6942fb1642c44cac19cf08f3d57f"
CANVAS_SIZE = (28, 44)
CONTENT_MAX = (24, 40)
RUNTIME_PLACEMENT = {"x": 290, "y": 324, "originX": 0.5, "originY": 1}


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    if file_hash(MASTER) != APPROVED_MASTER_SHA256:
        raise RuntimeError("Immutable CHR-001 master changed")

    source = Image.open(MASTER).convert("RGBA")
    alpha = source.getchannel("A").point(lambda value: 255 if value >= 16 else 0)
    bbox = alpha.getbbox()
    if bbox is None:
        raise RuntimeError("CHR-001 master has no visible pixels")

    cropped = source.crop(bbox)
    cropped.putalpha(
        cropped.getchannel("A").point(lambda value: 255 if value >= 128 else 0)
    )
    scale = min(CONTENT_MAX[0] / cropped.width, CONTENT_MAX[1] / cropped.height)
    runtime_size = (
        max(1, round(cropped.width * scale)),
        max(1, round(cropped.height * scale)),
    )
    resized = cropped.resize(runtime_size, Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    paste_at = (
        (CANVAS_SIZE[0] - runtime_size[0]) // 2,
        CANVAS_SIZE[1] - runtime_size[1],
    )
    canvas.alpha_composite(resized, paste_at)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUTPUT, optimize=True)
    write_json(
        OUTPUT.with_suffix(".json"),
        {
            "assetId": "CHR-001",
            "version": "v2",
            "status": "integrated",
            "texture": OUTPUT.name,
            "canvas": {"width": canvas.width, "height": canvas.height},
            "visibleBounds": {
                "x": paste_at[0],
                "y": paste_at[1],
                "width": runtime_size[0],
                "height": runtime_size[1],
            },
            "runtimePlacement": RUNTIME_PLACEMENT,
            "production": {
                "designMaster": MASTER.relative_to(ROOT).as_posix(),
                "designMasterSha256": file_hash(MASTER),
                "sourceBox": list(bbox),
                "buildScript": "scripts/build_delivery_girl_v2.py",
                "alphaCleanup": "threshold existing alpha at 128; no RGB/chroma deletion",
                "offlineResizeCount": 1,
                "resizeFilter": "nearest-neighbor",
                "paletteQuantization": False,
                "phaserTextureFilter": "nearest",
                "runtimeScale": 1,
                "runtimeSha256": file_hash(OUTPUT),
            },
        },
    )


if __name__ == "__main__":
    main()
