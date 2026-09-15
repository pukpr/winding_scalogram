#!/usr/bin/env python3
"""NEGATIVE-CONTROL REJECTION EXHIBIT: pdo_iaaft_detuned_surrogate.
IAAFT-drawn surrogate of PDO, detuned to baltic's winding triple
{0.1223, 0.2076, 0.9247} at production yl. Panels:
  1: real pdo obs + pdo-winding fit on pdo manifold   (r=0.81)
  2: surrogate obs + SAME fit                        (r=0.87 — HIGHER)
  3: surrogate obs + its own baltic-winding fit on its own manifold
  4: ridge spectra bits: real pdo vs surrogate vs AR1-noise pass rate
Conclusion drawn in README: in-sample fit r is saturated by smoothness;
the ridge QUALIFICATION and dCC are the discriminating statistics.
"""
import sys, os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, REPO)
from lte_forward import tide_sum, impulse_delta, iir, bessel

YL = 365.2463
PK = ("offs", "bg", "impA", "impB", "delA", "delB", "asym", "ma", "mp",
      "init", "shfT")


def month_grid(ts):
    return np.arange(round(ts[0]*12)/12, round(ts[-1]*12)/12 + 1e-9, 1/12)


def manifold(p, yl, tp):
    lpap = np.array(p["lpap"], float)
    per = np.abs(lpap[:, 0])
    B = {k: float(p[k]) for k in PK}
    tf = tide_sum(tp, lpap[:, 1:3], per, yl, 0.0, B["shfT"])
    comb = impulse_delta(tp, B["delA"], B["delB"], B["asym"], 12)
    R = iir(tf * comb, lag_a=1.0 - B["ma"], lag_c=B["mp"], init=B["init"],
            start_date=1880.0, dates=tp)
    return bessel(R, B["impA"], B["impB"], p["ltep"][-1], B["offs"],
                  B["bg"])


def local_fit(F, tp, x, sig, Ms, nmax):
    w = np.exp(-0.5 * ((tp[:, None] - tp[None, :]) / sig) ** 2)
    cols = [np.ones_like(F), F]
    for M in Ms:
        th = 2*np.pi*M
        for n in range(1, nmax+1):
            cols += [np.sin(n*th*F), np.cos(n*th*F)]
    cols += [np.sin(2*np.pi*tp), np.cos(2*np.pi*tp),
             np.sin(4*np.pi*tp), np.cos(4*np.pi*tp)]
    t = tp - tp[0]
    cols += [t, t**2]
    X = np.column_stack(cols)
    fit = np.empty(len(tp))
    for i in range(len(tp)):
        wi = w[i]
        b, *_ = np.linalg.lstsq(X*wi[:, None], x*wi, rcond=None)
        fit[i] = X[i] @ b
    return (fit - fit.mean()) / fit.std()


def norm(v):
    return (v - v.mean()) / v.std()


ppdo = json.load(open(f"{REPO}/pdo/lt.exe.p"))
psur = json.load(open(f"{REPO}/pdo_iaaft_detuned_surrogate/lt.exe.p"))
cp = np.loadtxt(f"{REPO}/pdo/lte_results.csv", delimiter=",")
cs = np.loadtxt(f"{REPO}/pdo_iaaft_detuned_surrogate/lte_results.csv",
                delimiter=",")
ts = cp[:, 0]
tp = month_grid(ts)
x_real = norm(np.interp(tp, ts, cp[:, 2]))
x_surr = norm(np.interp(tp, cs[:, 0], cs[:, 2]))
F_pdo = manifold(ppdo, YL, tp)
F_sur = manifold(psur, YL, tp)
Mpdo = [0.2073, 0.4488, 0.5934]
Msur = [0.1223, 0.2076, 0.9247]

fit_real = local_fit(F_pdo, tp, x_real, 10.0, Mpdo, 3)
fit_surr = local_fit(F_pdo, tp, x_surr, 10.0, Mpdo, 3)
fit_surr_own = local_fit(F_sur, tp, x_surr, 10.0, Msur, 6)
r1 = np.corrcoef(x_real, fit_real)[0, 1]
r2 = np.corrcoef(x_surr, fit_surr)[0, 1]
r3 = np.corrcoef(x_surr, fit_surr_own)[0, 1]

fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
ax = axes[0]
ax.plot(tp, x_real, color="0.6", lw=1.0)
ax.plot(tp, fit_real, color="tab:green", lw=1.1)
ax.set_ylabel(f"real PDO\nfit r={r1:.3f}", fontsize=9)
ax = axes[1]
ax.plot(tp, x_surr, color="0.6", lw=1.0)
ax.plot(tp, fit_surr, color="tab:green", lw=1.1)
ax.set_ylabel(f"SURROGATE obs\nSAME pdo fit r={r2:.3f}\nHIGHER than real!",
              fontsize=9)
ax = axes[2]
ax.plot(tp, x_surr, color="0.6", lw=1.0)
ax.plot(tp, fit_surr_own, color="saddlebrown", lw=1.1)
ax.set_ylabel(f"SURROGATE obs\nown baltic-winding fit r={r3:.3f}",
              fontsize=9)
ax = axes[3]
# smoothness comparison: lag-k autocorrelation
for lab, v in (("real pdo", x_real), ("surrogate", x_surr)):
    ac = [np.corrcoef(v[:-k], v[k:])[0, 1] for k in range(1, 61)]
    ax.plot(np.arange(1, 61), ac, lw=1.4, label=lab)
ax.axhline(0, color="0.7", lw=0.6)
ax.set_xlabel("lag (months)"); ax.set_ylabel("autocorr")
ax.legend(fontsize=8)
ax.set_title("why the fit chases both: surrogate is SMOOTHER "
             f"(lag1 rho 0.995 vs 0.967) — a fit r on smooth series "
             "measures smoothness, not locking", fontsize=9.5)
fig.suptitle("NEGATIVE CONTROL pdo_iaaft_detuned_surrogate: in-sample fit r "
             "is NOT the rejection statistic\n(ridge qualification + "
             "red-noise floor battery red_noise_floor.py do the rejecting)",
             y=0.995)
fig.tight_layout(rect=(0, 0, 1, 0.97))
out = f"{HERE}/figures/rejection_surrogate.png"
fig.savefig(out, dpi=130)
print(out)
print(f"real r={r1:.3f}  surrogate same-fit r={r2:.3f}  surrogate own-fit r={r3:.3f}")
