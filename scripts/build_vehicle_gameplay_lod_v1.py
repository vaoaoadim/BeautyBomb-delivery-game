from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "public" / "assets" / "game" / "vehicles"
MASTER_DIR = ROOT / "visual-references" / "gameplay-masters"
REVIEW_DIR = ROOT / "visual-references" / "reviews" / "vehicle-gameplay-lod-v1"
LOD_NAMES = ("near", "middle", "far")
FRAME_COUNT = 4


@dataclass(frozen=True)
class LodSpec:
    name: str
    canvas: tuple[int, int]
    visible_box: tuple[int, int, int, int]
    origin: tuple[float, float]
    collision: tuple[float, float, float, float]
    wheel_centers: tuple[tuple[float, float], tuple[float, float]]


@dataclass(frozen=True)
class VehicleSpec:
    asset_id: str
    slug: str
    source: Path
    approved_master: Path
    old_runtime: Path
    chroma: str
    frame_rate: int
    lods: tuple[LodSpec, LodSpec, LodSpec]


def lod(
    name: str,
    canvas: tuple[int, int],
    visible_box: tuple[int, int, int, int],
    origin: tuple[float, float],
    collision: tuple[float, float, float, float],
    wheel_x: tuple[float, float],
    wheel_y: float,
) -> LodSpec:
    left, top, right, bottom = visible_box
    width = right - left
    height = bottom - top
    centers = tuple(
        (left + width * x, top + height * wheel_y) for x in wheel_x
    )
    return LodSpec(name, canvas, visible_box, origin, collision, centers)  # type: ignore[arg-type]


VEHICLES = (
    VehicleSpec(
        "VEH-001",
        "veh-001-courier-waterbomb-brand",
        ROOT / "visual-references" / "veh-001-courier-waterbomb-brand-gameplay-lod-source-v1.png",
        ROOT / "visual-references" / "veh-001-courier-waterbomb-brand-concept-v6.png",
        PUBLIC_DIR / "veh-001-courier-waterbomb-brand-static-v4.png",
        "green",
        9,
        (
            lod("near", (138, 106), (4, 2, 134, 100), (69, 101), (20.2128, 54.4304, 97.5744, 37.6992), (0.20, 0.80), 0.90),
            lod("middle", (128, 98), (4, 2, 124, 93), (64, 93), (18.9088, 49.9584, 90.1824, 34.8432), (0.20, 0.80), 0.89),
            lod("far", (116, 90), (3, 2, 113, 85), (58, 85), (16.6048, 45.4864, 82.7904, 31.9872), (0.20, 0.80), 0.90),
        ),
    ),
    VehicleSpec(
        "OBS-001",
        "obs-001-pink-hatchback",
        ROOT / "visual-references" / "obs-001-pink-hatchback-gameplay-lod-source-v1.png",
        ROOT / "visual-references" / "obs-001-pink-hatchback-concept-v2.png",
        PUBLIC_DIR / "obs-001-pink-hatchback-static-v2.png",
        "green",
        7,
        (
            lod("near", (106, 74), (3, 18, 103, 69), (53, 69), (15.3008, 38.5344, 75.3984, 26.6112), (0.20, 0.80), 0.84),
            lod("middle", (98, 68), (3, 17, 95, 63), (49, 63), (14.1568, 34.8424, 69.6864, 24.5952), (0.20, 0.80), 0.83),
            lod("far", (90, 63), (2, 16, 87, 59), (45, 59), (13.0128, 33.1504, 63.9744, 22.5792), (0.20, 0.80), 0.84),
        ),
    ),
    VehicleSpec(
        "OBS-002",
        "obs-002-yellow-sedan",
        ROOT / "visual-references" / "obs-002-yellow-sedan-gameplay-lod-source-v1.png",
        ROOT / "visual-references" / "obs-002-yellow-sedan-concept-v2.png",
        PUBLIC_DIR / "obs-002-yellow-sedan-static-v2.png",
        "green",
        7,
        (
            lod("near", (120, 77), (2, 30, 117, 71), (60, 71), (17.8656, 43.5704, 84.2688, 23.2848), (0.20, 0.79), 0.85),
            lod("middle", (112, 71), (3, 28, 109, 66), (56, 66), (17.0576, 40.6484, 77.8848, 21.5208), (0.20, 0.79), 0.84),
            lod("far", (102, 65), (2, 25, 100, 60), (51, 60), (15.2496, 36.7264, 71.5008, 19.7568), (0.20, 0.79), 0.85),
        ),
    ),
    VehicleSpec(
        "OBS-003",
        "obs-003-green-wagon",
        ROOT / "visual-references" / "obs-003-green-wagon-gameplay-lod-source-v1.png",
        ROOT / "visual-references" / "obs-003-green-wagon-concept-v2.png",
        PUBLIC_DIR / "obs-003-green-wagon-static-v2.png",
        "magenta",
        7,
        (
            lod("near", (132, 90), (4, 35, 128, 84), (66, 84), (26.0832, 50.4456, 79.8336, 26.6112), (0.19, 0.77), 0.84),
            lod("middle", (122, 84), (3, 33, 118, 78), (61, 78), (24.1072, 46.9876, 73.7856, 24.5952), (0.19, 0.77), 0.83),
            lod("far", (112, 77), (3, 31, 109, 72), (56, 72), (22.1312, 43.5296, 67.7376, 22.5792), (0.19, 0.77), 0.84),
        ),
    ),
)


def is_chroma(pixel: tuple[int, int, int, int], mode: str) -> bool:
    red, green, blue, _alpha = pixel
    if mode == "magenta":
        return red > 80 and blue > 80 and red > green * 1.2 and blue > green * 1.2
    return green > 80 and green > red * 1.15 and green > blue * 1.15


def foreground_mask(image: Image.Image, mode: str) -> Image.Image:
    rgba = image.convert("RGBA")
    mask = Image.new("L", rgba.size)
    mask.putdata([0 if is_chroma(pixel, mode) else 255 for pixel in rgba.getdata()])
    return mask


def row_segments(mask: Image.Image) -> list[tuple[int, int]]:
    width, height = mask.size
    pixels = mask.load()
    counts = [sum(1 for x in range(width) if pixels[x, y] > 0) for y in range(height)]
    segments: list[tuple[int, int]] = []
    start: int | None = None
    for y, count in enumerate([*counts, 0]):
        if count > 5 and start is None:
            start = y
        elif count <= 5 and start is not None:
            if y - start > 5:
                segments.append((start, y))
            start = None
    if len(segments) != 3:
        raise RuntimeError(f"Expected three isolated LOD rows, found {segments}")
    return segments


def extract_source_lods(spec: VehicleSpec) -> dict[str, Image.Image]:
    source = Image.open(spec.source).convert("RGBA")
    mask = foreground_mask(source, spec.chroma)
    extracted: dict[str, Image.Image] = {}
    for lod_name, (top, bottom) in zip(LOD_NAMES, row_segments(mask), strict=True):
        row_mask = mask.crop((0, top, source.width, bottom))
        bounds = row_mask.getbbox()
        if bounds is None:
            raise RuntimeError(f"No foreground found for {spec.asset_id} {lod_name}")
        left, local_top, right, local_bottom = bounds
        box = (left, top + local_top, right, top + local_bottom)
        sprite = source.crop(box)
        sprite_mask = mask.crop(box)
        sprite.putalpha(sprite_mask.point(lambda alpha: 255 if alpha >= 128 else 0))
        extracted[lod_name] = sprite
    return extracted


def build_gameplay_master(source: Image.Image, spec: LodSpec) -> Image.Image:
    left, top, right, bottom = spec.visible_box
    target_size = (right - left, bottom - top)
    adapted = source.resize(target_size, Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", spec.canvas, (0, 0, 0, 0))
    canvas.alpha_composite(adapted, (left, top))
    return canvas


def wheel_phase_frame(master: Image.Image, lod_spec: LodSpec, phase: int) -> Image.Image:
    if phase == 0:
        return master.copy()
    frame = master.copy()
    draw = ImageDraw.Draw(frame)
    light = (255, 248, 214, 255)
    dark = (35, 30, 62, 255)
    patterns = {
        1: ((-1, -1, light), (1, 1, dark)),
        2: ((0, -1, light), (0, 1, dark)),
        3: ((1, -1, light), (-1, 1, dark)),
    }
    for center_x, center_y in lod_spec.wheel_centers:
        x = round(center_x)
        y = round(center_y)
        for offset_x, offset_y, color in patterns[phase]:
            draw.point((x + offset_x, y + offset_y), fill=color)
    return frame


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bounds(image: Image.Image) -> dict[str, int]:
    alpha_bounds = image.getchannel("A").getbbox()
    if alpha_bounds is None:
        return {"x": 0, "y": 0, "width": 0, "height": 0}
    left, top, right, bottom = alpha_bounds
    return {"x": left, "y": top, "width": right - left, "height": bottom - top}


def save_lod(spec: VehicleSpec, lod_spec: LodSpec, master: Image.Image) -> None:
    MASTER_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"{spec.slug}-gameplay-{lod_spec.name}-v1"
    master_path = MASTER_DIR / f"{stem}-pixel-master.png"
    static_path = PUBLIC_DIR / f"{stem}.png"
    drive_path = PUBLIC_DIR / f"{spec.slug}-gameplay-{lod_spec.name}-drive-v1.png"
    preview_path = REVIEW_DIR / f"{stem}-4x.png"
    metadata_path = PUBLIC_DIR / f"{stem}.json"

    master.save(master_path, optimize=False)
    shutil.copyfile(master_path, static_path)

    frames = [wheel_phase_frame(master, lod_spec, phase) for phase in range(FRAME_COUNT)]
    drive_sheet = Image.new(
        "RGBA", (lod_spec.canvas[0] * FRAME_COUNT, lod_spec.canvas[1]), (0, 0, 0, 0)
    )
    for frame_index, frame in enumerate(frames):
        drive_sheet.alpha_composite(frame, (frame_index * lod_spec.canvas[0], 0))
    drive_sheet.save(drive_path, optimize=False)
    master.resize(
        (master.width * 4, master.height * 4), Image.Resampling.NEAREST
    ).save(preview_path, optimize=False)

    frame_zero = drive_sheet.crop((0, 0, lod_spec.canvas[0], lod_spec.canvas[1]))
    if ImageChops.difference(master, frame_zero).getbbox() is not None:
        raise RuntimeError(f"Frame 0 differs from static gameplay master: {stem}")

    metadata = {
        "assetId": spec.asset_id,
        "version": "v1",
        "lod": lod_spec.name,
        "status": "integrated-gameplay-pixel-master",
        "texture": static_path.name,
        "driveTexture": drive_path.name,
        "canvas": {"width": lod_spec.canvas[0], "height": lod_spec.canvas[1]},
        "visibleBounds": bounds(master),
        "origin": {"pixelX": lod_spec.origin[0], "pixelY": lod_spec.origin[1]},
        "collision": {
            "x": lod_spec.collision[0],
            "y": lod_spec.collision[1],
            "width": lod_spec.collision[2],
            "height": lod_spec.collision[3],
            "includesRoofProduct": False if spec.asset_id == "VEH-001" else None,
        },
        "animation": {
            "frameWidth": lod_spec.canvas[0],
            "frameHeight": lod_spec.canvas[1],
            "frameCount": FRAME_COUNT,
            "frameRate": spec.frame_rate,
            "loop": True,
            "firstFrameMatchesStaticByteForByte": True,
            "motion": "wheel hub phase only; body, canvas, origin, baseline and collider remain fixed",
        },
        "production": {
            "approvedHighResolutionMaster": str(spec.approved_master.relative_to(ROOT)).replace("\\", "/"),
            "approvedHighResolutionMasterSha256": sha256(spec.approved_master),
            "independentLodSource": str(spec.source.relative_to(ROOT)).replace("\\", "/"),
            "independentLodSourceSha256": sha256(spec.source),
            "gameplayPixelMaster": str(master_path.relative_to(ROOT)).replace("\\", "/"),
            "gameplayPixelMasterSha256": sha256(master_path),
            "runtimeStaticSha256": sha256(static_path),
            "runtimeDriveSha256": sha256(drive_path),
            "buildScript": "scripts/build_vehicle_gameplay_lod_v1.py",
            "lodMethod": "independently authored near/middle/far source adaptations; each exported once to its own final pixel budget",
            "runtimeResizeCount": 0,
            "phaserScale": 1,
            "phaserTextureFilter": "nearest",
            "antialiasing": False,
            "subpixelPlacement": False,
        },
    }
    if metadata["collision"]["includesRoofProduct"] is None:
        del metadata["collision"]["includesRoofProduct"]
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


def fit_for_panel(image: Image.Image, size: tuple[int, int], resample: Image.Resampling) -> Image.Image:
    copy = image.convert("RGBA")
    copy.thumbnail(size, resample)
    return copy


def save_review_sheet(spec: VehicleSpec) -> None:
    panel_width = 300
    panel_height = 250
    sheet = Image.new("RGBA", (panel_width * 4, 54 + panel_height * 3), (24, 22, 48, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text((16, 16), f"{spec.asset_id} GAMEPLAY PIXEL LOD V1 / near, middle, far", fill=(255, 239, 92, 255))
    headings = ("HIGH-RES MASTER", "OLD IN-GAME ASSET", "NEW PIXEL MASTER 1x", "NEW PIXEL MASTER 4x NN")
    for column, heading in enumerate(headings):
        draw.text((column * panel_width + 12, 38), heading, fill=(248, 241, 223, 255))

    high_res = Image.open(spec.approved_master).convert("RGBA")
    old_runtime = Image.open(spec.old_runtime).convert("RGBA")
    for row, lod_spec in enumerate(spec.lods):
        y = 54 + row * panel_height
        draw.text((8, y + 6), lod_spec.name.upper(), fill=(255, 77, 145, 255))
        stem = f"{spec.slug}-gameplay-{lod_spec.name}-v1"
        master = Image.open(MASTER_DIR / f"{stem}-pixel-master.png").convert("RGBA")
        images = (
            fit_for_panel(high_res, (280, 205), Image.Resampling.LANCZOS),
            fit_for_panel(old_runtime, (280, 205), Image.Resampling.NEAREST),
            master,
            master.resize((master.width * 4, master.height * 4), Image.Resampling.NEAREST),
        )
        for column, image in enumerate(images):
            max_width, max_height = 280, 205
            if image.width > max_width or image.height > max_height:
                image = fit_for_panel(image, (max_width, max_height), Image.Resampling.NEAREST)
            x = column * panel_width + (panel_width - image.width) // 2
            image_y = y + 30 + (205 - image.height) // 2
            sheet.alpha_composite(image, (x, image_y))
    sheet.save(REVIEW_DIR / f"{spec.slug}-review-v1.png", optimize=False)


def main() -> None:
    for vehicle in VEHICLES:
        sources = extract_source_lods(vehicle)
        for lod_spec in vehicle.lods:
            master = build_gameplay_master(sources[lod_spec.name], lod_spec)
            save_lod(vehicle, lod_spec, master)
        save_review_sheet(vehicle)
        print(f"built {vehicle.asset_id}: {', '.join(lod.name for lod in vehicle.lods)}")


if __name__ == "__main__":
    main()
