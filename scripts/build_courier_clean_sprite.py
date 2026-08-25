from collections import deque
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "visual-references/veh-001-courier-clean-tube-concept-v5.png"
OUTPUT = ROOT / "public/assets/game/vehicles/veh-001-courier-master-static-v3.png"
METADATA = ROOT / "public/assets/game/vehicles/veh-001-courier-master-static-v3.json"
PREVIEW = ROOT / "visual-references/veh-001-courier-master-static-v3-preview-4x.png"
GUIDE = ROOT / "visual-references/veh-001-courier-master-static-v3-guide-4x.png"
COMPARISON = ROOT / "visual-references/veh-001-courier-master-static-v3-comparison.png"
OLD_RUNTIME = ROOT / "public/assets/game/vehicles/veh-001-courier-clean-static-v2.png"
LANE_SCREENSHOTS = {
    "FAR LANE": ROOT / "visual-references/veh-001-courier-master-static-v3-in-game-far.png",
    "MIDDLE LANE": ROOT / "visual-references/veh-001-courier-master-static-v3-in-game-middle.png",
    "NEAR LANE": ROOT / "visual-references/veh-001-courier-master-static-v3-in-game-near.png",
}

CANVAS_SIZE = (208, 160)
CONTENT_MAX_SIZE = (200, 143)
CONTENT_BASELINE_Y = 152
PREVIEW_SCALE = 4
COLLISION = {"x": 16, "y": 76, "width": 176, "height": 68}
ORIGIN = {"x": 104, "y": 152}


def is_background_candidate(red: int, green: int, blue: int) -> bool:
    """Match the connected pale-lilac studio background, not enclosed white parts."""
    return min(red, green, blue) >= 168 and max(red, green, blue) - min(red, green, blue) <= 68


def extract_foreground(source: Image.Image) -> Image.Image:
    rgba = source.convert("RGBA")
    width, height = rgba.size
    pixels = rgba.load()
    background = bytearray(width * height)
    queue: deque[tuple[int, int]] = deque()

    def enqueue_if_background(x: int, y: int) -> None:
        index = y * width + x
        if background[index]:
            return
        red, green, blue, _alpha = pixels[x, y]
        if not is_background_candidate(red, green, blue):
            return
        background[index] = 1
        queue.append((x, y))

    for x in range(width):
        enqueue_if_background(x, 0)
        enqueue_if_background(x, height - 1)
    for y in range(height):
        enqueue_if_background(0, y)
        enqueue_if_background(width - 1, y)

    while queue:
        x, y = queue.popleft()
        if x > 0:
            enqueue_if_background(x - 1, y)
        if x + 1 < width:
            enqueue_if_background(x + 1, y)
        if y > 0:
            enqueue_if_background(x, y - 1)
        if y + 1 < height:
            enqueue_if_background(x, y + 1)

    mask = Image.new("L", rgba.size, 255)
    mask_pixels = mask.load()
    for y in range(height):
        row_offset = y * width
        for x in range(width):
            if background[row_offset + x]:
                mask_pixels[x, y] = 0

    # Keep only the largest connected foreground component so isolated background
    # compression specks cannot become runtime pixels.
    visited = bytearray(width * height)
    largest_component: list[tuple[int, int]] = []
    for y in range(height):
        for x in range(width):
            index = y * width + x
            if visited[index] or mask_pixels[x, y] == 0:
                continue
            component: list[tuple[int, int]] = []
            component_queue = deque([(x, y)])
            visited[index] = 1
            while component_queue:
                current_x, current_y = component_queue.popleft()
                component.append((current_x, current_y))
                for next_x, next_y in (
                    (current_x - 1, current_y),
                    (current_x + 1, current_y),
                    (current_x, current_y - 1),
                    (current_x, current_y + 1),
                ):
                    if not (0 <= next_x < width and 0 <= next_y < height):
                        continue
                    next_index = next_y * width + next_x
                    if visited[next_index] or mask_pixels[next_x, next_y] == 0:
                        continue
                    visited[next_index] = 1
                    component_queue.append((next_x, next_y))
            if len(component) > len(largest_component):
                largest_component = component

    clean_mask = Image.new("L", rgba.size, 0)
    clean_pixels = clean_mask.load()
    for x, y in largest_component:
        clean_pixels[x, y] = 255

    rgba.putalpha(clean_mask)
    bounds = clean_mask.getbbox()
    if bounds is None:
        raise ValueError("Master foreground could not be extracted")
    return rgba.crop(bounds)


def export_runtime() -> Image.Image:
    foreground = extract_foreground(Image.open(MASTER))
    source_width, source_height = foreground.size
    scale = min(
        CONTENT_MAX_SIZE[0] / source_width,
        CONTENT_MAX_SIZE[1] / source_height,
    )
    target_size = (
        max(1, round(source_width * scale)),
        max(1, round(source_height * scale)),
    )

    # Exactly one resize from approved master to production texture.
    resized = foreground.resize(target_size, Image.Resampling.NEAREST)
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_metadata(runtime: Image.Image) -> None:
    left, top, right, bottom = visible_bounds(runtime)
    visible_colors = len(
        {
            (red, green, blue)
            for red, green, blue, alpha in runtime.get_flattened_data()
            if alpha > 0
        }
    )
    metadata = {
        "id": "VEH-001",
        "version": 3,
        "texture": OUTPUT.name,
        "canvas": {"width": runtime.width, "height": runtime.height},
        "visibleBounds": {
            "x": left,
            "y": top,
            "width": right - left,
            "height": bottom - top,
        },
        "runtimeScale": 0.5,
        "origin": {
            "normalizedX": ORIGIN["x"] / runtime.width,
            "normalizedY": ORIGIN["y"] / runtime.height,
            "pixelX": ORIGIN["x"],
            "pixelY": ORIGIN["y"],
        },
        "collision": {
            **COLLISION,
            "includesRoofProduct": False,
        },
        "production": {
            "designMaster": str(MASTER.relative_to(ROOT)).replace("\\", "/"),
            "designMasterSha256": sha256(MASTER),
            "shapeReference": "visual-references/beautybomb-water-bomb-reference.png",
            "buildScript": "scripts/build_courier_clean_sprite.py",
            "exportMethod": "connected-background extraction plus one production resize",
            "assetMode": "high-detail-pixel-style-raster",
            "offlineResizeCount": 1,
            "resizeFilter": "nearest-neighbor",
            "paletteQuantization": False,
            "visibleColors": visible_colors,
            "phaserTextureFilter": "nearest",
            "laneTextureScales": [0.56, 0.61, 0.66],
            "runtimeSha256": sha256(OUTPUT),
            "animationFrames": 1,
            "status": "master-derived-static-review-candidate",
        },
    }
    METADATA.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def save_review_images(runtime: Image.Image) -> None:
    preview_size = (
        runtime.width * PREVIEW_SCALE,
        runtime.height * PREVIEW_SCALE,
    )
    preview = runtime.resize(preview_size, Image.Resampling.NEAREST)
    preview.save(PREVIEW)

    guide = preview.copy()
    guide_draw = ImageDraw.Draw(guide)
    collision = (
        COLLISION["x"],
        COLLISION["y"],
        COLLISION["x"] + COLLISION["width"] - 1,
        COLLISION["y"] + COLLISION["height"] - 1,
    )
    guide_draw.rectangle(
        tuple(value * PREVIEW_SCALE for value in collision),
        outline=(255, 77, 145, 255),
        width=2,
    )
    origin_x = ORIGIN["x"] * PREVIEW_SCALE
    origin_y = ORIGIN["y"] * PREVIEW_SCALE
    guide_draw.line(
        (origin_x - 8, origin_y, origin_x + 8, origin_y),
        fill=(216, 243, 74, 255),
        width=2,
    )
    guide_draw.line(
        (origin_x, origin_y - 8, origin_x, origin_y + 8),
        fill=(216, 243, 74, 255),
        width=2,
    )
    guide.save(GUIDE)


def checkerboard(size: tuple[int, int], cell: int = 8) -> Image.Image:
    image = Image.new("RGBA", size, (239, 240, 247, 255))
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2:
                draw.rectangle(
                    (
                        x,
                        y,
                        min(x + cell - 1, size[0] - 1),
                        min(y + cell - 1, size[1] - 1),
                    ),
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
    draw.rectangle(
        (x, y, x + width - 1, y + height - 1),
        fill=(29, 29, 48, 255),
    )
    draw.text((x + 10, y + 8), title, fill=(255, 255, 255, 255))
    body = fit_image(content, (width - 20, height - 40), resample)
    sheet.alpha_composite(body, (x + 10, y + 30))


def normalised_silhouette(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    alpha = image.convert("RGBA").getchannel("A")
    bounds = alpha.getbbox()
    if bounds is None:
        raise ValueError("Cannot compare an empty silhouette")
    cropped = alpha.crop(bounds)
    scale = min(size[0] / cropped.width, size[1] / cropped.height)
    resized = cropped.resize(
        (
            max(1, round(cropped.width * scale)),
            max(1, round(cropped.height * scale)),
        ),
        Image.Resampling.NEAREST,
    )
    canvas = Image.new("L", size, 0)
    canvas.paste(
        resized,
        ((size[0] - resized.width) // 2, size[1] - resized.height),
    )
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
    return screenshot.crop(
        (
            canvas_left,
            canvas_top + 282,
            canvas_left + 360,
            canvas_top + 522,
        )
    )


def save_comparison_sheet(runtime: Image.Image) -> None:
    if not OLD_RUNTIME.exists() or not all(
        path.exists() for path in LANE_SCREENSHOTS.values()
    ):
        return

    master_foreground = extract_foreground(Image.open(MASTER))
    old_runtime = Image.open(OLD_RUNTIME).convert("RGBA")
    sheet = Image.new("RGBA", (1200, 1050), (20, 20, 43, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text(
        (20, 14),
        "VEH-001 MASTER-DERIVED PIPELINE / STATIC V3",
        fill=(255, 239, 92, 255),
    )

    panels = (
        ((20, 45), "MASTER V5 / FOREGROUND", master_foreground),
        ((415, 45), "REJECTED 104x80 REDRAW", old_runtime),
        ((810, 45), "NEW 208x160 RUNTIME", runtime),
    )
    for position, title, content in panels:
        draw_panel(
            sheet,
            position,
            (370, 300),
            title,
            content,
            Image.Resampling.LANCZOS if content is master_foreground else Image.Resampling.NEAREST,
        )

    nearest_preview = runtime.resize(
        (runtime.width * 3, runtime.height * 3),
        Image.Resampling.NEAREST,
    )
    draw_panel(
        sheet,
        (20, 365),
        (570, 300),
        "NEW RUNTIME / NEAREST PREVIEW",
        nearest_preview,
    )
    draw_panel(
        sheet,
        (610, 365),
        (570, 300),
        "NORMALISED SILHOUETTE: CYAN MASTER / PINK RUNTIME",
        silhouette_overlay(master_foreground, runtime),
    )

    for index, (label, path) in enumerate(LANE_SCREENSHOTS.items()):
        draw_panel(
            sheet,
            (20 + index * 395, 685),
            (370, 340),
            label,
            lane_road_crop(path),
        )

    sheet.save(COMPARISON)


def main() -> None:
    runtime = export_runtime()
    runtime.save(OUTPUT)
    save_metadata(runtime)
    save_review_images(runtime)
    save_comparison_sheet(runtime)


if __name__ == "__main__":
    main()
