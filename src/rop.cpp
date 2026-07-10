#include "rop.h"

#include <algorithm>
#include <cmath>
#include <numeric>
#include <sstream>

static Vec3 mean_rgb(const Img &img, const std::vector<unsigned char> *mask = nullptr) {
    Vec3 s{0, 0, 0};
    double cnt = 0.0;
    const int n = img.w * img.h;
    for (int i = 0; i < n; ++i) {
        if (mask && !(*mask)[i]) continue;
        s[0] += img.data[i * 3 + 0];
        s[1] += img.data[i * 3 + 1];
        s[2] += img.data[i * 3 + 2];
        cnt += 1.0;
    }
    if (cnt < 1.0) cnt = 1.0;
    for (float &x : s) x = static_cast<float>(x / cnt);
    return s;
}

static Vec3 l1_norm(Vec3 v) {
    const float s = std::max(v[0] + v[1] + v[2], 1e-6f);
    for (float &x : v) x /= s;
    return v;
}

static Vec3 l2_norm(Vec3 v) {
    const float s = std::sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
    const float d = std::max(s, 1e-6f);
    for (float &x : v) x /= d;
    return v;
}

static Img initial_scatter(const Img &img, Vec3 rgb, Vec3 &snu) {
    const Vec3 basis = l2_norm(rgb);
    snu = l1_norm(rgb);
    Img st(img.w, img.h);
    const float sum_rgb = std::max(rgb[0] + rgb[1] + rgb[2], 1e-6f);
    for (int y = 0; y < img.h; ++y) {
        for (int x = 0; x < img.w; ++x) {
            const float r = img.at(x, y, 0);
            const float g = img.at(x, y, 1);
            const float b = img.at(x, y, 2);
            const float len = std::max(std::sqrt(r * r + g * g + b * b), 1e-6f);
            const float cosv = (r * basis[0] + g * basis[1] + b * basis[2]) / len;
            const float mag = cosv * (r + g + b) / sum_rgb;
            st.at(x, y, 0) = clamp01(mag * rgb[0]);
            st.at(x, y, 1) = clamp01(mag * rgb[1]);
            st.at(x, y, 2) = clamp01(mag * rgb[2]);
        }
    }
    return st;
}

static Vec3 fix_air(const Img &img, Img &st, Vec3 snu, float top_rate, bool plus) {
    const int n = img.w * img.h;
    std::vector<std::pair<float, int>> a;
    a.reserve(n);
    for (int i = 0; i < n; ++i) {
        a.push_back({st.data[i * 3] + st.data[i * 3 + 1] + st.data[i * 3 + 2], i});
    }
    const int k = std::max(1, static_cast<int>(n * top_rate));
    std::nth_element(a.begin(), a.begin() + k - 1, a.end(), [](auto x, auto y) {
        return x.first > y.first;
    });
    Vec3 air{0, 0, 0};
    for (int i = 0; i < k; ++i) {
        const int id = a[i].second;
        for (int c = 0; c < 3; ++c) air[c] += img.data[id * 3 + c];
    }
    for (float &x : air) x = std::max(x / k, 1e-4f);

    std::sort(a.begin(), a.end(), [](auto x, auto y) { return x.first > y.first; });
    const float sek = a[k - 1].first;
    for (int i = 0; i < n; ++i) {
        const float ss = st.data[i * 3] + st.data[i * 3 + 1] + st.data[i * 3 + 2];
        if (ss <= sek) continue;
        for (int c = 0; c < 3; ++c) {
            const float limit = plus ? (2.0f * sek * snu[c]) : (2.0f * sek / 3.0f);
            st.data[i * 3 + c] = clamp01(limit - st.data[i * 3 + c]);
        }
    }
    return air;
}

static Img gamma_y(const Img &src) {
    Img out = src;
    for (int i = 0; i < src.w * src.h; ++i) {
        float r = clamp01(out.data[i * 3 + 0]);
        float g = clamp01(out.data[i * 3 + 1]);
        float b = clamp01(out.data[i * 3 + 2]);
        float y = 0.299f * r + 0.587f * g + 0.114f * b;
        const float yy = std::pow(clamp01(y), 5.0f / 6.0f);
        const float k = yy / std::max(y, 1e-4f);
        out.data[i * 3 + 0] = clamp01(r * k);
        out.data[i * 3 + 1] = clamp01(g * k);
        out.data[i * 3 + 2] = clamp01(b * k);
    }
    return out;
}

static float percentile(std::vector<float> v, float pct) {
    if (v.empty()) return 0.0f;
    std::sort(v.begin(), v.end());
    const float pos = (pct / 100.0f) * (v.size() - 1);
    const int i = static_cast<int>(std::floor(pos));
    const int j = std::min(i + 1, static_cast<int>(v.size()) - 1);
    const float t = pos - i;
    return v[i] * (1.0f - t) + v[j] * t;
}

static Img stretch_gamma(const Img &src, float lo_pct, float hi_pct) {
    Img out = src;
    for (int c = 0; c < 3; ++c) {
        std::vector<float> vals;
        vals.reserve(src.w * src.h);
        for (int i = 0; i < src.w * src.h; ++i) {
            float x = src.data[i * 3 + c];
            if (std::isfinite(x)) vals.push_back(x);
        }
        const float lo = percentile(vals, lo_pct);
        const float hi = percentile(vals, hi_pct);
        const float den = std::max(hi - lo, 1e-5f);
        for (int i = 0; i < src.w * src.h; ++i) {
            out.data[i * 3 + c] = clamp01((src.data[i * 3 + c] - lo) / den);
        }
    }
    return gamma_y(out);
}

static Img recover_from_scatter(const Img &img, const Img &st, Vec3 air, float omega) {
    Img out(img.w, img.h);
    for (int i = 0; i < img.w * img.h; ++i) {
        for (int c = 0; c < 3; ++c) {
            const float t = std::max(1.0f - omega * st.data[i * 3 + c], 0.001f);
            out.data[i * 3 + c] = (img.data[i * 3 + c] - air[c]) / t + air[c];
        }
    }
    return out;
}

static Img recover_from_t(const Img &img, const Img &t, Vec3 air) {
    Img out(img.w, img.h);
    for (int i = 0; i < img.w * img.h; ++i) {
        for (int c = 0; c < 3; ++c) {
            out.data[i * 3 + c] = (img.data[i * 3 + c] - air[c]) / std::max(t.data[i * 3 + c], 0.01f) + air[c];
        }
    }
    return out;
}

static void grad_img(const Img &img, std::vector<float> &gx, std::vector<float> &gy) {
    const int w = img.w;
    const int h = img.h;
    gx.assign(static_cast<size_t>(w * h * 3), 0.0f);
    gy.assign(static_cast<size_t>(w * h * 3), 0.0f);
    for (int y = 0; y < h; ++y) {
        const int yn = (y + 1) % h;
        for (int x = 0; x < w; ++x) {
            const int xn = (x + 1) % w;
            const int id = (y * w + x) * 3;
            for (int c = 0; c < 3; ++c) {
                gx[id + c] = img.at(xn, y, c) - img.at(x, y, c);
                gy[id + c] = img.at(x, yn, c) - img.at(x, y, c);
            }
        }
    }
}

static void grad_1(const std::vector<float> &u, int w, int h, std::vector<float> &gx, std::vector<float> &gy) {
    gx.assign(static_cast<size_t>(w * h), 0.0f);
    gy.assign(static_cast<size_t>(w * h), 0.0f);
    for (int y = 0; y < h; ++y) {
        const int yn = (y + 1) % h;
        for (int x = 0; x < w; ++x) {
            const int xn = (x + 1) % w;
            const int id = y * w + x;
            gx[id] = u[y * w + xn] - u[id];
            gy[id] = u[yn * w + x] - u[id];
        }
    }
}

static float div_at(const std::vector<float> &xv, const std::vector<float> &yv, int w, int h, int x, int y, int c, bool rgb) {
    const int xl = (x - 1 + w) % w;
    const int yu = (y - 1 + h) % h;
    if (rgb) {
        const int id = (y * w + x) * 3 + c;
        return xv[(y * w + xl) * 3 + c] - xv[id] + yv[(yu * w + x) * 3 + c] - yv[id];
    }
    const int id = y * w + x;
    return xv[y * w + xl] - xv[id] + yv[yu * w + x] - yv[id];
}

static std::vector<float> refine_c(const Img &img, const Img &t0, Vec3 snu, const Params &p) {
    const int w = img.w;
    const int h = img.h;
    const int n = w * h;
    constexpr float lambda1 = 5.0f;
    constexpr float lambda2 = 0.5f;
    constexpr float lambda3 = 0.5f;
    constexpr float beta = 10.0f;
    constexpr float tao = 1.618f;
    std::vector<float> c0(n), c(n);
    for (int i = 0; i < n; ++i) c0[i] = c[i] = t0.data[i * 3] + t0.data[i * 3 + 1] + t0.data[i * 3 + 2];
    const float s2 = snu[0] * snu[0] + snu[1] * snu[1] + snu[2] * snu[2];

    std::vector<float> d1i, d2i, d1c, d2c;
    grad_img(img, d1i, d2i);
    grad_1(c, w, h, d1c, d2c);

    std::vector<float> lxi1(n * 3), lxi2(n * 3), leta1(n), leta2(n);
    std::vector<float> xmg1(n * 3), xmg2(n * 3), zmg1(n), zmg2(n);
    std::vector<float> zeta1x(n * 3), zeta1y(n * 3), zeta2x(n), zeta2y(n);
    for (int it = 0; it < p.iter; ++it) {
        for (int i = 0; i < n; ++i) {
            for (int ch = 0; ch < 3; ++ch) {
                const int id = i * 3 + ch;
                const float a = snu[ch] * d1c[i] - d1i[id] + lxi1[id] / beta;
                const float b = snu[ch] * d2c[i] - d2i[id] + lxi2[id] / beta;
                const float mag = std::sqrt(a * a + b * b);
                const float ww = std::exp(-p.gamma * (std::abs(d1i[id]) + std::abs(d2i[id])));
                const float sh = std::max(mag - ww * lambda1 / beta, 0.0f) / (mag + 1e-8f);
                xmg1[id] = a * sh;
                xmg2[id] = b * sh;
                zeta1x[id] = xmg1[id] + d1i[id] - lxi1[id] / beta;
                zeta1y[id] = xmg2[id] + d2i[id] - lxi2[id] / beta;
            }
            const float za = d1c[i] + leta1[i] / beta;
            const float zb = d2c[i] + leta2[i] / beta;
            const float zmag = std::sqrt(za * za + zb * zb);
            const float zsh = std::max(zmag - lambda2 / beta, 0.0f) / (zmag + 1e-8f);
            zmg1[i] = za * zsh;
            zmg2[i] = zb * zsh;
            zeta2x[i] = zmg1[i] - leta1[i] / beta;
            zeta2y[i] = zmg2[i] - leta2[i] / beta;
        }

        std::vector<float> rhs(n, 0.0f), next = c;
        for (int y = 0; y < h; ++y) {
            for (int x = 0; x < w; ++x) {
                const int i = y * w + x;
                float v = lambda3 * c0[i] + beta * div_at(zeta2x, zeta2y, w, h, x, y, 0, false);
                for (int ch = 0; ch < 3; ++ch) {
                    const float divv = div_at(zeta1x, zeta1y, w, h, x, y, ch, true);
                    v += beta * snu[ch] * divv;
                }
                rhs[i] = v;
            }
        }
        const float coef = beta * (s2 + 1.0f);
        for (int relax = 0; relax < 25; ++relax) {
            for (int y = 0; y < h; ++y) {
                const int yd = (y + 1) % h;
                const int yu = (y - 1 + h) % h;
                for (int x = 0; x < w; ++x) {
                    const int xl = (x - 1 + w) % w;
                    const int xr = (x + 1) % w;
                    const int i = y * w + x;
                    const float nb = next[y * w + xl] + next[y * w + xr] + next[yu * w + x] + next[yd * w + x];
                    c[i] = clamp01((rhs[i] + coef * nb) / (lambda3 + 4.0f * coef));
                }
            }
            std::swap(c, next);
        }
        c = next;
        grad_1(c, w, h, d1c, d2c);
        for (int i = 0; i < n; ++i) {
            for (int ch = 0; ch < 3; ++ch) {
                const int id = i * 3 + ch;
                lxi1[id] -= tao * beta * (xmg1[id] - (snu[ch] * d1c[i] - d1i[id]));
                lxi2[id] -= tao * beta * (xmg2[id] - (snu[ch] * d2c[i] - d2i[id]));
            }
            leta1[i] -= tao * beta * (zmg1[i] - d1c[i]);
            leta2[i] -= tao * beta * (zmg2[i] - d2c[i]);
        }
    }
    return c;
}

Res run_rop(const Img &img, const Params &p) {
    Res r;
    Vec3 snu{};
    r.init_scatter = initial_scatter(img, mean_rgb(img), snu);
    r.air = fix_air(img, r.init_scatter, snu, 0.001f, false);
    const int m = std::min(img.w, img.h);
    const float rate = m < 800 ? 0.02f : (m < 1500 ? 0.01f : 0.005f);
    Img small = resize_bilinear(r.init_scatter, std::max(2, static_cast<int>(img.w * rate)), std::max(2, static_cast<int>(img.h * rate)));
    r.scatter = resize_bilinear(small, img.w, img.h);
    r.out = stretch_gamma(recover_from_scatter(img, r.scatter, r.air, p.omega), p.low_pct, p.high_pct);
    r.spectrum = snu;
    r.coef.resize(static_cast<size_t>(img.w * img.h));
    for (int i = 0; i < img.w * img.h; ++i) r.coef[i] = (r.scatter.data[i * 3] + r.scatter.data[i * 3 + 1] + r.scatter.data[i * 3 + 2]) / 3.0f;
    return r;
}

Res run_rop_plus(const Img &img, const Params &p) {
    Res r;
    const int n = img.w * img.h;
    std::vector<unsigned char> mask(n, 1);
    Vec3 rgb = mean_rgb(img);
    Vec3 prev{1, 1, 1};
    for (int step = 0; step < 20; ++step) {
        rgb = mean_rgb(img, &mask);
        const Vec3 b = l2_norm(rgb);
        float delta = std::abs(b[0] - prev[0]) + std::abs(b[1] - prev[1]) + std::abs(b[2] - prev[2]);
        prev = b;
        int kept = 0;
        for (int i = 0; i < n; ++i) {
            const float rr = img.data[i * 3], gg = img.data[i * 3 + 1], bb = img.data[i * 3 + 2];
            const float len = std::max(std::sqrt(rr * rr + gg * gg + bb * bb), 1e-6f);
            const float cosv = (rr * b[0] + gg * b[1] + bb * b[2]) / len;
            mask[i] = cosv > 0.99f;
            kept += mask[i] ? 1 : 0;
        }
        if (kept < n / 50) std::fill(mask.begin(), mask.end(), 1);
        if (delta < 1e-5f) break;
    }
    Vec3 snu{};
    r.init_scatter = initial_scatter(img, rgb, snu);
    r.air = fix_air(img, r.init_scatter, snu, 0.01f, true);

    r.coef = refine_c(img, r.init_scatter, snu, p);
    Img t(img.w, img.h);
    r.scatter = Img(img.w, img.h);
    for (int i = 0; i < n; ++i) {
        for (int ch = 0; ch < 3; ++ch) {
            r.scatter.data[i * 3 + ch] = clamp01(r.coef[i] * snu[ch]);
            t.data[i * 3 + ch] = clamp01(1.0f - p.omega * r.scatter.data[i * 3 + ch]);
        }
    }
    r.out = stretch_gamma(recover_from_t(img, t, r.air), p.low_pct, p.high_pct);
    r.spectrum = snu;
    return r;
}

Img retinex_lowlight(const Img &img, const Params &p, bool plus) {
    Img inv = img;
    for (float &x : inv.data) x = 1.0f - x;
    Res r = plus ? run_rop_plus(inv, p) : run_rop(inv, p);
    Img out = r.out;
    for (float &x : out.data) x = 1.0f - x;
    return gamma_y(out);
}

std::string vec3_text(const Vec3 &v) {
    std::ostringstream ss;
    ss.precision(4);
    ss << v[0] << ";" << v[1] << ";" << v[2];
    return ss.str();
}
