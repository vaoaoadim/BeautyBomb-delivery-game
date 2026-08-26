"""Build DST-001 and CHR-001 from immutable generated masters."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]

ASSETS = (
    {
        "assetId": "DST-001",
        "master": ROOT / "visual-references/dst-001-arrival-house-master-v1.png",
        "masterSha256": "02477733bf24b931250bf4bb08730eb17a2c76e2a118521a18de942a9eae4386",
        "runtime": ROOT / "public/assets/game/environment/dst-001-arrival-house-v1.png",
        "canvas": (176, 176),
        "contentMax": (168, 168),
        "runtimePlacement": {"x": 270, "y": 292, "originX": 0.5, "originY": 1},
        "runtimeScale": 0.88,
        "promptSummary": "One small solitary pink premium pixel-art house with a compact yard, transparent background, no UI or characters.",
    },
    {
        "assetId": "CHR-001",
        "master": ROOT / "visual-references/chr-001-waiting-girl-master-v1.png",
        "masterSha256": "c687fc7019c6a7af2662bc66e3094d9e71ae6942fb1642c44cac19cf08f3d57f",
        "runtime": ROOT / "public/assets/game/characters/chr-001-waiting-girl-v1.png",
        "canvas": (56, 88),
        "contentMax": (52, 84),
        "runtimePlacement": {"x": 220, "y": 362, "originX": 0.5, "originY": 1},
        "runtimeScale": 1,
        "promptSummary": "One full-body friendly blonde girl in a simple pink dress, turned slightly left, transparent background, empty hands.",
    },
)


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def alpha_bbox(source: Image.Image) -> tuple[int, int, int, int]:
    alpha = source.getchannel("A").point(lambda value: 255 if value >= 16 else 0)
    bbox = alpha.getbbox()
    if bbox is None:
        raise RuntimeError("Generated master has no visible pixels")
    return bbox


def build_asset(spec: dict[str, Any]) -> None:
    master: Path = spec["master"]
    runtime: Path = spec["runtime"]
    if file_hash(master) != spec["masterSha256"]:
        raise RuntimeError(f"Immutable generated master changed: {master.name}")

    source = Image.open(master).convert("RGBA")
    source_dimensions = source.size
    bbox = alpha_bbox(source)
    cropped = source.crop(bbox)
    cropped.putalpha(cropped.getchannel("A").point(lambda value: 255 if value >= 128 else 0))

    max_width, max_height = spec["contentMax"]
    scale = min(max_width / cropped.width, max_height / cropped.height)
    runtime_size = (
        max(1, round(cropped.width * scale)),
        max(1, round(cropped.height * scale)),
    )
    resized = cropped.resize(runtime_size, Image.Resampling.NEAREST)
    canvas_width, canvas_height = spec["canvas"]
    canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
    paste_at = (
        (canvas_width - runtime_size[0]) // 2,
        canvas_height - runtime_size[1],
    )
    canvas.alpha_composite(resized, paste_at)
    runtime.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(runtime)

    master_metadata = {
        "assetId": spec["assetId"],
        "version": "master-v1",
        "status": "generated-master",
        "source": "built-in image_gen; two-asset finale batch",
        "canvas": {"width": source_dimensions[0], "height": source_dimensions[1]},
        "sha256": file_hash(master),
        "promptSummary": spec["promptSummary"],
        "transparentBackgroundRequested": True,
        "licenseNote": "Original generated artwork for this independent portfolio concept.",
    }
    write_json(master.with_suffix(".json"), master_metadata)

    metadata = {
        "assetId": spec["assetId"],
        "version": "v1",
        "status": "integrated",
        "texture": runtime.name,
        "canvas": {"width": canvas_width, "height": canvas_height},
        "visibleBounds": {
            "x": paste_at[0],
            "y": paste_at[1],
            "width": runtime_size[0],
            "height": runtime_size[1],
        },
        "runtimePlacement": spec["runtimePlacement"],
        "production": {
            "designMaster": str(master.relative_to(ROOT)),
            "designMasterSha256": file_hash(master),
            "sourceBox": list(bbox),
            "buildScript": "scripts/build_delivery_finale_assets_v1.py",
            "alphaCleanup": "threshold existing alpha at 128; no RGB/chroma deletion",
            "offlineResizeCount": 1,
            "resizeFilter": "nearest-neighbor",
            "paletteQuantization": False,
            "phaserTextureFilter": "nearest",
            "runtimeScale": spec["runtimeScale"],
            "runtimeSha256": file_hash(runtime),
        },
    }
    write_json(runtime.with_suffix(".json"), metadata)


def main() -> None:
    for spec in ASSETS:
        build_asset(spec)


if __name__ == "__main__":
    main()
