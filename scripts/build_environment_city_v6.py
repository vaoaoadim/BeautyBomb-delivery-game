"""Build one versioned coherent city layer; preserve every other parallax asset."""

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
from build_environment_parallax_v5 import checkerboard


CONTENT = Path("src/game/content/environmentParallax.json")
RUNTIME_DIRECTORY = Path("public/assets/game/environment")
OLD_CITY = RUNTIME_DIRECTORY / "env-004-coherent-city-v5.png"
REVIEW_ALPHA = Path("visual-references/environment-parallax-v6-alpha-review.png")
REVIEW_COMPARISON = Path("visual-references/environment-parallax-v6-before-after.png")
REVIEW_LOOP = Path("visual-references/environment-parallax-v6-loop-review.png")
REVIEW_MOTION = Path("visual-references/environment-parallax-v6-motion-review.png")
REVIEW_SEAM = Path("visual-references/environment-parallax-v6-seam-review.png")


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


def write_alpha_review(city: Image.Image, matte: Image.Image) -> None:
    panel_size = (1024, 256)
    review = Image.new("RGBA", (1024, 512), (29, 29, 27, 255))
    mask_panel = matte.convert("RGBA").resize(panel_size, Image.Resampling.NEAREST)
    city_panel = checkerboard(panel_size)
    city_panel.alpha_composite(city.resize(panel_size, Image.Resampling.NEAREST))
    review.alpha_composite(mask_panel, (0, 0))
    review.alpha_composite(city_panel, (0, 256))
    review.save(REVIEW_ALPHA, optimize=True)


def write_comparison(
    old_rendered: list[tuple[dict[str, Any], Image.Image]],
    new_rendered: list[tuple[dict[str, Any], Image.Image]],
    route: dict[str, Any],
) -> None:
    review = Image.new("RGBA", (720, 640), (29, 29, 27, 255))
    review.alpha_composite(render_frame(old_rendered, route, 0), (0, 0))
    review.alpha_composite(render_frame(new_rendered, route, 0), (360, 0))
    review.save(REVIEW_COMPARISON, optimize=True)


def write_motion_review(
    rendered: list[tuple[dict[str, Any], Image.Image]],
    route: dict[str, Any],
) -> None:
    moments = (0.0, 6.0, 12.0, 18.0)
    review = Image.new("RGBA", (360 * len(moments), 640), (29, 29, 27, 255))
    for index, seconds in enumerate(moments):
        review.alpha_composite(render_frame(rendered, route, seconds), (index * 360, 0))
    review.save(REVIEW_MOTION, optimize=True)


def write_seam_review(
    rendered: list[tuple[dict[str, Any], Image.Image]],
    route: dict[str, Any],
    city_spec: dict[str, Any],
) -> None:
    city_speed = route["baseDisplaySpeedPxPerSecond"] * city_spec["speedMultiplier"]
    city_period = city_spec["textureCanvas"]["width"] * city_spec["tileScale"]["x"]
    seam_seconds = city_period / city_speed
    review = Image.new("RGBA", (720, 640), (29, 29, 27, 255))
    review.alpha_composite(render_frame(rendered, route, seam_seconds - 0.04), (0, 0))
    review.alpha_composite(render_frame(rendered, route, seam_seconds + 0.04), (360, 0))
    review.save(REVIEW_SEAM, optimize=True)


def main() -> None:
    content = json.loads(CONTENT.read_text(encoding="utf-8"))
    if content["version"] not in {"v6", "v7", "v8"}:
        raise RuntimeError("The city builder requires an active v6, v7, or v8 content contract")

    city_spec = next(
        spec for spec in content["layers"] if spec["assetId"] == "ENV-004"
    )
    other_specs = [
        spec for spec in content["layers"] if spec["assetId"] != "ENV-004"
    ]
    locked_other_hashes = {
        spec["assetId"]: file_hash(
            RUNTIME_DIRECTORY / f"{spec['runtimeName']}.png"
        )
        for spec in other_specs
    }

    master = next(
        item for item in content["masters"] if item["id"] == city_spec["masterId"]
    )
    master_path = Path(master["path"])
    if file_hash(master_path) != master["sha256"]:
        raise RuntimeError("The versioned v6 city master hash does not match its contract")

    with Image.open(master_path) as source_image:
        source = source_image.convert("RGBA").crop(tuple(city_spec["sourceBox"]))
    matte = source.getchannel("A")
    alpha_histogram = matte.histogram()
    alpha_bbox = matte.getbbox()
    if alpha_bbox is None or alpha_bbox[1] >= source.height:
        raise RuntimeError("The v6 city alpha master has no visible city content")
    if any(
        matte.getpixel(point) != 0
        for point in ((0, 0), (source.width - 1, 0))
    ):
        raise RuntimeError("The v6 city alpha master must be transparent above both loop edges")
    mask_stats = {
        "transparentPixels": alpha_histogram[0],
        "opaquePixels": alpha_histogram[255],
        "partialAlphaPixels": sum(alpha_histogram[1:255]),
        "alphaBoundingBox": list(alpha_bbox),
    }
    output_size = (
        city_spec["contentCanvas"]["width"],
        city_spec["contentCanvas"]["height"],
    )
    city_content = source.resize(output_size, Image.Resampling.NEAREST)
    runtime_matte = matte.resize(output_size, Image.Resampling.NEAREST)
    texture = build_cyclic_texture(city_content, city_spec)
    seams = seam_mismatches(texture, city_content.height)
    if seams["cycleWrap"]:
        raise RuntimeError(f"ENV-004 has a non-zero cyclic seam: {seams}")

    RUNTIME_DIRECTORY.mkdir(parents=True, exist_ok=True)
    runtime_path = RUNTIME_DIRECTORY / f"{city_spec['runtimeName']}.png"
    metadata_path = runtime_path.with_suffix(".json")
    texture.save(runtime_path, optimize=True)

    route = content["route"]
    tile_scale = city_spec["tileScale"]
    display_speed = route["baseDisplaySpeedPxPerSecond"] * city_spec["speedMultiplier"]
    display_period = city_spec["textureCanvas"]["width"] * tile_scale["x"]
    write_json(
        metadata_path,
        {
            "assetId": city_spec["assetId"],
            "version": content["version"],
            "status": "integrated",
            "runtime": {
                "path": runtime_path.as_posix(),
                "textureCanvas": city_spec["textureCanvas"],
                "contentRect": {
                    "x": 0,
                    "y": 0,
                    "width": city_content.width,
                    "height": city_content.height,
                },
                "loopPeriodTexturePx": texture.width,
                "displayPeriodPx": display_period,
                "sha256": file_hash(runtime_path),
            },
            "production": {
                "script": f"scripts/build_environment_city_{content['version']}.py",
                "contentSource": CONTENT.as_posix(),
                "approvedMaster": master_path.as_posix(),
                "approvedMasterSha256": master["sha256"],
                "reference": "C:/Users/пк/Downloads/ChatGPT Image 23 авг. 2026 г., 19_58_11.png",
                "generationMode": "built-in-imagegen",
                "sourceBox": city_spec["sourceBox"],
                "alphaExtraction": city_spec["alphaMode"],
                "maskMethod": "versioned transparent master derived from a flat magenta imagegen source via the installed remove_chroma_key helper",
                "chromaSource": "visual-references/env-001-parallax-neighborhood-v6-chroma-source.png",
                "chromaKeyMethod": "auto-key border; soft matte 12..220; despill",
                "maskStats": mask_stats,
                "offlineResizeCount": 1,
                "resizeFilter": "nearest-neighbor",
                "paletteQuantization": "none",
                "phaserTextureFilter": "nearest",
                "cyclicConstruction": city_spec["cycleMode"],
                "untouchedLayerHashes": locked_other_hashes,
            },
            "seamContract": {
                "mode": city_spec["cycleMode"],
                "safeGutterTexturePx": city_spec["seamGutterTexturePx"],
                "edgeMismatchRows": seams,
                "review": REVIEW_LOOP.as_posix(),
            },
            "alphaContract": {
                "cityComposition": "unified-neighborhood-skyline-to-sidewalk",
                "source": "approved RGBA master",
                "runtimeColorDeletion": "none",
                "detachedCloudsRetained": False,
            },
            "runtimePlacement": {
                "textureKey": city_spec["textureKey"],
                "layer": city_spec["layer"],
                "position": city_spec["position"],
                "tileScale": tile_scale,
                "displaySpeedPxPerSecond": display_speed,
                "textureScrollPixelsPerSecond": display_speed / tile_scale["x"],
                "fullCycleSeconds": display_period / display_speed,
                "depth": city_spec["depth"],
                "mode": route["mode"],
                "reducedMotion": city_spec["reducedMotion"],
            },
        },
    )

    old_rendered: list[tuple[dict[str, Any], Image.Image]] = []
    new_rendered: list[tuple[dict[str, Any], Image.Image]] = []
    for spec in content["layers"]:
        if spec["assetId"] == "ENV-004":
            old_rendered.append((spec, Image.open(OLD_CITY).convert("RGBA")))
            new_rendered.append((spec, texture))
        else:
            layer_path = RUNTIME_DIRECTORY / f"{spec['runtimeName']}.png"
            layer = Image.open(layer_path).convert("RGBA")
            old_rendered.append((spec, layer))
            new_rendered.append((spec, layer))

    for spec in other_specs:
        current_hash = file_hash(RUNTIME_DIRECTORY / f"{spec['runtimeName']}.png")
        if current_hash != locked_other_hashes[spec["assetId"]]:
            raise RuntimeError(f"{spec['assetId']} changed during the city-only build")

    write_alpha_review(city_content, runtime_matte)
    write_comparison(old_rendered, new_rendered, route)
    write_motion_review(new_rendered, route)
    write_seam_review(new_rendered, route, city_spec)
    loop_review = Image.new("RGBA", (texture.width * 2, texture.height), (29, 29, 47, 255))
    loop_review.alpha_composite(texture, (0, 0))
    loop_review.alpha_composite(texture, (texture.width, 0))
    loop_review.save(REVIEW_LOOP, optimize=True)

    print(f"ENV-004: {texture.width}x{texture.height}")
    print(f"cityMask={mask_stats}")
    print(f"untouchedLayers={locked_other_hashes}")
    print(f"comparison={REVIEW_COMPARISON}")
    print(f"motionReview={REVIEW_MOTION}")
    print(f"seamReview={REVIEW_SEAM}")


if __name__ == "__main__":
    main()
