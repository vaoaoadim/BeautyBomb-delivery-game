"""Build ENV-009: the finale house embedded in the coherent city tile.

The approved ENV-004 v8 route tile stays immutable. This derivation replaces
one complete cyclic street-front lot with DST-001, so the destination enters
and stops under the exact same TileSprite transform as the city around it.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
BASE_CITY = ROOT / "public/assets/game/environment/env-004-neighborhood-city-v8.png"
HOUSE_MASTER = ROOT / "visual-references/dst-001-arrival-house-master-v1.png"
OUTPUT = ROOT / "public/assets/game/environment/env-009-delivery-destination-city-v1.png"

APPROVED_CITY_SHA256 = "e888e436e39acf405e9ee0e8577c74d067e217ba2e03db8b6f08d0e1fdab3287"
APPROVED_HOUSE_SHA256 = "02477733bf24b931250bf4bb08730eb17a2c76e2a118521a18de942a9eae4386"

TEXTURE_SIZE = (2048, 512)
TILE_SCALE = {"x": 0.36, "y": 0.55078125}
HOUSE_DISPLAY_SIZE = 112
HOUSE_CENTER_TEXTURE_X = 1960
LOT_SEGMENTS = ((1805, 2048), (0, 68))
LOT_TOP = 309
SIDEWALK_TOP = 496
REDUCED_MOTION_FINAL_OFFSET = 1134


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
        raise RuntimeError("DST-001 master has no visible pixels")
    return bbox


def wrapped_alpha_composite(
    destination: Image.Image,
    source: Image.Image,
    center_x: int,
    bottom_y: int,
) -> None:
    paste_x = center_x - source.width // 2
    first_width = min(source.width, destination.width - paste_x)
    destination.alpha_composite(
        source.crop((0, 0, first_width, source.height)),
        (paste_x, bottom_y - source.height),
    )
    remaining = source.width - first_width
    if remaining > 0:
        destination.alpha_composite(
            source.crop((first_width, 0, source.width, source.height)),
            (0, bottom_y - source.height),
        )


def main() -> None:
    if file_hash(BASE_CITY) != APPROVED_CITY_SHA256:
        raise RuntimeError("Approved ENV-004 v8 runtime changed")
    if file_hash(HOUSE_MASTER) != APPROVED_HOUSE_SHA256:
        raise RuntimeError("Immutable DST-001 master changed")

    city = Image.open(BASE_CITY).convert("RGBA")
    if city.size != TEXTURE_SIZE:
        raise RuntimeError(f"Unexpected ENV-004 canvas: {city.size}")
    original_sidewalk = city.crop((0, SIDEWALK_TOP, city.width, city.height))

    for start_x, end_x in LOT_SEGMENTS:
        city.paste(
            (0, 0, 0, 0),
            (start_x, LOT_TOP, end_x, SIDEWALK_TOP),
        )

    master = Image.open(HOUSE_MASTER).convert("RGBA")
    source_box = alpha_bbox(master)
    house = master.crop(source_box)
    house.putalpha(
        house.getchannel("A").point(lambda value: 255 if value >= 128 else 0)
    )
    target_size = (
        round(HOUSE_DISPLAY_SIZE / TILE_SCALE["x"]),
        round(HOUSE_DISPLAY_SIZE / TILE_SCALE["y"]),
    )
    house = house.resize(target_size, Image.Resampling.NEAREST)
    wrapped_alpha_composite(city, house, HOUSE_CENTER_TEXTURE_X, city.height)

    # Preserve the approved continuous sidewalk in front of the destination lot.
    city.alpha_composite(original_sidewalk, (0, SIDEWALK_TOP))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    city.save(OUTPUT, optimize=True)

    final_center_x = (
        (HOUSE_CENTER_TEXTURE_X - REDUCED_MOTION_FINAL_OFFSET) % city.width
    ) * TILE_SCALE["x"]
    write_json(
        OUTPUT.with_suffix(".json"),
        {
            "assetId": "ENV-009",
            "version": "v1",
            "status": "integrated",
            "texture": OUTPUT.name,
            "canvas": {"width": city.width, "height": city.height},
            "composition": "ENV-004 v8 city with DST-001 baked into one complete cyclic street-front lot",
            "runtime": {
                "tileScale": TILE_SCALE,
                "depth": 1,
                "switchTrigger": "delivery progress complete",
                "reducedMotionFinalOffsetTexturePx": REDUCED_MOTION_FINAL_OFFSET,
                "expectedFinalHouseCenterX": round(final_center_x, 2),
            },
            "production": {
                "buildScript": "scripts/build_delivery_destination_city_v1.py",
                "baseCity": BASE_CITY.relative_to(ROOT).as_posix(),
                "baseCitySha256": file_hash(BASE_CITY),
                "houseMaster": HOUSE_MASTER.relative_to(ROOT).as_posix(),
                "houseMasterSha256": file_hash(HOUSE_MASTER),
                "houseSourceBox": list(source_box),
                "houseResizeCount": 1,
                "resizeFilter": "nearest-neighbor",
                "phaserTextureFilter": "nearest",
                "runtimeSha256": file_hash(OUTPUT),
            },
            "lot": {
                "wrappedTextureSegments": [list(segment) for segment in LOT_SEGMENTS],
                "topTextureY": LOT_TOP,
                "sidewalkTopTextureY": SIDEWALK_TOP,
                "houseCenterTextureX": HOUSE_CENTER_TEXTURE_X,
                "houseDisplaySize": {
                    "width": HOUSE_DISPLAY_SIZE,
                    "height": HOUSE_DISPLAY_SIZE,
                },
                "sidewalkPreserved": True,
                "independentHouseSprite": False,
            },
        },
    )


if __name__ == "__main__":
    main()
