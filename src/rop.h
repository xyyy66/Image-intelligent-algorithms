#pragma once

#include "img.h"

#include <string>
#include <vector>

struct Params {
    float omega = 0.80f;
    float gamma = 50.0f;
    int iter = 10;
    float low_pct = 1.0f;
    float high_pct = 95.0f;
};

struct Res {
    Img out;
    Img scatter;
    Img init_scatter;
    std::vector<float> coef;
    Vec3 spectrum{};
    Vec3 air{};
};

Res run_rop(const Img &img, const Params &p);
Res run_rop_plus(const Img &img, const Params &p);
Img retinex_lowlight(const Img &img, const Params &p, bool plus);
std::string vec3_text(const Vec3 &v);
