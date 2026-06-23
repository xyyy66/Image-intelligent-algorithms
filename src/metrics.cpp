#include "metrics.h"

#include <algorithm>
#include <cmath>
#include <sstream>

Metric measure(const Img &img, std::string name, std::string method, float omega, double ms) {
    Metric m;
    m.name = std::move(name);
    m.method = std::move(method);
    m.omega = omega;
    m.ms = ms;
    const int n = img.w * img.h;
    double sum = 0.0;
    double sr = 0.0, sg = 0.0, sb = 0.0;
    int hist[256]{};
    for (int i = 0; i < n; ++i) {
        const double r = img.data[i * 3];
        const double g = img.data[i * 3 + 1];
        const double b = img.data[i * 3 + 2];
        const double y = 0.299 * r + 0.587 * g + 0.114 * b;
        sum += y;
        sr += r;
        sg += g;
        sb += b;
        hist[std::clamp(static_cast<int>(std::lround(y * 255.0)), 0, 255)]++;
    }
    m.bright = sum / n;
    double var = 0.0;
    for (int i = 0; i < n; ++i) {
        const double y = 0.299 * img.data[i * 3] + 0.587 * img.data[i * 3 + 1] + 0.114 * img.data[i * 3 + 2];
        var += (y - m.bright) * (y - m.bright);
    }
    m.contrast = std::sqrt(var / n);
    for (int h : hist) {
        if (!h) continue;
        const double p = h / static_cast<double>(n);
        m.entropy -= p * std::log2(p);
    }
    sr /= n;
    sg /= n;
    sb /= n;
    const double mu = (sr + sg + sb) / 3.0;
    m.color_cast = std::sqrt((sr - mu) * (sr - mu) + (sg - mu) * (sg - mu) + (sb - mu) * (sb - mu));
    double e = 0.0;
    for (int y = 0; y + 1 < img.h; ++y) {
        for (int x = 0; x + 1 < img.w; ++x) {
            double dx = 0.0, dy = 0.0;
            for (int c = 0; c < 3; ++c) {
                dx += std::abs(img.at(x + 1, y, c) - img.at(x, y, c));
                dy += std::abs(img.at(x, y + 1, c) - img.at(x, y, c));
            }
            e += dx + dy;
        }
    }
    m.edge = e / std::max(1, (img.w - 1) * (img.h - 1));
    return m;
}

std::string metric_header() {
    return "image,method,omega,time_ms,brightness,contrast,entropy,color_cast,edge_energy\n";
}

std::string metric_row(const Metric &m) {
    std::ostringstream ss;
    ss.precision(6);
    ss << m.name << "," << m.method << "," << m.omega << "," << m.ms << ","
       << m.bright << "," << m.contrast << "," << m.entropy << ","
       << m.color_cast << "," << m.edge << "\n";
    return ss.str();
}
