#!/usr/bin/env python3
"""Draw the travel poster for VELMARA, a place that does not exist.

Vintage travel-poster style, 1024x1024: an amber sunset over a teal sea,
floating isles with waterfalls, a low sun, and the place name set in large
serif type. Deterministic (fixed seed, no timestamps, no network, no
external images). Only PIL shapes and DejaVu fonts. Output: entry.png.
"""
import math
import random

from PIL import Image, ImageDraw, ImageFont

random.seed(20261121)

W, H = 1024, 1024
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"

# Palette: deep indigo dusk -> violet -> amber sunset -> teal sea.
SKY_TOP = (22, 32, 74)
SKY_MID = (74, 62, 128)
SKY_LOW = (214, 116, 74)
HORIZON = (242, 168, 90)
SUN_CORE = (255, 236, 190)
SUN_EDGE = (244, 178, 96)
SEA_DEEP = (16, 68, 84)
SEA_MID = (24, 104, 112)
SEA_LIGHT = (52, 148, 138)
ISLE_DARK = (28, 52, 66)
ISLE_MID = (40, 76, 82)
ISLE_TOP = (58, 112, 92)
CREAM = (250, 238, 210)
GOLD = (232, 184, 96)
INK = (20, 28, 44)


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sky(img):
    """Vertical gradient, indigo top to amber horizon."""
    px = img.load()
    horizon_y = 640
    for y in range(horizon_y):
        t = y / horizon_y
        if t < 0.45:
            c = lerp(SKY_TOP, SKY_MID, t / 0.45)
        else:
            c = lerp(SKY_MID, HORIZON, (t - 0.45) / 0.55)
        for x in range(W):
            px[x, y] = c
    return img


def sea(d):
    """Teal sea below the horizon with a sun-reflection path."""
    d.rectangle([0, 640, W, H], fill=SEA_MID)
    # Deeper bands toward the bottom.
    for i, y0 in enumerate(range(700, H, 46)):
        shade = lerp(SEA_MID, SEA_DEEP, i / 7.0)
        d.rectangle([0, y0, W, min(H, y0 + 46)], fill=shade)
    # Sun reflection: horizontal amber dashes, wider near the horizon.
    for y in range(660, 1000, 14):
        spread = int(60 + (y - 660) * 0.55)
        cx = 512 + random.randint(-8, 8)
        w = random.randint(spread // 2, spread)
        col = lerp(SUN_EDGE, SEA_LIGHT, (y - 660) / 340.0)
        d.rectangle([cx - w // 2, y, cx + w // 2, y + 5], fill=col)
    # Thin wave lines.
    for _ in range(46):
        y = random.randint(680, 1000)
        x = random.randint(30, 950)
        ln = random.randint(24, 90)
        d.line([x, y, x + ln, y], fill=SEA_LIGHT, width=2)


def sun(d):
    """Low glowing sun sitting on the horizon."""
    cx, cy, r = 512, 618, 118
    for rr in range(r + 90, r, -6):
        alpha = (r + 90 - rr) / 90.0
        col = lerp(SUN_EDGE, HORIZON, alpha)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SUN_CORE)
    # Sun half-hidden by the horizon line: redraw sea strip over its bottom.
    d.rectangle([0, 640, W, 660], fill=SEA_MID)


def stars(d):
    for _ in range(150):
        x = random.randint(8, W - 8)
        y = random.randint(8, 380)
        s = random.choice([1, 1, 1, 2])
        bright = random.randint(150, 255)
        d.ellipse([x, y, x + s, y + s], fill=(bright, bright, 220))


def clouds(d):
    """Soft warm clouds drifting across the dusk sky."""
    for (cx, cy, s, col) in [
        (180, 250, 1.0, (232, 150, 110)),
        (830, 180, 0.8, (226, 138, 116)),
        (700, 330, 1.15, (240, 170, 120)),
        (300, 420, 0.7, (238, 164, 118)),
    ]:
        for dx, dy, r in [(-70, 0, 46), (0, -14, 58), (70, 4, 48), (-30, 12, 40), (40, 14, 42)]:
            d.ellipse(
                [cx + dx * s - r * s, cy + dy * s - r * s * 0.55,
                 cx + dx * s + r * s, cy + dy * s + r * s * 0.55],
                fill=col,
            )


def island(d, cx, top_y, w, h, tone):
    """A floating isle: flat grassy top, tapering rocky underside."""
    top = tone
    # Rocky body: stacked narrowing trapezoids.
    steps = 7
    for i in range(steps):
        t0 = i / steps
        t1 = (i + 1) / steps
        y0 = top_y + t0 * h
        y1 = top_y + t1 * h
        w0 = w * (1 - t0 * 0.82)
        w1 = w * (1 - t1 * 0.82)
        col = lerp(ISLE_DARK, ISLE_MID, 1 - t0)
        d.polygon([(cx - w0 / 2, y0), (cx + w0 / 2, y0),
                   (cx + w1 / 2, y1), (cx - w1 / 2, y1)], fill=col)
    # Grassy cap.
    d.ellipse([cx - w / 2, top_y - 14, cx + w / 2, top_y + 16], fill=ISLE_TOP)
    d.rectangle([cx - w / 2, top_y - 4, cx + w / 2, top_y + 10], fill=ISLE_TOP)
    return top_y + h


def waterfall(d, x, y0, y1):
    """Thin pale waterfall falling from an isle's edge."""
    d.line([x, y0, x, y1], fill=(214, 232, 226), width=5)
    d.line([x + 4, y0 + 6, x + 4, y1 - 8], fill=(180, 210, 205), width=2)


def temple(d, cx, base_y):
    """A tiny domed temple on the main isle."""
    d.rectangle([cx - 26, base_y - 34, cx + 26, base_y], fill=CREAM)
    d.rectangle([cx - 34, base_y - 6, cx + 34, base_y], fill=GOLD)
    d.polygon([(cx - 30, base_y - 34), (cx + 30, base_y - 34), (cx, base_y - 62)],
              fill=GOLD)
    d.ellipse([cx - 7, base_y - 76, cx + 7, base_y - 62], fill=GOLD)
    d.rectangle([cx - 5, base_y - 22, cx + 5, base_y], fill=INK)


def trees(d, cx, base_y, spread):
    for dx in range(-spread, spread + 1, 26):
        x = cx + dx + random.randint(-6, 6)
        h = random.randint(16, 30)
        d.polygon([(x - 8, base_y), (x + 8, base_y), (x, base_y - h)],
                  fill=(24, 66, 52))


def birds(d):
    for _ in range(14):
        x = random.randint(60, 960)
        y = random.randint(120, 420)
        s = random.randint(7, 13)
        d.arc([x - s, y - s // 2, x, y + s // 2], 200, 340, fill=INK, width=2)
        d.arc([x, y - s // 2, x + s, y + s // 2], 200, 340, fill=INK, width=2)


def centred(d, y, text, fnt, fill, shadow=None):
    bbox = d.textbbox((0, 0), text, font=fnt)
    w = bbox[2] - bbox[0]
    x = (W - w) // 2 - bbox[0]
    if shadow is not None:
        d.text((x + 3, y + 3), text, font=fnt, fill=shadow)
    d.text((x, y), text, font=fnt, fill=fill)
    return w


def main():
    img = Image.new("RGB", (W, H))
    sky(img)
    d = ImageDraw.Draw(img, "RGBA")

    stars(d)
    clouds(d)
    sun(d)

    # Floating isles, largest in the middle.
    island(d, 250, 470, 250, 150, ISLE_MID)
    island(d, 800, 440, 300, 175, ISLE_MID)
    tip = island(d, 512, 380, 360, 210, ISLE_DARK)
    waterfall(d, 400, 560, 640)
    waterfall(d, 640, 560, 640)
    waterfall(d, 180, 600, 660)
    waterfall(d, 880, 590, 660)
    temple(d, 512, 384)
    trees(d, 250, 470, 90)
    trees(d, 800, 440, 110)
    trees(d, 512, 380, 130)

    sea(d)
    # Mist band where sea meets sky.
    d.rectangle([0, 636, W, 656], fill=(242, 178, 110))

    birds(d)

    # Frame.
    d.rectangle([18, 18, W - 19, H - 19], outline=CREAM, width=4)
    d.rectangle([30, 30, W - 31, H - 31], outline=GOLD, width=2)

    # Type: the invented place's name, set into the picture.
    title = font("DejaVuSerif-Bold.ttf", 118)
    centred(d, 78, "VELMARA", title, CREAM, shadow=(30, 20, 60))
    sub = font("DejaVuSans.ttf", 34)
    centred(d, 214, "THE FLOATING ISLES", sub, CREAM, shadow=(30, 20, 60))
    small = font("DejaVuSans.ttf", 28)
    centred(d, 258, "O F   T H E   A M B E R   T I D E", small, GOLD,
            shadow=(30, 20, 60))

    # Bottom line, above the frame.
    foot = font("DejaVuSans-Bold.ttf", 30)
    centred(d, 918, "WHERE THE SUN NEVER SETS", foot, CREAM,
            shadow=(20, 30, 50))
    tiny = font("DejaVuSans.ttf", 22)
    centred(d, 958, "VISIT VELMARA", tiny, GOLD)

    img.save("entry.png", format="PNG", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
