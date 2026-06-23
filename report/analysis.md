# ROP 真实照片实验图文说明

## 素材来源
本版本不再使用几何合成图，而是自动下载 Wikimedia Commons 上的真实照片，覆盖雾霾风景、水下珊瑚、沙尘道路、夜景低照四类场景。素材脚本会保存本地 PPM/PNG 副本，保证 C++ 算法可以一键复现。

# Online Photo Sources

All photos are fetched from Wikimedia Commons file pages. The script stores resized local PPM/PNG copies for reproducible course experiments.

| local name | source file | use | page |
|---|---|---|---|
| `real_haze_mountain` | Fog over a national park (Unsplash).jpg | Fog-covered mountain landscape, used for natural haze recovery. | https://commons.wikimedia.org/wiki/File:Fog_over_a_national_park_(Unsplash).jpg |
| `real_underwater_reef` | Underwater photo of coral reef.jpg | Underwater coral reef scene, used for blue-green color cast recovery. | https://commons.wikimedia.org/wiki/File:Underwater_photo_of_coral_reef.jpg |
| `real_sandstorm_road` | Sand Storm on the Asphalt roads.jpg | Road scene under sand storm, used for yellow dust degradation recovery. | https://commons.wikimedia.org/wiki/File:Sand_Storm_on_the_Asphalt_roads.jpg |
| `real_lowlight_city` | Sarlat-medieval-city-by-night-15.jpg | Night city street, used for the Retinex/dehazing duality extension. | https://commons.wikimedia.org/wiki/File:Sarlat-medieval-city-by-night-15.jpg |

## 算法与绘图逻辑
ROP 的核心是将观测图像 $I$ 投影到统一光谱方向，得到散射图 $\tilde{t}$，再由物理退化模型恢复潜在清晰图像 $J$。ROP$^{+}$ 在统一光谱估计时排除方向偏离大的像素，并用边缘加权的散射系数细化减少前景误估计。
绘图统一采用 serif 字体、数学公式标签和子图编号。定量图不是把数值直接堆成普通柱状图，而是围绕亮度对比度 $\sigma_Y$、熵 $H(Y)$、色偏距离 $d_{\mathrm{rgb}}$、边缘能量 $E_{\nabla}$ 和 CPU 耗时 $T$ 展开，便于读书报告正文引用。

## 每张图表说明

### real_haze_mountain_qualitative.png
图片内容：该图包含退化输入、ROP 输出、ROP$^{+}$ 输出、两种散射图热力可视化以及 $3|J-I|$ 差异图。前三幅给出主观视觉质量，后三幅解释算法内部估计与像素变化区域。
绘图逻辑：C++ 输出恢复图与中间散射图，Python 按论文常见的子图编号方式排成 2x3 面板。散射热力图越偏暖，表示估计的介质散射/传输修正越强。
实验现象：ROP$^{+}$ 相比输入的 $\Delta\sigma_Y=0.0756$，$\Delta H=0.4932$，恢复后 $d_{\mathrm{rgb}}=0.0750$。这些数值可用于报告中描述可见度、信息量和色偏变化。
理论分析：若 ROP$^{+}$ 的散射图比 ROP 更贴合远景和低对比区域，说明统一光谱筛选与 TV 细化减少了近景纹理对散射估计的干扰。若差异图在强边缘处明显，通常代表恢复公式主要增强结构边界；若在平坦区域大面积发亮，则可能存在过校正。

### real_haze_mountain_luminance_profile.png
图片内容：左图为图像中线亮度剖面 $Y(x,y_0)$，右图为亮度概率密度 $p(Y)$。
绘图逻辑：用同一行像素比较 Input、ROP、ROP$^{+}$ 的亮度变化，再用全图直方分布观察动态范围是否扩展。
理论分析：退化图像往往亮度集中、对比度低；恢复后曲线起伏增大且直方图分布变宽，说明图像层次被拉开。若曲线出现尖峰或直方图贴近 0/1 边界，则说明参数可能过强。

### real_lowlight_city_qualitative.png
图片内容：该图包含退化输入、ROP 输出、ROP$^{+}$ 输出、两种散射图热力可视化以及 $3|J-I|$ 差异图。前三幅给出主观视觉质量，后三幅解释算法内部估计与像素变化区域。
绘图逻辑：C++ 输出恢复图与中间散射图，Python 按论文常见的子图编号方式排成 2x3 面板。散射热力图越偏暖，表示估计的介质散射/传输修正越强。
实验现象：ROP$^{+}$ 相比输入的 $\Delta\sigma_Y=0.0066$，$\Delta H=0.2479$，恢复后 $d_{\mathrm{rgb}}=0.2132$。这些数值可用于报告中描述可见度、信息量和色偏变化。
理论分析：若 ROP$^{+}$ 的散射图比 ROP 更贴合远景和低对比区域，说明统一光谱筛选与 TV 细化减少了近景纹理对散射估计的干扰。若差异图在强边缘处明显，通常代表恢复公式主要增强结构边界；若在平坦区域大面积发亮，则可能存在过校正。

### real_lowlight_city_luminance_profile.png
图片内容：左图为图像中线亮度剖面 $Y(x,y_0)$，右图为亮度概率密度 $p(Y)$。
绘图逻辑：用同一行像素比较 Input、ROP、ROP$^{+}$ 的亮度变化，再用全图直方分布观察动态范围是否扩展。
理论分析：退化图像往往亮度集中、对比度低；恢复后曲线起伏增大且直方图分布变宽，说明图像层次被拉开。若曲线出现尖峰或直方图贴近 0/1 边界，则说明参数可能过强。

### real_sandstorm_road_qualitative.png
图片内容：该图包含退化输入、ROP 输出、ROP$^{+}$ 输出、两种散射图热力可视化以及 $3|J-I|$ 差异图。前三幅给出主观视觉质量，后三幅解释算法内部估计与像素变化区域。
绘图逻辑：C++ 输出恢复图与中间散射图，Python 按论文常见的子图编号方式排成 2x3 面板。散射热力图越偏暖，表示估计的介质散射/传输修正越强。
实验现象：ROP$^{+}$ 相比输入的 $\Delta\sigma_Y=0.0758$，$\Delta H=1.0816$，恢复后 $d_{\mathrm{rgb}}=0.0327$。这些数值可用于报告中描述可见度、信息量和色偏变化。
理论分析：若 ROP$^{+}$ 的散射图比 ROP 更贴合远景和低对比区域，说明统一光谱筛选与 TV 细化减少了近景纹理对散射估计的干扰。若差异图在强边缘处明显，通常代表恢复公式主要增强结构边界；若在平坦区域大面积发亮，则可能存在过校正。

### real_sandstorm_road_luminance_profile.png
图片内容：左图为图像中线亮度剖面 $Y(x,y_0)$，右图为亮度概率密度 $p(Y)$。
绘图逻辑：用同一行像素比较 Input、ROP、ROP$^{+}$ 的亮度变化，再用全图直方分布观察动态范围是否扩展。
理论分析：退化图像往往亮度集中、对比度低；恢复后曲线起伏增大且直方图分布变宽，说明图像层次被拉开。若曲线出现尖峰或直方图贴近 0/1 边界，则说明参数可能过强。

### real_underwater_reef_qualitative.png
图片内容：该图包含退化输入、ROP 输出、ROP$^{+}$ 输出、两种散射图热力可视化以及 $3|J-I|$ 差异图。前三幅给出主观视觉质量，后三幅解释算法内部估计与像素变化区域。
绘图逻辑：C++ 输出恢复图与中间散射图，Python 按论文常见的子图编号方式排成 2x3 面板。散射热力图越偏暖，表示估计的介质散射/传输修正越强。
实验现象：ROP$^{+}$ 相比输入的 $\Delta\sigma_Y=-0.0045$，$\Delta H=0.1845$，恢复后 $d_{\mathrm{rgb}}=0.0629$。这些数值可用于报告中描述可见度、信息量和色偏变化。
理论分析：若 ROP$^{+}$ 的散射图比 ROP 更贴合远景和低对比区域，说明统一光谱筛选与 TV 细化减少了近景纹理对散射估计的干扰。若差异图在强边缘处明显，通常代表恢复公式主要增强结构边界；若在平坦区域大面积发亮，则可能存在过校正。

### real_underwater_reef_luminance_profile.png
图片内容：左图为图像中线亮度剖面 $Y(x,y_0)$，右图为亮度概率密度 $p(Y)$。
绘图逻辑：用同一行像素比较 Input、ROP、ROP$^{+}$ 的亮度变化，再用全图直方分布观察动态范围是否扩展。
理论分析：退化图像往往亮度集中、对比度低；恢复后曲线起伏增大且直方图分布变宽，说明图像层次被拉开。若曲线出现尖峰或直方图贴近 0/1 边界，则说明参数可能过强。

### metrics_summary.png
图片内容：四联图同时展示 $\sigma_Y$、$H(Y)$、$d_{\mathrm{rgb}}$ 和 $E_{\nabla}$ 在不同真实照片与不同方法下的变化。
绘图逻辑：每个场景使用 Input、ROP、ROP$^{+}$ 三根柱，避免只看单张照片导致结论片面。该图适合作为读书报告的总量化对比图。
理论分析：$\sigma_Y$ 和 $E_{\nabla}$ 增大通常说明可见度和边缘细节增强；$H(Y)$ 增大说明亮度层次更丰富；$d_{\mathrm{rgb}}$ 下降代表整体色偏被抑制。指标之间可能冲突，因此需要结合 qualitative 图共同判断。

### runtime_comparison.png
图片内容：展示 ROP 与 ROP$^{+}$ 在四张真实照片上的 CPU 耗时。
绘图逻辑：同一场景并列两根柱，对应闭式 O(N) 流程和迭代细化流程。
理论分析：ROP 只包含均值光谱、投影、重采样和恢复公式，因此耗时低；ROP$^{+}$ 增加散射系数优化，耗时上升但可改善复杂前景/背景条件下的恢复稳定性。

### real_haze_mountain_omega_ablation_grid.png
图片内容：展示同一真实照片在不同松弛系数 $\omega$ 下的 ROP$^{+}$ 恢复结果。
绘图逻辑：保持其他参数不变，仅改变 $\omega\in\{0.50,0.65,0.80,0.95\}$，用横向网格直观看参数影响。
理论分析：$\omega$ 越大，散射扣除越强，通常图像更清晰、颜色更鲜明；但过大时容易产生过饱和、暗部噪声放大和边缘伪影。论文默认约 0.8，本实验也将 $\omega=0.8$ 作为主设置。

### real_haze_mountain_omega_ablation_curve.png
图片内容：绘制 $\omega$ 与 $\sigma_Y$、$H(Y)$、$d_{\mathrm{rgb}}$ 的关系曲线。
绘图逻辑：使用 LaTeX 数学符号标注横纵坐标，左轴显示对比度和色偏，右轴显示熵，便于观察参数变化趋势。
理论分析：若 $\sigma_Y$ 与 $H(Y)$ 随 $\omega$ 增加而升高，说明去散射强度增强；若 $d_{\mathrm{rgb}}$ 同时升高，则说明颜色校正可能开始失稳。该图可支撑报告中的参数敏感性讨论。

## 可直接写入报告的总结
真实照片实验比合成图更能暴露 ROP 类方法的优缺点。ROP 的优势是速度快、实现简单，在整体退化较均匀的场景中能快速提高对比度；ROP$^{+}$ 的优势是统一光谱估计更稳，散射图更接近真实场景结构，适合前景/背景差异明显的照片。局限在于该方法仍依赖单幅图像中的颜色统计，当原图存在局部强色光、噪声、JPEG 块效应或本身不是散射退化时，恢复公式会放大这些异常，因此需要结合参数消融与差异图判断是否过校正。