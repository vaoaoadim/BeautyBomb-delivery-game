"""Build the deterministic Beauty Bomb touch-control sprite sheet v2."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from PIL import Image, ImageDraw


OUTPUT = Path("public/assets/game/ui")
RUNTIME = OUTPUT / "ui-004-touch-controls-v2.png"
METADATA = OUTPUT / "ui-004-touch-controls-v2.json"
REVIEW = Path("visual-references/ui-004-touch-controls-v2-review.png")

FRAME_WIDTH = 76
FRAME_HEIGHT = 48
STATES = ("up", "up-pressed", "down", "down-pressed")

PALETTE = {
    "ink": (29, 29, 27, 255),
    "yellow": (255, 239, 92, 255),
    "yellow_pressed": (224, 210, 54, 255),
    "highlight": (255, 249, 177, 255),
    "pink": (255, 79, 171, 255),
    "pink_shadow": (190, 43, 123, 255),
    "review_surface": (238, 240, 255, 255),
}


def hex_color(color: tuple[int, int, int, int]) -> str:
    return "#" + "".join(f"{channel:02x}" for channel in color[:3])


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def button_shape(top: int, bottom: int) -> list[tuple[int, int]]:
    return [
        (4, top),
        (72, top),
        (75, top + 3),
        (75, bottom - 3),
        (72, bottom),
        (4, bottom),
        (1, bottom - 3),
        (1, top + 3),
    ]


def inset_shape(top: int, bottom: int) -> list[tuple[int, int]]:
    return [
        (6, top),
        (70, top),
        (72, top + 2),
        (72, bottom - 2),
        (70, bottom),
        (6, bottom),
        (4, bottom - 2),
        (4, top + 2),
    ]


def arrow_shape(direction: str, y_shift: int) -> list[tuple[int, int]]:
    if direction == "up":
        return [
            (38, 12 + y_shift),
            (25, 25 + y_shift),
            (32, 25 + y_shift),
            (32, 32 + y_shift),
            (44, 32 + y_shift),
            (44, 25 + y_shift),
            (51, 25 + y_shift),
        ]
    return [
        (32, 13 + y_shift),
        (44, 13 + y_shift),
        (44, 20 + y_shift),
        (51, 20 + y_shift),
        (38, 33 + y_shift),
        (25, 20 + y_shift),
        (32, 20 + y_shift),
    ]


def draw_frame(direction: str, pressed: bool) -> Image.Image:
    frame = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(frame)

    press_shift = 3 if pressed else 0
    face_top = 1 + press_shift
    face_bottom = 39 + press_shift
    surface = PALETTE["yellow_pressed"] if pressed else PALETTE["yellow"]

    # A single clean Beauty Bomb pink extrusion keeps the button dimensional.
    draw.polygon(button_shape(7, 47), fill=PALETTE["pink_shadow"])
    draw.rectangle((4, 40, 71, 46), fill=PALETTE["pink"])

    # Crisp two-pixel dark frame and a flat yellow face are legible at any scale.
    draw.polygon(button_shape(face_top, face_bottom), fill=PALETTE["ink"])
    draw.polygon(inset_shape(face_top + 3, face_bottom - 3), fill=surface)
    draw.line(
        (8, face_top + 4, 68, face_top + 4),
        fill=PALETTE["highlight"],
        width=2,
    )

    draw.polygon(arrow_shape(direction, press_shift), fill=PALETTE["ink"])
    return frame


def build_sheet() -> Image.Image:
    sheet = Image.new(
        "RGBA",
        (FRAME_WIDTH, FRAME_HEIGHT * len(STATES)),
        (0, 0, 0, 0),
    )
    for index, state in enumerate(STATES):
        direction = "up" if state.startswith("up") else "down"
        pressed = state.endswith("pressed")
        sheet.alpha_composite(
            draw_frame(direction, pressed),
            (0, index * FRAME_HEIGHT),
        )
    return sheet


def write_metadata(sheet: Image.Image) -> None:
    metadata = {
        "assetId": "UI-004",
        "version": "v2",
        "status": "integrated",
        "texture": RUNTIME.name,
        "canvas": {"width": sheet.width, "height": sheet.height},
        "frame": {
            "width": FRAME_WIDTH,
            "height": FRAME_HEIGHT,
            "count": len(STATES),
            "states": list(STATES),
        },
        "palette": {name: hex_color(color) for name, color in PALETTE.items()},
        "production": {
            "buildScript": "scripts/build_touch_controls_v2.py",
            "assetMode": "authored-low-resolution-pixel-art",
            "offlineResizeCount": 0,
            "antialiasing": False,
            "paletteQuantization": False,
            "phaserTextureFilter": "nearest",
            "runtimeSha256": file_hash(RUNTIME),
        },
        "runtime": {
            "centers": [{"x": 111, "y": 572}, {"x": 249, "y": 572}],
            "layout": {"left": "down", "right": "up"},
            "displayScale": 1.5,
            "hitArea": {"width": 114, "height": 72},
            "bottomClearancePx": 32,
            "interaction": "pressed frame on pointerdown; idle frame on pointerup or pointerout",
        },
    }
    METADATA.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_review(sheet: Image.Image) -> None:
    scale = 3
    gap = 10
    surface = Image.new(
        "RGBA",
        (
            FRAME_WIDTH * scale * len(STATES) + gap * (len(STATES) + 1),
            FRAME_HEIGHT * scale + gap * 2,
        ),
        PALETTE["review_surface"],
    )
    for index in range(len(STATES)):
        frame = sheet.crop(
            (
                0,
                index * FRAME_HEIGHT,
                FRAME_WIDTH,
                (index + 1) * FRAME_HEIGHT,
            )
        ).resize((FRAME_WIDTH * scale, FRAME_HEIGHT * scale), Image.Resampling.NEAREST)
        surface.alpha_composite(frame, (gap + index * (FRAME_WIDTH * scale + gap), gap))
    REVIEW.parent.mkdir(parents=True, exist_ok=True)
    surface.convert("RGB").save(REVIEW, optimize=True)


def assert_contract(sheet: Image.Image) -> None:
    assert sheet.size == (76, 192)
    assert sheet.getpixel((38, 18)) == PALETTE["ink"]
    assert sheet.getpixel((38, 48 + 21)) == PALETTE["ink"]
    assert sheet.getpixel((38, 96 + 27)) == PALETTE["ink"]
    assert sheet.getpixel((38, 144 + 30)) == PALETTE["ink"]
    assert sheet.getpixel((10, 10)) == PALETTE["yellow"]
    assert sheet.getpixel((10, 48 + 13)) == PALETTE["yellow_pressed"]


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    sheet = build_sheet()
    assert_contract(sheet)
    sheet.save(RUNTIME, optimize=True)
    write_metadata(sheet)
    build_review(sheet)
    print(f"built {RUNTIME}")
    print(f"built {METADATA}")
    print(f"built {REVIEW}")


if __name__ == "__main__":
    main()
