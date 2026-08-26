"""Build UI-016 v5 with an unaccented tail aimed at CHR-001 v2."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public/assets/game/ui"
FONT_PATH = ROOT / "visual-references/fonts/press-start-2p/PressStart2P-Regular.ttf"
FONT_LICENSE = ROOT / "visual-references/fonts/press-start-2p/OFL.txt"
INTRO_CALLOUT = OUTPUT / "ui-013-intro-callout-v3.png"

APPROVED_FONT_SHA256 = "034c77f1f05ec89421e4a63f0e3a4ca1ecf852cc6d2bf611f126f275728e017d"
APPROVED_INTRO_SHA256 = "096d26a25d6cf381c559e83a8d7a36832aa2fa6e9680ee8136e0665808a24edb"

CALLOUT_FILE = OUTPUT / "ui-016-delivery-callout-v5.png"
CALLOUT_SIZE = (332, 104)
RUNTIME_POSITION = {"x": 14, "y": 338, "originX": 0, "originY": 0}
TAIL_POINT_LOCAL = (276, 0)
TAIL_TARGET_RUNTIME = (290, 324)

PALETTE = {
    "violet": (30, 29, 62, 255),
    "lavender": (238, 240, 255, 255),
    "pink": (255, 79, 171, 255),
    "transparent": (0, 0, 0, 0),
}

TEXT_LINES = (
    "БОЛЬШОЕ СПАСИБО!",
    "ТЕПЕРЬ МОЖЕШЬ",
    "ЗАБРАТЬ НАГРАДУ!",
)


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def threshold(mask: Image.Image) -> Image.Image:
    return mask.point(lambda value: 255 if value >= 128 else 0)


def colorize(mask: Image.Image, color: tuple[int, int, int, int]) -> Image.Image:
    layer = Image.new("RGBA", mask.size, color)
    layer.putalpha(mask)
    return layer


def assert_binary_alpha(image: Image.Image) -> None:
    histogram = image.getchannel("A").histogram()
    if sum(histogram[1:255]) != 0:
        raise RuntimeError("UI-016 v5 contains antialiased alpha values")


def assert_tail_has_no_pink_outline(image: Image.Image) -> None:
    tail_cap = image.crop((245, 0, 301, 30))
    colors = tail_cap.getcolors(maxcolors=tail_cap.width * tail_cap.height) or []
    if any(color == PALETTE["pink"] for _, color in colors):
        raise RuntimeError("UI-016 v5 tail still contains pink outline pixels")


def build_callout(font: ImageFont.FreeTypeFont) -> Image.Image:
    image = Image.new("RGBA", CALLOUT_SIZE, PALETTE["transparent"])
    draw = ImageDraw.Draw(image)

    outer = [
        (8, 30),
        (318, 30),
        (326, 38),
        (326, 92),
        (318, 100),
        (8, 100),
        (0, 92),
        (0, 38),
    ]
    inner = [
        (11, 35),
        (315, 35),
        (321, 41),
        (321, 89),
        (315, 95),
        (11, 95),
        (5, 89),
        (5, 41),
    ]

    # UI-013's approved tail is reflected upward and translated to the
    # recipient. The tail deliberately receives no pink shadow/outline.
    tail_outer = [
        (250, 34),
        (295, 34),
        (291, 21),
        (276, 0),
        (272, 25),
        (250, 25),
    ]
    tail_inner = [
        (256, 38),
        (287, 38),
        (284, 25),
        (276, 10),
        (276, 32),
        (256, 32),
    ]

    draw.polygon([(x + 3, y + 4) for x, y in outer], fill=PALETTE["pink"])
    draw.polygon(outer, fill=PALETTE["violet"])
    draw.polygon(tail_outer, fill=PALETTE["violet"])
    draw.polygon(inner, fill=PALETTE["lavender"])
    draw.polygon(tail_inner, fill=PALETTE["lavender"])

    for index, line in enumerate(TEXT_LINES):
        width = round(font.getlength(line))
        x = round(CALLOUT_SIZE[0] / 2 - width / 2)
        y = 43 + index * 20
        mask = Image.new("L", CALLOUT_SIZE, 0)
        ImageDraw.Draw(mask).text((x, y), line, font=font, fill=255)
        image.alpha_composite(colorize(threshold(mask), PALETTE["violet"]))

    assert_binary_alpha(image)
    assert_tail_has_no_pink_outline(image)
    return image


def main() -> None:
    if file_hash(FONT_PATH) != APPROVED_FONT_SHA256 or not FONT_LICENSE.exists():
        raise RuntimeError("Press Start 2P source contract changed")
    if file_hash(INTRO_CALLOUT) != APPROVED_INTRO_SHA256:
        raise RuntimeError("Approved UI-013 v3 reference changed")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    callout = build_callout(ImageFont.truetype(str(FONT_PATH), 10))
    callout.save(CALLOUT_FILE, optimize=True)

    write_json(
        CALLOUT_FILE.with_suffix(".json"),
        {
            "assetId": "UI-016",
            "version": "v5",
            "status": "integrated",
            "texture": CALLOUT_FILE.name,
            "canvas": {"width": CALLOUT_SIZE[0], "height": CALLOUT_SIZE[1]},
            "runtimePosition": RUNTIME_POSITION,
            "copy": "Большое спасибо! Теперь можешь забрать награду!",
            "tailTarget": "CHR-001 v2",
            "tailPointLocal": {"x": TAIL_POINT_LOCAL[0], "y": TAIL_POINT_LOCAL[1]},
            "tailTargetRuntime": {"x": TAIL_TARGET_RUNTIME[0], "y": TAIL_TARGET_RUNTIME[1]},
            "tailPlacement": "UI-013 geometry reflected upward; continuous top join",
            "visibleBottomAtRuntime": RUNTIME_POSITION["y"] + CALLOUT_SIZE[1],
            "production": {
                "buildScript": "scripts/build_delivery_finale_ui_v5.py",
                "geometryReference": INTRO_CALLOUT.relative_to(ROOT).as_posix(),
                "geometryReferenceSha256": file_hash(INTRO_CALLOUT),
                "fontSource": FONT_PATH.relative_to(ROOT).as_posix(),
                "fontSha256": file_hash(FONT_PATH),
                "offlineResizeCount": 0,
                "antialiasing": False,
                "phaserTextureFilter": "nearest",
                "singleContinuousJoin": True,
                "highlightCrossesTail": False,
                "pinkTailOutline": False,
                "runtimeSha256": file_hash(CALLOUT_FILE),
            },
        },
    )


if __name__ == "__main__":
    main()
