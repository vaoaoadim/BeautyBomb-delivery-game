"""Build the simplified coherent v4 parallax from approved masters."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageOps


CONTENT = Path("src/game/content/environmentParallax.v4.json")
RUNTIME_DIRECTORY = Path("public/assets/game/environment")
REVIEW_COMPARISON = Path(
    "visual-references/environment-parallax-v4-master-runtime-comparison.png"
)
REVIEW_LOOP = Path("visual-references/environment-parallax-v4-loop-review.png")
REVIEW_MASKS = Path("visual-references/environment-parallax-v4-mask-review.png")
REVIEW_MOTION = Path("visual-references/environment-parallax-v4-motion-review.png")
CITY_MASTER_ID = "environment-coherent-v4"
ROAD_MASTER_ID = "environment-seamless-v3"


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def is_power_of_two(value: int) -> bool:
    return value > 0 and value & (value - 1) == 0


def circular_median(values: list[int], radius: int) -> list[int]:
    size = len(values)
    result: list[int] = []
    for index in range(size):
        window = sorted(values[(index + offset) % size] for offset in range(-radius, radius + 1))
        result.append(window[len(window) // 2])
    return result


def detect_boundary(image: Image.Image, profile: dict[str, Any]) -> list[int]:
    """Trace one continuous polygon boundary from local geometry, never pixel deletion."""

    source = image.convert("RGB")
    pixels = source.load()
    search_start, search_end = profile["searchY"]
    target_y = profile["targetY"]
    target_penalty = profile["targetPenalty"]
    dark_bias = profile["darkBias"]
    maximum_brightness = profile["maximumBrightness"]
    raw: list[int] = []

    for x in range(source.width):
        best_y = target_y
        best_score = float("-inf")
        for y in range(search_start, search_end):
            current = pixels[x, y]
            above = pixels[x, max(0, y - 4)]
            brightness = sum(current) / 3
            if brightness > maximum_brightness:
                continue
            vertical_edge = sum(
                abs(current[channel] - above[channel]) for channel in range(3)
            )
            darkness = max(0.0, 100.0 - brightness) * dark_bias
            score = vertical_edge + darkness - abs(y - target_y) * target_penalty
            if score > best_score:
                best_score = score
                best_y = y
        raw.append(best_y)

    return circular_median(raw, profile["medianRadius"])


def representative_sky_rows(source: Image.Image) -> list[tuple[int, int, int, int]]:
    """Reconstruct only the neutral sky field from colors sampled in the approved master."""

    rgb = source.convert("RGB")
    pixels = rgb.load()
    rows: list[tuple[int, int, int, int]] = []
    previous = (82, 203, 238, 255)
    sampling_end = min(225, rgb.height)

    for y in range(rgb.height):
        if y < sampling_end:
            candidates = [
                pixels[x, y]
                for x in range(rgb.width)
                if 60 <= pixels[x, y][0] <= 115
                and 184 <= pixels[x, y][1] <= 222
                and 218 <= pixels[x, y][2] <= 252
            ]
            if candidates:
                channels = [sorted(color[channel] for color in candidates) for channel in range(3)]
                middle = len(candidates) // 2
                previous = (
                    channels[0][middle],
                    channels[1][middle],
                    channels[2][middle],
                    255,
                )
        rows.append(previous)
    return rows


def cloud_components(source: Image.Image) -> list[list[tuple[int, int]]]:
    """Select large pale cloud shapes; tiny window highlights are deliberately rejected."""

    rgb = source.convert("RGB")
    pixels = rgb.load()
    limit_y = min(195, rgb.height)
    eligible = bytearray(rgb.width * limit_y)
    for y in range(limit_y):
        for x in range(rgb.width):
            red, green, blue = pixels[x, y]
            if red > 185 and green > 190 and blue > 170:
                eligible[y * rgb.width + x] = 1

    seen = bytearray(len(eligible))
    components: list[list[tuple[int, int]]] = []
    for y in range(limit_y):
        for x in range(rgb.width):
            start = y * rgb.width + x
            if not eligible[start] or seen[start]:
                continue
            stack = [(x, y)]
            seen[start] = 1
            component: list[tuple[int, int]] = []
            min_x = max_x = x
            min_y = max_y = y
            while stack:
                current_x, current_y = stack.pop()
                component.append((current_x, current_y))
                min_x = min(min_x, current_x)
                max_x = max(max_x, current_x)
                min_y = min(min_y, current_y)
                max_y = max(max_y, current_y)
                for next_x, next_y in (
                    (current_x - 1, current_y),
                    (current_x + 1, current_y),
                    (current_x, current_y - 1),
                    (current_x, current_y + 1),
                ):
                    if 0 <= next_x < rgb.width and 0 <= next_y < limit_y:
                        index = next_y * rgb.width + next_x
                        if eligible[index] and not seen[index]:
                            seen[index] = 1
                            stack.append((next_x, next_y))
            if (
                len(component) >= 24
                and max_x - min_x + 1 >= 8
                and max_y - min_y + 1 >= 4
            ):
                components.append(component)
    return components


def reconstruct_sky(source: Image.Image) -> Image.Image:
    sky = Image.new("RGBA", source.size)
    draw = ImageDraw.Draw(sky)
    for y, color in enumerate(representative_sky_rows(source)):
        draw.line((0, y, source.width - 1, y), fill=color)

    source_rgba = source.convert("RGBA")
    source_pixels = source_rgba.load()
    sky_pixels = sky.load()
    for component in cloud_components(source):
        for x, y in component:
            sky_pixels[x, y] = source_pixels[x, y]
    return sky


def polygon_layer(
    source: Image.Image,
    top: list[int],
    city_bottom: int,
) -> Image.Image:
    if len(top) != source.width:
        raise ValueError("Polygon profiles must match the approved master width")

    mask = Image.new("L", source.size, 0)
    draw = ImageDraw.Draw(mask)
    for x in range(source.width):
        start_y = max(0, min(city_bottom, top[x]))
        if city_bottom > start_y:
            draw.line((x, start_y, x, city_bottom - 1), fill=255)

    visible = source.convert("RGBA")
    transparent = Image.new("RGBA", source.size, (0, 0, 0, 0))
    return Image.composite(visible, transparent, mask)


def render_content(
    master: Image.Image,
    spec: dict[str, Any],
    boundaries: dict[str, list[int]],
    mask_profiles: dict[str, Any],
) -> Image.Image:
    source_box = tuple(spec["sourceBox"])
    source = master.crop(source_box).convert("RGBA")
    alpha_mode = spec["alphaMode"]
    city_bottom = mask_profiles["cityBottomSourceY"]

    if alpha_mode == "reconstructed-sky":
        source = reconstruct_sky(source)
    elif alpha_mode == "polygon-city":
        source = polygon_layer(source, boundaries["farTop"], city_bottom)
    elif alpha_mode != "opaque-source-crop":
        raise ValueError(f"Unknown alpha mode: {alpha_mode}")

    size = spec["contentCanvas"]
    return source.resize((size["width"], size["height"]), Image.Resampling.NEAREST)


def close_periodic_edge(texture: Image.Image) -> None:
    texture.paste(
        texture.crop((0, 0, 1, texture.height)),
        (texture.width - 1, 0),
    )


def build_cyclic_texture(content: Image.Image, spec: dict[str, Any]) -> Image.Image:
    canvas = spec["textureCanvas"]
    width = canvas["width"]
    height = canvas["height"]
    if not is_power_of_two(width) or not is_power_of_two(height):
        raise ValueError(f"{spec['assetId']} requires a POT texture canvas")
    if content.height > height:
        raise ValueError(f"{spec['assetId']} content does not fit its texture canvas")

    cycle_mode = spec["cycleMode"]
    gutter = spec["seamGutterTexturePx"]
    if cycle_mode == "direct-approved-loop":
        if gutter != 0 or content.size != (width, height):
            raise ValueError(f"{spec['assetId']} direct loop must fill its POT canvas")
        texture = content.copy()
        close_periodic_edge(texture)
        return texture

    if cycle_mode != "safe-gutter-direct-panorama":
        raise ValueError(f"Unknown cycle mode: {cycle_mode}")
    if gutter <= 0 or content.width + gutter * 2 != width:
        raise ValueError(f"{spec['assetId']} has an invalid neutral gutter contract")

    texture = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    neutral = content.crop((0, 0, gutter, content.height))
    texture.alpha_composite(neutral, (0, 0))
    texture.alpha_composite(content, (gutter, 0))
    texture.alpha_composite(ImageOps.mirror(neutral), (gutter + content.width, 0))
    close_periodic_edge(texture)
    return texture


def seam_mismatches(texture: Image.Image, content_height: int) -> dict[str, int]:
    pixels = texture.load()
    return {
        "cycleWrap": sum(
            pixels[texture.width - 1, y] != pixels[0, y]
            for y in range(content_height)
        )
    }


def tile_preview(
    texture: Image.Image,
    spec: dict[str, Any],
    display_offset_px: float = 0,
) -> Image.Image:
    scale = spec["tileScale"]
    display = texture.resize(
        (
            round(texture.width * scale["x"]),
            round(texture.height * scale["y"]),
        ),
        Image.Resampling.NEAREST,
    )
    tiled = Image.new("RGBA", (360, display.height), (0, 0, 0, 0))
    x = -(round(display_offset_px) % display.width)
    while x < tiled.width:
        tiled.alpha_composite(display, (x, 0))
        x += display.width
    return tiled


def write_comparison(
    city_master: Image.Image,
    road_master: Image.Image,
    rendered: list[tuple[dict[str, Any], Image.Image]],
) -> None:
    runtime = Image.new("RGBA", (360, 640), (82, 203, 238, 255))
    for spec, texture in rendered:
        runtime.alpha_composite(
            tile_preview(texture, spec),
            (spec["position"]["x"], spec["position"]["y"]),
        )

    reference = Image.new("RGBA", (360, 640), (82, 203, 238, 255))
    city = city_master.crop((0, 0, city_master.width, 512)).resize(
        (round(city_master.width * 0.36), 282),
        Image.Resampling.NEAREST,
    )
    road = road_master.crop((0, 540, 1774, 887)).resize(
        (630, 240),
        Image.Resampling.NEAREST,
    )
    reference.alpha_composite(city.crop((0, 0, 360, 282)), (0, 0))
    reference.alpha_composite(road.crop((0, 0, 360, 240)), (0, 282))

    comparison = Image.new("RGBA", (720, 640), (29, 29, 27, 255))
    comparison.alpha_composite(reference, (0, 0))
    comparison.alpha_composite(runtime, (360, 0))
    comparison.save(REVIEW_COMPARISON)


def write_motion_review(
    rendered: list[tuple[dict[str, Any], Image.Image]],
    route: dict[str, Any],
) -> None:
    moments = (0.0, 6.0, 12.0, 18.0)
    review = Image.new("RGBA", (360 * len(moments), 640), (29, 29, 27, 255))
    for index, seconds in enumerate(moments):
        frame = Image.new("RGBA", (360, 640), (82, 203, 238, 255))
        for spec, texture in rendered:
            display_speed = (
                route["baseDisplaySpeedPxPerSecond"] * spec["speedMultiplier"]
            )
            frame.alpha_composite(
                tile_preview(texture, spec, display_speed * seconds),
                (spec["position"]["x"], spec["position"]["y"]),
            )
        review.alpha_composite(frame, (index * 360, 0))
    review.save(REVIEW_MOTION)


def write_loop_review(rendered: list[tuple[dict[str, Any], Image.Image]]) -> None:
    gutter = 12
    width = max(texture.width * 2 for _spec, texture in rendered)
    height = sum(texture.height + gutter for _spec, texture in rendered) - gutter
    review = Image.new("RGBA", (width, height), (29, 29, 47, 255))
    y = 0
    for _spec, texture in rendered:
        review.alpha_composite(texture, (0, y))
        review.alpha_composite(texture, (texture.width, y))
        y += texture.height + gutter
    review.save(REVIEW_LOOP)


def write_mask_review(master: Image.Image, boundaries: dict[str, list[int]]) -> None:
    city = master.crop((0, 0, master.width, 512)).convert("RGB")
    draw = ImageDraw.Draw(city)
    for name, profile in boundaries.items():
        draw.line(
            [(x, profile[x]) for x in range(city.width)],
            fill=(255, 255, 255),
            width=3,
        )
    city.resize((1086, 256), Image.Resampling.NEAREST).save(REVIEW_MASKS)


def main() -> None:
    content = json.loads(CONTENT.read_text(encoding="utf-8"))
    masters = {
        master["id"]: {
            "path": Path(master["path"]),
            "sha256": master["sha256"],
        }
        for master in content["masters"]
    }
    source_images: dict[str, Image.Image] = {}
    for master_id, master in masters.items():
        if file_hash(master["path"]) != master["sha256"]:
            raise RuntimeError(
                f"Approved environment master {master_id} changed. Create a new versioned master and decision before export."
            )
        with Image.open(master["path"]) as source:
            source_images[master_id] = source.convert("RGBA")

    coherent_master = source_images[CITY_MASTER_ID]
    city_source = coherent_master.crop((0, 0, coherent_master.width, 512))
    mask_profiles = content["maskProfiles"]
    boundaries = {
        "farTop": detect_boundary(city_source, mask_profiles["farTop"]),
    }

    RUNTIME_DIRECTORY.mkdir(parents=True, exist_ok=True)
    rendered: list[tuple[dict[str, Any], Image.Image]] = []
    route = content["route"]
    for spec in content["layers"]:
        master_id = spec["masterId"]
        layer_content = render_content(
            source_images[master_id],
            spec,
            boundaries,
            mask_profiles,
        )
        texture = build_cyclic_texture(layer_content, spec)
        seams = seam_mismatches(texture, layer_content.height)
        if seams["cycleWrap"]:
            raise RuntimeError(f"{spec['assetId']} has a non-zero cyclic seam: {seams}")

        runtime_path = RUNTIME_DIRECTORY / f"{spec['runtimeName']}.png"
        metadata_path = RUNTIME_DIRECTORY / f"{spec['runtimeName']}.json"
        texture.save(runtime_path, optimize=True)
        tile_scale = spec["tileScale"]
        display_speed = route["baseDisplaySpeedPxPerSecond"] * spec["speedMultiplier"]
        display_period = spec["textureCanvas"]["width"] * tile_scale["x"]
        write_json(
            metadata_path,
            {
                "assetId": spec["assetId"],
                "version": content["version"],
                "status": "integrated",
                "runtime": {
                    "path": runtime_path.as_posix(),
                    "textureCanvas": spec["textureCanvas"],
                    "contentRect": {
                        "x": spec["seamGutterTexturePx"],
                        "y": 0,
                        "width": layer_content.width,
                        "height": layer_content.height,
                    },
                    "loopPeriodTexturePx": texture.width,
                    "displayPeriodPx": display_period,
                    "sha256": file_hash(runtime_path),
                },
                "production": {
                    "script": "scripts/build_environment_parallax_v4.py",
                    "contentSource": CONTENT.as_posix(),
                    "approvedMaster": masters[master_id]["path"].as_posix(),
                    "approvedMasterSha256": masters[master_id]["sha256"],
                    "sourceBox": spec["sourceBox"],
                    "alphaExtraction": spec["alphaMode"],
                    "maskMethod": (
                        "single continuous city silhouette; no independently scrolling city masks"
                        if spec["alphaMode"] == "polygon-city"
                        else "not applicable to this layer"
                    ),
                    "offlineResizeCount": 1,
                    "resizeFilter": "nearest-neighbor",
                    "paletteQuantization": "none",
                    "phaserTextureFilter": "nearest",
                    "cyclicConstruction": spec["cycleMode"],
                },
                "maskContract": {
                    "sharedSourceCoordinates": master_id == CITY_MASTER_ID,
                    "segmentOrder": ["A", "B", "C"],
                    "segmentSourceWidthPx": 724 if master_id == CITY_MASTER_ID else None,
                    "cityComposition": (
                        "unified-skyline-to-sidewalk"
                        if spec["alphaMode"] == "polygon-city"
                        else None
                    ),
                    "review": REVIEW_MASKS.as_posix(),
                },
                "seamContract": {
                    "mode": spec["cycleMode"],
                    "safeGutterTexturePx": spec["seamGutterTexturePx"],
                    "edgeMismatchRows": seams,
                    "review": REVIEW_LOOP.as_posix(),
                },
                "runtimePlacement": {
                    "textureKey": spec["textureKey"],
                    "layer": spec["layer"],
                    "position": spec["position"],
                    "tileScale": tile_scale,
                    "displaySpeedPxPerSecond": display_speed,
                    "textureScrollPixelsPerSecond": display_speed / tile_scale["x"],
                    "fullCycleSeconds": display_period / display_speed,
                    "depth": spec["depth"],
                    "mode": route["mode"],
                    "reducedMotion": spec["reducedMotion"],
                },
            },
        )
        rendered.append((spec, texture))
        print(
            f"{spec['assetId']}: {texture.width}x{texture.height}, "
            f"period={display_period:.2f}px, speed={display_speed:.2f}px/s"
        )

    write_comparison(coherent_master, source_images[ROAD_MASTER_ID], rendered)
    write_motion_review(rendered, route)
    write_loop_review(rendered)
    write_mask_review(coherent_master, boundaries)
    print(f"comparison={REVIEW_COMPARISON}")
    print(f"loopReview={REVIEW_LOOP}")
    print(f"maskReview={REVIEW_MASKS}")
    print(f"motionReview={REVIEW_MOTION}")


if __name__ == "__main__":
    main()
