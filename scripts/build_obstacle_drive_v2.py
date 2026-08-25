import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

from build_obstacle_static_v2 import (
    ROOT,
    SPECS as STATIC_SPECS,
    checkerboard,
    draw_panel,
    fit_image,
    foreground,
    render_foreground,
    sha256,
    visible_bounds,
)


FRAME_COUNT = 4
FRAME_RATE = 7
PREVIEW_SCALE = 4
COMPARISON = ROOT / "visual-references/obstacle-vehicles-drive-v2-comparison.png"
IN_GAME_SCREENSHOT = ROOT / "visual-references/obstacle-vehicles-drive-v2-in-game.png"


@dataclass(frozen=True)
class DriveSpec:
    asset_id: str
    kind: str
    master: Path
    static_output: Path
    output: Path
    metadata: Path
    preview: Path
    hub_boxes: tuple[tuple[int, int, int, int], tuple[int, int, int, int]]


def drive_paths(slug: str) -> tuple[Path, Path, Path]:
    runtime = ROOT / "public/assets/game/vehicles"
    references = ROOT / "visual-references"
    return (
        runtime / f"{slug}-drive-v2.png",
        runtime / f"{slug}-drive-v2.json",
        references / f"{slug}-drive-v2-preview-4x.png",
    )


pink_output, pink_metadata, pink_preview = drive_paths("obs-001-pink-hatchback")
yellow_output, yellow_metadata, yellow_preview = drive_paths("obs-002-yellow-sedan")
green_output, green_metadata, green_preview = drive_paths("obs-003-green-wagon")

SPECS = (
    DriveSpec(
        asset_id="OBS-001",
        kind="pink-hatchback",
        master=ROOT / "visual-references/obs-001-pink-hatchback-concept-v2.png",
        static_output=ROOT / "public/assets/game/vehicles/obs-001-pink-hatchback-static-v2.png",
        output=pink_output,
        metadata=pink_metadata,
        preview=pink_preview,
        hub_boxes=((178, 441, 284, 548), (930, 441, 1036, 548)),
    ),
    DriveSpec(
        asset_id="OBS-002",
        kind="yellow-sedan",
        master=ROOT / "visual-references/obs-002-yellow-sedan-concept-v2.png",
        static_output=ROOT / "public/assets/game/vehicles/obs-002-yellow-sedan-static-v2.png",
        output=yellow_output,
        metadata=yellow_metadata,
        preview=yellow_preview,
        hub_boxes=((216, 324, 348, 459), (1044, 324, 1176, 459)),
    ),
    DriveSpec(
        asset_id="OBS-003",
        kind="green-wagon",
        master=ROOT / "visual-references/obs-003-green-wagon-concept-v2.png",
        static_output=ROOT / "public/assets/game/vehicles/obs-003-green-wagon-static-v2.png",
        output=green_output,
        metadata=green_metadata,
        preview=green_preview,
        hub_boxes=((199, 369, 309, 478), (1017, 369, 1127, 478)),
    ),
)


def static_spec(kind: str):
    return next(spec for spec in STATIC_SPECS if spec.kind == kind)


def square_box(box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    left, top, right, bottom = box
    size = max(right - left, bottom - top)
    center_x = (left + right) // 2
    center_y = (top + bottom) // 2
    return (
        center_x - size // 2,
        center_y - size // 2,
        center_x - size // 2 + size,
        center_y - size // 2 + size,
    )


def rotate_hub(
    frame: Image.Image,
    source: Image.Image,
    box: tuple[int, int, int, int],
    rotation: Image.Transpose,
) -> None:
    left, top, right, bottom = square_box(box)
    if left < 0 or top < 0 or right > source.width or bottom > source.height:
        raise ValueError(f"Hub box {box} exceeds master frame bounds {source.size}")
    patch = source.crop((left, top, right, bottom))
    frame.paste((0, 0, 0, 0), (left, top, right, bottom))
    frame.alpha_composite(patch.transpose(rotation), (left, top))


def high_resolution_frames(spec: DriveSpec) -> list[Image.Image]:
    source = foreground(Image.open(spec.master))
    rotations = (
        None,
        Image.Transpose.ROTATE_270,
        Image.Transpose.ROTATE_180,
        Image.Transpose.ROTATE_90,
    )
    frames: list[Image.Image] = []
    for rotation in rotations:
        if rotation is None:
            frames.append(source.copy())
            continue
        frame = source.copy()
        for hub_box in spec.hub_boxes:
            rotate_hub(frame, source, hub_box, rotation)
        frames.append(frame)
    return frames


def build_runtime_frames(spec: DriveSpec) -> list[Image.Image]:
    static = static_spec(spec.kind)
    frames = [render_foreground(static, frame) for frame in high_resolution_frames(spec)]
    approved_static = Image.open(spec.static_output).convert("RGBA")
    if frames[0].tobytes() != approved_static.tobytes():
        raise ValueError(f"{spec.asset_id} frame zero does not match its approved static runtime")
    bounds = [visible_bounds(frame) for frame in frames]
    if any(bound != bounds[0] for bound in bounds[1:]):
        raise ValueError(f"{spec.asset_id} drive frames changed visible bounds: {bounds}")
    return frames


def save_metadata(spec: DriveSpec, frames: list[Image.Image]) -> None:
    static = static_spec(spec.kind)
    sheet = Image.open(spec.output).convert("RGBA")
    metadata = {
        "id": spec.asset_id,
        "version": 2,
        "kind": spec.kind,
        "texture": spec.output.name,
        "frame": {
            "width": static.canvas[0],
            "height": static.canvas[1],
            "count": FRAME_COUNT,
        },
        "frameVisibleBounds": [
            {
                "x": left,
                "y": top,
                "width": right - left,
                "height": bottom - top,
            }
            for left, top, right, bottom in map(visible_bounds, frames)
        ],
        "origin": {
            "normalizedX": static.origin[0] / static.canvas[0],
            "normalizedY": static.origin[1] / static.canvas[1],
            "pixelX": static.origin[0],
            "pixelY": static.origin[1],
        },
        "collision": static.collision,
        "animation": {
            "frameRate": FRAME_RATE,
            "loop": True,
            "firstFrameMatchesApprovedStatic": True,
            "motion": "hub rotation only; body and wheel baseline remain stable",
        },
        "production": {
            "designMaster": str(spec.master.relative_to(ROOT)).replace("\\", "/"),
            "designMasterSha256": sha256(spec.master),
            "approvedStaticTexture": spec.static_output.name,
            "approvedStaticRuntimeSha256": sha256(spec.static_output),
            "staticRuntimeUsage": "approval anchor only; not an export input",
            "buildScript": "scripts/build_obstacle_drive_v2.py",
            "exportMethod": "high-resolution hub rotation plus one production resize per frame",
            "assetMode": "high-detail-pixel-style-raster",
            "offlineResizeCountPerFrame": 1,
            "resizeFilter": "nearest-neighbor",
            "paletteQuantization": False,
            "phaserTextureFilter": "nearest",
            "laneVisualScales": [1.12, 1.22, 1.32],
            "visualScaleMultiplier": static.visual_scale_multiplier,
            "collisionToVisualRatio": 0.84 / static.visual_scale_multiplier,
            "runtimeSha256": sha256(spec.output),
            "status": "approved-drive-cycle",
        },
    }
    spec.metadata.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def save_preview(spec: DriveSpec, sheet: Image.Image) -> None:
    sheet.resize(
        (sheet.width * PREVIEW_SCALE, sheet.height * PREVIEW_SCALE),
        Image.Resampling.NEAREST,
    ).save(spec.preview)


def frame_zero_diff(static: Image.Image, frame_zero: Image.Image) -> Image.Image:
    return ImageChops.difference(static, frame_zero)


def lane_road_crop(path: Path) -> Image.Image:
    screenshot = Image.open(path).convert("RGBA")
    canvas_left = (screenshot.width - 360) // 2
    canvas_top = (screenshot.height - 640) // 2
    return screenshot.crop((canvas_left, canvas_top + 282, canvas_left + 360, canvas_top + 522))


def save_comparison_sheet(results: dict[str, tuple[list[Image.Image], Image.Image]]) -> None:
    sheet = Image.new("RGBA", (1600, 1280), (20, 20, 43, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text((20, 14), "OBSTACLE DRIVE V2 / DERIVED REVIEW CANDIDATES", fill=(255, 239, 92, 255))
    panel_width, panel_height = 292, 270
    panel_x = (20, 336, 652, 968, 1284)

    for row, spec in enumerate(SPECS):
        y = 48 + row * 290
        frames, runtime_sheet = results[spec.asset_id]
        static = Image.open(spec.static_output).convert("RGBA")
        master = foreground(Image.open(spec.master))
        preview = Image.open(spec.preview).convert("RGBA")
        panels = (
            (f"{spec.asset_id} / APPROVED MASTER", master, Image.Resampling.LANCZOS),
            ("STATIC V2 / FRAME 0", static, Image.Resampling.NEAREST),
            ("FOUR-FRAME DRIVE SHEET", runtime_sheet, Image.Resampling.NEAREST),
            ("SHEET / NEAREST PREVIEW", preview, Image.Resampling.NEAREST),
            ("FRAME 0 STATIC PIXEL DIFF: 0", frame_zero_diff(static, frames[0]), Image.Resampling.NEAREST),
        )
        for x, (title, content, resample) in zip(panel_x, panels, strict=True):
            draw_panel(sheet, (x, y), (panel_width, panel_height), title, content, resample)
    if IN_GAME_SCREENSHOT.exists():
        draw_panel(
            sheet,
            (20, 920),
            (1560, 340),
            "PHASER REVIEW / DRIVE SHEETS ACTIVE",
            lane_road_crop(IN_GAME_SCREENSHOT),
        )
    sheet.save(COMPARISON)


def main() -> None:
    results: dict[str, tuple[list[Image.Image], Image.Image]] = {}
    for spec in SPECS:
        frames = build_runtime_frames(spec)
        static = static_spec(spec.kind)
        runtime_sheet = Image.new(
            "RGBA", (static.canvas[0] * FRAME_COUNT, static.canvas[1]), (0, 0, 0, 0)
        )
        for index, frame in enumerate(frames):
            runtime_sheet.alpha_composite(frame, (index * static.canvas[0], 0))
        runtime_sheet.save(spec.output)
        save_preview(spec, runtime_sheet)
        save_metadata(spec, frames)
        results[spec.asset_id] = (frames, runtime_sheet)
        print(f"{spec.asset_id}: frame bounds {[visible_bounds(frame) for frame in frames]}")
    save_comparison_sheet(results)


if __name__ == "__main__":
    main()
