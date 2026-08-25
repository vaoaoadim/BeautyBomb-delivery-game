import json
from pathlib import Path

from PIL import Image

from build_courier_waterbomb_brand_sprite import (
    CANVAS_SIZE,
    COLLISION,
    ORIGIN,
    ROOT,
    foreground,
    render_foreground,
    sha256,
)


MASTER = ROOT / "visual-references/veh-001-courier-clean-concept-v7.png"
STATIC_OUTPUT = ROOT / "public/assets/game/vehicles/veh-001-courier-clean-static-v5.png"
STATIC_METADATA = ROOT / "public/assets/game/vehicles/veh-001-courier-clean-static-v5.json"
DRIVE_OUTPUT = ROOT / "public/assets/game/vehicles/veh-001-courier-clean-drive-v6.png"
DRIVE_METADATA = ROOT / "public/assets/game/vehicles/veh-001-courier-clean-drive-v6.json"
STATIC_PREVIEW = ROOT / "visual-references/veh-001-courier-clean-static-v5-preview-4x.png"
DRIVE_PREVIEW = ROOT / "visual-references/veh-001-courier-clean-drive-v6-preview-4x.png"

FRAME_COUNT = 4
FRAME_RATE = 9
MASTER_TUBE_END_Y = 387
WHEEL_BOXES = ((154, 670, 364, 874), (822, 670, 1031, 874))
HUB_BOXES = ((186, 749, 286, 848), (884, 734, 984, 833))
BODY_BOUNCE_Y = (0, -4, -6, -4)
TUBE_BOUNCE_Y = (0, 0, -6, -6)
PREVIEW_SCALE = 4


def visible_bounds(image: Image.Image) -> dict[str, int]:
    bounds = image.getchannel("A").getbbox()
    if bounds is None:
        raise ValueError("Courier frame has no visible pixels")
    left, top, right, bottom = bounds
    return {"x": left, "y": top, "width": right - left, "height": bottom - top}


def compose_master_frame(source: Image.Image, frame_index: int) -> Image.Image:
    """Reuse the approved drive motion while keeping the clean artwork unchanged."""
    if frame_index == 0:
        return source.copy()

    width, height = source.size
    frame = Image.new("RGBA", source.size, (0, 0, 0, 0))
    tube = source.crop((0, 0, width, MASTER_TUBE_END_Y))
    body = source.crop((0, MASTER_TUBE_END_Y, width, height))
    frame.alpha_composite(body, (0, MASTER_TUBE_END_Y + BODY_BOUNCE_Y[frame_index]))
    frame.alpha_composite(tube, (0, TUBE_BOUNCE_Y[frame_index]))

    for wheel_box, hub_box in zip(WHEEL_BOXES, HUB_BOXES, strict=True):
        frame.alpha_composite(source.crop(wheel_box), wheel_box[:2])
        rotation = {
            1: Image.Transpose.ROTATE_90,
            2: Image.Transpose.ROTATE_180,
            3: Image.Transpose.ROTATE_270,
        }[frame_index]
        frame.alpha_composite(source.crop(hub_box).transpose(rotation), hub_box[:2])
    return frame


def save_static_metadata(static: Image.Image) -> None:
    metadata = {
        "id": "VEH-001",
        "version": 5,
        "texture": STATIC_OUTPUT.name,
        "canvas": {"width": static.width, "height": static.height},
        "visibleBounds": visible_bounds(static),
        "runtimeScale": 0.5,
        "origin": {
            "normalizedX": ORIGIN["x"] / static.width,
            "normalizedY": ORIGIN["y"] / static.height,
            "pixelX": ORIGIN["x"],
            "pixelY": ORIGIN["y"],
        },
        "collision": {**COLLISION, "includesRoofProduct": False},
        "production": {
            "designMaster": str(MASTER.relative_to(ROOT)).replace("\\", "/"),
            "designMasterSha256": sha256(MASTER),
            "buildScript": "scripts/build_courier_clean_asset.py",
            "exportMethod": "alpha-bounds crop plus one production resize",
            "assetMode": "high-detail-pixel-style-raster",
            "offlineResizeCount": 1,
            "resizeFilter": "nearest-neighbor",
            "paletteQuantization": False,
            "phaserTextureFilter": "nearest",
            "laneTextureScales": [0.56, 0.61, 0.66],
            "runtimeSha256": sha256(STATIC_OUTPUT),
            "animationFrames": 1,
            "status": "approved-static-master",
        },
    }
    STATIC_METADATA.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


def save_drive_metadata(frames: list[Image.Image]) -> None:
    metadata = {
        "id": "VEH-001",
        "version": 6,
        "texture": DRIVE_OUTPUT.name,
        "frame": {"width": CANVAS_SIZE[0], "height": CANVAS_SIZE[1], "count": FRAME_COUNT},
        "frameVisibleBounds": [visible_bounds(frame) for frame in frames],
        "runtimeScale": 0.5,
        "origin": {
            "normalizedX": ORIGIN["x"] / CANVAS_SIZE[0],
            "normalizedY": ORIGIN["y"] / CANVAS_SIZE[1],
            "pixelX": ORIGIN["x"],
            "pixelY": ORIGIN["y"],
        },
        "collision": {**COLLISION, "includesRoofProduct": False},
        "animation": {
            "frameRate": FRAME_RATE,
            "loop": True,
            "firstFrameMatchesApprovedStatic": True,
        },
        "production": {
            "designMaster": str(MASTER.relative_to(ROOT)).replace("\\", "/"),
            "designMasterSha256": sha256(MASTER),
            "approvedStaticTexture": STATIC_OUTPUT.name,
            "approvedStaticRuntimeSha256": sha256(STATIC_OUTPUT),
            "staticRuntimeUsage": "approval anchor only; not an export input",
            "buildScript": "scripts/build_courier_clean_asset.py",
            "exportMethod": "master-component motion transforms plus one production resize per frame",
            "assetMode": "high-detail-pixel-style-raster",
            "offlineResizeCountPerFrame": 1,
            "resizeFilter": "nearest-neighbor",
            "paletteQuantization": False,
            "phaserTextureFilter": "nearest",
            "laneTextureScales": [0.56, 0.61, 0.66],
            "runtimeSha256": sha256(DRIVE_OUTPUT),
            "status": "approved-drive-cycle",
        },
    }
    DRIVE_METADATA.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    master = foreground(Image.open(MASTER))
    static = render_foreground(master)
    static.save(STATIC_OUTPUT)
    save_static_metadata(static)
    static.resize(
        (static.width * PREVIEW_SCALE, static.height * PREVIEW_SCALE),
        Image.Resampling.NEAREST,
    ).save(STATIC_PREVIEW)

    frames = [
        render_foreground(compose_master_frame(master, frame_index))
        for frame_index in range(FRAME_COUNT)
    ]
    if frames[0].tobytes() != static.tobytes():
        raise ValueError("Drive frame zero diverges from the clean static runtime")

    sheet = Image.new("RGBA", (CANVAS_SIZE[0] * FRAME_COUNT, CANVAS_SIZE[1]), (0, 0, 0, 0))
    for frame_index, frame in enumerate(frames):
        sheet.alpha_composite(frame, (CANVAS_SIZE[0] * frame_index, 0))
    sheet.save(DRIVE_OUTPUT)
    save_drive_metadata(frames)
    sheet.resize(
        (sheet.width * PREVIEW_SCALE, sheet.height * PREVIEW_SCALE),
        Image.Resampling.NEAREST,
    ).save(DRIVE_PREVIEW)


if __name__ == "__main__":
    main()
