"""Create an approval-only environment still that matches the locked gameplay bands."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


SOURCE = Path("visual-references/env-001-gameplay-still-concept-v1.png")
OUTPUT = Path("visual-references/env-001-gameplay-still-concept-v2.png")

LOGICAL_HEIGHT = 640
ROAD_TOP = 282
ROAD_BOTTOM = 522
LANE_SEPARATORS = (363, 437)


def logical_y(height: int, value: int) -> int:
    return round(height * value / LOGICAL_HEIGHT)


def draw_road(canvas: Image.Image, top: int, bottom: int, scale: float) -> None:
    draw = ImageDraw.Draw(canvas)
    width = canvas.width
    draw.rectangle((0, top, width, bottom), fill=(61, 68, 105, 255))

    patch_height = max(2, round(2 * scale))
    patch_width = max(8, round(10 * scale))
    patch_rows = ((310, (18, 86, 157, 243, 318)), (392, (48, 122, 202, 278)), (470, (84, 185, 264, 342)))
    for logical_row, positions in patch_rows:
        y = logical_y(canvas.height, logical_row)
        for index, logical_x in enumerate(positions):
            x = round(logical_x * canvas.width / 360)
            draw.rectangle(
                (x, y, x + patch_width + (index % 3) * round(3 * scale), y + patch_height),
                fill=(47, 54, 89, 255),
            )

    lime_height = max(3, round(3 * scale))
    edge_height = max(1, round(scale))
    for y in (top, bottom - lime_height):
        draw.rectangle((0, y, width, y + lime_height), fill=(200, 240, 0, 255))
        draw.rectangle((0, y - edge_height, width, y), fill=(30, 29, 62, 255))

    mark_height = max(3, round(3 * scale))
    mark_width = round(18 * canvas.width / 360)
    gap = round(14 * canvas.width / 360)
    for logical_row in LANE_SEPARATORS:
        y = logical_y(canvas.height, logical_row)
        for x in range(round(4 * canvas.width / 360), width, mark_width + gap):
            draw.rectangle((x, y, x + mark_width, y + mark_height), fill=(255, 244, 223, 255))


def main() -> None:
    with Image.open(SOURCE) as source:
        source = source.convert("RGBA")
        width, height = source.size
        road_top = logical_y(height, ROAD_TOP)
        road_bottom = logical_y(height, ROAD_BOTTOM)
        source_road_top = 814
        source_road_bottom = 1_205

        canvas = Image.new("RGBA", (width, height), (238, 240, 255, 255))
        city = source.crop((0, 0, width, source_road_top)).resize(
            (width, road_top), Image.Resampling.NEAREST
        )
        bottom = source.crop((0, source_road_bottom, width, height)).resize(
            (width, height - road_bottom), Image.Resampling.NEAREST
        )
        canvas.alpha_composite(city, (0, 0))
        draw_road(canvas, road_top, road_bottom, height / LOGICAL_HEIGHT)
        canvas.alpha_composite(bottom, (0, road_bottom))
        canvas.save(OUTPUT)

        print(f"source={SOURCE}")
        print(f"output={OUTPUT}")
        print(f"size={width}x{height}")
        print(f"road={road_top}:{road_bottom}")
        print(
            "separators="
            + ",".join(str(logical_y(height, value)) for value in LANE_SEPARATORS)
        )


if __name__ == "__main__":
    main()
