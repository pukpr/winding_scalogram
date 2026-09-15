#!/usr/bin/env python3
"""IODE capture with TREND DISCRIMINATION (PI: upward trend inflates r;
separate linear/accelerating trend from the variations).

Three reports:
  r_raw    obs vs fit WITH trend block (the inflated number, for reference)
  r_var    detrended obs vs detrended fit  (the honest winding capture)
  dCC_var  micro-lines on the detrended series
  trend_r  corr(obs, quadratic trend alone)  -> nuisance factor size
Detrending: quadratic (lin+accel) on the common grid; sensitivity with
cubic. Chart: obs raw | trend-only | detrended obs vs detrended fit.
Model = shared-dial manifold (own windings/IR/constants), local window,
basis WITHOUT calendar annual/semiannual (trend handled explicitly)."""
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

IDX = sys.argv[1] if len(sys.argv) > 1 else "iode"
YL = 365.2463
SIG = 10.0   # optimized (PI trend-discrimination pass): sigma 15->10

p, ts, series = load_index(IDX)
tp = np.arange(round(ts[0] * 12) / 12, round(ts[-1] * 12) / 12, 1 / 12)
x = np.interp(tp, ts, series)
F = manifold(p, YL, tp)
Ms = sorted({round(abs(m), 4) for m in p["ltep"] if 0.002 < abs(m) < 10})


def detrend(v, deg):
    t = tp - tp.mean()
    V = np.vander(t, deg + 1)
    b, *_ = np.linalg.lstsq(V, v, rcond=None)
    return v - V @ b, V @ b


def run(deg, cal=True):
    # fit WITH trend basis as-is (local quadratic inside the window)
    y_full = local_fit(F, tp, x, SIG, Ms, IR=0.0, mode="plain")
    r_raw = np.corrcoef(x, y_full)[0, 1]
    xd, tr = detrend(x, deg)
    yd, _ = detrend(y_full, deg)
    r_var = np.corrcoef(xd, yd)[0, 1]
    d_var = dcc(xd, yd)
    r_trend = np.corrcoef(x, tr)[0, 1]
    # variance shares
    s_var = np.var(xd) / np.var(x)
    return dict(deg=deg, r_raw=r_raw, r_var=r_var, dCC_var=d_var,
                r_trend=r_trend, var_frac_wiggles=s_var,
                sd_xd=xd.std(), sd_yd=yd.std()), xd, yd, tr


# production model for comparison, detrended identically
prod = np.interp(tp, ts, np.loadtxt(f"{ROOT}/{IDX}/lte_results.csv",
                                    delimiter=",")[:, 1])
pd_var, _ = detrend(prod, 2)
xd2 = detrend(x, 2)[0]
r_prod_var = np.corrcoef(xd2, pd_var)[0, 1]

print(f"{IDX}: windings={Ms}  IR={p['IR']:+.3f}  year_off={p['year']:.2e}")
for deg in (2, 3):
    res, xd, yd, tr = run(deg)
    print(f"  detrend-deg={deg}:  r_raw={res['r_raw']:+.3f}  "
          f"r_var={res['r_var']:+.3f}  dCC_var={res['dCC_var']:+.3f}  "
          f"r_trend={res['r_trend']:+.3f}  "
          f"wiggle-var-frac={res['var_frac_wiggles']:.2f}")
print(f"  production col2 detrended identically: r_var={r_prod_var:+.3f}")

res, xd, yd, tr = run(2)
fig, axes = plt.subplots(4, 1, figsize=(12, 8.5), sharex=True)
axes[0].plot(tp, x, color="0.4", lw=0.9)
axes[0].set_ylabel(f"{IDX} obs (raw)")
axes[1].plot(tp, tr, color="brown", lw=1.4)
axes[1].set_ylabel("quadratic trend\nextracted")
axes[2].plot(tp, xd, color="0.3", lw=0.9, label="obs detrended")
axes[2].plot(tp, yd, color="crimson", lw=0.9,
             label=f"fit detrended  r={res['r_var']:.3f} dCC={res['dCC_var']:.3f}")
axes[2].plot(tp, pd_var, color="tab:blue", lw=0.9, ls=":", alpha=0.8,
             label=f"production detrended  r={r_prod_var:.3f}")
axes[2].legend(fontsize=8, ncol=3)
axes[2].set_ylabel("variations only")
axes[3].plot(tp[1:], np.diff(xd), color="0.3", lw=0.6)
axes[3].plot(tp[1:], np.diff(yd), color="crimson", lw=0.6, alpha=0.85)
axes[3].set_ylabel("d/dt (micro)")
fig.suptitle(f"IODE {IDX}: one-dial manifold fit vs TREND-discriminated signal "
             f"(r_raw {res['r_raw']:.3f} = trend {res['r_trend']:.3f} + wiggles; "
             f"honest r_var={res['r_var']:.3f})")
fig.tight_layout()
out = f"{GEN}/../figures/fig_iode_trend.png"
fig.savefig(out, dpi=130)
print("chart:", out)
