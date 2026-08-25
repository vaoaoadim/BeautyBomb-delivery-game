"""Build seam-safe POT parallax textures from approved environment masters."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps


CONTENT = Path("src/game/content/environmentParallax.json")
RUNTIME_DIRECTORY = Path("public/assets/game/environment")
REVIEW_COMPARISON = Path(
    "visual-references/environment-parallax-v3-master-runtime-comparison.png"
)
REVIEW_LOOP = Path("visual-references/environment-parallax-v3-loop-review.png")


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def is_power_of_two(value: int) -> bool:
    return value > 0 and value & (value - 1) == 0


def remove_cyan_sky(image: Image.Image) -> Image.Image:
    result = image.convert("RGBA")
    pixels = result.load()
    for y in range(result.height):
        for x in range(result.width):
            red, green, blue, _alpha = pixels[x, y]
            if 100 <= red <= 200 and green >= 210 and blue >= 230:
                pixels[x, y] = (red, green, blue, 0)
    return result


def render_content(master: Image.Image, spec: dict[str, Any]) -> Image.Image:
    source_box = tuple(spec["sourceBox"])
    content = master.crop(source_box).convert("RGBA")
    if spec["alphaMode"] == "remove-cyan-sky":
        content = remove_cyan_sky(content)
    elif spec["alphaMode"] != "opaque-source-crop":
        raise ValueError(f"Unknown alpha mode: {spec['alphaMode']}")

    size = spec["contentCanvas"]
    return content.resize((size["width"], size["height"]), Image.Resampling.NEAREST)


def build_cyclic_texture(content: Image.Image, spec: dict[str, Any]) -> Image.Image:
    texture_canvas = spec["textureCanvas"]
    texture_width = texture_canvas["width"]
    texture_height = texture_canvas["height"]
    if not is_power_of_two(texture_width) or not is_power_of_two(texture_height):
        raise ValueError(f"{spec['assetId']} requires a POT texture canvas")

    gutter_width = spec["seamGutterTexturePx"]
    if gutter_width <= 0 or content.width + gutter_width * 2 != texture_width:
        raise ValueError(
            f"{spec['assetId']} must reserve matching safe gutters at both cycle edges"
        )
    if content.height > texture_height:
        raise ValueError(f"{spec['assetId']} content does not fit its texture canvas")

    texture = Image.new("RGBA", (texture_width, texture_height), (0, 0, 0, 0))
    left_safe_gutter = content.crop((0, 0, gutter_width, content.height))
    texture.alpha_composite(left_safe_gutter, (0, 0))
    texture.alpha_composite(content, (gutter_width, 0))
    # Only the object-free left gutter is mirrored. Buildings, trees, and shops
    # remain a direct, non-mirrored panorama in the useful content region.
    texture.alpha_composite(
        ImageOps.mirror(left_safe_gutter),
        (gutter_width + content.width, 0),
    )
    return texture


def seam_mismatches(texture: Image.Image, content_height: int) -> dict[str, int]:
    pixels = texture.load()
    cycle_wrap = sum(
        pixels[texture.width - 1, y] != pixels[0, y]
        for y in range(content_height)
    )
    return {"cycleWrap": cycle_wrap}


def write_comparison(master: Image.Image, rendered: list[tuple[dict[str, Any], Image.Image]]) -> None:
    runtime_preview = Image.new("RGBA", (360, 640), (115, 230, 247, 255))
    for spec, content in rendered:
        scale = spec["tileScale"]
        display_size = (
            round(content.width * scale["x"]),
            round(content.height * scale["y"]),
        )
        display = content.resize(display_size, Image.Resampling.NEAREST)
        position = spec["position"]
        runtime_preview.alpha_composite(display, (position["x"], position["y"]))

    master_preview = master.resize((360, 640), Image.Resampling.NEAREST)
    comparison = Image.new("RGBA", (720, 640), (29, 29, 27, 255))
    comparison.alpha_composite(master_preview, (0, 0))
    comparison.alpha_composite(runtime_preview, (360, 0))
    comparison.save(REVIEW_COMPARISON)


def write_loop_review(rendered: list[tuple[dict[str, Any], Image.Image]]) -> None:
    gutter = 12
    review_width = max(texture.width * 2 for _spec, texture in rendered)
    review_height = sum(texture.height + gutter for _spec, texture in rendered) - gutter
    review = Image.new("RGBA", (review_width, review_height), (29, 29, 47, 255))
    y = 0
    for _spec, texture in rendered:
        review.alpha_composite(texture, (0, y))
        review.alpha_composite(texture, (texture.width, y))
        y += texture.height + gutter
    review.save(REVIEW_LOOP)


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

    RUNTIME_DIRECTORY.mkdir(parents=True, exist_ok=True)

    comparison_layers: list[tuple[dict[str, Any], Image.Image]] = []
    loop_review_layers: list[tuple[dict[str, Any], Image.Image]] = []
    route = content["route"]
    for spec in content["layers"]:
        master_id = spec["masterId"]
        if master_id not in source_images:
            raise ValueError(f"{spec['assetId']} references an unknown master: {master_id}")
        rendered_content = render_content(source_images[master_id], spec)
        texture = build_cyclic_texture(rendered_content, spec)
        seams = seam_mismatches(texture, rendered_content.height)
        if seams["cycleWrap"]:
            raise RuntimeError(f"{spec['assetId']} has a non-zero cyclic seam: {seams}")

        runtime_path = RUNTIME_DIRECTORY / f"{spec['runtimeName']}.png"
        metadata_path = RUNTIME_DIRECTORY / f"{spec['runtimeName']}.json"
        texture.save(runtime_path)
        tile_scale = spec["tileScale"]
        display_speed = route["baseDisplaySpeedPxPerSecond"] * spec["speedMultiplier"]
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
                        "width": rendered_content.width,
                        "height": rendered_content.height,
                    },
                    "loopPeriodTexturePx": texture.width,
                    "sha256": file_hash(runtime_path),
                },
                "production": {
                    "script": "scripts/build_environment_parallax_v3.py",
                    "contentSource": CONTENT.as_posix(),
                    "approvedMaster": masters[master_id]["path"].as_posix(),
                    "approvedMasterSha256": masters[master_id]["sha256"],
                    "sourceBox": spec["sourceBox"],
                    "alphaExtraction": spec["alphaMode"],
                    "offlineResizeCount": 1,
                    "resizeFilter": "nearest-neighbor",
                    "paletteQuantization": "none",
                    "phaserTextureFilter": "nearest",
                    "cyclicConstruction": "safe-gutter-plus-direct-panorama; only the neutral source gutter is mirrored; no generated pixels",
                },
                "seamContract": {
                    "mode": "safe-gutter-direct-panorama",
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
                    "depth": spec["depth"],
                    "mode": route["mode"],
                    "reducedMotion": spec["reducedMotion"],
                },
            },
        )
        comparison_layers.append((spec, rendered_content))
        loop_review_layers.append((spec, texture))
        print(
            f"{spec['assetId']}: {texture.width}x{texture.height}, "
            f"period={texture.width}, speed={display_speed:.2f}px/s"
        )

    write_comparison(source_images["environment-seamless-v3"], comparison_layers)
    write_loop_review(loop_review_layers)
    print(f"comparison={REVIEW_COMPARISON}")
    print(f"loopReview={REVIEW_LOOP}")


if __name__ == "__main__":
    main()
