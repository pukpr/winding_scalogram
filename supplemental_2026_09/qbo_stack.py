#!/usr/bin/env python3
"""QBO stack — k=0 parallel category, same house style as
milestone_2026_09/marquee_stack.png and supplemental stacks.

Differences from the ocean marquee, deliberate and labelled:
  - forcing manifold = draconic ecliptic family ONLY (27.2122 N dominates,
    [26.9,27.7] u [13.5,13.9] d from production lpap) x annual comb x IIR
    at the shared dial yl=365.2463; NO dLOD backbone, NO Bessel FM (the
    ocean marquee's backbone 0.2076/Bessel stage is the wavenumber>0
    machinery and does not apply to a zonal index),
  - windings {0.42, 0.68} are the scalogram ridge teeth (cont=1.00), i.e.
    discovered by the winding instrument, not Ada-optimized,
  - each panel carries the honest-r accounting: r vs spectrum-exact
    random-phase IAAFT rung (20 clones, own local fit), and the production
    Ada fit (all-constituent, dLOD-calibrated) as prod r for context,
  - qbo50 shows the descent caveat: zero-lag coherence does not transfer
    to the 50 hPa level (honest r negative there).
"""
import sys, os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, REPO)

from lte_forward import tide_sum, impulse_delta, iir
from wavelet_scalogram import standardize

YL = 365.2463
PK = ("offs", "bg", "impA", "impB", "delA", "delB", "asym", "ma", "mp",
      "init", "shfT")
MS = [0.42, 0.68]          # ridge teeth (cont 1.00), k=0 lattice
SIGMA, NMAX = 10.0, 3


def month_grid(ts):
    return np.arange(round(ts[0] * 12) / 12,
                     round(ts[-1] * 12) / 12 + 1e-9, 1 / 12)


def draconic_manifold(p, tp):
    lpap = np.array(p["lpap"], float)
    per = lpap[:, 0]
    sel = np.logical_or(np.logical_and(per >= 26.9, per <= 27.7),
                        np.logical_and(np.abs(per) >= 13.5, np.abs(per) <= 13.9))
    B = {k: float(p[k]) for k in PK}
    tf = tide_sum(tp, lpap[sel][:, 1:3], np.abs(per[sel]), YL, 0.0, B["shfT"])
    comb = impulse_delta(tp, B["delA"], B["delB"], B["asym"], 12)
    return iir(tf * comb, lag_a=1.0 - B["ma"], lag_c=B["mp"], init=B["init"],
               start_date=tp[0], dates=tp)


def local_fit(F, tp, x, sig=SIGMA, Ms=MS, nmax=NMAX):
    w = np.exp(-0.5 * ((tp[:, None] - tp[None, :]) / sig) ** 2)
    cols = [np.ones_like(F), F]
    for M in Ms:
        th = 2 * np.pi * M
        for n in range(1, nmax + 1):
            cols += [np.sin(n * th * F), np.cos(n * th * F)]
    t = tp - tp[0]
    cols += [np.sin(2 * np.pi * t), np.cos(2 * np.pi * t), t, t ** 2]
    X = np.column_stack(cols)
    fit = np.empty(len(tp))
    for i in range(len(tp)):
        b, *_ = np.linalg.lstsq(X * w[i][:, None], x * w[i], rcond=None)
        fit[i] = X[i] @ b
    return fit


def dcc(a, b):
    return float(np.corrcoef(np.diff(a), np.diff(b))[0, 1])


def iaaft(y, seed):
    rng = np.random.default_rng(seed)
    N = len(y); nf = np.fft.rfftfreq(N, d=1 / 12)
    Am = np.abs(np.fft.rfft(y - y.mean()))
    ph = rng.uniform(0, 2 * np.pi, len(nf)); ph[0] = 0.0
    s = np.fft.irfft(Am * np.exp(1j * ph), n=N)
    for _ in range(30):
        s = np.interp(np.linspace(0, 1, N), np.sort(s), np.sort(y))
        f = np.fft.rfft(s - s.mean())
        s = np.fft.irfft(Am * np.exp(1j * np.angle(f)), n=N)
    return s


CFG = {"qbo30": ("darkorange", "30 hPa"), "qbo50": ("tab:purple", "50 hPa")}
fig, axes = plt.subplots(len(CFG), 1, figsize=(12, 2.6 * len(CFG)))
summary = {}
for k, (idx, (col, lvl)) in enumerate(CFG.items()):
    p = json.load(open(f"{REPO}/{idx}/lt.exe.p"))
    ts = np.loadtxt(f"{REPO}/{idx}/{idx}.dat")[:, 0]
    x = np.interp(month_grid(ts), ts, np.loadtxt(f"{REPO}/{idx}/{idx}.dat")[:, 1])
    x = standardize(x)
    tp = month_grid(ts)
    F = draconic_manifold(p, tp)
    y = local_fit(F, tp, x)
    r = float(np.corrcoef(x, y)[0, 1]); d = dcc(x, y)
    # honest-r rung: same design refit on 20 IAAFT clones of this index
    flat = []
    for j in range(20):
        s = standardize(iaaft(x, 2001 + j))
        flat.append(float(np.corrcoef(s, local_fit(F, tp, s))[0, 1]))
    fm, fs = float(np.mean(flat)), float(np.std(flat))
    c = np.loadtxt(f"{REPO}/{idx}/lte_results.csv", delimiter=",", skiprows=1)
    prod = standardize(np.interp(tp, c[:, 0], c[:, 1]))
    rp = float(np.corrcoef(x, prod)[0, 1])
    summary[idx] = dict(r=r, dCC=d, flat=fm, flat_std=fs, honest=r - fm,
                        z=(r - fm) / fs, prod=rp)
    ax = axes[k]
    ax.plot(tp, x, color="0.65", lw=1.0, zorder=1)
    ax.plot(tp, y, color=col, lw=1.1, alpha=0.85, zorder=2)
    ax.set_ylabel(f"{idx} ({lvl})\nr={r:.3f}  dCC={d:.3f}\nhonest r={r-fm:+.3f} "
                  f"(flat {fm:.3f}±{fs:.3f})  prod r={rp:.3f}", fontsize=8.5)
    ax.text(0.995, 0.90, f"k=0 draconic manifold  windings {MS}  n≤{NMAX}",
            transform=ax.transAxes, ha="right", fontsize=7.5, color=col)
fig.suptitle("QBO — the wavenumber=0 category  (draconic family 27.2122-d N × annual comb × IIR, "
             "yl=365.2463, no dLOD; grey=obs, colour=fit)\n"
             "2.369-yr alias predicts the period at BOTH levels; flat rung = spectrum-exact IAAFT x20, "
             "design identical to marquee local_fit",
             y=0.985, fontsize=10)
fig.tight_layout(rect=(0, 0, 1, 0.93))
out = f"{REPO}/supplemental_2026_09/figures/qbo_stack.png"
fig.savefig(out, dpi=130)
print(out)
for i, s in summary.items():
    print(f"  {i}: r={s['r']:+.3f} dCC={s['dCC']:+.3f} flat={s['flat']:.3f}"
          f"±{s['flat_std']:.3f} honest={s['honest']:+.3f} (z={s['z']:+.1f})"
          f" prod={s['prod']:+.3f}")
json.dump(summary, open(f"{REPO}/supplemental_2026_09/figures/qbo_stack_stats.json", "w"), indent=1)
