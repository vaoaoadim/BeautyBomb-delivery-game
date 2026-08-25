"""Build the deterministic Beauty Bomb arcade HUD v1 asset kit."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter


OUTPUT = Path("public/assets/game/ui")
REVIEW = Path("visual-references/ui-hud-v1-review.png")
TITLE_REVIEW = Path("visual-references/ui-game-title-v1-review.png")

PALETTE = {
    "ink": (29, 29, 27, 255),
    "violet": (30, 29, 62, 255),
    "purple": (152, 42, 221, 255),
    "lavender": (238, 240, 255, 255),
    "lavender_shadow": (207, 204, 237, 255),
    "cream": (255, 243, 220, 255),
    "white": (255, 255, 255, 255),
    "cyan": (0, 183, 214, 255),
    "cyan_light": (84, 224, 255, 255),
    "pink": (255, 79, 171, 255),
    "pink_shadow": (210, 43, 133, 255),
    "yellow": (255, 239, 92, 255),
    "yellow_pressed": (218, 215, 61, 255),
}


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def save_asset(
    image: Image.Image,
    filename: str,
    *,
    asset_id: str,
    frame: dict[str, Any],
    runtime: dict[str, Any],
) -> tuple[Path, Image.Image]:
    path = OUTPUT / filename
    image.save(path, optimize=True)
    write_json(
        path.with_suffix(".json"),
        {
            "assetId": asset_id,
            "version": "v1",
            "status": "integrated",
            "texture": filename,
            "canvas": {"width": image.width, "height": image.height},
            "frame": frame,
            "palette": {name: "#" + "".join(f"{channel:02x}" for channel in color[:3]) for name, color in PALETTE.items()},
            "production": {
                "buildScript": "scripts/build_hud_ui_v1.py",
                "assetMode": "authored-low-resolution-pixel-art",
                "offlineResizeCount": 0,
                "antialiasing": False,
                "paletteQuantization": False,
                "phaserTextureFilter": "nearest",
                "runtimeSha256": file_hash(path),
            },
            "runtime": runtime,
        },
    )
    return path, image


def draw_heart_frame(canvas: Image.Image, offset_x: int, filled: bool) -> None:
    draw = ImageDraw.Draw(canvas)
    outline = [
        (offset_x + 4, 1),
        (offset_x + 8, 1),
        (offset_x + 10, 3),
        (offset_x + 12, 1),
        (offset_x + 16, 1),
        (offset_x + 19, 4),
        (offset_x + 19, 9),
        (offset_x + 10, 18),
        (offset_x + 1, 9),
        (offset_x + 1, 4),
    ]
    draw.polygon(outline, fill=PALETTE["violet"])
    inner = [
        (offset_x + 5, 4),
        (offset_x + 8, 4),
        (offset_x + 10, 6),
        (offset_x + 12, 4),
        (offset_x + 15, 4),
        (offset_x + 17, 6),
        (offset_x + 17, 8),
        (offset_x + 10, 15),
        (offset_x + 3, 8),
        (offset_x + 3, 6),
    ]
    draw.polygon(
        inner,
        fill=PALETTE["pink"] if filled else PALETTE["lavender_shadow"],
    )
    if filled:
        draw.rectangle((offset_x + 5, 4, offset_x + 7, 5), fill=PALETTE["yellow"])
        draw.point((offset_x + 4, 7), fill=PALETTE["white"])
        draw.rectangle((offset_x + 7, 12, offset_x + 9, 13), fill=PALETTE["pink_shadow"])
    else:
        draw.rectangle((offset_x + 5, 4, offset_x + 7, 5), fill=PALETTE["cream"])


def build_hearts() -> Image.Image:
    image = Image.new("RGBA", (40, 18), (0, 0, 0, 0))
    draw_heart_frame(image, 0, True)
    draw_heart_frame(image, 20, False)
    return image


def build_progress_frame() -> Image.Image:
    image = Image.new("RGBA", (324, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    outline = [(4, 0), (320, 0), (324, 4), (324, 12), (320, 16), (4, 16), (0, 12), (0, 4)]
    draw.polygon(outline, fill=PALETTE["violet"])
    inner = [(4, 3), (320, 3), (321, 4), (321, 12), (320, 13), (4, 13), (3, 12), (3, 4)]
    draw.polygon(inner, fill=PALETTE["cyan"])
    draw.line((5, 4, 310, 4), fill=PALETTE["cyan_light"], width=1)
    draw.rectangle((314, 1, 316, 3), fill=PALETTE["yellow"])
    draw.point((313, 2), fill=PALETTE["yellow"])
    draw.point((317, 2), fill=PALETTE["yellow"])
    draw.point((315, 0), fill=PALETTE["white"])
    draw.rectangle((5, 13, 319, 14), fill=PALETTE["purple"])
    return image


def arrow_points(direction: str, y_shift: int) -> list[tuple[int, int]]:
    if direction == "up":
        return [
            (38, 12 + y_shift),
            (49, 25 + y_shift),
            (44, 25 + y_shift),
            (44, 32 + y_shift),
            (32, 32 + y_shift),
            (32, 25 + y_shift),
            (27, 25 + y_shift),
        ]
    return [
        (27, 19 + y_shift),
        (32, 19 + y_shift),
        (32, 12 + y_shift),
        (44, 12 + y_shift),
        (44, 19 + y_shift),
        (49, 19 + y_shift),
        (38, 32 + y_shift),
    ]


def draw_button_frame(
    sheet: Image.Image,
    frame_y: int,
    direction: str,
    pressed: bool,
) -> None:
    frame = Image.new("RGBA", (76, 48), (0, 0, 0, 0))
    draw = ImageDraw.Draw(frame)
    if pressed:
        face_top = 4
        face_bottom = 45
        shadow_top = 44
        arrow_shift = 3
        surface = PALETTE["yellow_pressed"]
    else:
        face_top = 0
        face_bottom = 42
        shadow_top = 40
        arrow_shift = 0
        surface = PALETTE["yellow"]

    shadow = [(4, shadow_top), (72, shadow_top), (76, shadow_top + 4), (76, 47), (0, 47), (0, shadow_top + 4)]
    draw.polygon(shadow, fill=PALETTE["purple"])
    outer = [(4, face_top), (72, face_top), (76, face_top + 4), (76, face_bottom - 4), (72, face_bottom), (4, face_bottom), (0, face_bottom - 4), (0, face_top + 4)]
    draw.polygon(outer, fill=PALETTE["violet"])
    inner = [(5, face_top + 4), (71, face_top + 4), (72, face_top + 5), (72, face_bottom - 5), (71, face_bottom - 4), (5, face_bottom - 4), (4, face_bottom - 5), (4, face_top + 5)]
    draw.polygon(inner, fill=surface)
    draw.line((8, face_top + 5, 58, face_top + 5), fill=PALETTE["white"], width=2)
    draw.polygon(arrow_points(direction, arrow_shift), fill=PALETTE["violet"])
    sheet.alpha_composite(frame, (0, frame_y))


def build_controls() -> Image.Image:
    sheet = Image.new("RGBA", (76, 192), (0, 0, 0, 0))
    draw_button_frame(sheet, 0, "up", False)
    draw_button_frame(sheet, 48, "up", True)
    draw_button_frame(sheet, 96, "down", False)
    draw_button_frame(sheet, 144, "down", True)
    return sheet


def draw_pause_frame(sheet: Image.Image, frame_y: int, pressed: bool) -> None:
    frame = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(frame)
    face_top = 3 if pressed else 0
    face_bottom = 30 if pressed else 27
    surface = PALETTE["yellow_pressed"] if pressed else PALETTE["yellow"]
    icon_shift = 2 if pressed else 0

    draw.polygon(
        ((3, 26), (29, 26), (32, 29), (32, 31), (0, 31), (0, 29)),
        fill=PALETTE["purple"],
    )
    draw.polygon(
        (
            (3, face_top),
            (29, face_top),
            (32, face_top + 3),
            (32, face_bottom - 3),
            (29, face_bottom),
            (3, face_bottom),
            (0, face_bottom - 3),
            (0, face_top + 3),
        ),
        fill=PALETTE["violet"],
    )
    draw.rectangle((4, face_top + 4, 27, face_bottom - 4), fill=surface)
    draw.line((6, face_top + 5, 21, face_top + 5), fill=PALETTE["white"], width=1)
    pause_bar_top = 8 + icon_shift
    pause_bar_width = 4
    pause_bar_height = 13
    pause_bar_left = 10
    pause_bar_right = pause_bar_left + pause_bar_width + 4
    for x in (pause_bar_left, pause_bar_right):
        draw.rectangle(
            (x, pause_bar_top, x + pause_bar_width - 1, pause_bar_top + pause_bar_height - 1),
            fill=PALETTE["ink"],
        )
    sheet.alpha_composite(frame, (0, frame_y))


def build_pause_control() -> Image.Image:
    sheet = Image.new("RGBA", (32, 64), (0, 0, 0, 0))
    draw_pause_frame(sheet, 0, False)
    draw_pause_frame(sheet, 32, True)
    return sheet


def draw_exit_frame(sheet: Image.Image, frame_y: int, pressed: bool) -> None:
    frame = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(frame)
    face_top = 3 if pressed else 0
    face_bottom = 30 if pressed else 27
    surface = PALETTE["yellow_pressed"] if pressed else PALETTE["yellow"]
    icon_shift = 2 if pressed else 0

    draw.polygon(
        ((3, 26), (29, 26), (32, 29), (32, 31), (0, 31), (0, 29)),
        fill=PALETTE["purple"],
    )
    draw.polygon(
        (
            (3, face_top),
            (29, face_top),
            (32, face_top + 3),
            (32, face_bottom - 3),
            (29, face_bottom),
            (3, face_bottom),
            (0, face_bottom - 3),
            (0, face_top + 3),
        ),
        fill=PALETTE["violet"],
    )
    draw.rectangle((4, face_top + 4, 27, face_bottom - 4), fill=surface)
    draw.line((6, face_top + 5, 21, face_top + 5), fill=PALETTE["white"], width=1)

    top = 8 + icon_shift
    bottom = 22 + icon_shift
    draw.rectangle((8, top, 10, bottom), fill=PALETTE["ink"])
    draw.rectangle((8, top, 19, top + 2), fill=PALETTE["ink"])
    draw.rectangle((8, bottom - 2, 19, bottom), fill=PALETTE["ink"])
    draw.polygon(
        ((13, top + 3), (22, top + 1), (22, bottom - 1), (13, bottom - 3)),
        fill=PALETTE["ink"],
    )
    draw.polygon(
        ((15, top + 5), (20, top + 4), (20, bottom - 4), (15, bottom - 5)),
        fill=surface,
    )
    draw.rectangle((18, top + 8, 19, top + 9), fill=PALETTE["ink"])
    sheet.alpha_composite(frame, (0, frame_y))


def build_exit_control() -> Image.Image:
    sheet = Image.new("RGBA", (32, 64), (0, 0, 0, 0))
    draw_exit_frame(sheet, 0, False)
    draw_exit_frame(sheet, 32, True)
    return sheet


def draw_sound_tab_frame(sheet: Image.Image, frame_y: int, pressed: bool) -> None:
    frame = Image.new("RGBA", (28, 28), (0, 0, 0, 0))
    draw = ImageDraw.Draw(frame)
    face_top = 3 if pressed else 0
    face_bottom = 26 if pressed else 23
    surface = PALETTE["yellow_pressed"] if pressed else PALETTE["yellow"]
    icon_shift = 2 if pressed else 0

    draw.polygon(
        ((3, 22), (28, 22), (28, 27), (0, 27), (0, 25)),
        fill=PALETTE["purple"],
    )
    draw.polygon(
        (
            (3, face_top),
            (28, face_top),
            (28, face_bottom),
            (3, face_bottom),
            (0, face_bottom - 3),
            (0, face_top + 3),
        ),
        fill=PALETTE["violet"],
    )
    draw.polygon(
        (
            (4, face_top + 4),
            (27, face_top + 4),
            (27, face_bottom - 4),
            (4, face_bottom - 4),
            (3, face_bottom - 5),
            (3, face_top + 5),
        ),
        fill=surface,
    )
    draw.line((6, face_top + 5, 20, face_top + 5), fill=PALETTE["white"], width=1)

    top = 9 + icon_shift
    draw.rectangle((7, top + 3, 10, top + 8), fill=PALETTE["ink"])
    draw.polygon(((10, top + 3), (15, top), (15, top + 11), (10, top + 8)), fill=PALETTE["ink"])
    draw.line((18, top + 3, 20, top + 5, 20, top + 7, 18, top + 9), fill=PALETTE["ink"], width=2)
    sheet.alpha_composite(frame, (0, frame_y))


def build_sound_tab() -> Image.Image:
    sheet = Image.new("RGBA", (28, 56), (0, 0, 0, 0))
    draw_sound_tab_frame(sheet, 0, False)
    draw_sound_tab_frame(sheet, 28, True)
    return sheet


def build_control_panel() -> Image.Image:
    image = Image.new("RGBA", (360, 118), PALETTE["cyan"])
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 359, 1), fill=PALETTE["violet"])
    draw.rectangle((0, 2, 359, 4), fill=PALETTE["yellow"])
    draw.rectangle((0, 5, 359, 6), fill=PALETTE["purple"])
    draw.rectangle((0, 7, 359, 8), fill=PALETTE["cyan_light"])
    return image


TITLE_GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
}


def colorize_mask(mask: Image.Image, color: tuple[int, int, int, int]) -> Image.Image:
    layer = Image.new("RGBA", mask.size, color)
    layer.putalpha(mask)
    return layer


def build_game_title() -> Image.Image:
    text = "BEAUTY BOMB DELIVERY"
    scale = 2
    glyph_width = 5 * scale
    glyph_gap = 2
    space_width = 6
    advances = [space_width if character == " " else glyph_width for character in text]
    text_width = sum(advances) + glyph_gap * (len(text) - 1)
    canvas = Image.new("RGBA", (text_width + 12, 28), (0, 0, 0, 0))
    face = Image.new("L", canvas.size, 0)
    draw = ImageDraw.Draw(face)
    cursor_x = 4
    origin_y = 3
    word_starts: list[int] = []
    at_word_start = True

    for index, character in enumerate(text):
        if character == " ":
            cursor_x += space_width
            at_word_start = True
        else:
            if at_word_start:
                word_starts.append(cursor_x)
                at_word_start = False
            for row, bits in enumerate(TITLE_GLYPHS[character]):
                for column, bit in enumerate(bits):
                    if bit == "1":
                        x = cursor_x + column * scale
                        y = origin_y + row * scale
                        draw.rectangle((x, y, x + scale - 1, y + scale - 1), fill=255)
            cursor_x += glyph_width
        if index < len(text) - 1:
            cursor_x += glyph_gap

    outline = face.filter(ImageFilter.MaxFilter(5))
    extruded_outline = Image.new("L", canvas.size, 0)
    extruded_outline.paste(outline, (3, 3))
    extrusion = Image.new("L", canvas.size, 0)
    extrusion.paste(face, (3, 3))

    canvas.alpha_composite(colorize_mask(extruded_outline, PALETTE["violet"]))
    canvas.alpha_composite(colorize_mask(extrusion, PALETTE["pink"]))
    canvas.alpha_composite(colorize_mask(outline, PALETTE["violet"]))
    canvas.alpha_composite(colorize_mask(face, PALETTE["yellow"]))

    highlights = ImageDraw.Draw(canvas)
    for word_x in word_starts:
        highlights.point((word_x, origin_y), fill=PALETTE["white"])
        highlights.point((word_x + 1, origin_y), fill=PALETTE["cyan_light"])
    return canvas


def write_title_review(title: Image.Image) -> None:
    review = Image.new("RGBA", (720, 220), PALETTE["ink"])
    enlarged = title.resize((title.width * 2, title.height * 2), Image.Resampling.NEAREST)
    review.alpha_composite(enlarged, ((720 - enlarged.width) // 2, 18))

    native_panel = Image.new("RGBA", (360, 120), PALETTE["violet"])
    native_panel.alpha_composite(title, ((360 - title.width) // 2, 28))
    review.alpha_composite(native_panel, (0, 100))

    game_panel = Image.new("RGBA", (360, 120), (82, 203, 238, 255))
    game_draw = ImageDraw.Draw(game_panel)
    game_draw.polygon(((48, 82), (68, 62), (82, 73), (98, 50), (120, 82)), fill=PALETTE["white"])
    game_draw.rectangle((48, 82, 120, 88), fill=PALETTE["white"])
    game_panel.alpha_composite(title, ((360 - title.width) // 2, 18))
    review.alpha_composite(game_panel, (360, 100))
    review.save(TITLE_REVIEW, optimize=True)


def write_review(assets: dict[str, Image.Image]) -> None:
    review = Image.new("RGBA", (720, 360), PALETTE["ink"])
    panel = assets["panel"]
    review.alpha_composite(panel, (0, 242))
    review.alpha_composite(panel, (360, 242))

    hearts = assets["hearts"].resize((160, 72), Image.Resampling.NEAREST)
    progress = assets["progress"].resize((648, 32), Image.Resampling.NEAREST)
    controls = assets["controls"]
    up = controls.crop((0, 0, 76, 48)).resize((152, 96), Image.Resampling.NEAREST)
    down = controls.crop((0, 96, 76, 144)).resize((152, 96), Image.Resampling.NEAREST)
    pause = assets["pause"].crop((0, 0, 32, 32)).resize((96, 96), Image.Resampling.NEAREST)
    exit_button = assets["exit"].crop((0, 0, 32, 32)).resize((96, 96), Image.Resampling.NEAREST)
    sound = assets["sound"].crop((0, 0, 28, 28)).resize((84, 84), Image.Resampling.NEAREST)
    review.alpha_composite(hearts, (24, 24))
    review.alpha_composite(progress, (36, 116))
    review.alpha_composite(up, (120, 164))
    review.alpha_composite(down, (448, 164))
    review.alpha_composite(pause, (312, 18))
    review.alpha_composite(exit_button, (204, 18))
    review.alpha_composite(sound, (624, 250))
    review.save(REVIEW, optimize=True)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    assets = {
        "hearts": build_hearts(),
        "progress": build_progress_frame(),
        "controls": build_controls(),
        "pause": build_pause_control(),
        "exit": build_exit_control(),
        "sound": build_sound_tab(),
        "panel": build_control_panel(),
        "title": build_game_title(),
    }
    save_asset(
        assets["hearts"],
        "ico-001-life-heart-v1.png",
        asset_id="ICO-001",
        frame={"width": 20, "height": 18, "count": 2, "states": ["full", "empty"]},
        runtime={"position": {"x": 18, "y": 106}, "gapPx": 2, "maxLives": 3},
    )
    save_asset(
        assets["progress"],
        "ui-003-progress-bar-v1.png",
        asset_id="UI-003",
        frame={"width": 324, "height": 16, "count": 1},
        runtime={"position": {"x": 18, "y": 134}, "fillRect": {"x": 20, "centerY": 142, "width": 320, "height": 8}},
    )
    save_asset(
        assets["controls"],
        "ui-004-touch-controls-v1.png",
        asset_id="UI-004",
        frame={"width": 76, "height": 48, "count": 4, "states": ["up", "up-pressed", "down", "down-pressed"]},
        runtime={
            "centers": [{"x": 111, "y": 572}, {"x": 249, "y": 572}],
            "displayScale": 1.5,
            "hitArea": {"width": 114, "height": 72},
            "bottomClearancePx": 32,
        },
    )
    save_asset(
        assets["pause"],
        "ui-010-pause-button-v1.png",
        asset_id="UI-010",
        frame={"width": 32, "height": 32, "count": 2, "states": ["idle", "pressed"]},
        runtime={
            "center": {"x": 332, "y": 32},
            "edgeInsets": {"top": 16, "right": 12},
            "fixedToCamera": True,
        },
    )
    save_asset(
        assets["exit"],
        "ui-011-exit-button-v1.png",
        asset_id="UI-011",
        frame={"width": 32, "height": 32, "count": 2, "states": ["idle", "pressed"]},
        runtime={
            "center": {"x": 28, "y": 32},
            "edgeInsets": {"top": 16, "left": 12},
            "fixedToCamera": True,
            "behavior": "visual-placeholder",
            "futureAction": "exit-game",
        },
    )
    save_asset(
        assets["sound"],
        "ui-012-sound-tab-v1.png",
        asset_id="UI-012",
        frame={"width": 28, "height": 28, "count": 2, "states": ["idle", "pressed"]},
        runtime={
            "center": {"x": 346, "y": 540},
            "attachedPanelEdge": "right",
            "fixedToCamera": True,
            "behavior": "visual-placeholder",
            "futureAction": "toggle-sound",
        },
    )
    save_asset(
        assets["panel"],
        "ui-008-control-panel-v1.png",
        asset_id="UI-008",
        frame={"width": 360, "height": 118, "count": 1},
        runtime={"position": {"x": 0, "y": 522}, "fixedToCamera": True},
    )
    save_asset(
        assets["title"],
        "ui-009-game-title-v1.png",
        asset_id="UI-009",
        frame={"width": assets["title"].width, "height": assets["title"].height, "count": 1},
        runtime={
            "position": {"x": 180, "y": 38},
            "origin": {"x": 0.5, "y": 0.5},
            "fixedToCamera": True,
            "text": "BEAUTY BOMB DELIVERY",
        },
    )
    write_review(assets)
    write_title_review(assets["title"])
    print(f"assets={OUTPUT}")
    print(f"review={REVIEW}")
    print(f"titleReview={TITLE_REVIEW}")


if __name__ == "__main__":
    main()
