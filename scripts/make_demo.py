#!/usr/bin/env python3
"""Download realistic test photos and prepare PPM inputs.

Conda environment:
    conda activate py312
    conda install -n py312 -y numpy pillow matplotlib pandas
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
import ssl
from urllib.parse import quote
from urllib.request import Request, urlopen

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "input"


PHOTOS = [
    {
        "name": "real_haze_mountain",
        "file": "Fog over a national park (Unsplash).jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Fog_over_a_national_park_%28Unsplash%29.jpg/1280px-Fog_over_a_national_park_%28Unsplash%29.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Fog_over_a_national_park_(Unsplash).jpg",
        "caption": "Fog-covered mountain landscape, used for natural haze recovery.",
    },
    {
        "name": "real_underwater_reef",
        "file": "Underwater photo of coral reef.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Underwater_photo_of_coral_reef.jpg/1280px-Underwater_photo_of_coral_reef.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Underwater_photo_of_coral_reef.jpg",
        "caption": "Underwater coral reef scene, used for blue-green color cast recovery.",
    },
    {
        "name": "real_sandstorm_road",
        "file": "Sand Storm on the Asphalt roads.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Sand_Storm_on_the_Asphalt_roads.jpg/1280px-Sand_Storm_on_the_Asphalt_roads.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Sand_Storm_on_the_Asphalt_roads.jpg",
        "caption": "Road scene under sand storm, used for yellow dust degradation recovery.",
    },
    {
        "name": "real_lowlight_city",
        "file": "Sarlat-medieval-city-by-night-15.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Sarlat-medieval-city-by-night-15.jpg/960px-Sarlat-medieval-city-by-night-15.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Sarlat-medieval-city-by-night-15.jpg",
        "caption": "Night city street, used for the Retinex/dehazing duality extension.",
    },
]


def file_url(file_name: str) -> str:
    return "https://commons.wikimedia.org/wiki/Special:FilePath/" + quote(file_name) + "?width=1280"


def crop_fit(img: Image.Image, size=(720, 480)) -> Image.Image:
    img = img.convert("RGB")
    sw, sh = img.size
    tw, th = size
    scale = max(tw / sw, th / sh)
    nw, nh = int(sw * scale + 0.5), int(sh * scale + 0.5)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return img.crop((left, top, left + tw, top + th))


def save_case(name: str, img: Image.Image) -> None:
    img = crop_fit(img)
    img.save(OUT / f"{name}.ppm")
    img.save(OUT / f"{name}.png")


def fallback_photo(name: str) -> Image.Image:
    img = Image.new("RGB", (720, 480), (150, 160, 165))
    d = ImageDraw.Draw(img)
    for k in range(12):
        col = (120 + k * 5, 135 + k * 4, 150 + k * 3)
        d.rectangle((0, k * 40, 720, (k + 1) * 40), fill=col)
    d.rectangle((90, 250, 260, 420), fill=(90, 88, 82))
    d.rectangle((430, 210, 630, 420), fill=(82, 86, 96))
    d.polygon([(0, 300), (210, 150), (390, 305)], fill=(92, 105, 92))
    d.polygon([(280, 310), (520, 130), (740, 305)], fill=(80, 95, 100))
    d.text((24, 24), f"network fallback: {name}", fill=(255, 255, 255))
    return img


def download_photo(item: dict) -> Image.Image:
    url = item.get("url") or file_url(item["file"])
    req = Request(url, headers={"User-Agent": "ROP-course-reproduction/1.0"})
    ctx = ssl._create_unverified_context()
    with urlopen(req, timeout=25, context=ctx) as r:
        raw = r.read()
    return Image.open(BytesIO(raw)).convert("RGB")


def write_sources(rows: list[dict]) -> None:
    lines = [
        "# Online Photo Sources",
        "",
        "All photos are fetched from Wikimedia Commons file pages. The script stores resized local PPM/PNG copies for reproducible course experiments.",
        "",
        "| local name | source file | use | page |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(f"| `{row['name']}` | {row['file']} | {row['caption']} | {row['page']} |")
    (OUT / "sources.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("std_*.*"):
        old.unlink()

    used = []
    for item in PHOTOS:
        try:
            img = download_photo(item)
            status = "downloaded"
        except Exception as exc:
            img = fallback_photo(item["name"])
            status = f"fallback ({exc})"
        save_case(item["name"], img)
        used.append(item)
        print(f"{item['name']}: {status}")
    write_sources(used)
    print(f"demo photos written to {OUT}")


if __name__ == "__main__":
    main()
