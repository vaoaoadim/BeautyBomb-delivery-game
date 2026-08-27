from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PALETTE = (
    (30, 29, 62),
    (238, 240, 255),
    (84, 224, 255),
    (0, 183, 214),
    (255, 79, 171),
    (152, 42, 221),
    (255, 239, 92),
    (255, 255, 255),
)


def nearest_palette(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    return min(
        PALETTE,
        key=lambda color: sum((channel - target) ** 2 for channel, target in zip(rgb, color)),
    )


def is_chroma_key(rgb: tuple[int, int, int]) -> bool:
    red, green, blue = rgb
    return green >= 145 and green >= red * 1.55 and green >= blue * 1.55


def build_master(source: Path, destination: Path) -> Image.Image:
    source_image = Image.open(source).convert("RGB")
    output = Image.new("RGBA", source_image.size, (0, 0, 0, 0))
    source_pixels = source_image.load()
    output_pixels = output.load()

    for y in range(source_image.height):
        for x in range(source_image.width):
            pixel = source_pixels[x, y]
            if is_chroma_key(pixel):
                continue
            output_pixels[x, y] = (*nearest_palette(pixel), 255)

    destination.parent.mkdir(parents=True, exist_ok=True)
    output.save(destination, optimize=True)
    return output


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        Path("C:/Windows/Fonts/consolab.ttf"),
        Path("C:/Windows/Fonts/consola.ttf"),
        Path("visual-references/fonts/press-start-2p/PressStart2P-Regular.ttf"),
    )
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def centered_text(
    draw: ImageDraw.ImageDraw,
    center: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    fill: tuple[int, int, int, int],
    spacing: int = 4,
) -> None:
    bounds = draw.multiline_textbbox((0, 0), text, font=font, align="center", spacing=spacing)
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    draw.multiline_text(
        (center[0] - width / 2, center[1] - height / 2 - bounds[1]),
        text,
        font=font,
        fill=fill,
        align="center",
        spacing=spacing,
    )


def build_preview(master: Image.Image, destination: Path) -> None:
    viewport = Image.new("RGBA", (360, 640), (30, 29, 62, 255))
    runtime = master.resize((304, 456), Image.Resampling.NEAREST)
    viewport.alpha_composite(runtime, (28, 92))
    draw = ImageDraw.Draw(viewport)

    # Live UI preview only. These elements are intentionally absent from the master.
    draw.rectangle((68, 286, 242, 330), fill=(152, 42, 221, 255))
    draw.rectangle((66, 283, 240, 327), fill=(238, 240, 255, 255), outline=(30, 29, 62, 255), width=3)
    centered_text(draw, (153, 305), "XQZ-20476", load_font(20), (30, 29, 62, 255))

    draw.rectangle((250, 286, 294, 330), fill=(152, 42, 221, 255))
    draw.rectangle((248, 283, 292, 327), fill=(30, 29, 62, 255))
    draw.rectangle((252, 286, 288, 320), fill=(255, 79, 171, 255))
    draw.rectangle((260, 293, 273, 308), fill=(238, 240, 255, 255), outline=(30, 29, 62, 255), width=2)
    draw.rectangle((267, 301, 280, 316), fill=(238, 240, 255, 255), outline=(30, 29, 62, 255), width=2)

    centered_text(
        draw,
        (180, 468),
        "Ваш купон с 20% скидкой\nна любые товары!\nСкопируйте его!",
        load_font(13),
        (30, 29, 62, 255),
        spacing=5,
    )

    destination.parent.mkdir(parents=True, exist_ok=True)
    viewport.convert("RGB").save(destination, optimize=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--master", type=Path, required=True)
    parser.add_argument("--preview", type=Path, required=True)
    args = parser.parse_args()

    master = build_master(args.source, args.master)
    build_preview(master, args.preview)
    colors = master.getcolors(maxcolors=10_000_000) or []
    alpha_values = {color[1][3] for color in colors}
    print(f"master={args.master} sha256={sha256(args.master)} colors={len(colors)} alpha={sorted(alpha_values)}")
    print(f"preview={args.preview} sha256={sha256(args.preview)}")


if __name__ == "__main__":
    main()
