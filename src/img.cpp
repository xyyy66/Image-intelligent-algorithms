#include "img.h"

#include <algorithm>
#include <cctype>
#include <cmath>
#include <fstream>
#include <stdexcept>

Img::Img(int ww, int hh, float v) : w(ww), h(hh), data(static_cast<size_t>(ww * hh * 3), v) {}

float &Img::at(int x, int y, int c) {
    return data[(static_cast<size_t>(y) * w + x) * 3 + c];
}

float Img::at(int x, int y, int c) const {
    return data[(static_cast<size_t>(y) * w + x) * 3 + c];
}

float clamp01(float v) {
    return std::min(1.0f, std::max(0.0f, v));
}

static std::string next_token(std::istream &in) {
    std::string s;
    char ch = 0;
    while (in.get(ch)) {
        if (std::isspace(static_cast<unsigned char>(ch))) continue;
        if (ch == '#') {
            std::string line;
            std::getline(in, line);
            continue;
        }
        s.push_back(ch);
        break;
    }
    while (in.get(ch)) {
        if (std::isspace(static_cast<unsigned char>(ch))) break;
        s.push_back(ch);
    }
    if (s.empty()) throw std::runtime_error("bad ppm header");
    return s;
}

Img read_ppm(const std::string &path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) throw std::runtime_error("can not open " + path);
    const std::string magic = next_token(in);
    if (magic != "P6") throw std::runtime_error("only P6 ppm is supported: " + path);
    const int w = std::stoi(next_token(in));
    const int h = std::stoi(next_token(in));
    const int maxv = std::stoi(next_token(in));
    if (w <= 0 || h <= 0 || maxv <= 0 || maxv > 255) throw std::runtime_error("bad ppm size");

    std::vector<unsigned char> raw(static_cast<size_t>(w * h * 3));
    in.read(reinterpret_cast<char *>(raw.data()), static_cast<std::streamsize>(raw.size()));
    if (in.gcount() != static_cast<std::streamsize>(raw.size())) throw std::runtime_error("truncated ppm");

    Img img(w, h);
    for (size_t i = 0; i < raw.size(); ++i) img.data[i] = raw[i] / static_cast<float>(maxv);
    return img;
}

void write_ppm(const std::string &path, const Img &img) {
    std::ofstream out(path, std::ios::binary);
    if (!out) throw std::runtime_error("can not write " + path);
    out << "P6\n" << img.w << " " << img.h << "\n255\n";
    std::vector<unsigned char> raw(img.data.size());
    for (size_t i = 0; i < img.data.size(); ++i) {
        raw[i] = static_cast<unsigned char>(std::lround(clamp01(img.data[i]) * 255.0f));
    }
    out.write(reinterpret_cast<const char *>(raw.data()), static_cast<std::streamsize>(raw.size()));
}

void write_pgm(const std::string &path, int w, int h, const std::vector<float> &v) {
    std::ofstream out(path, std::ios::binary);
    if (!out) throw std::runtime_error("can not write " + path);
    out << "P5\n" << w << " " << h << "\n255\n";
    auto mm = std::minmax_element(v.begin(), v.end());
    const float lo = *mm.first;
    const float hi = *mm.second;
    const float den = std::max(hi - lo, 1e-6f);
    std::vector<unsigned char> raw(v.size());
    for (size_t i = 0; i < v.size(); ++i) {
        raw[i] = static_cast<unsigned char>(std::lround(clamp01((v[i] - lo) / den) * 255.0f));
    }
    out.write(reinterpret_cast<const char *>(raw.data()), static_cast<std::streamsize>(raw.size()));
}

Img resize_bilinear(const Img &src, int nw, int nh) {
    Img dst(nw, nh);
    const float sx = src.w / static_cast<float>(nw);
    const float sy = src.h / static_cast<float>(nh);
    for (int y = 0; y < nh; ++y) {
        const float fy = (y + 0.5f) * sy - 0.5f;
        const int y0 = std::clamp(static_cast<int>(std::floor(fy)), 0, src.h - 1);
        const int y1 = std::min(y0 + 1, src.h - 1);
        const float wy = fy - y0;
        for (int x = 0; x < nw; ++x) {
            const float fx = (x + 0.5f) * sx - 0.5f;
            const int x0 = std::clamp(static_cast<int>(std::floor(fx)), 0, src.w - 1);
            const int x1 = std::min(x0 + 1, src.w - 1);
            const float wx = fx - x0;
            for (int c = 0; c < 3; ++c) {
                const float a = src.at(x0, y0, c) * (1 - wx) + src.at(x1, y0, c) * wx;
                const float b = src.at(x0, y1, c) * (1 - wx) + src.at(x1, y1, c) * wx;
                dst.at(x, y, c) = a * (1 - wy) + b * wy;
            }
        }
    }
    return dst;
}

std::vector<float> resize_bilinear(const std::vector<float> &src, int w, int h, int nw, int nh) {
    Img tmp(w, h);
    for (int i = 0; i < w * h; ++i) {
        tmp.data[i * 3 + 0] = src[i];
        tmp.data[i * 3 + 1] = src[i];
        tmp.data[i * 3 + 2] = src[i];
    }
    Img out = resize_bilinear(tmp, nw, nh);
    std::vector<float> dst(static_cast<size_t>(nw * nh));
    for (int i = 0; i < nw * nh; ++i) dst[i] = out.data[i * 3];
    return dst;
}

Img heatmap(const std::vector<float> &v, int w, int h) {
    Img out(w, h);
    auto mm = std::minmax_element(v.begin(), v.end());
    const float lo = *mm.first;
    const float hi = *mm.second;
    const float den = std::max(hi - lo, 1e-6f);
    for (int i = 0; i < w * h; ++i) {
        const float t = clamp01((v[i] - lo) / den);
        out.data[i * 3 + 0] = clamp01(1.5f * t - 0.20f);
        out.data[i * 3 + 1] = clamp01(1.5f - std::abs(2.0f * t - 1.0f));
        out.data[i * 3 + 2] = clamp01(1.25f * (1.0f - t));
    }
    return out;
}

Img abs_diff(const Img &a, const Img &b) {
    if (a.w != b.w || a.h != b.h) throw std::runtime_error("image size mismatch");
    Img out(a.w, a.h);
    for (size_t i = 0; i < a.data.size(); ++i) out.data[i] = std::abs(a.data[i] - b.data[i]) * 3.0f;
    return out;
}
