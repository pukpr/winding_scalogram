#!/usr/bin/env python3
"""JOINT v5 — LOCAL-WINDOW winding fit (what the scalogram actually
measures), on ONE year-length dial with per-index slightly-jiggled
tidal factors. fit(t) = local MLR on the winding basis within a
Gaussian window sigma=15yr; interior centered, edges one-sided.
Metrics: r (macro), dCC (micro/short excursions). Charts per PI mandate.
"""
import os as _os
_R = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
import json
import math
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, _R)
from lte_forward import (tide_sum, impulse_delta, iir, bessel,
                         YEAR_IN_DAYS)

ROOT = _R
OUT = _R + "/milestone_2026_09/figures/"
prov = np.loadtxt(ROOT + "/amo/lte_results.csv", delimiter=",")
pp = np.loadtxt(ROOT + "/pdo/lte_results.csv", delimiter=",")
tp = np.arange(max(prov[0, 0], pp[0, 0]),
               min(prov[-1, 0], pp[-1, 0]) + 1 / 24, 1 / 12)


def zz(v, src):
    v = (v - v.mean()) / v.std()
    return np.interp(tp, src[:, 0], v)


OBS = {"amo": zz(prov[:, 2], prov), "pdo": zz(pp[:, 2], pp)}
PROD = {"amo": zz(prov[:, 1], prov), "pdo": zz(pp[:, 1], pp)}
PK = ("offs", "bg", "impA", "impB", "delA", "delB", "asym", "ma", "mp",
      "init", "shfT")
WIND = {"amo": [0.0134, 0.2075], "pdo": [0.5934, 0.4489, 0.2073]}


def manifold(idx, yl=365.2463):
    p = json.load(open(f"{ROOT}/{idx}/lt.exe.p"))
    lpap = np.array(p["lpap"], float)
    per = np.abs(lpap[:, 0])
    B = {k: float(p[k]) for k in PK}
    tf = tide_sum(tp, lpap[:, 1:3], per, yl, 0.0, B["shfT"])
    comb = impulse_delta(tp, B["delA"], B["delB"], B["asym"], 12)
    R = iir(tf * comb, lag_a=1.0 - B["ma"], lag_c=B["mp"], init=B["init"],
            start_date=1880.0, dates=tp)
    return bessel(R, B["impA"], B["impB"], p["ltep"][-1], B["offs"],
                  B["bg"])


def basis(F, Ms):
    cols = [np.ones_like(F), F]        # k0*F carries comb micro-steps
    for M in Ms:
        cols += [np.sin(2*np.pi*M*F), np.cos(2*np.pi*M*F)]
    cols += [np.sin(2*np.pi*tp), np.cos(2*np.pi*tp),
             np.sin(4*np.pi*tp), np.cos(4*np.pi*tp),
             tp - tp.mean(), (tp - tp[0])**2 * 1e-4]
    return np.column_stack(cols)


def local_fit(B, x, sigma=15.0):
    y = np.empty_like(x)
    n = len(tp)
    half = int(2.5 * sigma * 12)
    for i in range(n):
        lo, hi = max(0, i - half), min(n, i + half)
        if i < half:                      # one-sided at start
            lo, hi = 0, 2 * half
        elif i > n - half - 1:            # one-sided at end
            lo, hi = n - 2 * half, n
        w = np.exp(-0.5 * ((tp[lo:hi] - tp[i]) / sigma) ** 2)
        A = B[lo:hi] * w[:, None]
        beta, *_ = np.linalg.lstsq(A, x[lo:hi] * w, rcond=None)
        y[i] = B[i] @ beta
    return y


print("local-window winding fit — ONE dial yl=365.2463, per-index "
      "jiggled tidal factors")
fits = {}
for idx in ("amo", "pdo"):
    F = manifold(idx)
    B = basis(F, WIND[idx])
    y = local_fit(B, OBS[idx])
    r = float(np.corrcoef(y, OBS[idx])[0, 1])
    d = float(np.corrcoef(np.diff(y), np.diff(OBS[idx]))[0, 1])
    fits[idx] = y
    pr = float(np.corrcoef(PROD[idx], OBS[idx])[0, 1])
    pd = float(np.corrcoef(np.diff(PROD[idx]),
                           np.diff(OBS[idx]))[0, 1])
    print(f"  {idx}: r={r:+.3f} dCC={d:+.3f}   (production col2: "
          f"r={pr:+.3f} dCC={pd:+.3f})")

fig, axes = plt.subplots(6, 1, figsize=(12.5, 12.5), sharex=True)
axes[0].plot(tp, OBS["amo"], color="0.5", lw=1.0)
axes[0].set_ylabel("AMO observed", fontsize=9)
axes[1].plot(tp, fits["amo"], color="tab:blue", lw=1.0)
axes[1].set_ylabel("AMO joint fit\n(local winding)", fontsize=8)
axes[2].plot(tp, PROD["amo"], color="navy", lw=0.9, alpha=0.85)
axes[2].set_ylabel("AMO production\ncol2", fontsize=8)
axes[3].plot(tp, OBS["pdo"], color="0.5", lw=1.0)
axes[3].set_ylabel("PDO observed", fontsize=9)
axes[4].plot(tp, fits["pdo"], color="tab:green", lw=1.0)
axes[4].set_ylabel("PDO joint fit\n(local winding)", fontsize=8)
axes[5].plot(tp, PROD["pdo"], color="darkgreen", lw=0.9, alpha=0.85)
axes[5].set_ylabel("PDO production\ncol2", fontsize=8)
for a in axes:
    a.axhline(0, color="k", lw=0.4)
axes[-1].set_xlim(1880, 2022)
axes[-1].set_xlabel("year")
fig.suptitle("Simultaneous AMO+PDO from ONE year-length dial (365.2463) "
             "+ per-index tidal factors — local-window winding fit "
             "(rows 2,5) vs production (rows 3,6)", fontsize=10)
fig.tight_layout(rect=(0, 0, 1, 0.96))
f = OUT + "fig_joint_local.png"
fig.savefig(f, dpi=110)
print("wrote", f)
