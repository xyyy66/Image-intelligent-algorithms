#!/usr/bin/env python3
import ssl
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "assets" / "input"

IMAGES = {
    "paper_hazy1": "https://raw.githubusercontent.com/junliumath/ROP/main/rankoneplus/images/hazy1.png",
    "paper_sandstorm1": "https://raw.githubusercontent.com/junliumath/ROP/main/rankoneplus/images/sandstorm1.png",
    "paper_underw1": "https://raw.githubusercontent.com/junliumath/ROP/main/rankoneplus/images/underw1.jpg"
}

def download_and_convert():
    OUT.mkdir(parents=True, exist_ok=True)
    ctx = ssl._create_unverified_context()
    for name, url in IMAGES.items():
        try:
            req = Request(url, headers={"User-Agent": "ROP-repro/1.0"})
            with urlopen(req, timeout=25, context=ctx) as r:
                data = r.read()
            # Save raw png/jpg
            ext = ".png" if "png" in url else ".jpg"
            temp_path = OUT / f"{name}_raw{ext}"
            temp_path.write_bytes(data)
            
            # Open and save as PNG and PPM
            with Image.open(temp_path) as img:
                img = img.convert("RGB")
                img.save(OUT / f"{name}.png")
                img.save(OUT / f"{name}.ppm")
            temp_path.unlink()
            print(f"Downloaded and converted {name}")
        except Exception as e:
            print(f"Failed to download {name}: {e}")

if __name__ == "__main__":
    download_and_convert()
