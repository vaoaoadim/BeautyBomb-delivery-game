"""Build the corrected coherent v5 parallax from immutable approved masters."""

from __future__ import annotations

from collections import deque
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from build_environment_parallax_v4 import (
    build_cyclic_texture,
    file_hash,
    reconstruct_sky,
    representative_sky_rows,
    seam_mismatches,
    tile_preview,
    write_json,
)


CONTENT = Path("src/game/content/environmentParallax.json")
ARCHIVED_V4_CONTENT = Path("src/game/content/environmentParallax.v4.json")
RUNTIME_DIRECTORY = Path("public/assets/game/environment")
REVIEW_ALPHA = Path("visual-references/environment-parallax-v5-alpha-review.png")
REVIEW_COMPARISON = Path(
    "visual-references/environment-parallax-v5-before-after.png"
)
REVIEW_LOOP = Path("visual-references/environment-parallax-v5-loop-review.png")
REVIEW_MOTION = Path("visual-references/environment-parallax-v5-motion-review.png")
REVIEW_SEAM = Path("visual-references/environment-parallax-v5-seam-review.png")
CITY_MASTER_ID = "environment-coherent-v4"
ROAD_MASTER_ID = "environment-seamless-v3"


def boundary_connected_city_matte(
    source: Image.Image,
    *,
    max_channel_tolerance: int,
    euclidean_tolerance: int,
    anchor_min_y: int,
) -> tuple[Image.Image, Image.Image, dict[str, int]]:
    """Remove only boundary-connected sky, then retain the city anchor component.

    Sky-like pixels enclosed by architectural outlines are deliberately preserved:
    color alone never authorizes deletion. Detached pale cloud components are rejected
    because they do not reach the city anchor band.
    """

    rgb = source.convert("RGB")
    rgba = source.convert("RGBA")
    width, height = rgb.size
    pixels = rgb.load()
    sky_rows = representative_sky_rows(rgb)
    squared_limit = euclidean_tolerance * euclidean_tolerance
    sky_like = bytearray(width * height)

    for y in range(height):
        reference = sky_rows[y]
        for x in range(width):
            color = pixels[x, y]
            differences = tuple(abs(color[channel] - reference[channel]) for channel in range(3))
            if max(differences) <= max_channel_tolerance and sum(
                difference * difference for difference in differences
            ) <= squared_limit:
                sky_like[y * width + x] = 1

    boundary_sky = bytearray(width * height)
    queue: deque[tuple[int, int]] = deque()

    def seed(x: int, y: int) -> None:
        index = y * width + x
        if sky_like[index] and not boundary_sky[index]:
            boundary_sky[index] = 1
            queue.append((x, y))

    for x in range(width):
        seed(x, 0)
    for y in range(height):
        seed(0, y)
        seed(width - 1, y)

    while queue:
        x, y = queue.popleft()
        for next_x, next_y in (
            (x - 1, y),
            (x + 1, y),
            (x, y - 1),
            (x, y + 1),
        ):
            if 0 <= next_x < width and 0 <= next_y < height:
                index = next_y * width + next_x
                if sky_like[index] and not boundary_sky[index]:
                    boundary_sky[index] = 1
                    queue.append((next_x, next_y))

    component_seen = bytearray(width * height)
    matte = bytearray(width * height)
    retained_components = 0
    retained_pixels = 0
    discarded_components = 0
    discarded_pixels = 0

    for start in range(width * height):
        if boundary_sky[start] or component_seen[start]:
            continue
        component_seen[start] = 1
        stack = [start]
        component: list[int] = []
        maximum_y = 0
        while stack:
            index = stack.pop()
            component.append(index)
            y, x = divmod(index, width)
            maximum_y = max(maximum_y, y)
            for next_x, next_y in (
                (x - 1, y),
                (x + 1, y),
                (x, y - 1),
                (x, y + 1),
            ):
                if 0 <= next_x < width and 0 <= next_y < height:
                    next_index = next_y * width + next_x
                    if not boundary_sky[next_index] and not component_seen[next_index]:
                        component_seen[next_index] = 1
                        stack.append(next_index)

        if maximum_y >= anchor_min_y:
            retained_components += 1
            retained_pixels += len(component)
            for index in component:
                matte[index] = 255
        else:
            discarded_components += 1
            discarded_pixels += len(component)

    if retained_components != 1:
        raise RuntimeError(
            "The coherent city must resolve to exactly one anchor-connected component; "
            f"found {retained_components}."
        )

    mask = Image.frombytes("L", (width, height), bytes(matte))
    transparent = Image.new("RGBA", source.size, (0, 0, 0, 0))
    city = Image.composite(rgba, transparent, mask)
    return city, mask, {
        "boundaryConnectedSkyPixels": sum(boundary_sky),
        "retainedComponents": retained_components,
        "retainedPixels": retained_pixels,
        "discardedDetachedComponents": discarded_components,
        "discardedDetachedPixels": discarded_pixels,
    }


def render_content(
    master: Image.Image,
    spec: dict[str, Any],
    mask_profiles: dict[str, Any],
) -> tuple[Image.Image, Image.Image | None, dict[str, int] | None]:
    source = master.crop(tuple(spec["sourceBox"])).convert("RGBA")
    alpha_mode = spec["alphaMode"]
    matte = None
    matte_stats = None

    if alpha_mode == "reconstructed-sky":
        source = reconstruct_sky(source)
    elif alpha_mode == "boundary-connected-city":
        source, matte, matte_stats = boundary_connected_city_matte(
            source,
            max_channel_tolerance=mask_profiles["skyToleranceMaxChannel"],
            euclidean_tolerance=mask_profiles["skyToleranceEuclidean"],
            anchor_min_y=mask_profiles["cityAnchorMinY"],
        )
    elif alpha_mode != "opaque-source-crop":
        raise ValueError(f"Unknown alpha mode: {alpha_mode}")

    size = spec["contentCanvas"]
    output_size = (size["width"], size["height"])
    content = source.resize(output_size, Image.Resampling.NEAREST)
    if matte is not None:
        matte = matte.resize(output_size, Image.Resampling.NEAREST)
    return content, matte, matte_stats


def checkerboard(size: tuple[int, int], tile: int = 16) -> Image.Image:
    image = Image.new("RGBA", size, (46, 45, 66, 255))
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], tile):
        for x in range(0, size[0], tile):
            if (x // tile + y // tile) % 2:
                draw.rectangle(
                    (x, y, min(size[0] - 1, x + tile - 1), min(size[1] - 1, y + tile - 1)),
                    fill=(91, 89, 112, 255),
                )
    return image


def write_alpha_review(
    old_city: Image.Image,
    new_city: Image.Image,
    matte: Image.Image,
) -> None:
    panel_size = (1024, 256)
    review = Image.new("RGBA", (1024, 768), (29, 29, 27, 255))
    old_panel = checkerboard(panel_size)
    old_panel.alpha_composite(old_city.resize(panel_size, Image.Resampling.NEAREST))
    mask_panel = matte.convert("RGBA").resize(panel_size, Image.Resampling.NEAREST)
    new_panel = checkerboard(panel_size)
    new_panel.alpha_composite(new_city.resize(panel_size, Image.Resampling.NEAREST))
    review.alpha_composite(old_panel, (0, 0))
    review.alpha_composite(mask_panel, (0, 256))
    review.alpha_composite(new_panel, (0, 512))
    review.save(REVIEW_ALPHA, optimize=True)


def composite_frame(
    rendered: list[tuple[dict[str, Any], Image.Image]],
    route: dict[str, Any],
    seconds: float,
) -> Image.Image:
    frame = Image.new("RGBA", (360, 640), (82, 203, 238, 255))
    for spec, texture in rendered:
        display_speed = route["baseDisplaySpeedPxPerSecond"] * spec["speedMultiplier"]
        frame.alpha_composite(
            tile_preview(texture, spec, display_speed * seconds),
            (spec["position"]["x"], spec["position"]["y"]),
        )
    return frame


def write_motion_review(
    rendered: list[tuple[dict[str, Any], Image.Image]],
    route: dict[str, Any],
) -> None:
    moments = (0.0, 6.0, 12.0, 18.0)
    review = Image.new("RGBA", (360 * len(moments), 640), (29, 29, 27, 255))
    for index, seconds in enumerate(moments):
        review.alpha_composite(composite_frame(rendered, route, seconds), (index * 360, 0))
    review.save(REVIEW_MOTION, optimize=True)


def write_seam_review(
    rendered: list[tuple[dict[str, Any], Image.Image]],
    route: dict[str, Any],
) -> None:
    city_spec = next(spec for spec, _texture in rendered if spec["assetId"] == "ENV-004")
    city_speed = route["baseDisplaySpeedPxPerSecond"] * city_spec["speedMultiplier"]
    city_period = city_spec["textureCanvas"]["width"] * city_spec["tileScale"]["x"]
    seam_seconds = city_period / city_speed
    review = Image.new("RGBA", (720, 640), (29, 29, 27, 255))
    review.alpha_composite(composite_frame(rendered, route, seam_seconds - 0.04), (0, 0))
    review.alpha_composite(composite_frame(rendered, route, seam_seconds + 0.04), (360, 0))
    review.save(REVIEW_SEAM, optimize=True)


def write_before_after(
    rendered: list[tuple[dict[str, Any], Image.Image]],
    route: dict[str, Any],
) -> None:
    archived = json.loads(ARCHIVED_V4_CONTENT.read_text(encoding="utf-8"))
    old_rendered = [
        (
            spec,
            Image.open(RUNTIME_DIRECTORY / f"{spec['runtimeName']}.png").convert("RGBA"),
        )
        for spec in archived["layers"]
    ]
    comparison = Image.new("RGBA", (720, 640), (29, 29, 27, 255))
    comparison.alpha_composite(composite_frame(old_rendered, archived["route"], 12.0), (0, 0))
    comparison.alpha_composite(composite_frame(rendered, route, 12.0), (360, 0))
    comparison.save(REVIEW_COMPARISON, optimize=True)


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
    review.save(REVIEW_LOOP, optimize=True)


def main() -> None:
    content = json.loads(CONTENT.read_text(encoding="utf-8"))
    if content["version"] != "v5":
        raise RuntimeError("The v5 builder requires the active v5 content contract")

    masters = {
        master["id"]: {"path": Path(master["path"]), "sha256": master["sha256"]}
        for master in content["masters"]
    }
    source_images: dict[str, Image.Image] = {}
    for master_id, master in masters.items():
        if file_hash(master["path"]) != master["sha256"]:
            raise RuntimeError(
                f"Approved environment master {master_id} changed. "
                "Create a new versioned master and decision before export."
            )
        with Image.open(master["path"]) as source:
            source_images[master_id] = source.convert("RGBA")

    RUNTIME_DIRECTORY.mkdir(parents=True, exist_ok=True)
    rendered: list[tuple[dict[str, Any], Image.Image]] = []
    route = content["route"]
    city_matte = None
    city_content = None
    city_stats = None

    for spec in content["layers"]:
        master_id = spec["masterId"]
        layer_content, matte, matte_stats = render_content(
            source_images[master_id], spec, content["maskProfiles"]
        )
        texture = build_cyclic_texture(layer_content, spec)
        seams = seam_mismatches(texture, layer_content.height)
        if seams["cycleWrap"]:
            raise RuntimeError(f"{spec['assetId']} has a non-zero cyclic seam: {seams}")

        runtime_path = RUNTIME_DIRECTORY / f"{spec['runtimeName']}.png"
        metadata_path = runtime_path.with_suffix(".json")
        texture.save(runtime_path, optimize=True)
        tile_scale = spec["tileScale"]
        display_speed = route["baseDisplaySpeedPxPerSecond"] * spec["speedMultiplier"]
        display_period = spec["textureCanvas"]["width"] * tile_scale["x"]
        is_city = spec["alphaMode"] == "boundary-connected-city"
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
                    "script": "scripts/build_environment_parallax_v5.py",
                    "contentSource": CONTENT.as_posix(),
                    "approvedMaster": masters[master_id]["path"].as_posix(),
                    "approvedMasterSha256": masters[master_id]["sha256"],
                    "sourceBox": spec["sourceBox"],
                    "alphaExtraction": spec["alphaMode"],
                    "maskMethod": (
                        "boundary-connected adaptive sky flood; inverse anchor-connected city matte"
                        if is_city
                        else "not applicable to this layer"
                    ),
                    "maskStats": matte_stats,
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
                    "cityComposition": "unified-skyline-to-sidewalk" if is_city else None,
                    "colorDeletion": "boundary-connected only; enclosed cyan is preserved" if is_city else None,
                    "detachedCloudsRetained": False if is_city else None,
                    "review": REVIEW_ALPHA.as_posix(),
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
        if is_city:
            city_matte = matte
            city_content = layer_content
            city_stats = matte_stats
        rendered.append((spec, texture))
        print(
            f"{spec['assetId']}: {texture.width}x{texture.height}, "
            f"period={display_period:.2f}px, speed={display_speed:.2f}px/s"
        )

    if city_matte is None or city_content is None or city_stats is None:
        raise RuntimeError("The active layer set has no corrected coherent city")

    old_city = Image.open(RUNTIME_DIRECTORY / "env-004-coherent-city-v4.png").convert("RGBA")
    write_alpha_review(old_city, city_content, city_matte)
    write_before_after(rendered, route)
    write_motion_review(rendered, route)
    write_seam_review(rendered, route)
    write_loop_review(rendered)
    print(f"cityMask={city_stats}")
    print(f"alphaReview={REVIEW_ALPHA}")
    print(f"comparison={REVIEW_COMPARISON}")
    print(f"motionReview={REVIEW_MOTION}")
    print(f"seamReview={REVIEW_SEAM}")
    print(f"loopReview={REVIEW_LOOP}")


if __name__ == "__main__":
    main()
