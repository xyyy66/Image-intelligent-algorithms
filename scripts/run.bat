@echo off
setlocal
cd /d "%~dp0\.."

call conda activate py312 2>NUL
python scripts\make_demo.py || exit /b 1

if not exist build mkdir build
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic src\main.cpp src\img.cpp src\rop.cpp src\metrics.cpp -o build\rop_demo.exe || exit /b 1
build\rop_demo.exe --input assets\input --output output --omega 0.8 --iter 10 --gamma 50 || exit /b 1
python scripts\plot.py || exit /b 1

echo Done. Charts: output\charts
echo Report text: report\analysis.md
