import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
PREVIEW_SCALE = 4
ALPHA_THRESHOLD = 16
LANE_SCALES = (1.12, 1.22, 1.32)
IN_GAME_SCREENSHOTS = {
    "PINK / MIDDLE LANE": ROOT
    / "visual-references/obstacle-vehicles-static-v2-in-game-pink-middle.png",
    "YELLOW / FAR LANE": ROOT
    / "visual-references/obstacle-vehicles-static-v2-in-game-yellow-far.png",
    "GREEN / NEAR LANE": ROOT
    / "visual-references/obstacle-vehicles-static-v2-in-game-green-near.png",
}
COMPARISON = ROOT / "visual-references/obstacle-vehicles-static-v2-comparison.png"


@dataclass(frozen=True)
class ObstacleSpec:
    asset_id: str
    kind: str
    canvas: tuple[int, int]
    content_max_size: tuple[int, int]
    baseline_y: int
    origin: tuple[int, int]
    collision: dict[str, int]
    visual_scale_multiplier: float
    master: Path
    output: Path
    metadata: Path
    prior_runtime: Path
    preview: Path
    guide: Path


def vehicle_paths(slug: str) -> tuple[Path, Path, Path, Path]:
    base = ROOT / "public/assets/game/vehicles"
    references = ROOT / "visual-references"
    return (
        base / f"{slug}-static-v2.png",
        base / f"{slug}-static-v2.json",
        references / f"{slug}-static-v2-preview-4x.png",
        references / f"{slug}-static-v2-guide-4x.png",
    )


pink_output, pink_metadata, pink_preview, pink_guide = vehicle_paths(
    "obs-001-pink-hatchback"
)
yellow_output, yellow_metadata, yellow_preview, yellow_guide = vehicle_paths(
    "obs-002-yellow-sedan"
)
green_output, green_metadata, green_preview, green_guide = vehicle_paths(
    "obs-003-green-wagon"
)

SPECS = (
    ObstacleSpec(
        asset_id="OBS-001",
        kind="pink-hatchback",
        canvas=(80, 56),
        content_max_size=(76, 38),
        baseline_y=52,
        origin=(40, 52),
        collision={"x": 6, "y": 27, "width": 68, "height": 24},
        visual_scale_multiplier=1.0,
        master=ROOT / "visual-references/obs-001-pink-hatchback-concept-v2.png",
        output=pink_output,
        metadata=pink_metadata,
        prior_runtime=ROOT
        / "public/assets/game/vehicles/obs-001-pink-hatchback-static-v1.png",
        preview=pink_preview,
        guide=pink_guide,
    ),
    ObstacleSpec(
        asset_id="OBS-002",
        kind="yellow-sedan",
        canvas=(88, 56),
        content_max_size=(84, 34),
        baseline_y=52,
        origin=(44, 52),
        collision={"x": 6, "y": 30, "width": 76, "height": 21},
        visual_scale_multiplier=1.04,
        master=ROOT / "visual-references/obs-002-yellow-sedan-concept-v2.png",
        output=yellow_output,
        metadata=yellow_metadata,
        prior_runtime=ROOT
        / "public/assets/game/vehicles/obs-002-yellow-sedan-static-v1.png",
        preview=yellow_preview,
        guide=yellow_guide,
    ),
    ObstacleSpec(
        asset_id="OBS-003",
        kind="green-wagon",
        canvas=(84, 58),
        content_max_size=(80, 32),
        baseline_y=54,
        origin=(42, 54),
        collision={"x": 6, "y": 29, "width": 72, "height": 24},
        visual_scale_multiplier=1.18,
        master=ROOT / "visual-references/obs-003-green-wagon-concept-v2.png",
        output=green_output,
        metadata=green_metadata,
        prior_runtime=ROOT
        / "public/assets/game/vehicles/obs-003-green-wagon-static-v1.png",
        preview=green_preview,
        guide=green_guide,
    ),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def foreground(master: Image.Image) -> Image.Image:
    """Remove only near-transparent source noise and crop transparent padding."""
    rgba = master.convert("RGBA")
    alpha = rgba.getchannel("A").point(
        lambda value: 0 if value < ALPHA_THRESHOLD else value
    )
    bounds = alpha.getbbox()
    if bounds is None:
        raise ValueError("Master has no visible foreground")
    rgba.putalpha(alpha)
    return rgba.crop(bounds)


def export_runtime(spec: ObstacleSpec) -> Image.Image:
    return render_foreground(spec, foreground(Image.open(spec.master)))


def render_foreground(spec: ObstacleSpec, source: Image.Image) -> Image.Image:
    """Export one fixed-canvas runtime frame from an approved master frame."""
    scale = min(
        spec.content_max_size[0] / source.width,
        spec.content_max_size[1] / source.height,
    )
    target_size = (
        max(1, round(source.width * scale)),
        max(1, round(source.height * scale)),
    )

    # The only production resize: immutable approved master -> native runtime texture.
    resized = source.resize(target_size, Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", spec.canvas, (0, 0, 0, 0))
    offset_x = (spec.canvas[0] - target_size[0]) // 2
    offset_y = spec.baseline_y - target_size[1]
    canvas.alpha_composite(resized, (offset_x, offset_y))
    return canvas


def visible_bounds(image: Image.Image) -> tuple[int, int, int, int]:
    bounds = image.getchannel("A").getbbox()
    if bounds is None:
        raise ValueError("Runtime export has no visible pixels")
    return bounds


def checkerboard(size: tuple[int, int], cell: int = 8) -> Image.Image:
    image = Image.new("RGBA", size, (239, 240, 247, 255))
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2:
                draw.rectangle(
                    (x, y, min(x + cell - 1, size[0] - 1), min(y + cell - 1, size[1] - 1)),
                    fill=(214, 216, 229, 255),
                )
    return image


def fit_image(
    image: Image.Image,
    size: tuple[int, int],
    resample: Image.Resampling,
) -> Image.Image:
    source = image.convert("RGBA")
    scale = min(size[0] / source.width, size[1] / source.height)
    fitted_size = (
        max(1, round(source.width * scale)),
        max(1, round(source.height * scale)),
    )
    fitted = source.resize(fitted_size, resample)
    canvas = checkerboard(size)
    canvas.alpha_composite(
        fitted,
        ((size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2),
    )
    return canvas


def draw_panel(
    sheet: Image.Image,
    position: tuple[int, int],
    size: tuple[int, int],
    title: str,
    content: Image.Image,
    resample: Image.Resampling = Image.Resampling.NEAREST,
) -> None:
    x, y = position
    width, height = size
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((x, y, x + width - 1, y + height - 1), fill=(29, 29, 48, 255))
    draw.text((x + 10, y + 8), title, fill=(255, 255, 255, 255))
    sheet.alpha_composite(
        fit_image(content, (width - 20, height - 40), resample),
        (x + 10, y + 30),
    )


def save_preview_and_guide(spec: ObstacleSpec, runtime: Image.Image) -> None:
    preview = runtime.resize(
        (runtime.width * PREVIEW_SCALE, runtime.height * PREVIEW_SCALE),
        Image.Resampling.NEAREST,
    )
    preview.save(spec.preview)

    guide = preview.copy()
    draw = ImageDraw.Draw(guide)
    collision = (
        spec.collision["x"] * PREVIEW_SCALE,
        spec.collision["y"] * PREVIEW_SCALE,
        (spec.collision["x"] + spec.collision["width"] - 1) * PREVIEW_SCALE,
        (spec.collision["y"] + spec.collision["height"] - 1) * PREVIEW_SCALE,
    )
    draw.rectangle(collision, outline=(255, 77, 145, 255), width=2)
    origin_x = spec.origin[0] * PREVIEW_SCALE
    origin_y = spec.origin[1] * PREVIEW_SCALE
    draw.line((origin_x - 8, origin_y, origin_x + 8, origin_y), fill=(216, 243, 74, 255), width=2)
    draw.line((origin_x, origin_y - 8, origin_x, origin_y + 8), fill=(216, 243, 74, 255), width=2)
    guide.save(spec.guide)


def save_metadata(spec: ObstacleSpec, runtime: Image.Image) -> None:
    left, top, right, bottom = visible_bounds(runtime)
    metadata = {
        "id": spec.asset_id,
        "version": 2,
        "kind": spec.kind,
        "texture": spec.output.name,
        "canvas": {"width": runtime.width, "height": runtime.height},
        "visibleBounds": {"x": left, "y": top, "width": right - left, "height": bottom - top},
        "origin": {
            "normalizedX": spec.origin[0] / runtime.width,
            "normalizedY": spec.origin[1] / runtime.height,
            "pixelX": spec.origin[0],
            "pixelY": spec.origin[1],
        },
        "collision": spec.collision,
        "production": {
            "designMaster": str(spec.master.relative_to(ROOT)).replace("\\", "/"),
            "designMasterSha256": sha256(spec.master),
            "sourceGeneration": str(
                spec.master.with_name(f"{spec.master.stem}-source.png").relative_to(ROOT)
            ).replace("\\", "/"),
            "buildScript": "scripts/build_obstacle_static_v2.py",
            "exportMethod": "alpha-noise threshold plus alpha-bounds crop and one production resize",
            "assetMode": "high-detail-pixel-style-raster",
            "alphaNoiseThreshold": ALPHA_THRESHOLD,
            "offlineResizeCount": 1,
            "resizeFilter": "nearest-neighbor",
            "paletteQuantization": False,
            "visibleColors": len(
                {(red, green, blue) for red, green, blue, alpha in runtime.get_flattened_data() if alpha > 0}
            ),
            "phaserTextureFilter": "nearest",
            "laneVisualScales": list(LANE_SCALES),
            "visualScaleMultiplier": spec.visual_scale_multiplier,
            "collisionToVisualRatio": 0.84 / spec.visual_scale_multiplier,
            "runtimeSha256": sha256(spec.output),
            "animationFrames": 1,
            "status": "approved-static-master",
        },
    }
    spec.metadata.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def lane_road_crop(path: Path) -> Image.Image:
    screenshot = Image.open(path).convert("RGBA")
    canvas_left = (screenshot.width - 360) // 2
    canvas_top = (screenshot.height - 640) // 2
    return screenshot.crop((canvas_left, canvas_top + 282, canvas_left + 360, canvas_top + 522))


def save_comparison_sheet(runtimes: dict[str, Image.Image]) -> None:
    sheet = Image.new("RGBA", (1600, 1235), (20, 20, 43, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text((20, 14), "OBSTACLE STATIC V2 / APPROVED MASTERS", fill=(255, 239, 92, 255))
    panel_width, panel_height = 292, 250
    panel_x = (20, 336, 652, 968, 1284)

    for row, spec in enumerate(SPECS):
        y = 48 + row * 270
        runtime = runtimes[spec.asset_id]
        master = foreground(Image.open(spec.master))
        preview = Image.open(spec.preview).convert("RGBA")
        guide = Image.open(spec.guide).convert("RGBA")
        panels = (
            (f"{spec.asset_id} / MASTER V2", master, Image.Resampling.LANCZOS),
            ("PRIOR V1 RUNTIME", Image.open(spec.prior_runtime), Image.Resampling.NEAREST),
            ("NEW V2 RUNTIME", runtime, Image.Resampling.NEAREST),
            ("V2 / NEAREST PREVIEW", preview, Image.Resampling.NEAREST),
            ("V2 / COLLISION + ORIGIN", guide, Image.Resampling.NEAREST),
        )
        for x, (title, content, resample) in zip(panel_x, panels, strict=True):
            draw_panel(sheet, (x, y), (panel_width, panel_height), title, content, resample)

    if all(path.exists() for path in IN_GAME_SCREENSHOTS.values()):
        for index, (label, path) in enumerate(IN_GAME_SCREENSHOTS.items()):
            draw_panel(
                sheet,
                (20 + index * 520, 870),
                (500, 340),
                f"PHASER REVIEW / {label}",
                lane_road_crop(path),
            )
    else:
        draw.text(
            (20, 890),
            "Awaiting individual Phaser lane screenshots after static V2 integration.",
            fill=(255, 255, 255, 255),
        )
    sheet.save(COMPARISON)


def main() -> None:
    runtimes: dict[str, Image.Image] = {}
    for spec in SPECS:
        runtime = export_runtime(spec)
        runtime.save(spec.output)
        save_metadata(spec, runtime)
        save_preview_and_guide(spec, runtime)
        runtimes[spec.asset_id] = runtime
        print(f"{spec.asset_id}: visible bounds {visible_bounds(runtime)}")
    save_comparison_sheet(runtimes)


if __name__ == "__main__":
    main()
