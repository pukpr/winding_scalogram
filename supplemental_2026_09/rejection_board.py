#!/usr/bin/env python3
"""REJECTED EXHIBIT, FULL BOARD: pdo_iaaft_detuned_surrogate 3 ways:
(A) model overlaid on the synthetic data (it FITS beautifully),
(B) winding-ridge spectra vs real PDO and 8 AR1-noise reps,
(C) its manifold overlaid on amo's (they overlay too!).
"""
import json
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import sys
sys.path.insert(0, "/home/paul/eval/winding_scalogram")
from winding_rank import read_results_csv, winding_transform, ar1_floor
from wavelet_scalogram import standardize

SRC = open("/home/paul/eval/winding_scalogram/supplemental_2026_09/"
           "supplemental2.py").read().split("CFG = {")[0]
exec(SRC)
IDX = "pdo_iaaft_detuned_surrogate"
ROOT = Path("/home/paul/eval/winding_scalogram")
p_s = json.load(open(f"{IDX}/lt.exe.p"))
c = np.loadtxt(f"{IDX}/lte_results.csv", delimiter=",")
tp = month_grid(c[:, 0]); xs = np.interp(tp, c[:, 0], c[:, 2])
xs = (xs - xs.mean()) / xs.std()
mask = np.ones(len(tp), bool)
Ms_s = sorted({round(abs(m), 4) for m in p_s["ltep"]
               if 0.002 < abs(m) < 10})
Ms_p = [0.2073, 0.4488, 0.5934]
F_s = manifold(p_s, YL, tp)
p_pdo = json.load(open("pdo/lt.exe.p"))
F_pdo = manifold(p_pdo, YL, tp)
F_amo = manifold(json.load(open("amo/lt.exe.p")), YL, tp)
fig = plt.figure(figsize=(13.5, 14.5))
gs = fig.add_gridspec(5, 2, height_ratios=[1.05, 1.05, 1.05, 1.25, 1.05],
                      hspace=0.55, wspace=0.18)

# ---- A1: surrogate + its own baltic-triple fit (0.866)
y = local_fit(F_s, tp, xs, 10.0, Ms_s, nmax=6, mask=mask)
ax = fig.add_subplot(gs[0, :])
ax.plot(tp, xs, color="0.55", lw=0.9)
ax.plot(tp, y, color="tab:red", lw=1.1,
        label=f"surrogate manifold + windings {Ms_s} n<=6 (its own prod)")
ax.text(0.99, 0.94, f"r={np.corrcoef(xs, y)[0, 1]:.3f}  <-- rejected",
        transform=ax.transAxes, ha="right", color="tab:red",
        fontweight="bold", fontsize=11)
ax.set_ylabel("detrended std units")
ax.legend(loc="lower left", fontsize=9)
ax.set_title("(A) REJECTED BUT FITS: model overlaid on (synthetic) data")
# ---- A2: surrogate + PDO manifold & windings (0.904)
y2 = local_fit(F_pdo, tp, xs, 10.0, Ms_p, nmax=3, mask=mask)
ax = fig.add_subplot(gs[1, :])
ax.plot(tp, xs, color="0.55", lw=0.9)
ax.plot(tp, y2, color="tab:red", lw=1.1,
        label="PDO manifold + PDO windings n<=3 (the REAL PDO design)")
ax.text(0.99, 0.94, f"r={np.corrcoef(xs, y2)[0, 1]:.3f} vs real-PDO 0.814",
        transform=ax.transAxes, ha="right", color="tab:red",
        fontweight="bold", fontsize=11)
ax.set_ylabel("detrended std units"); ax.legend(loc="lower left", fontsize=9)
# ---- A3: real pdo same design for the eye
cr = np.loadtxt("pdo/lte_results.csv", delimiter=",")
tr = month_grid(cr[:, 0]); xr = np.interp(tr, cr[:, 0], cr[:, 2])
xr = (xr - xr.mean()) / xr.std()
yr = local_fit(F_pdo, tr, xr, 10.0, Ms_p, nmax=3, mask=np.ones(len(tr), bool))
ax = fig.add_subplot(gs[2, :])
ax.plot(tr, xr, color="0.55", lw=0.9)
ax.plot(tr, yr, color="tab:green", lw=1.1, label="same design on REAL pdo")
ax.text(0.99, 0.94, f"r={np.corrcoef(xr, yr)[0, 1]:.3f}  <-- real target "
        "fits WORSE than the surrogate", transform=ax.transAxes, ha="right",
        color="tab:green", fontweight="bold", fontsize=11)
ax.set_ylabel("detrended std units"); ax.legend(loc="lower left", fontsize=9)
ax.set_xlabel("year")

# ---- B: ridge spectra vs real + AR1 floor
dm = 0.004; m_max = 1.5
m_grid = np.arange(0.0, m_max + dm / 2, dm)
sig, t0s = 15.0, 5.0
def spectrum(t, x, forcing):
    t0_grid = np.arange(t[0] + sig / 2, t[-1] - sig / 2 + 1e-9, t0s)
    G, _, _ = winding_transform(t, standardize(x), forcing, m_grid,
                                t0_grid, sig)
    return np.abs(G).mean(axis=1)
t_r, x_r, f_r = read_results_csv(ROOT / "pdo" / "lte_results.csv")
t_s, x_s, f_s2 = read_results_csv(ROOT / IDX / "lte_results.csv")
spec_s = spectrum(t_s, x_s, f_s2)
spec_r = spectrum(t_r, x_r, f_r)
rng = np.random.default_rng(3)
floor = ar1_floor(t_s, f_s2, m_grid,
                  np.arange(t_s[0] + sig / 2, t_s[-1] - sig / 2 + 1e-9,
                            t0s), sig, n_reps=24, rho=0.9946)
# ---- B LEFT: ridge-candidate comparison (from the committed rank JSONs)
rp = json.load(open("/home/paul/eval/winding_scalogram/supplemental_2026_09/figures/pdo_rank.json"))["ridges"]
rs = json.load(open("/home/paul/eval/winding_scalogram/supplemental_2026_09/figures/surr_rank.json"))["ridges"]
ax = fig.add_subplot(gs[3, 0])
ys = np.arange(len(rp) + len(rs) + 2)
k = 0
for r in rp:
    ax.barh(k, r["peak_bits"], color="tab:green",
            alpha=1.0 if r["pass"] else 0.45, height=0.7)
    ax.text(0.05, k, f'M={r["M"]}  cont={r["continuity"]}'
            + ("  PASS" if r["pass"] else ""), va="center", fontsize=7.5,
            color="k" if r["pass"] else "0.3")
    k += 1
k += 1
ax.axhline(len(rp) + 0.5, color="0.7", lw=0.8)
for r in rs:
    ax.barh(k, r["peak_bits"], color="tab:red",
            alpha=1.0 if r["pass"] else 0.45, height=0.7)
    ax.text(0.05, k, f'M={r["M"]}  cont={r["continuity"]}'
            + ("  PASS" if r["pass"] else ""), va="center", fontsize=7.5,
            color="k" if r["pass"] else "0.3")
    k += 1
ax.set_yticks([]); ax.invert_yaxis(); ax.set_xlabel("ridge peak over AR1 floor (bits)")
ax.set_title("(B) all ridge candidates [0,1.5], each vs ITS OWN AR1 floor\n"
             "real: PASS only at claimed 0.448  |  surrogate: PASS only at\n"
             "0.952 (the baltic tooth it was detuned to imitate);\n"
             "claimed PDO band [0.35,0.55]: band-max SNR 0.27 bits = nothing",
             fontsize=9.5, loc="left")
# ---- B RIGHT: raw mean-|G| spectra (no floor, ratio-free comparison)
ax = fig.add_subplot(gs[3, 1])
ax.plot(m_grid, spec_r, color="tab:green", lw=1.0, label="real PDO")
ax.plot(m_grid, spec_s, color="tab:red", lw=1.0, label="surrogate")
ax.axvspan(0.35, 0.55, color="tab:purple", alpha=0.12)
ax.text(0.45, ax.get_ylim()[1]*0.55, "claimed\nPDO band", fontsize=7.5, ha="center",
        color="tab:purple")
ax.set_xscale("log"); ax.set_xlim(0.02, 1.5); ax.set_yscale("log")
ax.set_xlabel("winding M"); ax.legend(fontsize=8)
ax.set_title("(B\') raw ridge power vs M (note the purple band:\n"
             "real PDO has a local peak, surrogate monotone there)",
             fontsize=9.5)

# ---- C: surrogate manifold vs amo manifold
ax = fig.add_subplot(gs[4, 0])
ax.plot(tp, F_s, color="tab:red", lw=0.9, alpha=0.9, label="surrogate F")
ax.plot(tp, F_amo, color="0.1", lw=0.9, label="amo F (common manifold)")
ax.set_title("(C) manifolds: surrogate (baltic detuned consts) vs amo",
             fontsize=10)
ax.legend(fontsize=8); ax.set_xlabel("year")
ax = fig.add_subplot(gs[4, 1])
d = F_s - F_amo
ax.plot(tp, d, lw=0.8, color="tab:red")
ax.set_title(f"(C') deviation: rms {np.sqrt((d**2).mean()):.1f} windings, "
             f"end drift {d[-1]:+.1f}\n"
             f"r(F_s, F_amo) = {np.corrcoef(F_s, F_amo)[0, 1]:.3f}",
             fontsize=10)
ax.set_xlabel("year"); ax.set_ylabel("windings")
fig.suptitle("REJECTION EXHIBITS — pdo_iaaft_detuned_surrogate: "
             "fits great (A), no locking ridges (B), same manifold (C)",
             fontweight="bold", y=0.998)
out = ("/home/paul/eval/winding_scalogram/supplemental_2026_09/"
       "figures/rejection_board.png")
fig.savefig(out, dpi=125, bbox_inches="tight")
print("saved", out)
print(f"A: own n<=6 r={np.corrcoef(xs, y)[0,1]:.3f}   "
      f"pdo-design n<=3 r={np.corrcoef(xs, y2)[0,1]:.3f}   "
      f"real pdo same r={np.corrcoef(xr, yr)[0,1]:.3f}")
print(f"C: rms dev vs amo manifold {np.sqrt((d**2).mean()):.1f} windings, "
      f"r={np.corrcoef(F_s, F_amo)[0,1]:.3f}")
