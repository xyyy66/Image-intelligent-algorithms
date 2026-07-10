#!/usr/bin/env python3
"""Build publication-style figures and Chinese figure notes.

Conda environment:
    conda activate py312
    conda install -n py312 -y numpy pillow matplotlib pandas
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
IMG_DIR = ROOT / "output" / "images"
CHART_DIR = ROOT / "output" / "charts"
REPORT_DIR = ROOT / "report"
SRC_FILE = ROOT / "assets" / "input" / "sources.md"


mpl.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif", "STSong"],
        "mathtext.fontset": "dejavuserif",
        "axes.linewidth": 0.9,
        "axes.labelsize": 10,
        "axes.titlesize": 10,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "legend.fontsize": 8.5,
        "figure.dpi": 160,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.04,
    }
)

COL = {"input": "#4C78A8", "ROP": "#F58518", "ROP+": "#54A24B"}
LABEL = {"input": "Input", "ROP": "ROP", "ROP+": "ROP$^{+}$"}


def load_img(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB")).astype(np.float32) / 255.0


def luma(im: np.ndarray) -> np.ndarray:
    return 0.299 * im[..., 0] + 0.587 * im[..., 1] + 0.114 * im[..., 2]


def save_pngs():
    for p in IMG_DIR.glob("*.ppm"):
        Image.open(p).save(p.with_suffix(".png"))


def add_tag(ax, tag: str):
    ax.text(
        0.015,
        0.965,
        tag,
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=9,
        color="white",
        bbox={"facecolor": "black", "alpha": 0.58, "pad": 2, "linewidth": 0},
    )


def qualitative(name: str) -> Path:
    items = [
        (f"{name}_input.ppm", r"(a) $I$ degraded input"),
        (f"{name}_rop.ppm", r"(b) ROP recovered $J$"),
        (f"{name}_rop_plus.ppm", r"(c) ROP$^{+}$ recovered $J$"),
        (f"{name}_rop_scatter.ppm", r"(d) ROP $\tilde{t}$"),
        (f"{name}_rop_plus_scatter.ppm", r"(e) ROP$^{+}$ $\tilde{t}$"),
        (f"{name}_rop_plus_diff.ppm", r"(f) $3|J-I|$"),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(12.8, 5.9), gridspec_kw={"wspace": 0.03, "hspace": 0.055})
    for ax, (fn, tag) in zip(axes.ravel(), items):
        ax.imshow(load_img(IMG_DIR / fn))
        add_tag(ax, tag)
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)
    fig.suptitle(r"Rank-One Prior scene recovery: qualitative comparison", y=0.985, fontsize=12)
    fig.subplots_adjust(left=0.018, right=0.985, bottom=0.035, top=0.925, wspace=0.035, hspace=0.06)
    out = CHART_DIR / f"{name}_qualitative.png"
    fig.savefig(out, dpi=220)
    plt.close(fig)
    return out


def profile_figure(name: str) -> Path:
    imgs = {
        "input": load_img(IMG_DIR / f"{name}_input.ppm"),
        "ROP": load_img(IMG_DIR / f"{name}_rop.ppm"),
        "ROP+": load_img(IMG_DIR / f"{name}_rop_plus.ppm"),
    }
    y = imgs["input"].shape[0] // 2
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 3.8))
    x = np.arange(imgs["input"].shape[1])
    for key, im in imgs.items():
        yy = luma(im)
        axes[0].plot(x, yy[y], lw=1.45, color=COL[key], label=LABEL[key])
        axes[1].hist(yy.ravel(), bins=80, density=True, histtype="step", lw=1.5, color=COL[key], label=LABEL[key])
    axes[0].set_title(r"(a) Horizontal luminance profile $Y(x,y_0)$")
    axes[0].set_xlabel(r"pixel coordinate $x$")
    axes[0].set_ylabel(r"luminance $Y$")
    axes[0].grid(alpha=0.25, lw=0.5)
    axes[1].set_title(r"(b) Luminance distribution $p(Y)$")
    axes[1].set_xlabel(r"luminance $Y$")
    axes[1].set_ylabel(r"density")
    axes[1].grid(alpha=0.25, lw=0.5)
    axes[1].legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.18))
    fig.tight_layout()
    out = CHART_DIR / f"{name}_luminance_profile.png"
    fig.savefig(out, dpi=220)
    plt.close(fig)
    return out


def metric_panel(df: pd.DataFrame) -> Path:
    base = df[df.method.isin(["input", "ROP", "ROP+"])]
    methods = ["input", "ROP", "ROP+"]
    metrics = [
        ("contrast", r"contrast $\sigma_Y$"),
        ("entropy", r"entropy $H(Y)$"),
        ("color_cast", r"color cast $d_{\mathrm{rgb}}$"),
        ("edge_energy", r"edge energy $E_{\nabla}$"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(12.0, 7.2))
    xlabels = sorted(base.image.unique())
    x = np.arange(len(xlabels))
    width = 0.24
    for ax, (metric, title) in zip(axes.ravel(), metrics):
        piv = base.pivot_table(index="image", columns="method", values=metric).reindex(xlabels)
        for j, m in enumerate(methods):
            ax.bar(x + (j - 1) * width, piv[m], width=width, color=COL[m], label=LABEL[m], edgecolor="black", linewidth=0.25)
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels([s.replace("real_", "").replace("_", "\n") for s in xlabels])
        ax.grid(axis="y", alpha=0.25, lw=0.5)
    axes[0, 0].legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(1.1, 1.28))
    fig.suptitle(r"No-reference statistics on real Internet photographs", y=0.99, fontsize=12)
    fig.tight_layout()
    out = CHART_DIR / "metrics_summary.png"
    fig.savefig(out, dpi=220)
    plt.close(fig)
    return out


def runtime_panel(df: pd.DataFrame) -> Path:
    run = df[df.method.isin(["ROP", "ROP+"])]
    names = sorted(run.image.unique())
    piv = run.pivot_table(index="image", columns="method", values="time_ms").reindex(names)
    fig, ax = plt.subplots(figsize=(8.8, 4.4))
    x = np.arange(len(names))
    ax.bar(x - 0.17, piv["ROP"], width=0.34, color=COL["ROP"], edgecolor="black", linewidth=0.25, label="ROP")
    ax.bar(x + 0.17, piv["ROP+"], width=0.34, color=COL["ROP+"], edgecolor="black", linewidth=0.25, label=r"ROP$^{+}$")
    ax.set_ylabel(r"CPU time $T$ / ms")
    ax.set_xticks(x)
    ax.set_xticklabels([s.replace("real_", "").replace("_", "\n") for s in names])
    ax.set_title(r"Runtime comparison: closed-form ROP vs. iterative ROP$^{+}$")
    ax.grid(axis="y", alpha=0.25, lw=0.5)
    ax.legend(frameon=False)
    fig.tight_layout()
    out = CHART_DIR / "runtime_comparison.png"
    fig.savefig(out, dpi=220)
    plt.close(fig)
    return out


def ablation_figures(df: pd.DataFrame) -> tuple[Path | None, Path | None]:
    ab = df[df.method == "ablation"].sort_values("omega")
    if ab.empty:
        return None, None
    name = ab.image.iloc[0]
    fig, axes = plt.subplots(1, len(ab), figsize=(13.2, 3.4))
    for ax, (_, row) in zip(axes, ab.iterrows()):
        fn = f"{name}_ablation_w{int(row.omega * 100)}.ppm"
        ax.imshow(load_img(IMG_DIR / fn))
        add_tag(ax, rf"$\omega={row.omega:.2f}$")
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)
    fig.suptitle(r"Ablation study on relaxation coefficient $\omega$", y=0.99, fontsize=12)
    grid = CHART_DIR / f"{name}_omega_ablation_grid.png"
    fig.savefig(grid, dpi=220)
    plt.close(fig)

    fig, ax1 = plt.subplots(figsize=(8.4, 4.6))
    ax1.plot(ab.omega, ab.contrast, "o-", color="#4C78A8", label=r"$\sigma_Y$")
    ax1.plot(ab.omega, ab.color_cast, "s-", color="#E45756", label=r"$d_{\mathrm{rgb}}$")
    ax1.set_xlabel(r"relaxation coefficient $\omega$")
    ax1.set_ylabel(r"metric value")
    ax1.grid(alpha=0.25, lw=0.5)
    ax2 = ax1.twinx()
    ax2.plot(ab.omega, ab.entropy, "^-", color="#54A24B", label=r"$H(Y)$")
    ax2.set_ylabel(r"entropy $H(Y)$")
    lines = ax1.get_lines() + ax2.get_lines()
    ax1.legend(lines, [l.get_label() for l in lines], frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.16))
    ax1.set_title(r"Parameter sensitivity of ROP$^{+}$")
    fig.tight_layout()
    curve = CHART_DIR / f"{name}_omega_ablation_curve.png"
    fig.savefig(curve, dpi=220)
    plt.close(fig)
    return grid, curve


def read_sources() -> str:
    return SRC_FILE.read_text(encoding="utf-8") if SRC_FILE.exists() else ""


def write_report(df: pd.DataFrame, names: list[str], figs: list[Path]):
    lines = [
        "# ROP 论文真实照片实验图文说明",
        "",
        "## 素材来源",
        "本版本使用 ROP 官方论文中的三张真实代表性退化照片，分别是雾霾场景 (paper_hazy1)、沙尘场景 (paper_sandstorm1) 以及水下场景 (paper_underw1)，保证 C++ 算法可以一键复现论文效果。",
        "",
        "## 算法与绘图逻辑",
        "ROP 的核心是将观测图像 $I$ 投影到统一光谱方向，得到散射图 $\\tilde{t}$，再由物理退化模型恢复潜在清晰图像 $J$。ROP$^{+}$ 在统一光谱估计时排除方向偏离大的像素，并用边缘加权的散射系数细化减少前景误估计。",
        "绘图统一采用 serif 字体、数学公式标签和子图编号。定量图不是把数值直接堆成普通柱状图，而是围绕亮度对比度 $\\sigma_Y$、熵 $H(Y)$、色偏距离 $d_{\\mathrm{rgb}}$、边缘能量 $E_{\\nabla}$ 和 CPU 耗时 $T$ 展开，便于读书报告正文引用。",
        "",
        "## 每张图表说明",
    ]

    for name in names:
        sub = df[(df.image == name) & df.method.isin(["input", "ROP", "ROP+"])]
        rows = {r.method: r for _, r in sub.iterrows()}
        q = f"{name}_qualitative.png"
        p = f"{name}_luminance_profile.png"
        lines += [
            "",
            f"### {q}",
            "图片内容：该图包含退化输入、ROP 输出、ROP$^{+}$ 输出、两种散射图热力可视化以及 $3|J-I|$ 差异图。前三幅给出主观视觉质量，后三幅解释算法内部估计与像素变化区域。",
            "绘图逻辑：C++ 输出恢复图与中间散射图，Python 按论文常见的子图编号方式排成 2x3 面板。散射热力图越偏暖，表示估计的介质散射/传输修正越强。",
        ]
        if "input" in rows and "ROP+" in rows:
            lines.append(
                f"实验现象：ROP$^{{+}}$ 相比输入的 $\\Delta\\sigma_Y={rows['ROP+'].contrast - rows['input'].contrast:.4f}$，"
                f"$\\Delta H={rows['ROP+'].entropy - rows['input'].entropy:.4f}$，"
                f"恢复后 $d_{{\\mathrm{{rgb}}}}={rows['ROP+'].color_cast:.4f}$。这些数值可用于报告中描述可见度、信息量和色偏变化。"
            )
        lines.append(
            "理论分析：若 ROP$^{+}$ 的散射图比 ROP 更贴合远景和低对比区域，说明统一光谱筛选与 TV 细化减少了近景纹理对散射估计的干扰。若差异图在强边缘处明显，通常代表恢复公式主要增强结构边界；若在平坦区域大面积发亮，则可能存在过校正。"
        )
        lines += [
            "",
            f"### {p}",
            "图片内容：左图为图像中线亮度剖面 $Y(x,y_0)$，右图为亮度概率密度 $p(Y)$。",
            "绘图逻辑：用同一行像素比较 Input、ROP、ROP$^{+}$ 的亮度变化，再用全图直方分布观察动态范围是否扩展。",
            "理论分析：退化图像往往亮度集中、对比度低；恢复后曲线起伏增大且直方图分布变宽，说明图像层次被拉开。若曲线出现尖峰或直方图贴近 0/1 边界，则说明参数可能过强。",
        ]

    lines += [
        "",
        "### metrics_summary.png",
        "图片内容：四联图同时展示 $\\sigma_Y$、$H(Y)$、$d_{\\mathrm{rgb}}$ 和 $E_{\\nabla}$ 在不同真实照片与不同方法下的变化。",
        "绘图逻辑：每个场景使用 Input、ROP、ROP$^{+}$ 三根柱，避免只看单张照片导致结论片面。该图适合作为读书报告的总量化对比图。",
        "理论分析：$\\sigma_Y$ 和 $E_{\\nabla}$ 增大通常说明可见度和边缘细节增强；$H(Y)$ 增大说明亮度层次更丰富；$d_{\\mathrm{rgb}}$ 下降代表整体色偏被抑制。指标之间可能冲突，因此需要结合 qualitative 图共同判断。",
        "",
        "### runtime_comparison.png",
        "图片内容：展示 ROP 与 ROP$^{+}$ 在四张真实照片上的 CPU 耗时。",
        "绘图逻辑：同一场景并列两根柱，对应闭式 O(N) 流程和迭代细化流程。",
        "理论分析：ROP 只包含均值光谱、投影、重采样和恢复公式，因此耗时低；ROP$^{+}$ 增加散射系数优化，耗时上升但可改善复杂前景/背景条件下的恢复稳定性。",
        "",
    ]

    ab = df[df.method == "ablation"]
    if not ab.empty:
        nm = ab.image.iloc[0]
        lines += [
            f"### {nm}_omega_ablation_grid.png",
            "图片内容：展示同一真实照片在不同松弛系数 $\\omega$ 下的 ROP$^{+}$ 恢复结果。",
            "绘图逻辑：保持其他参数不变，仅改变 $\\omega\\in\\{0.50,0.65,0.80,0.95\\}$，用横向网格直观看参数影响。",
            "理论分析：$\\omega$ 越大，散射扣除越强，通常图像更清晰、颜色更鲜明；但过大时容易产生过饱和、暗部噪声放大和边缘伪影。论文默认约 0.8，本实验也将 $\\omega=0.8$ 作为主设置。",
            "",
            f"### {nm}_omega_ablation_curve.png",
            "图片内容：绘制 $\\omega$ 与 $\\sigma_Y$、$H(Y)$、$d_{\\mathrm{rgb}}$ 的关系曲线。",
            "绘图逻辑：使用 LaTeX 数学符号标注横纵坐标，左轴显示对比度和色偏，右轴显示熵，便于观察参数变化趋势。",
            "理论分析：若 $\\sigma_Y$ 与 $H(Y)$ 随 $\\omega$ 增加而升高，说明去散射强度增强；若 $d_{\\mathrm{rgb}}$ 同时升高，则说明颜色校正可能开始失稳。该图可支撑报告中的参数敏感性讨论。",
        ]

    lines += [
        "",
        "## 可直接写入报告的总结",
        "真实照片实验比合成图更能暴露 ROP 类方法的优缺点。ROP 的优势是速度快、实现简单，在整体退化较均匀的场景中能快速提高对比度；ROP$^{+}$ 的优势是统一光谱估计更稳，散射图更接近真实场景结构，适合前景/背景差异明显的照片。局限在于该方法仍依赖单幅图像中的颜色统计，当原图存在局部强色光、噪声、JPEG 块效应或本身不是散射退化时，恢复公式会放大这些异常，因此需要结合参数消融与差异图判断是否过校正。",
    ]
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "analysis.md").write_text("\n".join(lines), encoding="utf-8")
    (REPORT_DIR / "figure_notes.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    for old in CHART_DIR.glob("*.png"):
        old.unlink()
    save_pngs()
    df = pd.read_csv(ROOT / "output" / "csv" / "metrics.csv")
    names = sorted([p.name.replace("_input.ppm", "") for p in IMG_DIR.glob("*_input.ppm")])
    figs = []
    for name in names:
        figs.append(qualitative(name))
        figs.append(profile_figure(name))
    figs.append(metric_panel(df))
    figs.append(runtime_panel(df))
    figs.extend([p for p in ablation_figures(df) if p])
    write_report(df, names, figs)
    print(f"charts written to {CHART_DIR}")
    print(f"analysis written to {REPORT_DIR / 'analysis.md'}")


if __name__ == "__main__":
    main()
