"""Derive compact UI-010/UI-012 runtime sheets from the generated v1 master."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from PIL import Image


MASTER = Path("visual-references/ui-005-utility-buttons-master-v1.png")
OUTPUT = Path("public/assets/game/ui")
REVIEW = Path("visual-references/ui-utility-buttons-v2-review.png")
FRAME_SIZE = 32
FRAME_CROPS = {
    "pause": ((64, 56, 464, 456), (560, 56, 960, 456)),
    "sound": ((64, 568, 464, 968), (560, 568, 960, 968)),
}
PALETTE = {
    "ink": "#1d1d1b",
    "yellow": "#ffef5c",
    "pink": "#ff4fab",
}


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def derive_sheet(master: Image.Image, name: str) -> Image.Image:
    sheet = Image.new("RGBA", (FRAME_SIZE, FRAME_SIZE * 2), (0, 0, 0, 0))
    for index, crop in enumerate(FRAME_CROPS[name]):
        source = master.crop(crop)
        frame = source.resize(
            (FRAME_SIZE, FRAME_SIZE),
            Image.Resampling.NEAREST,
        )
        sheet.alpha_composite(frame, (0, index * FRAME_SIZE))
    return sheet


def write_metadata(
    *,
    asset_id: str,
    version: str,
    filename: str,
    sheet: Image.Image,
    runtime: dict[str, Any],
) -> None:
    runtime_path = OUTPUT / filename
    runtime_path.with_suffix(".json").write_text(
        json.dumps(
            {
                "assetId": asset_id,
                "version": version,
                "status": "integrated",
                "texture": filename,
                "canvas": {"width": sheet.width, "height": sheet.height},
                "frame": {
                    "width": FRAME_SIZE,
                    "height": FRAME_SIZE,
                    "count": 2,
                    "states": ["idle", "pressed"],
                },
                "palette": PALETTE,
                "production": {
                    "designMaster": MASTER.as_posix(),
                    "designMasterSha256": file_hash(MASTER),
                    "buildScript": "scripts/build_utility_buttons_v2.py",
                    "assetMode": "generated-master-derived-pixel-art",
                    "sourceCrop": runtime["sourceCrop"],
                    "offlineResizeCountPerFrame": 1,
                    "resizeFilter": "nearest-neighbor",
                    "antialiasing": False,
                    "paletteQuantization": False,
                    "phaserTextureFilter": "nearest",
                    "runtimeSha256": file_hash(runtime_path),
                },
                "runtime": runtime,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def build_review(pause: Image.Image, sound: Image.Image) -> None:
    scale = 4
    review = Image.new("RGBA", (296, 304), (238, 240, 255, 255))
    for index, sheet in enumerate((pause, sound)):
        for state in range(2):
            frame = sheet.crop((0, state * FRAME_SIZE, FRAME_SIZE, (state + 1) * FRAME_SIZE))
            frame = frame.resize((FRAME_SIZE * scale, FRAME_SIZE * scale), Image.Resampling.NEAREST)
            review.alpha_composite(frame, (16 + state * 144, 16 + index * 152))
    review.convert("RGB").save(REVIEW, optimize=True)


def assert_sheet(sheet: Image.Image) -> None:
    assert sheet.size == (32, 64)
    assert sheet.getchannel("A").getbbox() is not None


def main() -> None:
    assert MASTER.exists(), f"Missing generated master: {MASTER}"
    OUTPUT.mkdir(parents=True, exist_ok=True)
    master = Image.open(MASTER).convert("RGBA")
    assert master.size == (1024, 1024)

    pause = derive_sheet(master, "pause")
    sound = derive_sheet(master, "sound")
    assert_sheet(pause)
    assert_sheet(sound)

    pause_path = OUTPUT / "ui-010-pause-button-v2.png"
    sound_path = OUTPUT / "ui-012-sound-button-v2.png"
    pause.save(pause_path, optimize=True)
    sound.save(sound_path, optimize=True)

    write_metadata(
        asset_id="UI-010",
        version="v2",
        filename=pause_path.name,
        sheet=pause,
        runtime={
            "center": {"x": 332, "y": 32},
            "edgeInsets": {"top": 16, "right": 12},
            "hitArea": {"width": 44, "height": 44},
            "fixedToCamera": True,
            "interaction": "pressed frame on pointerdown; idle frame on pointerup or pointerout",
            "action": "existing-pause-flow",
            "sourceCrop": [list(crop) for crop in FRAME_CROPS["pause"]],
        },
    )
    write_metadata(
        asset_id="UI-012",
        version="v2",
        filename=sound_path.name,
        sheet=sound,
        runtime={
            "center": {"x": 332, "y": 84},
            "edgeInsets": {"right": 12, "belowPauseGap": 20},
            "hitArea": {"width": 44, "height": 44},
            "fixedToCamera": True,
            "interaction": "pressed frame on pointerdown; idle frame on pointerup or pointerout",
            "behavior": "visual-placeholder",
            "futureAction": "toggle-sound",
            "sourceCrop": [list(crop) for crop in FRAME_CROPS["sound"]],
        },
    )
    build_review(pause, sound)


if __name__ == "__main__":
    main()
