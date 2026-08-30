"""Derive the shadow-free PRD-003 v3 transfer cream from the v8 master."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "visual-references/veh-001-courier-clean-concept-v8-flip-top.png"
OUTPUT = ROOT / "public/assets/game/products/prd-003-delivery-transfer-v3.png"
SOURCE_BOX = (270, 78, 1138, 432)
CANVAS = (32, 64)
CONTENT = (22, 54)

# The roof-tube master contains a small upper-left cast offset at the cap. It
# is outside the physical cap silhouette once the product is rotated upright.
# This native-grid mask removes only that offset from the hand-off variant.
CAST_SHADOW_RECT = (5, 8, 8, 10)


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def remove_cap_cast_shadow(image: Image.Image) -> Image.Image:
    pixels = image.load()
    left, top, right, bottom = CAST_SHADOW_RECT
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            pixels[x, y] = (0, 0, 0, 0)
    return image


def main() -> None:
    master = Image.open(MASTER).convert("RGBA")
    product = master.crop(SOURCE_BOX).transpose(Image.Transpose.ROTATE_270)
    alpha = product.getchannel("A").point(lambda value: 0 if value < 16 else 255)
    product.putalpha(alpha)
    product = product.resize(CONTENT, Image.Resampling.NEAREST)

    runtime = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    runtime.alpha_composite(
        product,
        ((CANVAS[0] - CONTENT[0]) // 2, (CANVAS[1] - CONTENT[1]) // 2),
    )
    runtime = remove_cap_cast_shadow(runtime)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    runtime.save(OUTPUT)

    metadata = {
        "assetId": "PRD-003",
        "version": "v3",
        "status": "integrated",
        "texture": OUTPUT.name,
        "canvas": {"width": CANVAS[0], "height": CANVAS[1]},
        "visibleBounds": {
            "x": (CANVAS[0] - CONTENT[0]) // 2,
            "y": (CANVAS[1] - CONTENT[1]) // 2,
            "width": CONTENT[0],
            "height": CONTENT[1],
        },
        "orientation": "vertical; shadow-free flip-top roof tube rotated clockwise",
        "origin": {"x": 0.5, "y": 0.5},
        "runtimeScale": 1,
        "production": {
            "designMaster": str(MASTER.relative_to(ROOT)).replace("\\", "/"),
            "designMasterSha256": file_hash(MASTER),
            "sourceBox": list(SOURCE_BOX),
            "buildScript": "scripts/build_delivery_product_v3.py",
            "offlineResizeCount": 1,
            "resizeFilter": "nearest-neighbor",
            "paletteQuantization": False,
            "shadowTreatment": "fixed native-grid upper-left cap cast shadow removed",
            "phaserTextureFilter": "nearest",
            "runtimeSha256": file_hash(OUTPUT),
            "runtimeSource": "versioned master; not screenshot or runtime sprite",
        },
    }
    OUTPUT.with_suffix(".json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
