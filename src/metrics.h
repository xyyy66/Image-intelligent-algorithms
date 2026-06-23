#pragma once

#include "img.h"

#include <string>

struct Metric {
    std::string name;
    std::string method;
    float omega = 0.0f;
    double ms = 0.0;
    double bright = 0.0;
    double contrast = 0.0;
    double entropy = 0.0;
    double color_cast = 0.0;
    double edge = 0.0;
};

Metric measure(const Img &img, std::string name, std::string method, float omega, double ms);
std::string metric_header();
std::string metric_row(const Metric &m);
