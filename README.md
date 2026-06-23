# Image-intelligent-algorithms

## ROP Scene Recovery Reproduction

This project reproduces the image recovery method in `paper.pdf`:

- Rank-One Prior (ROP): unified spectrum projection and O(N) recovery.
- ROP+: selected-spectrum estimation plus edge-aware coefficient refinement.

The algorithm core is C++17. Python is only used for demo image generation, chart drawing and report text generation.

## Environment

Linux/macOS:

```bash
conda create -n py312 python=3.12 -y
conda activate py312
conda install -n py312 -y numpy pillow matplotlib pandas
bash scripts/run.sh
```

Windows with MinGW g++:

```bat
conda create -n py312 python=3.12 -y
conda activate py312
conda install -n py312 -y numpy pillow matplotlib pandas
scripts\run.bat
```

## Output

- `assets/input`: generated degraded demo images.
- `output/images`: raw PPM and converted PNG results.
- `output/charts`: comparison panels, heatmaps, metric charts and ablation charts.
- `output/csv/metrics.csv`: runtime and no-reference statistics.
- `report/analysis.md`: Chinese figure notes and reading-report analysis.
