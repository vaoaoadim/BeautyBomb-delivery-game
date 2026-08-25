"""Build the approved Beauty Bomb intro UI v1 runtime assets.

The approved 360 x 640 layout master is immutable. This builder authors the
callout and CTA directly on their final pixel grids, then proves that frame 0
reconstructs the approved layout pixel-for-pixel over the current ready scene.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public/assets/game/ui"
REFERENCES = ROOT / "visual-references"
LAYOUT_MASTER = REFERENCES / "ui-005-intro-composition-v1.png"
LAYOUT_METADATA = REFERENCES / "ui-005-intro-composition-v1.json"
REVIEW = REFERENCES / "ui-intro-v1-review.png"
FONT_DIR = REFERENCES / "fonts/press-start-2p"
FONT_PATH = FONT_DIR / "PressStart2P-Regular.ttf"
FONT_LICENSE = FONT_DIR / "OFL.txt"

APPROVED_LAYOUT_SHA256 = (
    "556aeffae26052aef844e4ed252189ccbb070c679df65da0214279722d86630e"
)
APPROVED_FONT_SHA256 = (
    "034c77f1f05ec89421e4a63f0e3a4ca1ecf852cc6d2bf611f126f275728e017d"
)

CALLOUT_FILENAME = "ui-013-intro-callout-v1.png"
CTA_FILENAME = "ui-014-intro-tap-v1.png"
CALLOUT_CROP = (16, 154, 348, 361)
CALLOUT_RUNTIME_POSITION = (16, 154)
CTA_APPROVED_VISUAL_CROP = (126, 338, 234, 370)
CTA_FRAME_SIZE = (112, 36)
CTA_RUNTIME_CENTER = (180, 354)
TEXT_THRESHOLD = 128

PALETTE = {
    "ink": (29, 29, 27, 255),
    "violet": (30, 29, 62, 255),
    "purple": (152, 42, 221, 255),
    "lavender": (238, 240, 255, 255),
    "white": (255, 255, 255, 255),
    "cyan": (0, 183, 214, 255),
    "cyan_light": (84, 224, 255, 255),
    "pink": (255, 79, 171, 255),
    "yellow": (255, 239, 92, 255),
    "transparent": (0, 0, 0, 0),
}

FINAL_TEXT_LINES = (
    "ПОМОГИ КУРЬЕРУ",
    "ДОСТАВИТЬ КРЕМ!",
    "В ФИНАЛЕ ВАС",
    "НАГРАДЯТ КУПОНОМ.",
    "ЖМИ КНОПКИ СНИЗУ",
    "ИЛИ СТРЕЛКИ",
    "НА КЛАВИАТУРЕ.",
    "СЧАСТЛИВОГО ПУТИ!",
)

CTA_STATES = (
    {
        "name": "idle-yellow",
        "face": "yellow",
        "extrusion": "pink",
        "leftChevron": "pink",
        "rightChevron": "cyan_light",
    },
    {
        "name": "transition-pink",
        "face": "pink",
        "extrusion": "purple",
        "leftChevron": "cyan_light",
        "rightChevron": "yellow",
    },
    {
        "name": "transition-cyan",
        "face": "cyan_light",
        "extrusion": "yellow",
        "leftChevron": "yellow",
        "rightChevron": "pink",
    },
)


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def pixel_hash(image: Image.Image) -> str:
    return sha256(image.convert("RGBA").tobytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def paste_rgba(
    destination: Image.Image,
    source: Image.Image,
    position: tuple[int, int],
) -> None:
    destination.alpha_composite(source.convert("RGBA"), dest=position)


def threshold_mask(mask: Image.Image) -> Image.Image:
    return mask.point(lambda value: 255 if value >= TEXT_THRESHOLD else 0)


def colorize_mask(
    mask: Image.Image,
    color: tuple[int, int, int, int],
) -> Image.Image:
    layer = Image.new("RGBA", mask.size, color)
    layer.putalpha(mask)
    return layer


def assert_source_contract() -> None:
    if file_hash(LAYOUT_MASTER) != APPROVED_LAYOUT_SHA256:
        raise RuntimeError("Approved UI-005 layout master hash changed.")
    if file_hash(FONT_PATH) != APPROVED_FONT_SHA256:
        raise RuntimeError("Press Start 2P source hash changed.")
    if not FONT_LICENSE.exists():
        raise RuntimeError("Press Start 2P OFL.txt is missing.")
    if Image.open(LAYOUT_MASTER).size != (360, 640):
        raise RuntimeError("UI-005 layout master must remain 360 x 640.")


def assert_binary_alpha(image: Image.Image, label: str) -> None:
    alpha_histogram = image.convert("RGBA").getchannel("A").histogram()
    if sum(alpha_histogram[1:255]) != 0:
        raise RuntimeError(f"{label} contains antialiased alpha values.")


def draw_callout_layer(font: ImageFont.FreeTypeFont) -> Image.Image:
    layer = Image.new("RGBA", (360, 640), PALETTE["transparent"])
    draw = ImageDraw.Draw(layer)

    outer = [
        (24, 156),
        (336, 156),
        (342, 162),
        (342, 318),
        (336, 324),
        (24, 324),
        (18, 318),
        (18, 162),
    ]
    tail_outer = [
        (60, 320),
        (105, 320),
        (101, 333),
        (86, 354),
        (82, 329),
        (60, 329),
    ]
    draw.polygon([(x + 3, y + 4) for x, y in outer], fill=PALETTE["pink"])
    draw.polygon(
        [(x + 3, y + 4) for x, y in tail_outer],
        fill=PALETTE["pink"],
    )
    draw.polygon(outer, fill=PALETTE["violet"])
    draw.polygon(tail_outer, fill=PALETTE["violet"])

    inner = [
        (27, 161),
        (333, 161),
        (337, 165),
        (337, 315),
        (332, 319),
        (28, 319),
        (23, 314),
        (23, 166),
    ]
    tail_inner = [
        (67, 316),
        (98, 316),
        (95, 329),
        (87, 344),
        (87, 322),
        (67, 322),
    ]
    draw.polygon(inner, fill=PALETTE["lavender"])
    draw.polygon(tail_inner, fill=PALETTE["lavender"])
    draw.rectangle((316, 312, 329, 314), fill=PALETTE["yellow"])

    for line_index, line in enumerate(FINAL_TEXT_LINES):
        line_width = round(font.getlength(line))
        x = round(180 - line_width / 2)
        y = 168 + line_index * 18
        mask = Image.new("L", layer.size, 0)
        ImageDraw.Draw(mask).text((x, y), line, font=font, fill=255)
        layer.alpha_composite(
            colorize_mask(threshold_mask(mask), PALETTE["violet"])
        )

    return layer


def draw_cta_visual(
    font: ImageFont.FreeTypeFont,
    state: dict[str, str],
) -> Image.Image:
    layer = Image.new("RGBA", (360, 640), PALETTE["transparent"])
    draw = ImageDraw.Draw(layer)

    draw.polygon(
        [(126, 350), (136, 338), (144, 338), (134, 350), (144, 362), (136, 362)],
        fill=PALETTE["violet"],
    )
    draw.polygon(
        [(130, 350), (138, 342), (141, 342), (133, 350), (141, 358), (138, 358)],
        fill=PALETTE[state["leftChevron"]],
    )
    draw.polygon(
        [(234, 350), (224, 338), (216, 338), (226, 350), (216, 362), (224, 362)],
        fill=PALETTE["violet"],
    )
    draw.polygon(
        [(230, 350), (222, 342), (219, 342), (227, 350), (219, 358), (222, 358)],
        fill=PALETTE[state["rightChevron"]],
    )

    face_mask = Image.new("L", (72, 32), 0)
    ImageDraw.Draw(face_mask).text((12, 8), "ЖМИ", font=font, fill=255)
    face_mask = threshold_mask(face_mask)
    outline_mask = face_mask.filter(ImageFilter.MaxFilter(5))
    extrusion_mask = Image.new("L", face_mask.size, 0)
    extrusion_mask.paste(outline_mask, (3, 3))

    for mask, palette_name in (
        (extrusion_mask, state["extrusion"]),
        (outline_mask, "violet"),
        (face_mask, state["face"]),
    ):
        paste_rgba(
            layer,
            colorize_mask(mask, PALETTE[palette_name]),
            (144, 332),
        )

    return layer


def build_callout(font: ImageFont.FreeTypeFont) -> Image.Image:
    callout = draw_callout_layer(font).crop(CALLOUT_CROP)
    assert_binary_alpha(callout, "UI-013")
    return callout


def build_cta_sheet(font: ImageFont.FreeTypeFont) -> Image.Image:
    sheet = Image.new(
        "RGBA",
        (CTA_FRAME_SIZE[0], CTA_FRAME_SIZE[1] * len(CTA_STATES)),
        PALETTE["transparent"],
    )
    for frame_index, state in enumerate(CTA_STATES):
        visual = draw_cta_visual(font, state).crop(CTA_APPROVED_VISUAL_CROP)
        frame = Image.new("RGBA", CTA_FRAME_SIZE, PALETTE["transparent"])
        paste_rgba(frame, visual, (2, 2))
        paste_rgba(sheet, frame, (0, frame_index * CTA_FRAME_SIZE[1]))
    assert_binary_alpha(sheet, "UI-014")
    return sheet


def tile_crop(
    path: Path,
    scale_x: float,
    scale_y: float,
    width: int,
    height: int,
) -> Image.Image:
    source = Image.open(path).convert("RGBA")
    scaled = source.resize(
        (round(source.width * scale_x), round(source.height * scale_y)),
        Image.Resampling.NEAREST,
    )
    result = Image.new("RGBA", (width, height), PALETTE["transparent"])
    x = 0
    while x < width:
        crop_width = min(scaled.width, width - x)
        paste_rgba(
            result,
            scaled.crop((0, 0, crop_width, min(height, scaled.height))),
            (x, 0),
        )
        x += scaled.width
    return result


def build_ready_scene() -> Image.Image:
    scene = Image.new("RGBA", (360, 640), (115, 230, 247, 255))
    parallax = json.loads(
        (ROOT / "src/game/content/environmentParallax.json").read_text(
            encoding="utf-8"
        )
    )
    for layer in sorted(parallax["layers"], key=lambda item: item["depth"]):
        runtime_path = ROOT / "public" / layer["runtimePath"].lstrip("/")
        display_height = round(
            layer["contentCanvas"]["height"] * layer["tileScale"]["y"]
        )
        paste_rgba(
            scene,
            tile_crop(
                runtime_path,
                layer["tileScale"]["x"],
                layer["tileScale"]["y"],
                360,
                display_height,
            ),
            (layer["position"]["x"], layer["position"]["y"]),
        )

    ui_path = ROOT / "public/assets/game/ui"
    paste_rgba(scene, Image.open(ui_path / "ui-008-control-panel-v1.png"), (0, 522))

    title = Image.open(ui_path / "ui-009-game-title-v1.png").convert("RGBA")
    paste_rgba(scene, title, (round(180 - title.width / 2), round(38 - title.height / 2)))

    heart_sheet = Image.open(ui_path / "ico-001-life-heart-v1.png").convert("RGBA")
    heart = heart_sheet.crop((0, 0, 20, 18))
    for heart_index in range(3):
        paste_rgba(scene, heart, (18 + heart_index * 22, 106))

    paste_rgba(scene, Image.open(ui_path / "ui-003-progress-bar-v1.png"), (18, 134))

    controls = Image.open(ui_path / "ui-004-touch-controls-v1.png").convert("RGBA")
    for frame_y, center_x in ((0, 111), (96, 249)):
        frame = controls.crop((0, frame_y, 76, frame_y + 48)).resize(
            (114, 72),
            Image.Resampling.NEAREST,
        )
        paste_rgba(scene, frame, (center_x - 57, 536))

    player_sheet = Image.open(
        ROOT / "public/assets/game/vehicles/veh-001-courier-clean-drive-v6.png"
    ).convert("RGBA")
    player_scale = 1.22 * 0.5
    player = player_sheet.crop((0, 0, 208, 160)).resize(
        (round(208 * player_scale), round(160 * player_scale)),
        Image.Resampling.NEAREST,
    )
    paste_rgba(
        scene,
        player,
        (
            round(74 - 104 * player_scale),
            round(424 - 152 * player_scale),
        ),
    )
    return scene


def compose_runtime_preview(
    ready_scene: Image.Image,
    callout: Image.Image,
    cta_sheet: Image.Image,
) -> Image.Image:
    preview = ready_scene.copy()
    paste_rgba(preview, callout, CALLOUT_RUNTIME_POSITION)
    idle_frame = cta_sheet.crop((0, 0, CTA_FRAME_SIZE[0], CTA_FRAME_SIZE[1]))
    paste_rgba(
        preview,
        idle_frame,
        (
            CTA_RUNTIME_CENTER[0] - CTA_FRAME_SIZE[0] // 2,
            CTA_RUNTIME_CENTER[1] - CTA_FRAME_SIZE[1] // 2,
        ),
    )
    return preview


def assert_layout_reproduction(preview: Image.Image) -> None:
    approved = Image.open(LAYOUT_MASTER).convert("RGBA")
    difference = ImageChops.difference(preview, approved)
    if difference.getbbox() is not None:
        bbox = difference.getbbox()
        raise RuntimeError(
            f"Runtime assets do not reproduce approved UI-005 pixels; difference={bbox}."
        )


def checkerboard(size: tuple[int, int], cell: int = 8) -> Image.Image:
    image = Image.new("RGBA", size, PALETTE["lavender"])
    draw = ImageDraw.Draw(image)
    alternate = (207, 204, 237, 255)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2:
                draw.rectangle(
                    (x, y, min(size[0] - 1, x + cell - 1), min(size[1] - 1, y + cell - 1)),
                    fill=alternate,
                )
    return image


def write_review(
    preview: Image.Image,
    callout: Image.Image,
    cta_sheet: Image.Image,
) -> None:
    review = Image.new("RGBA", (1200, 840), PALETTE["ink"])
    label_font = ImageFont.load_default()
    draw = ImageDraw.Draw(review)
    draw.text((24, 20), "UI-005 APPROVED RUNTIME COMPOSITION - NATIVE 360 x 640", font=label_font, fill=PALETTE["white"])
    paste_rgba(review, preview, (24, 48))

    draw.text((420, 20), "UI-013 NATIVE 332 x 207", font=label_font, fill=PALETTE["white"])
    native_panel = checkerboard(callout.size)
    paste_rgba(native_panel, callout, (0, 0))
    paste_rgba(review, native_panel, (420, 48))

    draw.text((800, 20), "UI-014 NATIVE FRAMES 112 x 36", font=label_font, fill=PALETTE["white"])
    for frame_index, state in enumerate(CTA_STATES):
        frame = cta_sheet.crop(
            (
                0,
                frame_index * CTA_FRAME_SIZE[1],
                CTA_FRAME_SIZE[0],
                (frame_index + 1) * CTA_FRAME_SIZE[1],
            )
        )
        panel = checkerboard(CTA_FRAME_SIZE, 4)
        paste_rgba(panel, frame, (0, 0))
        y = 48 + frame_index * 58
        paste_rgba(review, panel, (800, y))
        draw.text((924, y + 12), state["name"], font=label_font, fill=PALETTE["white"])

    draw.text((420, 276), "UI-013 NEAREST PREVIEW 2x", font=label_font, fill=PALETTE["white"])
    callout_2x = callout.resize(
        (callout.width * 2, callout.height * 2),
        Image.Resampling.NEAREST,
    )
    large_panel = checkerboard(callout_2x.size, 16)
    paste_rgba(large_panel, callout_2x, (0, 0))
    paste_rgba(review, large_panel, (420, 304))

    draw.text((420, 736), "UI-014 NEAREST PREVIEW 2x - ALL COLOR STATES", font=label_font, fill=PALETTE["white"])
    for frame_index in range(len(CTA_STATES)):
        frame = cta_sheet.crop(
            (
                0,
                frame_index * CTA_FRAME_SIZE[1],
                CTA_FRAME_SIZE[0],
                (frame_index + 1) * CTA_FRAME_SIZE[1],
            )
        ).resize(
            (CTA_FRAME_SIZE[0] * 2, CTA_FRAME_SIZE[1] * 2),
            Image.Resampling.NEAREST,
        )
        panel = checkerboard(frame.size, 8)
        paste_rgba(panel, frame, (0, 0))
        paste_rgba(review, panel, (420 + frame_index * 240, 760))

    review.save(REVIEW, optimize=True)


def write_metadata(callout_path: Path, cta_path: Path) -> None:
    common_production = {
        "buildScript": "scripts/build_intro_ui_v1.py",
        "assetMode": "authored-low-resolution-pixel-art",
        "layoutMaster": "visual-references/ui-005-intro-composition-v1.png",
        "layoutMasterSha256": APPROVED_LAYOUT_SHA256,
        "fontSource": "visual-references/fonts/press-start-2p/PressStart2P-Regular.ttf",
        "fontSha256": APPROVED_FONT_SHA256,
        "fontLicense": "visual-references/fonts/press-start-2p/OFL.txt",
        "fontLicenseId": "SIL-OFL-1.1",
        "offlineResizeCount": 0,
        "antialiasing": False,
        "textMaskThreshold": TEXT_THRESHOLD,
        "paletteQuantization": False,
        "phaserTextureFilter": "nearest",
    }

    write_json(
        LAYOUT_METADATA,
        {
            "assetId": "UI-005",
            "version": "v1",
            "status": "approved-layout-master",
            "canvas": {"width": 360, "height": 640},
            "sha256": APPROVED_LAYOUT_SHA256,
            "copy": list(FINAL_TEXT_LINES),
            "layout": {
                "calloutRuntimePosition": {"x": 16, "y": 154},
                "bubbleRect": {"x": 18, "y": 156, "width": 324, "height": 168},
                "textSafeRect": {"x": 36, "y": 168, "width": 288, "height": 142},
                "tailTip": {"x": 86, "y": 354},
                "ctaCenter": {"x": 180, "y": 354},
                "courierReviewBounds": {"x": 11, "y": 331, "width": 127, "height": 98},
            },
            "runtimeAssets": ["UI-013", "UI-014"],
        },
    )

    write_json(
        callout_path.with_suffix(".json"),
        {
            "assetId": "UI-013",
            "version": "v1",
            "status": "produced-awaiting-integration",
            "texture": CALLOUT_FILENAME,
            "canvas": {"width": 332, "height": 207},
            "frame": {"width": 332, "height": 207, "count": 1},
            "copy": list(FINAL_TEXT_LINES),
            "font": {"family": "Press Start 2P", "sizePx": 16},
            "palette": {key: "#" + "".join(f"{channel:02x}" for channel in value[:3]) for key, value in PALETTE.items() if key != "transparent"},
            "production": {
                **common_production,
                "runtimeSha256": file_hash(callout_path),
                "runtimePixelSha256": pixel_hash(Image.open(callout_path)),
            },
            "runtime": {
                "position": {"x": 16, "y": 154},
                "origin": {"x": 0, "y": 0},
                "transparentPaddingPx": 2,
                "tailTip": {"x": 86, "y": 354},
                "fixedToCamera": True,
            },
        },
    )

    write_json(
        cta_path.with_suffix(".json"),
        {
            "assetId": "UI-014",
            "version": "v1",
            "status": "produced-awaiting-integration",
            "texture": CTA_FILENAME,
            "canvas": {"width": 112, "height": 108},
            "frame": {
                "width": 112,
                "height": 36,
                "count": 3,
                "states": [state["name"] for state in CTA_STATES],
                "visualRect": {"x": 2, "y": 2, "width": 108, "height": 32},
            },
            "production": {
                **common_production,
                "runtimeSha256": file_hash(cta_path),
                "runtimePixelSha256": pixel_hash(Image.open(cta_path)),
            },
            "runtime": {
                "center": {"x": 180, "y": 354},
                "origin": {"x": 0.5, "y": 0.5},
                "frameOrder": [0, 1, 2],
                "idleFrame": 0,
                "transitionColorFrames": [0, 1, 2],
                "transparentPaddingPx": 2,
                "fixedToCamera": True,
            },
        },
    )


def main() -> None:
    assert_source_contract()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype(str(FONT_PATH), 16)

    callout = build_callout(font)
    cta_sheet = build_cta_sheet(font)
    callout_path = OUTPUT / CALLOUT_FILENAME
    cta_path = OUTPUT / CTA_FILENAME
    callout.save(callout_path, optimize=True)
    cta_sheet.save(cta_path, optimize=True)

    preview = compose_runtime_preview(build_ready_scene(), callout, cta_sheet)
    assert_layout_reproduction(preview)
    write_metadata(callout_path, cta_path)
    write_review(preview, callout, cta_sheet)

    print(f"layout={LAYOUT_MASTER}")
    print(f"callout={callout_path} sha256={file_hash(callout_path)}")
    print(f"cta={cta_path} sha256={file_hash(cta_path)}")
    print(f"review={REVIEW}")
    print("layoutReproduction=pixel-identical")


if __name__ == "__main__":
    main()
