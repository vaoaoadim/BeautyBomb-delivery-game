"""Export the approved UI-018 v2 coupon master once at its Phaser runtime size."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "visual-references/ui-018-reward-coupon-master-v2.png"
RUNTIME = ROOT / "public/assets/game/ui/ui-018-reward-coupon-v2.png"
METADATA = RUNTIME.with_suffix(".json")
APPROVED_MASTER_SHA256 = "b9c7e37d7fd8abb0a223bf6d322205a2190577373659374dcb57d00862e921b0"
RUNTIME_SIZE = (304, 456)


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if file_hash(MASTER) != APPROVED_MASTER_SHA256:
        raise RuntimeError("UI-018 v2 master hash differs from the approved source")

    with Image.open(MASTER) as source:
        if source.size != (1024, 1536):
            raise RuntimeError(f"Unexpected UI-018 v2 master size: {source.size}")
        rgba = source.convert("RGBA")
        alpha_values = {value for _, value in (rgba.getchannel("A").getcolors(256) or [])}
        if not alpha_values.issubset({0, 255}) or 0 not in alpha_values:
            raise RuntimeError("UI-018 v2 requires binary transparency")
        runtime = rgba.resize(RUNTIME_SIZE, Image.Resampling.NEAREST)

    RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    runtime.save(RUNTIME, optimize=True)

    metadata = {
        "assetId": "UI-018",
        "version": "v2",
        "asset": "delivery reward coupon background",
        "status": "integrated",
        "canvas": {"width": 304, "height": 456},
        "runtimePlacement": {"x": 180, "y": 320, "originX": 0.5, "originY": 0.5},
        "source": {
            "master": "visual-references/ui-018-reward-coupon-master-v2.png",
            "approvedMasterSha256": APPROVED_MASTER_SHA256,
            "dimensions": {"width": 1024, "height": 1536},
            "transparentBackground": True,
            "alpha": "binary",
        },
        "runtime": {
            "path": "public/assets/game/ui/ui-018-reward-coupon-v2.png",
            "dimensions": {"width": 304, "height": 456},
            "sha256": file_hash(RUNTIME),
            "phaserTextureFilter": "NEAREST",
            "origin": {"x": 0.5, "y": 0.5},
            "placement": {"x": 180, "y": 320},
        },
        "build": {
            "buildScript": "scripts/build_reward_coupon_v2.py",
            "resizeCount": 1,
            "resizeFilter": "nearest-neighbor",
            "paletteQuantization": "none after approval",
        },
        "production": {
            "designMaster": "visual-references/ui-018-reward-coupon-master-v2.png",
            "designMasterSha256": APPROVED_MASTER_SHA256,
            "buildScript": "scripts/build_reward_coupon_v2.py",
            "offlineResizeCount": 1,
            "resizeFilter": "nearest-neighbor",
            "paletteQuantization": False,
            "phaserTextureFilter": "nearest",
            "runtimeSha256": file_hash(RUNTIME),
        },
        "liveOverlay": {
            "couponCode": "XQZ-20476",
            "codeAndCopyControl": "Phaser runtime UI",
            "tearOffText": "Phaser runtime UI",
            "codeField": {"x": 153, "y": 305, "width": 174, "height": 44},
            "copyButton": {"x": 270, "y": 305, "width": 44, "height": 44},
            "tearOffTextCenter": {"x": 180, "y": 468},
        },
    }
    METADATA.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"runtime={RUNTIME} sha256={file_hash(RUNTIME)}")


if __name__ == "__main__":
    main()
