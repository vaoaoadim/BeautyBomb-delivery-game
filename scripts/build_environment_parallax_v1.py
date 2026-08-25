"""Derive the first parallax runtime set from the approved environment still master."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path

from PIL import Image


MASTER = Path("visual-references/env-001-gameplay-still-concept-v2.png")
MASTER_METADATA = Path("visual-references/env-001-gameplay-still-concept-v2.json")
REVIEW_COMPARISON = Path(
    "visual-references/environment-parallax-v1-master-runtime-comparison.png"
)
RUNTIME_DIRECTORY = Path("public/assets/game/environment")
APPROVED_MASTER_SHA256 = "a4c09eb3cf36b043717759931611ef84bff353c79775ebad10c59ebde027bb12"


@dataclass(frozen=True)
class LayerSpec:
    asset_id: str
    texture_key: str
    source_box: tuple[int, int, int, int]
    output_size: tuple[int, int]
    runtime_name: str
    status: str
    alpha_mode: str
    layer: str
    parallax_speed: float
    runtime_position: tuple[int, int]
    runtime_scale: tuple[float, float]


LAYERS = (
    LayerSpec(
        asset_id="ENV-001",
        texture_key="environment-sky-v1",
        source_box=(0, 0, 941, 331),
        output_size=(512, 180),
        runtime_name="env-001-sky-v1",
        status="integrated",
        alpha_mode="opaque-source-crop",
        layer="sky",
        parallax_speed=0.10,
        runtime_position=(0, 0),
        runtime_scale=(360 / 512, 360 / 512),
    ),
    LayerSpec(
        asset_id="ENV-002",
        texture_key="environment-far-skyline-v1",
        source_box=(0, 300, 941, 535),
        output_size=(512, 128),
        runtime_name="env-002-far-skyline-v1",
        status="integrated",
        alpha_mode="remove-cyan-sky",
        layer="far-skyline",
        parallax_speed=0.40,
        runtime_position=(0, 115),
        runtime_scale=(360 / 512, 360 / 512),
    ),
    LayerSpec(
        asset_id="ENV-003",
        texture_key="environment-mid-city-v1",
        source_box=(0, 387, 941, 681),
        output_size=(512, 160),
        runtime_name="env-003-mid-city-v1",
        status="integrated",
        alpha_mode="remove-cyan-sky",
        layer="mid-city",
        parallax_speed=0.80,
        runtime_position=(0, 148),
        runtime_scale=(360 / 512, 360 / 512),
    ),
    LayerSpec(
        asset_id="ENV-004",
        texture_key="environment-near-street-a-v1",
        source_box=(0, 468, 941, 737),
        output_size=(768, 220),
        runtime_name="env-004-near-street-a-v1",
        status="integrated",
        alpha_mode="opaque-source-crop",
        layer="near-street",
        parallax_speed=1.20,
        runtime_position=(0, 179),
        runtime_scale=(360 / 768, 360 / 768),
    ),
    LayerSpec(
        asset_id="ENV-006",
        texture_key="environment-road-v1",
        source_box=(0, 737, 941, 1364),
        output_size=(512, 240),
        runtime_name="env-006-road-v1",
        status="integrated",
        alpha_mode="opaque-source-crop",
        layer="road",
        parallax_speed=4.00,
        runtime_position=(0, 282),
        runtime_scale=(360 / 512, 1.0),
    ),
    LayerSpec(
        asset_id="ENV-008",
        texture_key="environment-foreground-accents-v1",
        source_box=(0, 1364, 941, 1672),
        output_size=(512, 128),
        runtime_name="env-008-foreground-accents-v1",
        status="integrated",
        alpha_mode="opaque-source-crop",
        layer="foreground-accents",
        parallax_speed=0.30,
        runtime_position=(0, 522),
        runtime_scale=(360 / 512, 118 / 128),
    ),
)


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def remove_cyan_sky(image: Image.Image) -> Image.Image:
    result = image.convert("RGBA")
    pixels = result.load()
    for y in range(result.height):
        for x in range(result.width):
            red, green, blue, _alpha = pixels[x, y]
            if 100 <= red <= 200 and green >= 210 and blue >= 230:
                pixels[x, y] = (red, green, blue, 0)
    return result


def render_layer(master: Image.Image, spec: LayerSpec) -> Image.Image:
    layer = master.crop(spec.source_box).convert("RGBA")
    if spec.alpha_mode == "remove-cyan-sky":
        layer = remove_cyan_sky(layer)
    elif spec.alpha_mode != "opaque-source-crop":
        raise ValueError(f"Unknown alpha mode: {spec.alpha_mode}")
    return layer.resize(spec.output_size, Image.Resampling.NEAREST)


def write_json(path: Path, value: dict[str, object]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_review_comparison(
    master: Image.Image,
    rendered_layers: list[tuple[LayerSpec, Image.Image]],
) -> None:
    runtime_preview = Image.new("RGBA", (360, 640), (115, 230, 247, 255))
    for spec, image in rendered_layers:
        display_size = (
            round(image.width * spec.runtime_scale[0]),
            round(image.height * spec.runtime_scale[1]),
        )
        display = image.resize(display_size, Image.Resampling.NEAREST)
        runtime_preview.alpha_composite(display, spec.runtime_position)

    master_preview = master.resize((360, 640), Image.Resampling.NEAREST)
    comparison = Image.new("RGBA", (720, 640), (29, 29, 27, 255))
    comparison.alpha_composite(master_preview, (0, 0))
    comparison.alpha_composite(runtime_preview, (360, 0))
    comparison.save(REVIEW_COMPARISON)


def main() -> None:
    if file_hash(MASTER) != APPROVED_MASTER_SHA256:
        raise RuntimeError(
            "The approved environment master changed. Create a new versioned master and decision before export."
        )

    RUNTIME_DIRECTORY.mkdir(parents=True, exist_ok=True)
    with Image.open(MASTER) as source:
        master = source.convert("RGBA")

    master_metadata = {
        "assetId": "ENV-SCENE-001",
        "version": "v2",
        "status": "approved-master",
        "approvedOn": "2026-08-20",
        "path": MASTER.as_posix(),
        "canvas": {"width": master.width, "height": master.height},
        "runtimeViewport": {"width": 360, "height": 640},
        "runtimeBandGuides": {
            "roadTop": 282,
            "roadBottom": 522,
            "laneSeparators": [363, 437],
        },
        "sha256": APPROVED_MASTER_SHA256,
        "provenance": {
            "generatedCandidate": "visual-references/env-001-gameplay-still-concept-v1.png",
            "compositionScript": "scripts/build_environment_still_candidate.py",
            "note": "The owner approved this exact v2 composition as the immutable visual master.",
        },
    }
    write_json(MASTER_METADATA, master_metadata)

    rendered_layers: list[tuple[LayerSpec, Image.Image]] = []
    for spec in LAYERS:
        image = render_layer(master, spec)
        rendered_layers.append((spec, image))
        runtime_path = RUNTIME_DIRECTORY / f"{spec.runtime_name}.png"
        metadata_path = RUNTIME_DIRECTORY / f"{spec.runtime_name}.json"
        image.save(runtime_path)
        write_json(
            metadata_path,
            {
                "assetId": spec.asset_id,
                "version": "v1",
                "status": spec.status,
                "runtime": {
                    "path": runtime_path.as_posix(),
                    "canvas": {"width": image.width, "height": image.height},
                    "sha256": file_hash(runtime_path),
                },
                "production": {
                    "script": "scripts/build_environment_parallax_v1.py",
                    "approvedMaster": MASTER.as_posix(),
                    "approvedMasterSha256": APPROVED_MASTER_SHA256,
                    "sourceBox": list(spec.source_box),
                    "alphaExtraction": spec.alpha_mode,
                    "offlineResizeCount": 1,
                    "resizeFilter": "nearest-neighbor",
                    "paletteQuantization": "none",
                    "phaserTextureFilter": "nearest",
                },
                "runtimePlacement": {
                    "textureKey": spec.texture_key,
                    "layer": spec.layer,
                    "position": {"x": spec.runtime_position[0], "y": spec.runtime_position[1]},
                    "scale": {"x": spec.runtime_scale[0], "y": spec.runtime_scale[1]},
                    "scrollPixelsPerSecond": spec.parallax_speed,
                },
            },
        )
        print(
            f"{spec.asset_id}: {image.width}x{image.height}, "
            f"source={spec.source_box}, speed={spec.parallax_speed}"
        )

    write_review_comparison(master, rendered_layers)
    print(f"review={REVIEW_COMPARISON}")


if __name__ == "__main__":
    main()
