#!/usr/bin/env python3
"""Figure for the 1880-2025 spectrum-exact sharp syntheses."""
import json
import sys
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "/home/paul/eval/winding_scalogram")
ROOT = Path("/home/paul/eval/winding_scalogram")
SRC = open(ROOT / "supplemental_2026_09/supplemental2.py").read()
exec(SRC.split("CFG = {")[0])

res = json.load(open("figures/sharp2025_results.json"))
t1, x1r = np.loadtxt(ROOT / "pdo/lte_results.csv", delimiter=",",
                        usecols=(0, 2), unpack=True)
tp1 = month_grid(t1); x1 = (x1r - x1r.mean()) / x1r.std()
p = json.load(open(ROOT / "pdo/lt.exe.p"))
Ms = sorted({round(abs(m), 4) for m in p["ltep"] if 0.002 < abs(m) < 10})
F1 = manifold(p, YL, tp1)
fig, axes = plt.subplots(5, 1, figsize=(13.5, 15))
fig.suptitle("SPECTRUM-EXACT SHARP SYNTHESIS 1880-2025 vs the soft "
             "surrogate: same design, sharper target -> fit r collapses,\n"
             "ridge instrument still says NO (real pdo PASSes at 0.448, "
             "these don't)", fontweight="bold", y=0.995)

def curve(fn):
    v = np.loadtxt(fn)
    return v[:, 0], (v[:, 1] - v[:, 1].mean()) / v[:, 1].std()

rows = []
y = local_fit(F1, tp1, x1, 10.0, Ms, nmax=3, mask=np.ones(len(tp1), bool))
rows.append(("real pdo (obs) + shipped design n<=3", tp1, x1, y,
             "tab:green", np.corrcoef(x1, y)[0, 1]))
t, v = curve("sharp2025_flat_a0.dat")
F = manifold(p, YL, t)
y = local_fit(F, t, v, 10.0, Ms, nmax=3, mask=np.ones(len(t), bool))
rows.append(("flat_a0 (spectrum-exact, random phase) n<=3", t, v, y,
             "tab:blue", np.corrcoef(v, y)[0, 1]))
t, v = curve("sharp2025_sharp_a05.dat")
F = manifold(p, YL, t)
y = local_fit(F, t, v, 10.0, Ms, nmax=3, mask=np.ones(len(t), bool))
rows.append(("sharp_a05 (f^0.5 tilt = 4x sharper) n<=3", t, v, y,
             "tab:red", np.corrcoef(v, y)[0, 1]))
cs = np.loadtxt(ROOT / "pdo_iaaft_detuned_surrogate/"
                "pdo_iaaft_detuned_surrogate.dat")
t, v = cs[:, 0], (cs[:, 1] - cs[:, 1].mean()) / cs[:, 1].std()
y = local_fit(F1, tp1, np.interp(tp1, t, v), 10.0, Ms, nmax=3,
              mask=np.ones(len(tp1), bool))
rows.append(("soft IAAFT surrogate (rho1 0.995) n<=3 — reference", tp1,
             np.interp(tp1, t, v), y, "0.45",
             np.corrcoef(np.interp(tp1, t, v), y)[0, 1]))
for ax, (lab, tt, v, y, col, rr) in zip(axes[:4], rows):
    ax.plot(tt, v, color="0.55", lw=0.9)
    ax.plot(tt, y, color=col, lw=1.0)
    ax.text(0.99, 0.93, f"{lab}:  r={rr:.3f}", transform=ax.transAxes,
            ha="right", fontsize=10, color=col, fontweight="bold")
    ax.set_ylim(-3.6, 3.6); ax.set_xlim(1880, 2026)
    ax.set_ylabel("std units")
axes[3].set_xlabel("year")

# ---- bottom: ridge band spectra (0.35-0.55) real vs members
from winding_rank import winding_transform, ar1_floor, standardize as wr_std
sig, t0s, dm = 15.0, 5.0, 0.004
bg = np.arange(0.35, 0.55 + dm / 2, dm)
t2g = np.arange(round(1880 * 12), round(2026 * 12)) / 12.0
forcing2 = manifold(p, YL, t2g)
t0g2 = np.arange(t2g[0] + sig / 2, t2g[-1] - sig / 2 + 1e-9, t0s)
t0g1 = np.arange(tp1[0] + sig / 2, tp1[-1] - sig / 2 + 1e-9, t0s)
forcing1 = manifold(p, YL, tp1)
fl2 = ar1_floor(t2g, forcing2, bg, t0g2, sig, n_reps=24)
ax = axes[4]
G, _, _ = winding_transform(tp1, wr_std(x1), forcing1, bg, t0g1, sig)
fl1 = ar1_floor(tp1, forcing1, bg, t0g1, sig, n_reps=24)
ax.plot(bg, np.log2(np.maximum(np.abs(G)**2/fl1[:,None],1e-9)).mean(axis=1),
        color="tab:green", lw=1.2, label="real pdo (PASS: 2.8 bits cont 1.0)")
for fn, col, lab in (("sharp2025_flat_a0.dat", "tab:blue", "flat_a0"),
                     ("sharp2025_sharp_a05.dat", "tab:red", "sharp_a05")):
    ct = res[lab]["band"]["cont@0.4488"]
    vv = np.loadtxt(fn)
    G, _, _ = winding_transform(vv[:, 0], wr_std(vv[:, 1]), forcing2, bg,
                                t0g2, sig)
    ax.plot(bg, np.log2(np.maximum(np.abs(G)**2/fl2[:,None],1e-9)).mean(axis=1),
            color=col, lw=1.1, alpha=0.9,
            label=f"{lab} (band 0.4488: {ct:.2f} cont, "
                  f"{res[lab]['band']['band_bits@0.4488']:.1f} bits)")
ax.axvline(0.4488, color="k", ls=":", lw=0.8)
ax.axhline(1.0, color="0.5", ls="--", lw=0.8)
ax.text(0.52, 1.05, "AR1 floor (0 dB)", fontsize=8, color="0.4")
ax.set_xlabel("winding M"); ax.set_ylabel("ridge power / AR1 floor (bits)")
ax.legend(fontsize=9, loc="upper right")
ax.set_title("ridge scan of the claimed PDO band: random-phase sharp "
             "members sit ON the floor — instrument answers NO",
             fontsize=10)
fig.tight_layout(rect=[0, 0, 1, 0.965])
fig.savefig("figures/sharp2025_board.png", dpi=125, bbox_inches="tight")
print("saved figures/sharp2025_board.png")
