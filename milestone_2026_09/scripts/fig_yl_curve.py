#!/usr/bin/env python3
"""r(yl) sharpness: production chain -> winding fit of AMO as the assumed
year length slides continuously from tropical 365.2422 to 365.2590.
Marks the physically-meaningful years and the comb-alias mapping."""
import os as _os
_R = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, _R)
from lte_forward import (tide_sum, impulse_delta, iir, bessel,
                         YEAR_IN_DAYS)

ROOT = _R
p = json.load(open(ROOT + "/amo/lt.exe.p"))
lpap = np.array(p["lpap"], float)
per = np.abs(lpap[:, 0])
B = {k: float(p[k]) for k in ("offs", "bg", "impA", "impB", "delA",
                              "delB", "asym", "ma", "mp", "init", "shfT")}
prov = np.loadtxt(ROOT + "/amo/lte_results.csv", delimiter=",")
tp, obs = prov[:, 0], prov[:, 2]
k1 = p["ltep"][1]
x = (obs - obs.mean()) / obs.std()

comb = impulse_delta(tp, B["delA"], B["delB"], B["asym"], 12)


def r_of(yl):
    tf = tide_sum(tp, lpap[:, 1:3], per, yl, 0.0, B["shfT"])
    R = iir(tf * comb, lag_a=1.0 - B["ma"], lag_c=B["mp"], init=B["init"],
            start_date=1880.0, dates=tp)
    F = bessel(R, B["impA"], B["impB"], k1, B["offs"], B["bg"])
    A = np.column_stack([np.ones_like(F), F,
                         np.sin(2*np.pi*0.0134*F), np.cos(2*np.pi*0.0134*F),
                         np.sin(2*np.pi*0.2075*F), np.cos(2*np.pi*0.2075*F),
                         np.sin(2*np.pi*tp), np.cos(2*np.pi*tp),
                         np.sin(4*np.pi*tp), np.cos(4*np.pi*tp),
                         tp, (tp - tp[0])**2])
    beta, *_ = np.linalg.lstsq(A, x, rcond=None)
    return float(np.corrcoef(A @ beta, x)[0, 1])


yls = np.arange(365.2400, 365.2601, 0.0001)
rs = np.array([r_of(y) for y in yls])
aliases = 1.0 / np.abs(40 - yls / 9.1330)

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(yls - 365.24, rs, color="crimson", lw=0.9, marker=".", ms=2.5)
ax.set_ylim(0.25, 0.75)
ax.set_yticks(np.arange(0.3, 0.76, 0.1))
ax.axvline(365.2463 - 365.24, color="k", ls=":", lw=1.2)
ax.annotate("PRODUCTION 365.2463\nr=0.704 = global max of sweep",
            xy=(0.0063, 0.704), xytext=(0.0105, 0.66), fontsize=9,
            arrowprops=dict(arrowstyle="->", lw=0.8))
for yl, lab in [(365.2422, "tropical"), (365.2425, "Gregorian"),
                (365.25, "Julian"), (365.2564, "sidereal")]:
    ax.axvline(yl - 365.24, color="0.6", lw=0.8)
    ax.text(yl - 365.24, 0.26, lab, rotation=90, fontsize=7, va="bottom",
            ha="right")
ax.set_xlabel("assumed length of year minus 365.24 (days)")
ax.set_ylabel("AMO fit r (winding basis)")
ax2 = ax.secondary_xaxis("top")
ax2.set_xticks([y - 365.24 for y in [365.2422, 365.2463, 365.25, 365.259]])
ax2.set_xticklabels(["117 yr", "124 yr", "130 yr", "150 yr"])
ax2.set_xlabel("Mt annual-sampling comb alias period")
ax.set_title("AMO fit vs assumed year length — all else = production "
             "constants (r sweeps 0.31-0.70; peak at production yl)")
ax.grid(alpha=0.3)
f = _R + "/milestone_2026_09/figures/fig_yl_curve.png"
fig.tight_layout()
fig.savefig(f, dpi=110)
print(f)
print("max r over sweep:", rs.max(), "at yl", yls[rs.argmax()])
