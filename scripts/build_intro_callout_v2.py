"""Build the v2 intro callout with the owner-requested yellow mark removed.

UI-013 v1 remains immutable. This small deterministic derivation preserves the
approved 332 x 207 callout pixels and clears only the yellow decorative mark in
the lower-right interior of the bubble.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public/assets/game/ui"
SOURCE = OUTPUT / "ui-013-intro-callout-v1.png"
TARGET = OUTPUT / "ui-013-intro-callout-v2.png"
TARGET_METADATA = TARGET.with_suffix(".json")

YELLOW = (255, 239, 92, 255)


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> None:
    image = Image.open(SOURCE).convert("RGBA")

    # The mark is the only yellow element in this native asset. Its local
    # bounds are x=300..313, y=158..160; clear exact yellow pixels only.
    removed_pixels: list[tuple[int, int]] = []
    for y in range(158, 161):
        for x in range(300, 314):
            if image.getpixel((x, y)) == YELLOW:
                image.putpixel((x, y), (0, 0, 0, 0))
                removed_pixels.append((x, y))

    expected_pixel_count = 42
    if len(removed_pixels) != expected_pixel_count:
        raise RuntimeError(
            f"Unexpected yellow-mark pixel count: {len(removed_pixels)} "
            f"(expected {expected_pixel_count})."
        )

    image.save(TARGET, optimize=True)
    metadata = {
        "assetId": "UI-013",
        "version": "v2",
        "status": "verified",
        "texture": TARGET.name,
        "canvas": {"width": image.width, "height": image.height},
        "frame": {"width": image.width, "height": image.height, "count": 1},
        "sourceAsset": SOURCE.name,
        "change": "Removed the yellow decorative mark from the lower-right interior of the thought bubble.",
        "removedLocalRect": {"x": 300, "y": 158, "width": 14, "height": 3},
        "removedPixelCount": len(removed_pixels),
        "runtimeSha256": file_hash(TARGET),
        "runtime": {
            "position": {"x": 16, "y": 154},
            "origin": {"x": 0, "y": 0},
            "fixedToCamera": True,
        },
    }
    TARGET_METADATA.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"source={SOURCE}")
    print(f"target={TARGET} sha256={file_hash(TARGET)}")
    print(f"removedPixels={len(removed_pixels)}")


if __name__ == "__main__":
    main()
