#!/usr/bin/env python3
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
DEST_DIR = ROOT.parent / "PicturePaper"
IMG_DIR = ROOT / "output" / "images"
CHART_DIR = ROOT / "output" / "charts"
CSV_FILE = ROOT / "output" / "csv" / "metrics.csv"
REPORT_FILE = ROOT / "report" / "analysis.md"

def copy_outputs():
    if not DEST_DIR.exists():
        print(f"Error: Destination {DEST_DIR} does not exist!")
        return

    # Copy output PNG images
    png_images = list(IMG_DIR.glob("*.png"))
    print(f"Copying {len(png_images)} PNG images from {IMG_DIR} to {DEST_DIR}...")
    for f in png_images:
        shutil.copy(f, DEST_DIR / f.name)

    # Copy charts
    charts = list(CHART_DIR.glob("*.png"))
    print(f"Copying {len(charts)} chart PNGs from {CHART_DIR} to {DEST_DIR}...")
    for f in charts:
        shutil.copy(f, DEST_DIR / f.name)

    # Copy metrics CSV
    if CSV_FILE.exists():
        print(f"Copying metrics.csv to {DEST_DIR}...")
        shutil.copy(CSV_FILE, DEST_DIR / "metrics.csv")

    # Copy report
    if REPORT_FILE.exists():
        print(f"Copying analysis.md to {DEST_DIR}...")
        shutil.copy(REPORT_FILE, DEST_DIR / "analysis.md")
        
    print("Done copying all output PNGs, metrics, and reports.")

if __name__ == "__main__":
    copy_outputs()
