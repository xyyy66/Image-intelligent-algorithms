#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if command -v conda >/dev/null 2>&1; then
  eval "$(conda shell.bash hook)"
  conda activate py312 2>/dev/null || true
fi

python3 scripts/make_demo.py
rm -rf output/images output/charts output/csv
mkdir -p output/images output/charts output/csv
make
./build/rop_demo --input assets/input --output output --omega 0.8 --iter 10 --gamma 50
python3 scripts/plot.py

echo "Done. Charts: output/charts"
echo "Report text: report/analysis.md"
