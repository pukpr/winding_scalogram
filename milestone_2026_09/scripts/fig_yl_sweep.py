#!/usr/bin/env python3
"""Year-length sweep charts: AMO obs vs winding fit for yl in
{365.2422 ... 365.259}. Production chain (tide_sum -> monthly comb ->
IIR -> Bessel FM, fitted lpap constants) re-evaluated at each yl;
fit = level + k0*F + [sin,cos](2pi*0.0134*F) + [sin,cos](2pi*0.2075*F)
+ annual/semiannual + trend + accel (production basis, lstsq).
Each panel: obs (grey), fit (red), residual excursions; second axis:
dF/dt showing the ~117-150yr alias envelope the comb drifts across.
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
p = json.load(open(ROOT + "/amo/lt.exe.p"))
lpap = np.array(p["lpap"], float)
per = np.abs(lpap[:, 0])
B = {k: float(p[k]) for k in ("offs", "bg", "impA", "impB", "delA",
                              "delB", "asym", "ma", "mp", "init", "shfT")}
prov = np.loadtxt(ROOT + "/amo/lte_results.csv", delimiter=",")
tp, col4, obs = prov[:, 0], prov[:, 3], prov[:, 2]
k1 = p["ltep"][1]
x = (obs - obs.mean()) / obs.std()

YLES = [365.2422, 365.2463, 365.2500, 365.2590]
LBL = ["365.2422 (tropical)", "365.2463 (PRODUCTION)",
       "365.2500", "365.2590"]


def manifold(yl):
    tf = tide_sum(tp, lpap[:, 1:3], per, yl, 0.0, B["shfT"])
    comb = impulse_delta(tp, B["delA"], B["delB"], B["asym"], 12)
    R = iir(tf * comb, lag_a=1.0 - B["ma"], lag_c=B["mp"], init=B["init"],
            start_date=1880.0, dates=tp)
    return bessel(R, B["impA"], B["impB"], k1, B["offs"], B["bg"])


def fit_amo(F):
    cols = [np.ones_like(F), F,
            np.sin(2*np.pi*0.0134*F), np.cos(2*np.pi*0.0134*F),
            np.sin(2*np.pi*0.2075*F), np.cos(2*np.pi*0.2075*F),
            np.sin(2*np.pi*tp), np.cos(2*np.pi*tp),
            np.sin(4*np.pi*tp), np.cos(4*np.pi*tp),
            tp, (tp - tp[0])**2]
    A = np.column_stack(cols)
    beta, *_ = np.linalg.lstsq(A, x, rcond=None)
    y = A @ beta
    return y, float(np.corrcoef(y, x)[0, 1])


fig, axes = plt.subplots(len(YLES), 2, figsize=(13, 2.35 * len(YLES)),
                         sharex=True,
                         gridspec_kw=dict(width_ratios=[3.2, 1]))
fig.suptitle("AMO fit on winding manifold vs assumed year length "
             "(comb alias of the 9.133-d Mt line)", fontsize=12)
for i, (yl, lab) in enumerate(zip(YLES, LBL)):
    F = manifold(yl)
    y, cc = fit_amo(F)
    cpy = yl / 9.1330                      # Mt cycles per year (~39.99)
    alias = 1.0 / abs(round(cpy) - cpy)    # annual-sampling beat period
    print(f"yl={yl}: r={cc:+.4f}  Mt cpy={yl/9.1330:.4f} alias={alias:.0f}yr")
    ax = axes[i, 0]
    ax.plot(tp, x, color="0.55", lw=0.9, label="AMO obs")
    ax.plot(tp, y, color="crimson", lw=1.1,
            label=f"winding fit r={cc:+.3f}")
    ax.set_title(f"{lab}   ({alias:.0f}-yr comb alias)   r={cc:+.3f}",
                 fontsize=9, loc="left")
    ax.axhline(0, color="k", lw=0.4)
    ax.set_xlim(1880, 2023)
    ax.legend(fontsize=7, loc="upper left")
    ax2 = axes[i, 1]
    dF = np.gradient(F, tp)
    ax2.plot(tp, dF, color="darkgreen", lw=0.7)
    ax2.set_title("dF/dt (alias envelope)", fontsize=8)
    ax2.axhline(0, color="k", lw=0.4)
axes[-1, 0].set_xlabel("year")
fig.tight_layout(rect=(0, 0, 1, 0.96))
f = OUT + "fig_yl_sweep.png"
fig.savefig(f, dpi=110)
print(f)
