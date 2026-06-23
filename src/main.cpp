#include "img.h"
#include "metrics.h"
#include "rop.h"

#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>

namespace fs = std::filesystem;

static std::string stem(const fs::path &p) {
    return p.stem().string();
}

template <class F>
static auto timed(F &&fn, double &ms) {
    const auto t0 = std::chrono::steady_clock::now();
    auto v = fn();
    const auto t1 = std::chrono::steady_clock::now();
    ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
    return v;
}

int main(int argc, char **argv) {
    std::string in_dir = "assets/input";
    std::string out_dir = "output";
    Params p;
    for (int i = 1; i < argc; ++i) {
        const std::string a = argv[i];
        if (a == "--input" && i + 1 < argc) in_dir = argv[++i];
        else if (a == "--output" && i + 1 < argc) out_dir = argv[++i];
        else if (a == "--omega" && i + 1 < argc) p.omega = std::stof(argv[++i]);
        else if (a == "--iter" && i + 1 < argc) p.iter = std::stoi(argv[++i]);
        else if (a == "--gamma" && i + 1 < argc) p.gamma = std::stof(argv[++i]);
    }

    fs::create_directories(fs::path(out_dir) / "images");
    fs::create_directories(fs::path(out_dir) / "csv");
    std::ofstream csv(fs::path(out_dir) / "csv" / "metrics.csv");
    csv << metric_header();

    bool first = true;
    for (const auto &e : fs::directory_iterator(in_dir)) {
        if (e.path().extension() != ".ppm") continue;
        const Img img = read_ppm(e.path().string());
        const std::string name = stem(e.path());
        write_ppm((fs::path(out_dir) / "images" / (name + "_input.ppm")).string(), img);
        csv << metric_row(measure(img, name, "input", p.omega, 0.0));

        double ms1 = 0.0;
        Res r1 = timed([&] { return run_rop(img, p); }, ms1);
        write_ppm((fs::path(out_dir) / "images" / (name + "_rop.ppm")).string(), r1.out);
        write_ppm((fs::path(out_dir) / "images" / (name + "_rop_scatter.ppm")).string(), heatmap(r1.coef, img.w, img.h));
        write_ppm((fs::path(out_dir) / "images" / (name + "_rop_diff.ppm")).string(), abs_diff(img, r1.out));
        csv << metric_row(measure(r1.out, name, "ROP", p.omega, ms1));

        double ms2 = 0.0;
        Res r2 = timed([&] { return run_rop_plus(img, p); }, ms2);
        write_ppm((fs::path(out_dir) / "images" / (name + "_rop_plus.ppm")).string(), r2.out);
        write_ppm((fs::path(out_dir) / "images" / (name + "_rop_plus_scatter.ppm")).string(), heatmap(r2.coef, img.w, img.h));
        write_ppm((fs::path(out_dir) / "images" / (name + "_rop_plus_diff.ppm")).string(), abs_diff(img, r2.out));
        csv << metric_row(measure(r2.out, name, "ROP+", p.omega, ms2));

        if (name.find("lowlight") != std::string::npos) {
            Img ll = retinex_lowlight(img, p, true);
            write_ppm((fs::path(out_dir) / "images" / (name + "_retinex_rop_plus.ppm")).string(), ll);
            csv << metric_row(measure(ll, name, "Retinex-ROP+", p.omega, 0.0));
        }

        if (first) {
            first = false;
            const float vals[] = {0.50f, 0.65f, 0.80f, 0.95f};
            for (float om : vals) {
                Params ap = p;
                ap.omega = om;
                double ms = 0.0;
                Res ar = timed([&] { return run_rop_plus(img, ap); }, ms);
                const std::string tag = name + "_ablation_w" + std::to_string(static_cast<int>(om * 100));
                write_ppm((fs::path(out_dir) / "images" / (tag + ".ppm")).string(), ar.out);
                csv << metric_row(measure(ar.out, name, "ablation", om, ms));
            }
        }
        std::cout << name << " done. spectrum ROP+=" << vec3_text(r2.spectrum) << "\n";
    }
    return 0;
}
