#!/usr/bin/env python3
"""Generate demo images for the ROP reproduction.

Conda environment:
    conda activate py312
    conda install -n py312 -y numpy pillow matplotlib pandas
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "input"


def save_ppm(name: str, arr: np.ndarray) -> None:
    arr = np.clip(arr * 255.0, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr, "RGB")
    img.save(OUT / f"{name}.ppm")
    img.save(OUT / f"{name}.png")


def base_city(w=480, h=320):
    y = np.linspace(0, 1, h)[:, None]
    sky = np.dstack([
        0.55 + 0.20 * (1 - y),
        0.68 + 0.12 * (1 - y),
        0.82 + 0.08 * (1 - y),
    ])
    img = np.repeat(sky, w, axis=1)
    pil = Image.fromarray((img * 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(pil)
    d.polygon([(0, 180), (100, 105), (225, 185)], fill=(76, 98, 82))
    d.polygon([(150, 190), (300, 90), (520, 190)], fill=(86, 105, 96))
    d.rectangle((40, 155, 128, 270), fill=(116, 98, 86))
    for x in range(55, 120, 22):
        for y0 in range(170, 238, 25):
            d.rectangle((x, y0, x + 9, y0 + 13), fill=(188, 198, 176))
    d.rectangle((305, 135, 425, 270), fill=(102, 112, 125))
    for x in range(320, 405, 24):
        for y0 in range(150, 245, 27):
            d.rectangle((x, y0, x + 10, y0 + 14), fill=(178, 193, 205))
    d.polygon([(185, 320), (295, 205), (370, 320)], fill=(78, 78, 75))
    d.line((240, 320, 295, 205), fill=(220, 220, 200), width=3)
    return np.asarray(pil).astype(np.float32) / 255.0


def base_desert(w=480, h=320):
    y = np.linspace(0, 1, h)[:, None]
    img = np.repeat(np.dstack([0.70 + 0.15 * (1 - y), 0.78 + 0.08 * (1 - y), 0.88 + 0.04 * (1 - y)]), w, axis=1)
    pil = Image.fromarray((img * 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(pil)
    d.ellipse((55, 42, 118, 105), fill=(255, 220, 120))
    for k in range(5):
        yy = 210 + k * 18
        d.arc((-80 + k * 30, yy - 80, 560, yy + 95), 180, 350, fill=(186, 142, 70), width=6)
    d.polygon([(0, 244), (130, 194), (300, 246), (480, 200), (480, 320), (0, 320)], fill=(206, 160, 86))
    d.rectangle((300, 130, 390, 210), fill=(118, 90, 62))
    d.polygon([(292, 130), (348, 90), (400, 130)], fill=(98, 70, 50))
    d.rectangle((330, 162, 360, 210), fill=(45, 55, 62))
    for x in [70, 105, 430]:
        d.line((x, 225, x, 180), fill=(64, 92, 62), width=5)
        d.line((x, 194, x - 20, 184), fill=(64, 92, 62), width=4)
        d.line((x, 205, x + 18, 190), fill=(64, 92, 62), width=4)
    return np.asarray(pil).astype(np.float32) / 255.0


def base_underwater(w=480, h=320):
    y = np.linspace(0, 1, h)[:, None]
    img = np.repeat(np.dstack([0.06 + 0.08 * y, 0.38 + 0.20 * (1 - y), 0.58 + 0.22 * (1 - y)]), w, axis=1)
    pil = Image.fromarray((img * 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(pil, "RGBA")
    d.polygon([(0, 285), (85, 250), (180, 285), (280, 245), (480, 288), (480, 320), (0, 320)], fill=(64, 76, 62, 255))
    for x, y0, col in [(60, 250, (235, 114, 96)), (105, 265, (236, 165, 84)), (375, 258, (205, 88, 146))]:
        for a in range(-35, 45, 14):
            d.line((x, y0, x + a, y0 - 50 + abs(a) // 3), fill=col + (220,), width=5)
    for cx, cy, sc in [(250, 130, 1.0), (315, 175, 0.75), (160, 112, 0.65)]:
        d.ellipse((cx - 34 * sc, cy - 14 * sc, cx + 34 * sc, cy + 14 * sc), fill=(220, 155, 60, 230))
        d.polygon([(cx + 34 * sc, cy), (cx + 58 * sc, cy - 17 * sc), (cx + 58 * sc, cy + 17 * sc)], fill=(220, 155, 60, 230))
        d.ellipse((cx - 22 * sc, cy - 5 * sc, cx - 15 * sc, cy + 2 * sc), fill=(20, 30, 35, 255))
    for r in range(18, 70, 13):
        d.ellipse((410 - r, 85 - r, 410 + r, 85 + r), outline=(190, 230, 255, 60), width=2)
    return np.asarray(pil.filter(ImageFilter.GaussianBlur(0.4))).astype(np.float32) / 255.0


def base_room(w=480, h=320):
    img = np.ones((h, w, 3), dtype=np.float32)
    img[:] = np.array([0.42, 0.37, 0.32])
    pil = Image.fromarray((img * 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(pil)
    d.rectangle((0, 212, 480, 320), fill=(74, 58, 46))
    d.rectangle((80, 105, 235, 215), fill=(96, 116, 128))
    d.rectangle((98, 122, 217, 190), fill=(170, 180, 178))
    d.rectangle((300, 105, 336, 213), fill=(82, 55, 44))
    d.polygon([(260, 108), (376, 108), (342, 62), (292, 62)], fill=(210, 176, 92))
    d.ellipse((286, 75, 350, 138), fill=(255, 216, 115))
    d.rectangle((45, 230, 192, 280), fill=(122, 76, 48))
    d.ellipse((65, 205, 135, 250), fill=(165, 56, 46))
    return np.asarray(pil).astype(np.float32) / 255.0


def degrade(img, air, beta, kind):
    h, w, _ = img.shape
    yy = np.linspace(0, 1, h)[:, None]
    xx = np.linspace(0, 1, w)[None, :]
    depth = 0.25 + 0.75 * (0.65 * yy + 0.35 * xx)
    if kind == "underwater":
        att = np.array([0.45, 0.82, 0.95], dtype=np.float32)
        clear = img * att
        depth = 0.2 + 0.8 * yy
    elif kind == "sand":
        clear = img * np.array([1.03, 0.92, 0.62], dtype=np.float32)
    else:
        clear = img
    t = np.exp(-beta * depth)[..., None]
    out = clear * t + np.array(air, dtype=np.float32) * (1 - t)
    if kind == "lowlight":
        out = np.power(np.clip(img, 0, 1), 1.35) * 0.23
        lamp = np.exp(-(((xx - 0.66) ** 2) / 0.035 + ((yy - 0.33) ** 2) / 0.08))[..., None]
        out += lamp * np.array([0.22, 0.17, 0.08])
    return np.clip(out, 0, 1)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cases = [
        ("std_haze_city", degrade(base_city(), [0.86, 0.90, 0.96], 1.75, "haze")),
        ("std_sand_desert", degrade(base_desert(), [0.96, 0.77, 0.43], 1.55, "sand")),
        ("std_underwater", degrade(base_underwater(), [0.05, 0.48, 0.72], 1.65, "underwater")),
        ("std_lowlight_room", degrade(base_room(), [0, 0, 0], 0.0, "lowlight")),
    ]
    for name, arr in cases:
        save_ppm(name, arr)
    print(f"demo images written to {OUT}")


if __name__ == "__main__":
    main()
