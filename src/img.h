#pragma once

#include <array>
#include <string>
#include <vector>

struct Img {
    int w = 0;
    int h = 0;
    std::vector<float> data;

    Img() = default;
    Img(int ww, int hh, float v = 0.0f);

    float &at(int x, int y, int c);
    float at(int x, int y, int c) const;
};

using Vec3 = std::array<float, 3>;

Img read_ppm(const std::string &path);
void write_ppm(const std::string &path, const Img &img);
void write_pgm(const std::string &path, int w, int h, const std::vector<float> &v);

float clamp01(float v);
Img resize_bilinear(const Img &src, int nw, int nh);
std::vector<float> resize_bilinear(const std::vector<float> &src, int w, int h, int nw, int nh);
Img heatmap(const std::vector<float> &v, int w, int h);
Img abs_diff(const Img &a, const Img &b);
