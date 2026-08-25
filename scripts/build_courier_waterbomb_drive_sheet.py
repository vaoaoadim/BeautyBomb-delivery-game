import json
from pathlib import Path

from PIL import Image, ImageDraw

from build_courier_waterbomb_brand_sprite import (
    CANVAS_SIZE,
    COLLISION,
    MASTER,
    ORIGIN,
    ROOT,
    checkerboard,
    draw_panel,
    foreground,
    render_foreground,
    sha256,
)


STATIC_RUNTIME = ROOT / "public/assets/game/vehicles/veh-001-courier-waterbomb-brand-static-v4.png"
OUTPUT = ROOT / "public/assets/game/vehicles/veh-001-courier-waterbomb-brand-drive-v5.png"
METADATA = ROOT / "public/assets/game/vehicles/veh-001-courier-waterbomb-brand-drive-v5.json"
PREVIEW = ROOT / "visual-references/veh-001-courier-waterbomb-brand-drive-v5-preview-4x.png"
GUIDE = ROOT / "visual-references/veh-001-courier-waterbomb-brand-drive-v5-guide-4x.png"
COMPARISON = ROOT / "visual-references/veh-001-courier-waterbomb-brand-drive-v5-comparison.png"
LANE_SCREENSHOTS = {
    "FAR LANE": ROOT / "visual-references/veh-001-courier-waterbomb-brand-drive-v5-in-game-far.png",
    "MIDDLE LANE": ROOT / "visual-references/veh-001-courier-waterbomb-brand-drive-v5-in-game-middle.png",
    "NEAR LANE": ROOT / "visual-references/veh-001-courier-waterbomb-brand-drive-v5-in-game-near.png",
}

FRAME_COUNT = 4
FRAME_RATE = 9
MASTER_TUBE_END_Y = 390
WHEEL_BOXES = ((155, 675, 365, 880), (825, 675, 1035, 880))
HUB_BOXES = ((187, 754, 287, 854), (887, 739, 987, 839))
BODY_BOUNCE_Y = (0, -4, -6, -4)
TUBE_BOUNCE_Y = (0, 0, -6, -6)
PREVIEW_SCALE = 4


def compose_master_frame(source: Image.Image, frame_index: int) -> Image.Image:
    """Create a motion pose without redrawing or resizing the approved master."""
    if frame_index == 0:
        return source.copy()

    width, height = source.size
    frame = Image.new("RGBA", source.size, (0, 0, 0, 0))
    tube = source.crop((0, 0, width, MASTER_TUBE_END_Y))
    body = source.crop((0, MASTER_TUBE_END_Y, width, height))
    frame.alpha_composite(body, (0, MASTER_TUBE_END_Y + BODY_BOUNCE_Y[frame_index]))
    frame.alpha_composite(tube, (0, TUBE_BOUNCE_Y[frame_index]))

    # Keep tyre contact fixed on the documented wheel baseline, then rotate only
    # the already-authored hub pixels. Neither operation introduces new artwork.
    for wheel_box, hub_box in zip(WHEEL_BOXES, HUB_BOXES, strict=True):
        frame.alpha_composite(source.crop(wheel_box), wheel_box[:2])
        hub = source.crop(hub_box)
        rotation = {
            1: Image.Transpose.ROTATE_90,
            2: Image.Transpose.ROTATE_180,
            3: Image.Transpose.ROTATE_270,
        }[frame_index]
        frame.alpha_composite(hub.transpose(rotation), hub_box[:2])
    return frame


def build_frames() -> list[Image.Image]:
    source = foreground(Image.open(MASTER))
    frames = [render_foreground(compose_master_frame(source, index)) for index in range(FRAME_COUNT)]
    static_runtime = Image.open(STATIC_RUNTIME).convert("RGBA")
    if frames[0].tobytes() != static_runtime.tobytes():
        raise ValueError("Drive frame zero diverges from the approved static runtime")
    return frames


def build_sheet(frames: list[Image.Image]) -> Image.Image:
    sheet = Image.new("RGBA", (CANVAS_SIZE[0] * FRAME_COUNT, CANVAS_SIZE[1]), (0, 0, 0, 0))
    for index, frame in enumerate(frames):
        sheet.alpha_composite(frame, (CANVAS_SIZE[0] * index, 0))
    return sheet


def visible_bounds(frame: Image.Image) -> dict[str, int]:
    bounds = frame.getchannel("A").getbbox()
    if bounds is None:
        raise ValueError("Drive frame has no visible pixels")
    left, top, right, bottom = bounds
    return {"x": left, "y": top, "width": right - left, "height": bottom - top}


def save_metadata(frames: list[Image.Image]) -> None:
    metadata = {
        "id": "VEH-001",
        "version": 5,
        "texture": OUTPUT.name,
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
        "animation": {"frameRate": FRAME_RATE, "loop": True, "firstFrameMatchesApprovedStatic": True},
        "production": {
            "designMaster": str(MASTER.relative_to(ROOT)).replace("\\", "/"),
            "designMasterSha256": sha256(MASTER),
            "approvedStaticTexture": STATIC_RUNTIME.name,
            "approvedStaticRuntimeSha256": sha256(STATIC_RUNTIME),
            "staticRuntimeUsage": "approval anchor only; not an export input",
            "buildScript": "scripts/build_courier_waterbomb_drive_sheet.py",
            "exportMethod": "master-component motion transforms plus one production resize per frame",
            "assetMode": "high-detail-pixel-style-raster",
            "offlineResizeCountPerFrame": 1,
            "resizeFilter": "nearest-neighbor",
            "paletteQuantization": False,
            "phaserTextureFilter": "nearest",
            "laneTextureScales": [0.56, 0.61, 0.66],
            "runtimeSha256": sha256(OUTPUT),
            "status": "approved-drive-cycle",
        },
    }
    METADATA.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def save_review_images(sheet: Image.Image) -> None:
    preview = sheet.resize((sheet.width * PREVIEW_SCALE, sheet.height * PREVIEW_SCALE), Image.Resampling.NEAREST)
    preview.save(PREVIEW)

    guide = preview.copy()
    draw = ImageDraw.Draw(guide)
    for index in range(FRAME_COUNT):
        offset_x = index * CANVAS_SIZE[0] * PREVIEW_SCALE
        collision = (
            offset_x + COLLISION["x"] * PREVIEW_SCALE,
            COLLISION["y"] * PREVIEW_SCALE,
            offset_x + (COLLISION["x"] + COLLISION["width"] - 1) * PREVIEW_SCALE,
            (COLLISION["y"] + COLLISION["height"] - 1) * PREVIEW_SCALE,
        )
        draw.rectangle(collision, outline=(255, 77, 145, 255), width=2)
        origin_x = offset_x + ORIGIN["x"] * PREVIEW_SCALE
        origin_y = ORIGIN["y"] * PREVIEW_SCALE
        draw.line((origin_x - 8, origin_y, origin_x + 8, origin_y), fill=(216, 243, 74, 255), width=2)
        draw.line((origin_x, origin_y - 8, origin_x, origin_y + 8), fill=(216, 243, 74, 255), width=2)
    guide.save(GUIDE)


def lane_road_crop(path: Path) -> Image.Image:
    screenshot = Image.open(path).convert("RGBA")
    canvas_left = (screenshot.width - 360) // 2
    canvas_top = (screenshot.height - 640) // 2
    return screenshot.crop((canvas_left, canvas_top + 282, canvas_left + 360, canvas_top + 522))


def save_comparison_sheet(sheet: Image.Image) -> None:
    if not all(path.exists() for path in LANE_SCREENSHOTS.values()):
        return

    master = foreground(Image.open(MASTER))
    static_runtime = Image.open(STATIC_RUNTIME).convert("RGBA")
    review = Image.new("RGBA", (1200, 1050), (20, 20, 43, 255))
    draw = ImageDraw.Draw(review)
    draw.text((20, 14), "VEH-001 WATERBOMB BRAND / DRIVE V5", fill=(255, 239, 92, 255))
    for position, title, content, resample in (
        ((20, 45), "APPROVED MASTER V6", master, Image.Resampling.LANCZOS),
        ((415, 45), "APPROVED STATIC V4 / FRAME 0", static_runtime, Image.Resampling.NEAREST),
        ((810, 45), "NEW FOUR-FRAME SHEET", sheet, Image.Resampling.NEAREST),
    ):
        draw_panel(review, position, (370, 300), title, content, resample)

    draw_panel(
        review,
        (20, 365),
        (570, 300),
        "DRIVE SHEET / NEAREST PREVIEW",
        sheet.resize((sheet.width * 2, sheet.height * 2), Image.Resampling.NEAREST),
    )
    draw_panel(
        review,
        (610, 365),
        (570, 300),
        "FRAME 0 / APPROVED STATIC PIXEL DIFF: 0",
        static_runtime,
    )

    for index, (label, path) in enumerate(LANE_SCREENSHOTS.items()):
        draw_panel(review, (20 + index * 395, 685), (370, 340), label, lane_road_crop(path))
    review.save(COMPARISON)


def main() -> None:
    frames = build_frames()
    sheet = build_sheet(frames)
    sheet.save(OUTPUT)
    save_metadata(frames)
    save_review_images(sheet)
    save_comparison_sheet(sheet)


if __name__ == "__main__":
    main()
