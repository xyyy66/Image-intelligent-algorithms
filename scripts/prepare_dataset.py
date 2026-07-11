#!/usr/bin/env python3
import os
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "input"

def prepare_dataset():
    # Recreate the output directory
    if OUT.exists():
        for f in OUT.glob("*"):
            f.unlink()
    OUT.mkdir(parents=True, exist_ok=True)
    
    categories = {
        "hazy": ROOT.parent / "hazy",
        "sandstorm": ROOT.parent / "sandstorm",
        "underwater": ROOT.parent / "unwater" # folder is unwater
    }
    
    for cat_name, cat_dir in categories.items():
        if not cat_dir.exists():
            print(f"Error: Directory {cat_dir} does not exist!")
            continue
            
        # Get sorted list of files
        files = sorted([f for f in cat_dir.glob("*") if f.suffix.lower() in [".jpg", ".jpeg", ".png", ".ppm"]])
        print(f"Processing category '{cat_name}': found {len(files)} files.")
        
        for idx, fpath in enumerate(files):
            new_name = f"{cat_name}_{idx + 1}"
            try:
                with Image.open(fpath) as img:
                    img = img.convert("RGB")
                    # Save as PPM (for C++ input) and PNG (for easy viewing)
                    img.save(OUT / f"{new_name}.ppm")
                    img.save(OUT / f"{new_name}.png")
                print(f"  -> Converted {fpath.name} to {new_name}.ppm/.png")
            except Exception as e:
                print(f"  -> Failed to convert {fpath.name}: {e}")

if __name__ == "__main__":
    prepare_dataset()
