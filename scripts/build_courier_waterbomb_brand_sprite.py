import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "visual-references/veh-001-courier-waterbomb-brand-concept-v6.png"
OUTPUT = ROOT / "public/assets/game/vehicles/veh-001-courier-waterbomb-brand-static-v4.png"
METADATA = ROOT / "public/assets/game/vehicles/veh-001-courier-waterbomb-brand-static-v4.json"
PREVIEW = ROOT / "visual-references/veh-001-courier-waterbomb-brand-static-v4-preview-4x.png"
GUIDE = ROOT / "visual-references/veh-001-courier-waterbomb-brand-static-v4-guide-4x.png"
COMPARISON = ROOT / "visual-references/veh-001-courier-waterbomb-brand-static-v4-comparison.png"
OLD_RUNTIME = ROOT / "public/assets/game/vehicles/veh-001-courier-master-static-v3.png"
LANE_SCREENSHOTS = {
    "FAR LANE": ROOT / "visual-references/veh-001-courier-waterbomb-brand-static-v4-in-game-far.png",
    "MIDDLE LANE": ROOT / "visual-references/veh-001-courier-waterbomb-brand-static-v4-in-game-middle.png",
    "NEAR LANE": ROOT / "visual-references/veh-001-courier-waterbomb-brand-static-v4-in-game-near.png",
}

CANVAS_SIZE = (208, 160)
CONTENT_MAX_SIZE = (200, 149)
CONTENT_BASELINE_Y = 152
PREVIEW_SCALE = 4
COLLISION = {"x": 16, "y": 76, "width": 176, "height": 68}
ORIGIN = {"x": 104, "y": 152}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def foreground(master: Image.Image) -> Image.Image:
    """Crop only transparent padding; the alpha-master is otherwise immutable."""
    rgba = master.convert("RGBA")
    bounds = rgba.getchannel("A").getbbox()
    if bounds is None:
        raise ValueError("Master has no visible foreground")
    return rgba.crop(bounds)


def export_runtime() -> Image.Image:
    return render_foreground(foreground(Image.open(MASTER)))


def render_foreground(source: Image.Image) -> Image.Image:
    """Export one fixed-canvas runtime frame from a high-resolution master frame."""
    scale = min(
        CONTENT_MAX_SIZE[0] / source.width,
        CONTENT_MAX_SIZE[1] / source.height,
    )
    target_size = (
        max(1, round(source.width * scale)),
        max(1, round(source.height * scale)),
    )

    # The only production resize: immutable alpha-master -> native runtime texture.
    resized = source.resize(target_size, Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    offset_x = (CANVAS_SIZE[0] - target_size[0]) // 2
    offset_y = CONTENT_BASELINE_Y - target_size[1]
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


def normalised_silhouette(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    alpha = image.convert("RGBA").getchannel("A")
    bounds = alpha.getbbox()
    if bounds is None:
        raise ValueError("Cannot compare an empty silhouette")
    cropped = alpha.crop(bounds)
    scale = min(size[0] / cropped.width, size[1] / cropped.height)
    resized = cropped.resize(
        (max(1, round(cropped.width * scale)), max(1, round(cropped.height * scale))),
        Image.Resampling.NEAREST,
    )
    canvas = Image.new("L", size, 0)
    canvas.paste(resized, ((size[0] - resized.width) // 2, size[1] - resized.height))
    return canvas


def silhouette_overlay(master: Image.Image, runtime: Image.Image) -> Image.Image:
    size = (550, 260)
    master_mask = normalised_silhouette(master, size)
    runtime_mask = normalised_silhouette(runtime, size)
    overlay = checkerboard(size)
    overlay_pixels = overlay.load()
    master_pixels = master_mask.load()
    runtime_pixels = runtime_mask.load()
    for y in range(size[1]):
        for x in range(size[0]):
            in_master = master_pixels[x, y] > 0
            in_runtime = runtime_pixels[x, y] > 0
            if in_master and in_runtime:
                overlay_pixels[x, y] = (255, 255, 255, 255)
            elif in_master:
                overlay_pixels[x, y] = (0, 205, 233, 255)
            elif in_runtime:
                overlay_pixels[x, y] = (255, 79, 171, 255)
    return overlay


def lane_road_crop(path: Path) -> Image.Image:
    screenshot = Image.open(path).convert("RGBA")
    canvas_left = (screenshot.width - 360) // 2
    canvas_top = (screenshot.height - 640) // 2
    return screenshot.crop((canvas_left, canvas_top + 282, canvas_left + 360, canvas_top + 522))


def save_review_images(runtime: Image.Image) -> None:
    preview = runtime.resize(
        (runtime.width * PREVIEW_SCALE, runtime.height * PREVIEW_SCALE),
        Image.Resampling.NEAREST,
    )
    preview.save(PREVIEW)

    guide = preview.copy()
    draw = ImageDraw.Draw(guide)
    collision = (
        COLLISION["x"] * PREVIEW_SCALE,
        COLLISION["y"] * PREVIEW_SCALE,
        (COLLISION["x"] + COLLISION["width"] - 1) * PREVIEW_SCALE,
        (COLLISION["y"] + COLLISION["height"] - 1) * PREVIEW_SCALE,
    )
    draw.rectangle(collision, outline=(255, 77, 145, 255), width=2)
    origin_x = ORIGIN["x"] * PREVIEW_SCALE
    origin_y = ORIGIN["y"] * PREVIEW_SCALE
    draw.line((origin_x - 8, origin_y, origin_x + 8, origin_y), fill=(216, 243, 74, 255), width=2)
    draw.line((origin_x, origin_y - 8, origin_x, origin_y + 8), fill=(216, 243, 74, 255), width=2)
    guide.save(GUIDE)


def save_metadata(runtime: Image.Image) -> None:
    left, top, right, bottom = visible_bounds(runtime)
    metadata = {
        "id": "VEH-001",
        "version": 4,
        "texture": OUTPUT.name,
        "canvas": {"width": runtime.width, "height": runtime.height},
        "visibleBounds": {"x": left, "y": top, "width": right - left, "height": bottom - top},
        "runtimeScale": 0.5,
        "origin": {
            "normalizedX": ORIGIN["x"] / runtime.width,
            "normalizedY": ORIGIN["y"] / runtime.height,
            "pixelX": ORIGIN["x"],
            "pixelY": ORIGIN["y"],
        },
        "collision": {**COLLISION, "includesRoofProduct": False},
        "production": {
            "designMaster": str(MASTER.relative_to(ROOT)).replace("\\", "/"),
            "designMasterSha256": sha256(MASTER),
            "shapeReference": "visual-references/beautybomb-water-bomb-reference.png",
            "buildScript": "scripts/build_courier_waterbomb_brand_sprite.py",
            "exportMethod": "alpha-bounds crop plus one production resize",
            "assetMode": "high-detail-pixel-style-raster",
            "offlineResizeCount": 1,
            "resizeFilter": "nearest-neighbor",
            "paletteQuantization": False,
            "visibleColors": len({(red, green, blue) for red, green, blue, alpha in runtime.get_flattened_data() if alpha > 0}),
            "phaserTextureFilter": "nearest",
            "laneTextureScales": [0.56, 0.61, 0.66],
            "runtimeSha256": sha256(OUTPUT),
            "animationFrames": 1,
            "status": "approved-static-master",
        },
    }
    METADATA.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def save_comparison_sheet(runtime: Image.Image) -> None:
    if not OLD_RUNTIME.exists() or not all(path.exists() for path in LANE_SCREENSHOTS.values()):
        return

    master_foreground = foreground(Image.open(MASTER))
    old_runtime = Image.open(OLD_RUNTIME).convert("RGBA")
    sheet = Image.new("RGBA", (1200, 1050), (20, 20, 43, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text((20, 14), "VEH-001 WATERBOMB BRAND / STATIC V4", fill=(255, 239, 92, 255))

    for position, title, content, resample in (
        ((20, 45), "MASTER V6 / ALPHA FOREGROUND", master_foreground, Image.Resampling.LANCZOS),
        ((415, 45), "PRIOR V3 RUNTIME", old_runtime, Image.Resampling.NEAREST),
        ((810, 45), "NEW 208x160 RUNTIME", runtime, Image.Resampling.NEAREST),
    ):
        draw_panel(sheet, position, (370, 300), title, content, resample)

    draw_panel(
        sheet,
        (20, 365),
        (570, 300),
        "NEW RUNTIME / NEAREST PREVIEW",
        runtime.resize((runtime.width * 3, runtime.height * 3), Image.Resampling.NEAREST),
    )
    draw_panel(
        sheet,
        (610, 365),
        (570, 300),
        "NORMALISED SILHOUETTE: CYAN MASTER / PINK RUNTIME",
        silhouette_overlay(master_foreground, runtime),
    )

    for index, (label, path) in enumerate(LANE_SCREENSHOTS.items()):
        draw_panel(sheet, (20 + index * 395, 685), (370, 340), label, lane_road_crop(path))
    sheet.save(COMPARISON)


def main() -> None:
    runtime = export_runtime()
    runtime.save(OUTPUT)
    save_metadata(runtime)
    save_review_images(runtime)
    save_comparison_sheet(runtime)


if __name__ == "__main__":
    main()
