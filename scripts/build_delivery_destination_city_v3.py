"""Build ENV-009 v3 and close the doorstep curb gap deterministically."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "visual-references/env-009-delivery-destination-city-alpha-master-v2.png"
CHROMA_MASTER = ROOT / "visual-references/env-009-delivery-destination-city-chroma-master-v2.png"
OUTPUT = ROOT / "public/assets/game/environment/env-009-delivery-destination-city-v3.png"

APPROVED_MASTER_SHA256 = "4c39e80712adc35e506280c85c1674c6364418b37fe222769e797394770c2aa8"
APPROVED_CHROMA_SHA256 = "a05df5fd146f38dcd73acbcd89b2e555d6aaaaec41405b195be06d1cae1b03b1"
SOURCE_BOX = (0, 0, 2172, 644)
RUNTIME_SIZE = (2048, 512)
TILE_SCALE = {"x": 0.36, "y": 0.55078125}
HOUSE_CENTER_SOURCE_X = 1618
HOUSE_CENTER_RUNTIME_X = round(
    HOUSE_CENTER_SOURCE_X * RUNTIME_SIZE[0] / (SOURCE_BOX[2] - SOURCE_BOX[0])
)
START_OFFSET_TEXTURE_PX = HOUSE_CENTER_RUNTIME_X - round(360 / TILE_SCALE["x"])
REDUCED_MOTION_FINAL_OFFSET_TEXTURE_PX = round(
    HOUSE_CENTER_RUNTIME_X - 297 / TILE_SCALE["x"]
)

# The generated panorama has one transparent 37 x 6 px interval directly
# below the doorstep. Extend the immediately adjacent approved curb sample
# into that interval without redrawing or rescaling any city content.
CURB_SAMPLE_BOX = (1451, 506, 1493, 512)
CURB_DESTINATION = (1493, 506)


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    if file_hash(MASTER) != APPROVED_MASTER_SHA256:
        raise RuntimeError("Approved ENV-009 alpha master changed")
    if file_hash(CHROMA_MASTER) != APPROVED_CHROMA_SHA256:
        raise RuntimeError("Approved ENV-009 chroma master changed")

    master = Image.open(MASTER).convert("RGBA")
    if master.size != (2172, 724):
        raise RuntimeError(f"Unexpected ENV-009 master canvas: {master.size}")

    runtime = master.crop(SOURCE_BOX).resize(
        RUNTIME_SIZE,
        Image.Resampling.NEAREST,
    )
    curb_patch = runtime.crop(CURB_SAMPLE_BOX)
    curb_patch.putalpha(Image.new("L", curb_patch.size, 255))
    runtime.paste(curb_patch, CURB_DESTINATION)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    runtime.save(OUTPUT, optimize=True)
    write_json(
        OUTPUT.with_suffix(".json"),
        {
            "assetId": "ENV-009",
            "version": "v3",
            "status": "integrated",
            "texture": OUTPUT.name,
            "canvas": {"width": runtime.width, "height": runtime.height},
            "composition": "One generated city panorama with the destination house integrated as a complete foreground lot",
            "runtime": {
                "tileScale": TILE_SCALE,
                "depth": 1,
                "switchTrigger": "delivery progress complete",
                "startOffsetTexturePx": START_OFFSET_TEXTURE_PX,
                "reducedMotionFinalOffsetTexturePx": REDUCED_MOTION_FINAL_OFFSET_TEXTURE_PX,
                "expectedFinalHouseCenterX": 297,
            },
            "production": {
                "buildScript": "scripts/build_delivery_destination_city_v3.py",
                "chromaMaster": CHROMA_MASTER.relative_to(ROOT).as_posix(),
                "chromaMasterSha256": file_hash(CHROMA_MASTER),
                "alphaMaster": MASTER.relative_to(ROOT).as_posix(),
                "alphaMasterSha256": file_hash(MASTER),
                "sourceBox": list(SOURCE_BOX),
                "offlineResizeCount": 1,
                "resizeFilter": "nearest-neighbor",
                "alphaExtraction": "auto-key border with soft matte and despill",
                "phaserTextureFilter": "nearest",
                "runtimeSha256": file_hash(OUTPUT),
            },
            "integration": {
                "houseCenterSourceX": HOUSE_CENTER_SOURCE_X,
                "houseCenterRuntimeX": HOUSE_CENTER_RUNTIME_X,
                "independentHouseSprite": False,
                "sharedCityTransform": True,
                "continuousSidewalk": True,
                "rectangularHouseBackdrop": False,
                "doorstepGapFilled": True,
                "curbSampleBox": list(CURB_SAMPLE_BOX),
                "curbDestination": list(CURB_DESTINATION),
            },
        },
    )


if __name__ == "__main__":
    main()
