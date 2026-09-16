#!/usr/bin/env python3
"""SPECTRUM-EXACT SHARP SYNTHESIS, 1880.0-2025.9 monthly.
Recipe: amplitude spectrum of real monthly pdo (optionally tilted
f^alpha), random phase, 20 IAAFT passes to the pdo marginal -> same
SPECTRAL SPREAD as the soft surrogate but real-like sharpness
(surrogate curvature 0.0002, real 0.039). Then: fit the shipped PDO
design (pdo manifold, windings from lt.exe.p, sigma=10) and the
winding_rank ridge scan + targeted 0.4488-band test. Prediction: r
falls back from 0.865 to the ~0.81 real-capture level (smoothness
gift removed); ridges stay empty (random phase -> no locking).
"""
import json
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/paul/eval/winding_scalogram")
from winding_rank import (read_results_csv, winding_transform, ar1_floor,
                          find_ridges, continuity)
from wavelet_scalogram import standardize

ROOT = Path("/home/paul/eval/winding_scalogram")
SRC = open(ROOT / "supplemental_2026_09/supplemental2.py").read()
exec(SRC.split("CFG = {")[0])

t1, x1_raw, f1raw = read_results_csv(ROOT / "pdo" / "lte_results.csv")
tp1 = month_grid(t1)
x1 = standardize(np.interp(tp1, t1, x1_raw))
N1 = len(x1)
t2 = np.arange(round(1880 * 12), round(2026 * 12)) / 12.0   # ->2025.9166
N2 = len(t2)
fr1 = np.fft.rfftfreq(N1, d=1 / 12)
fr2 = np.fft.rfftfreq(N2, d=1 / 12)
A2 = np.interp(fr2, fr1, np.abs(np.fft.rfft(x1)))
A2[0] = 0.0
f_ref = 1 / 5

def synth(alpha, seed, nit=20):
    rng = np.random.default_rng(seed)
    Am = A2 * (np.maximum(fr2, 1e-9) / f_ref) ** alpha
    ph = rng.uniform(-np.pi, np.pi, len(Am))
    z = np.fft.irfft(Am * np.exp(1j * ph), n=N2)
    tv = np.sort(x1)
    fr = (np.arange(N2) + 0.5) / N2          # full-marginal quantile map
    for _ in range(nit):
        Z = np.fft.rfft(z)
        Z = Am * np.exp(1j * np.angle(Z))
        zf = np.fft.irfft(Z, n=N2)
        z = np.quantile(tv, fr[np.argsort(np.argsort(zf))])
    return standardize(z)

def st(v):
    return (float(np.corrcoef(v[:-1], v[1:])[0, 1]),
            float(np.var(np.diff(v, 2)) / np.var(v)))

def lowfrac(v, t):
    P = np.abs(np.fft.rfft(v)) ** 2
    f = np.fft.rfftfreq(len(v), d=1 / 12)
    m = f > 1e-6
    return float(P[m & (f < 0.1)].sum() / P[m].sum())

cs = np.loadtxt(ROOT / "pdo_iaaft_detuned_surrogate" /
                "pdo_iaaft_detuned_surrogate.dat")
xs = standardize(cs[:, 1])
p = json.load(open(ROOT / "pdo" / "lt.exe.p"))
Ms = sorted({round(abs(m), 4) for m in p["ltep"] if 0.002 < abs(m) < 10})

def fit(F, tp, v, nmax):
    y = local_fit(F, tp, v, 10.0, Ms, nmax=nmax, mask=np.ones(len(tp), bool))
    return (float(np.corrcoef(v, y)[0, 1]),
            float(np.corrcoef(np.diff(v), np.diff(y))[0, 1]), y)

print(f"{'series':12s} {'rho1':>7s} {'curv':>7s} {'lowfrac':>8s}")
print(f"{'real pdo':12s} {st(x1)[0]:7.4f} {st(x1)[1]:7.4f} "
      f"{lowfrac(x1, tp1):8.3f}")
print(f"{'surrogate':12s} {st(xs)[0]:7.4f} {st(xs)[1]:7.4f} "
      f"{lowfrac(xs, cs[:,0]):8.3f}")
series = {"flat_a0": synth(0.0, 7), "sharp_a05": synth(0.5, 8)}
for k, v in series.items():
    print(f"{k:12s} {st(v)[0]:7.4f} {st(v)[1]:7.4f} {lowfrac(v, t2):8.3f}")

F1 = manifold(p, YL, tp1)
r3, d3, _ = fit(F1, tp1, x1, 3)
print(f"\nfit pdo design: real pdo n<=3 r={r3:.3f} dCC={d3:.3f}")
Fs = manifold(p, YL, cs[:, 0])
r3, d3, _ = fit(Fs, cs[:, 0], xs, 3)
print(f"                soft surrogate  r={r3:.3f} dCC={d3:.3f}")
out = {}
for k, v in series.items():
    F = manifold(p, YL, t2)
    r3, d3, y3 = fit(F, t2, v, 3)
    r6, d6, y6 = fit(F, t2, v, 6)
    out[k] = dict(rho1=st(v)[0], curv=st(v)[1], r3=r3, d3=d3, r6=r6, d6=d6)
    np.savetxt(ROOT / f"supplemental_2026_09/sharp2025_{k}.dat",
               np.vstack([t2, v]).T, fmt="%.6f")
    print(f"                {k}: n<=3 r={r3:.3f} dCC={d3:.3f} | "
          f"n<=6 r={r6:.3f} dCC={d6:.3f}")

# ---- ridge scans on the new grid (floor once, shared forcing)
sig, t0s, dm, mmax = 15.0, 5.0, 0.004, 1.5
m_grid = np.arange(0.0, mmax + dm / 2, dm)
t0g = np.arange(t2[0] + sig / 2, t2[-1] - sig / 2 + 1e-9, t0s)
forcing = manifold(p, YL, t2)   # common manifold extended to 2026
floor = ar1_floor(t2, forcing, m_grid, t0g, sig, n_reps=24)
bg = np.arange(0.35, 0.55 + dm / 2, dm)
floorb = ar1_floor(t2, forcing, bg, t0g, sig, n_reps=24)

def scan(v, lab):
    G, _, _ = winding_transform(t2, standardize(v), forcing, m_grid, t0g, sig)
    lp = np.log2(np.maximum(np.abs(G) ** 2 / floor[:, None], 1e-9))
    prof = np.abs(G).mean(axis=1)
    cands = []
    for M, pk, fw in find_ridges(m_grid, prof, lp, 2.0, 0.12):
        ct = continuity(lp, m_grid, M)
        cands.append({"M": round(M, 4), "bits": round(float(pk), 2),
                      "fwhm": round(fw, 3), "cont": round(ct, 2),
                      "pass": bool(fw <= 0.12 and ct >= 0.70)})
    Gb, _, _ = winding_transform(t2, standardize(v), forcing, bg, t0g, sig)
    lpb = np.log2(np.maximum(np.abs(Gb) ** 2 / floorb[:, None], 1e-9))
    profb = np.abs(Gb).mean(axis=1)
    j = int(np.argmin(np.abs(bg - 0.4488)))
    bd = {"band_bits@0.4488": round(float(lpb.mean(axis=1)[j]), 2),
          "band_max_bits": round(float(lpb.mean(axis=1).max()), 2),
          "cont@0.4488": round(continuity(lpb, bg, 0.4488), 2)}
    out.setdefault(lab, {})["ridges"] = cands
    out[lab]["band"] = bd
    print(f"\n{lab} ridges: {cands}")
    print(f"{lab} band@0.4488: {bd}")

for k, v in series.items():
    scan(v, k)
json.dump(out, open(ROOT / "supplemental_2026_09/figures/"
                    "sharp2025_results.json", "w"), indent=1)
print("\nsaved figures/sharp2025_results.json + .dat members")
