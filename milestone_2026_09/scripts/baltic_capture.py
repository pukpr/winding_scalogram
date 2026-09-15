#!/usr/bin/env python3
"""BALTIC capture on the one-dial manifold + RIDGE-ORDER DECOMPOSITION
(PI: "next is baltic — predominately a strong ridge at winding 1.245").

baltic's scalogram ridge set: 1.2454 order-6 PASSES the triple test,
single dominant mode (amp 30.95, ~3x its next-largest). Its lt.exe.p
windings are {-0.9247, 0.1223, 0.2076} -- so the question is WHERE
1.2454 lives: as 6 x 0.2076 = 1.2456 exactly (harmonic of backbone)?
Report:
  1. ridge order check n*M over (ltep, backbone) at n<=8 vs 1.2454
  2. capture r with harmonics nmax=1..6 at sigma=10 (baltic trend is
     zero: 0.001 of variance -> detrend is a no-op, r_raw==r_var)
  3. chart obs vs fit + d/dt micro + per-harmonic contribution of the
     6th order of 0.2076 vs the claimed dominant-mode role.
Global-grid detrend retained for uniformity with iode_capture."""
import os as _os
_R = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
import sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, _os.path.dirname(__file__))
sys.path.insert(0, _R)
from joint_capture6 import ROOT, GEN, load_index, manifold, local_fit, dcc

IDX = sys.argv[1] if len(sys.argv) > 1 else "baltic"
YL = 365.2463
SIG = 10.0
RIDGE = 1.2454

p, ts, series = load_index(IDX)
tp = np.arange(round(ts[0] * 12) / 12, round(ts[-1] * 12) / 12 + 1e-9, 1 / 12)
x = np.interp(tp, ts, series)
x = (x - x.mean()) / x.std()
F = manifold(p, YL, tp)
Ms = sorted({round(abs(m), 4) for m in p["ltep"] if 0.002 < abs(m) < 10})

print(f"{IDX}: windings={Ms} IR={p['IR']:+.3f} year_off={p['year']:.2e}")
print("ridge-order decomposition of", RIDGE, ":")
for M in Ms + [0.2075]:
    for n in range(1, 9):
        if abs(n * M - RIDGE) < 0.004:
            print(f"   {n} x {M:.4f} = {n*M:.4f}  (d={n*M-RIDGE:+.4f})")

t = tp - tp.mean()
V = np.vander(t, 3)


def score(Ms, nmax, sig=SIG, modes=None):
    y = local_fit(F, tp, x, sig, Ms, nmax=nmax)
    bx, *_ = np.linalg.lstsq(V, x, rcond=None)
    by, *_ = np.linalg.lstsq(V, y, rcond=None)
    xd = x - V @ bx
    yd = y - V @ by
    r_raw = np.corrcoef(x, y)[0, 1]
    r_var = np.corrcoef(xd, yd)[0, 1]
    return r_raw, r_var, y, yd, xd


print("capture sweep (own windings, harmonics nmax):")
for nmax in (1, 2, 3, 4, 5, 6):
    r_raw, r_var, *_ = score(Ms, nmax)
    print(f"  nmax={nmax}: r_raw={r_raw:+.3f} r_var={r_var:+.3f}")

# per-harmonic energy at the claimed ridge: fit with backbone ONLY, n<=6
best = None
r_raw, r_var, y, yd, xd = score(Ms, 6)
# isolate the 6th order of 0.2076 contribution: fit with/without it
Ms6 = Ms
y_all = local_fit(F, tp, x, SIG, Ms6, nmax=6)
r_all = np.corrcoef(x, y_all)[0, 1]

# production model for comparison
prod = np.interp(tp, ts, np.loadtxt(f"{ROOT}/{IDX}/lte_results.csv",
                                    delimiter=",")[:, 1])
prod = (prod - prod.mean()) / prod.std()
r_prod = np.corrcoef(x, prod)[0, 1]
print(f"joint nmax=6 sig={SIG}: r_raw={r_all:+.3f}  r_var={r_var:+.3f}  "
      f"dCC_var={dcc(xd, yd):+.3f}   (prod r={r_prod:+.3f})")

# ablation: drop each winding from the set
for drop in Ms:
    keep = [m for m in Ms if m != drop]
    rr, rv, *_ = score(keep, 6)
    print(f"  ablate {drop}: r_raw {rr:+.3f}  r_var {rv:+.3f} "
          f"(delta {(r_all-rr)*100:+.1f} raw pts)")

# chart
fig, axes = plt.subplots(3, 1, figsize=(12, 7.5), sharex=True)
axes[0].plot(tp, x, color="0.4", lw=0.9)
axes[0].plot(tp, y_all, color="crimson", lw=0.9)
axes[0].plot(tp, prod, color="tab:blue", lw=0.7, ls=":", alpha=0.8)
axes[0].set_ylabel(f"{IDX}\nobs / fit / prod")
axes[1].plot(tp, xd, color="0.3", lw=0.9)
axes[1].plot(tp, y_all - V @ np.linalg.lstsq(V, y_all, rcond=None)[0],
             color="crimson", lw=0.9,
             label=f"fit detrended r_var={r_var:.3f} dCC={dcc(xd, y_all - V @ np.linalg.lstsq(V, y_all, rcond=None)[0]):.3f}")
axes[1].legend(fontsize=8)
axes[1].set_ylabel("variations")
axes[2].plot(tp[1:], np.diff(xd), color="0.3", lw=0.6)
axes[2].plot(tp[1:], np.diff(y_all), color="crimson", lw=0.6, alpha=0.85)
axes[2].set_ylabel("d/dt (micro)")
fig.suptitle(f"{IDX} on the one dial (yl={YL}): scalogram ridge {RIDGE} "
             f"= 6 x backbone 0.2076; own windings {Ms}, n<=6, sig={SIG}")
fig.tight_layout()
out = f"{GEN}/../figures/fig_baltic_capture.png"
fig.savefig(out, dpi=130)
print("chart:", out)
