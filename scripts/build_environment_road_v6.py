"""Build only ENV-006 with white top and bottom curbs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image

from build_environment_parallax_v4 import (
    build_cyclic_texture,
    file_hash,
    seam_mismatches,
    tile_preview,
    write_json,
)


CONTENT = Path("src/game/content/environmentParallax.json")
RUNTIME_DIRECTORY = Path("public/assets/game/environment")
OLD_ROAD = RUNTIME_DIRECTORY / "env-006-road-v5.png"
REVIEW_COMPARISON = Path("visual-references/environment-road-v6-before-after.png")
REVIEW_LOOP = Path("visual-references/environment-road-v6-loop-review.png")
REVIEW_MOTION = Path("visual-references/environment-road-v6-motion-review.png")
REVIEW_SEAM = Path("visual-references/environment-road-v6-seam-review.png")
CURB_ROW_RANGES = ((0, 6), (388, 398))


def neutralize_curbs(content: Image.Image) -> tuple[Image.Image, dict[str, Any]]:
    output = content.copy().convert("RGBA")
    pixels = output.load()
    changed = 0
    for start_y, end_y in CURB_ROW_RANGES:
        for y in range(start_y, end_y):
            for x in range(output.width):
                red, green, blue, alpha = pixels[x, y]
                luminance = round(0.2126 * red + 0.7152 * green + 0.0722 * blue)
                neutral = max(144, min(255, round(96 + luminance * 0.66)))
                pixels[x, y] = (neutral, neutral, neutral, alpha)
                changed += 1

    for start_y, end_y in CURB_ROW_RANGES:
        for y in range(start_y, end_y):
            if any(
                pixels[x, y][0] != pixels[x, y][1]
                or pixels[x, y][1] != pixels[x, y][2]
                for x in range(output.width)
            ):
                raise RuntimeError("ENV-006 curb neutralization left colored pixels")

    return output, {
        "sourceRows": [list(row_range) for row_range in CURB_ROW_RANGES],
        "changedPixels": changed,
        "outputColorModel": "neutral grayscale preserving source luminance",
    }


def render_frame(
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


def main() -> None:
    content = json.loads(CONTENT.read_text(encoding="utf-8"))
    if content["version"] != "v9":
        raise RuntimeError("The white-curb road builder requires the active v9 contract")

    road_spec = next(
        spec for spec in content["layers"] if spec["assetId"] == "ENV-006"
    )
    other_specs = [
        spec for spec in content["layers"] if spec["assetId"] != "ENV-006"
    ]
    locked_other_hashes = {
        spec["assetId"]: file_hash(
            RUNTIME_DIRECTORY / f"{spec['runtimeName']}.png"
        )
        for spec in other_specs
    }

    master = next(
        item for item in content["masters"] if item["id"] == road_spec["masterId"]
    )
    master_path = Path(master["path"])
    if file_hash(master_path) != master["sha256"]:
        raise RuntimeError("The approved road master hash does not match its contract")

    with Image.open(master_path) as master_image:
        source = master_image.convert("RGBA").crop(tuple(road_spec["sourceBox"]))
    content_size = (
        road_spec["contentCanvas"]["width"],
        road_spec["contentCanvas"]["height"],
    )
    road_content = source.resize(content_size, Image.Resampling.NEAREST)
    white_curb_content, curb_stats = neutralize_curbs(road_content)
    texture = build_cyclic_texture(white_curb_content, road_spec)
    seams = seam_mismatches(texture, white_curb_content.height)
    if seams["cycleWrap"]:
        raise RuntimeError(f"ENV-006 has a non-zero cyclic seam: {seams}")

    runtime_path = RUNTIME_DIRECTORY / f"{road_spec['runtimeName']}.png"
    metadata_path = runtime_path.with_suffix(".json")
    texture.save(runtime_path, optimize=True)

    route = content["route"]
    tile_scale = road_spec["tileScale"]
    display_speed = route["baseDisplaySpeedPxPerSecond"] * road_spec["speedMultiplier"]
    display_period = road_spec["textureCanvas"]["width"] * tile_scale["x"]
    write_json(
        metadata_path,
        {
            "assetId": road_spec["assetId"],
            "version": content["version"],
            "status": "integrated",
            "runtime": {
                "path": runtime_path.as_posix(),
                "textureCanvas": road_spec["textureCanvas"],
                "contentRect": {
                    "x": road_spec["seamGutterTexturePx"],
                    "y": 0,
                    "width": white_curb_content.width,
                    "height": white_curb_content.height,
                },
                "loopPeriodTexturePx": texture.width,
                "displayPeriodPx": display_period,
                "sha256": file_hash(runtime_path),
            },
            "production": {
                "script": "scripts/build_environment_road_v6.py",
                "contentSource": CONTENT.as_posix(),
                "approvedMaster": master_path.as_posix(),
                "approvedMasterSha256": master["sha256"],
                "sourceBox": road_spec["sourceBox"],
                "alphaExtraction": road_spec["alphaMode"],
                "curbTransform": curb_stats,
                "offlineResizeCount": 1,
                "resizeFilter": "nearest-neighbor",
                "paletteQuantization": "none",
                "phaserTextureFilter": "nearest",
                "cyclicConstruction": road_spec["cycleMode"],
                "untouchedLayerHashes": locked_other_hashes,
            },
            "curbContract": {
                "top": "white neutral pixel curb",
                "bottom": "white neutral pixel curb",
                "laneMarkingsChanged": False,
                "roadSurfaceChanged": False,
            },
            "seamContract": {
                "mode": road_spec["cycleMode"],
                "safeGutterTexturePx": road_spec["seamGutterTexturePx"],
                "edgeMismatchRows": seams,
                "review": REVIEW_LOOP.as_posix(),
            },
            "runtimePlacement": {
                "textureKey": road_spec["textureKey"],
                "layer": road_spec["layer"],
                "position": road_spec["position"],
                "tileScale": tile_scale,
                "displaySpeedPxPerSecond": display_speed,
                "textureScrollPixelsPerSecond": display_speed / tile_scale["x"],
                "fullCycleSeconds": display_period / display_speed,
                "depth": road_spec["depth"],
                "mode": route["mode"],
                "reducedMotion": road_spec["reducedMotion"],
            },
        },
    )

    old_rendered: list[tuple[dict[str, Any], Image.Image]] = []
    new_rendered: list[tuple[dict[str, Any], Image.Image]] = []
    for spec in content["layers"]:
        if spec["assetId"] == "ENV-006":
            old_rendered.append((spec, Image.open(OLD_ROAD).convert("RGBA")))
            new_rendered.append((spec, texture))
        else:
            layer_path = RUNTIME_DIRECTORY / f"{spec['runtimeName']}.png"
            layer = Image.open(layer_path).convert("RGBA")
            old_rendered.append((spec, layer))
            new_rendered.append((spec, layer))

    for spec in other_specs:
        current_hash = file_hash(RUNTIME_DIRECTORY / f"{spec['runtimeName']}.png")
        if current_hash != locked_other_hashes[spec["assetId"]]:
            raise RuntimeError(f"{spec['assetId']} changed during the road-only build")

    comparison = Image.new("RGBA", (720, 640), (29, 29, 27, 255))
    comparison.alpha_composite(render_frame(old_rendered, route, 0), (0, 0))
    comparison.alpha_composite(render_frame(new_rendered, route, 0), (360, 0))
    comparison.save(REVIEW_COMPARISON, optimize=True)

    moments = (0.0, 2.5, 5.0, 7.5)
    motion = Image.new("RGBA", (360 * len(moments), 640), (29, 29, 27, 255))
    for index, seconds in enumerate(moments):
        motion.alpha_composite(
            render_frame(new_rendered, route, seconds), (index * 360, 0)
        )
    motion.save(REVIEW_MOTION, optimize=True)

    seam_seconds = display_period / display_speed
    seam = Image.new("RGBA", (720, 640), (29, 29, 27, 255))
    seam.alpha_composite(render_frame(new_rendered, route, seam_seconds - 0.04), (0, 0))
    seam.alpha_composite(render_frame(new_rendered, route, seam_seconds + 0.04), (360, 0))
    seam.save(REVIEW_SEAM, optimize=True)

    loop = Image.new("RGBA", (texture.width * 2, texture.height), (29, 29, 47, 255))
    loop.alpha_composite(texture, (0, 0))
    loop.alpha_composite(texture, (texture.width, 0))
    loop.save(REVIEW_LOOP, optimize=True)

    print(f"ENV-006: {texture.width}x{texture.height}")
    print(f"curbs={curb_stats}")
    print(f"untouchedLayers={locked_other_hashes}")
    print(f"comparison={REVIEW_COMPARISON}")
    print(f"motionReview={REVIEW_MOTION}")
    print(f"seamReview={REVIEW_SEAM}")


if __name__ == "__main__":
    main()
