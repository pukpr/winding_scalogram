#!/usr/bin/env python3
"""Figure for the sharpness ladder + v2 battery."""
import json
import sys
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "/home/paul/eval/winding_scalogram")
import sharp_surrogates as SS
res = json.load(open("figures/sharp_battery_v2.json"))
SS.fams0 = {"flat": np.loadtxt("sharp_flat_alpha0.dat")[:, 1],
            "a1": np.loadtxt("sharp_sharp_a1.dat")[:, 1],
            "a2": np.loadtxt("sharp_sharp_a2.dat")[:, 1]}
IDX = ["pdo", "amo", "baltic", "nino4", "iode"]
FAMS = ["flat", "a1", "a2", "ar1"]
fig, axes = plt.subplots(4, 2, figsize=(14, 12.5),
                         gridspec_kw={"height_ratios": [1, 1, 1, 1.5]})
for ax, (name, ylab) in zip(axes[:3, 0], [("flat", "phase-randomized,\nspectrum EXACT"),
                                       ("a1", "f^1 tilt\n(rho1 0.69)"),
                                       ("a2", "f^2 tilt\n(rho1 0.37)")]):
    v = SS.fams0[name]
    ax.plot(SS.t, SS.x, color="0.55", lw=0.8, label="real pdo")
    ax.plot(SS.t, v, lw=0.7, label="ladder member (seed 1)")
    ax.set_ylim(-3.4, 3.4)
    ax.text(0.01, 0.93, ylab, transform=ax.transAxes, fontsize=9)
    ax.legend(fontsize=8, loc="lower right")
    ax.set_xlim(1880, 2022)
ax = axes[0, 1]
lab = ["real\npdo","flat","a1","a2","ar1"]
cv = [float(np.var(np.diff(SS.x,2))/np.var(SS.x)),
      float(np.var(np.diff(SS.fams0["flat"],2))/np.var(SS.fams0["flat"])),
      float(np.var(np.diff(SS.fams0["a1"],2))/np.var(SS.fams0["a1"])),
      float(np.var(np.diff(SS.fams0["a2"],2))/np.var(SS.fams0["a2"])),
      float(np.var(np.diff(SS.ar1(0.9668,200),2))/np.var(SS.ar1(0.9668,200)))]
ax.bar(lab, cv, color=["0.55","tab:blue","tab:red","tab:green","tab:orange"])
ax.set_yscale("log"); ax.set_ylabel("curvature var(d2x)/var(x)")
ax.set_title("the SHARPNESS knob itself: curvature per rung\n"
             "(flat = real's 0.039; a1 x19; a2 x58)", fontsize=9.5)
ax = axes[1, 1]
def acf(v, k=36):
    v = v - v.mean()
    c0 = np.dot(v, v)
    return [np.dot(v[:-k2], v[k2:]) / c0 for k2 in range(1, k + 1)]
lags = np.arange(1, 37)
ax.plot(lags, acf(SS.x), "o-", ms=3, color="0.55", label="real pdo")
for name, col in (("flat", "tab:blue"), ("a1", "tab:red"),
                  ("a2", "tab:green")):
    ax.plot(lags, acf(SS.fams0[name]), lw=1.0, color=col, alpha=0.85,
            label=name)
ax.axhline(0, color="k", lw=0.6)
ax.legend(fontsize=8)
ax.set_xlabel("lag (months)"); ax.set_ylabel("ACF")
ax.set_title("autocorrelation: flat tracks real (same spectrum);\n"
             "a1/a2 decay in ~1-2 months = no low-freq gift",
             fontsize=9.5)
ax = axes[2, 1]
ax.plot(SS.t, SS.ar1(0.9668, 200), lw=0.7, color="tab:orange",
        label="AR(1) rho=real rho1")
ax.plot(SS.t, SS.x, color="0.55", lw=0.8, label="real pdo")
ax.set_ylim(-3.4, 3.4); ax.legend(fontsize=8)
ax.set_title("AR1 member: same rho1, LESS sharp than real\n"
             "(its extra 1-5yr power is why it out-fits the captures)",
             fontsize=9.5)
ax = axes[3, 0]
def spec(v):
    V = np.abs(np.fft.rfft(v - v.mean()))
    f = np.fft.rfftfreq(len(v), 1 / 12)
    m = f > 0.02
    return f[m], V[m] / V[m].sum()
f0, s0 = spec(SS.x)
ax.loglog(f0, s0, color="0.5", lw=1.2, label="real pdo")
for name, col in (("flat", "tab:blue"), ("a1", "tab:red"),
                  ("a2", "tab:green")):
    f1, s1 = spec(SS.fams0[name])
    ax.loglog(f1, s1, color=col, lw=1.0, alpha=0.85, label=name)
ax.set_xlabel("frequency (cyc/yr)"); ax.legend(fontsize=8)
ax.set_title("spectra: flat=exact; a1/a2 drain the >0.5 cyc/yr band\n"
             "where CC inflation lives", fontsize=9.5)
ax = axes[3, 1]
w = 0.2
for j, fam in enumerate(FAMS):
    zs = [res[i][fam]["z"] for i in IDX]
    ax.bar(np.arange(len(IDX)) + (j - 1.5) * w, zs, w * 0.9,
           label=fam + (" (spectrum-matched)" if fam == "flat" else ""))
ax.axhline(2, color="k", ls="--", lw=0.8)
ax.axhline(0, color="k", lw=0.8)
ax.set_xticks(np.arange(len(IDX)))
ax.set_xticklabels(IDX)
ax.set_yscale("symlog", linthresh=3)
ax.set_ylabel("z of real r over family floor (n<=3)")
ax.legend(fontsize=8)
ax.set_title("battery: sharp nulls crushed (z>8); flat spectrum-matched\n"
             "null sits at z~0 for pdo/amo/baltic (r is NOT locking)",
             fontsize=9.5)
fig.suptitle("SHARPNESS LADDER — synthetic targets with inflated "
             "smoothness removed (recipe: sharp_surrogates.py)",
             fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.97])
fig.savefig("figures/sharp_ladder.png", dpi=125, bbox_inches="tight")
print("saved figures/sharp_ladder.png")
