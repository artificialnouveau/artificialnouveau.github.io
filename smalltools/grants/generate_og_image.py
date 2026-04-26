#!/usr/bin/env python3
"""Generate og-image.png for The Grant Desk.

1200x630, paper background (no rule lines), title with yellow highlight under
'Grant', URL pill at the bottom, and three slightly-rotated sticky notes.

Run: python3 smalltools/grants/generate_og_image.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = Path(__file__).parent
REPO = HERE.parent.parent

PAPER = (244, 236, 220)
INK = (31, 27, 22)
INK_SOFT = (74, 65, 58)
LINE = (42, 36, 29)
HOT = (217, 75, 60)
STICKY_YELLOW = (255, 224, 102)
STICKY_PINK = (255, 179, 186)
STICKY_BLUE = (181, 232, 255)
WHITE = (255, 255, 255)

WIDTH, HEIGHT = 1200, 630

SERIF_PATH = str(REPO / "assets/fonts/YoungSerif-Regular.ttf")
MONO_CANDIDATES = [
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Monaco.ttf",
]


def serif(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(SERIF_PATH, size)


def mono(size: int) -> ImageFont.FreeTypeFont:
    for path in MONO_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def text_size(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_sticky(
    canvas: Image.Image,
    *,
    pos: tuple[int, int],
    size: tuple[int, int],
    color: tuple[int, int, int],
    lines: list[tuple[str, int]],
    angle: float,
    text_color: tuple[int, int, int] = INK,
) -> None:
    """Render a sticky note off-canvas, rotate it, paste with a soft shadow."""
    w, h = size
    sticky = Image.new("RGBA", (w, h), color + (255,))
    sd = ImageDraw.Draw(sticky)
    pad_x, pad_top, line_gap = 22, 22, 8
    y = pad_top
    for text, font_size in lines:
        f = mono(font_size)
        sd.text((pad_x, y), text, font=f, fill=text_color)
        y += font_size + line_gap

    pad = 40
    backing = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    shadow = Image.new("RGBA", backing.size, (0, 0, 0, 0))
    sh_draw = ImageDraw.Draw(shadow)
    sh_draw.rectangle((pad + 6, pad + 8, pad + w + 6, pad + h + 8), fill=(0, 0, 0, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=8))
    backing.alpha_composite(shadow)
    backing.paste(sticky, (pad, pad), sticky)

    rotated = backing.rotate(angle, resample=Image.BICUBIC, expand=True)
    cx, cy = pos
    px = cx - rotated.size[0] // 2
    py = cy - rotated.size[1] // 2
    canvas.alpha_composite(rotated, (px, py))


def main() -> int:
    img = Image.new("RGBA", (WIDTH, HEIGHT), PAPER + (255,))
    draw = ImageDraw.Draw(img)

    draw.rectangle((0, 0, WIDTH, 14), fill=HOT)

    title_font = serif(118)
    title = "The Grant Desk"
    tw, th = text_size(draw, title, title_font)
    tx = (WIDTH - tw) // 2
    ty = 200

    pre = "The "
    pre_w = text_size(draw, pre, title_font)[0]
    grant_w = text_size(draw, "Grant", title_font)[0]
    hl_x0 = tx + pre_w - 4
    hl_x1 = hl_x0 + grant_w + 8
    hl_h = 30
    hl_y0 = ty + th - hl_h + 14
    hl_y1 = ty + th + 14
    draw.rectangle((hl_x0, hl_y0, hl_x1, hl_y1), fill=STICKY_YELLOW)

    draw.text((tx, ty), title, font=title_font, fill=INK)

    sub_font = serif(32)
    subtitle = [
        "Paid open calls, fellowships and residencies",
        "for tech, art and research",
    ]
    sy = ty + th + 50
    for line in subtitle:
        lw = text_size(draw, line, sub_font)[0]
        draw.text(((WIDTH - lw) // 2, sy), line, font=sub_font, fill=INK_SOFT)
        sy += 44

    url = "artificialnouveau.com/smalltools/grants"
    url_font = mono(28)
    uw, uh = text_size(draw, url, url_font)
    pad_x, pad_y = 28, 16
    pw = uw + pad_x * 2
    ph = uh + pad_y * 2
    px = (WIDTH - pw) // 2
    py = HEIGHT - ph - 44
    draw.rounded_rectangle(
        (px, py, px + pw, py + ph), radius=10, fill=WHITE, outline=LINE, width=3
    )
    draw.text((px + pad_x, py + pad_y - 4), url, font=url_font, fill=INK)

    draw_sticky(
        img,
        pos=(160, 140),
        size=(280, 170),
        color=STICKY_YELLOW,
        lines=[("HOT GRANTS", 22), ("Closing soon", 26), ("Apply now", 26)],
        angle=-4,
    )
    draw_sticky(
        img,
        pos=(WIDTH - 160, 145),
        size=(240, 150),
        color=STICKY_BLUE,
        lines=[("CALENDAR", 22), ("Subscribe", 26), ("via .ics", 26)],
        angle=3,
    )
    draw_sticky(
        img,
        pos=(170, HEIGHT - 165),
        size=(220, 130),
        color=STICKY_PINK,
        lines=[("Paid only", 26), ("No exposure", 26)],
        angle=-3,
    )

    out = HERE / "og-image.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print(f"Wrote {out} ({out.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
