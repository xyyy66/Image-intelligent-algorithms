#!/usr/bin/env python3
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IN_DIR = ROOT.parent / "PicturePaper"
OUT_DIR = ROOT / "assets" / "input"

def prepare():
    if not IN_DIR.exists():
        print(f"Error: {IN_DIR} does not exist!")
        return
        
    # Recreate OUT_DIR
    if OUT_DIR.exists():
        for f in OUT_DIR.glob("*"):
            f.unlink()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Convert all PNGs in PicturePaper to PPM in assets/input
    png_files = sorted(IN_DIR.glob("*.png"))
    print(f"Found {len(png_files)} PNG files in {IN_DIR}")
    for idx, fpath in enumerate(png_files):
        # We want to keep the name exactly the same (without extension)
        name = fpath.stem
        # Exclude output files if any are already present (e.g. from previous runs)
        if any(suffix in name for suffix in ["_rop", "_rop_plus", "_scatter", "_diff", "_ablation", "_profile", "_qualitative", "metrics_summary", "runtime_comparison"]):
            continue
        try:
            with Image.open(fpath) as img:
                img = img.convert("RGB")
                img.save(OUT_DIR / f"{name}.ppm")
            print(f"  -> Converted {fpath.name} to {name}.ppm")
        except Exception as e:
            print(f"  -> Failed to convert {fpath.name}: {e}")

if __name__ == "__main__":
    prepare()
