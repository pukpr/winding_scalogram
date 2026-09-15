#!/usr/bin/env python3
"""JOINT v6 — generalized + AUTONOMOUS lag-12 delay differential.
Shared-yl joint local fit (as joint_capture5) for any set of indices
that have an lt.exe.p, optionally with model-level L(x)=x-IR*x[i-12]
(production regression factors also carry Exp(F*Third) tilt).
nino4 = first new target; pdo+amo = control.
Outputs chart + r / r_delay / dCC per index."""
import os as _os
_R = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
import sys, json, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, _R)
from lte_forward import (YEAR_IN_DAYS, tide_sum, impulse_delta, iir,
                         bessel)

ROOT = _R
GEN = _R + "/milestone_2026_09/data"
PK = ("offs", "bg", "impA", "impB", "delA", "delB", "asym", "ma", "mp",
      "init", "shfT")


def load_index(idx):
    p = json.load(open(f"{ROOT}/{idx}/lt.exe.p"))
    c = np.loadtxt(f"{ROOT}/{idx}/lte_results.csv", delimiter=",")
    return p, c[:, 0], c[:, 2]


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


def local_fit(F, tp, x, sig, Ms, nmax=3, third=0.0, IR=0.0, mode="plain"):
    """mode: plain      = regress against raw x
       dr_target = production default: regress against DR = x + IR*x[-12],
                   then apply L (delay) to the fit
       gls       = UNCOMPENSATED mode: fold L into basis columns,
                   regress against raw x (fit IS the delayed model)"""
    w = np.exp(-0.5 * ((tp[:, None] - tp[None, :]) / sig) ** 2)
    tilt = np.exp(F * third)
    cols = [np.ones_like(F), F]
    for M in Ms:
        th = 2 * np.pi * M
        for n in range(1, nmax + 1):
            cols += [np.sin(n * th * F) * tilt, np.cos(n * th * F) * tilt]
    cols += [np.sin(2*np.pi*tp), np.cos(2*np.pi*tp),
             np.sin(4*np.pi*tp), np.cos(4*np.pi*tp)]
    t = tp - tp[0]
    cols += [t, t**2]
    X = np.column_stack(cols)

    def L(v):
        if IR == 0.0 or mode == "plain":
            return v
        z = v.copy()
        for i in range(12, len(z)):
            z[i] = v[i] - IR * v[i - 12]
        return z

    tgt = x.copy()
    if mode == "dr_target" and IR != 0.0:
        tgt[12:] = x[12:] + IR * x[:-12]
    Xin = L(X) if mode == "gls" else X
    fit = np.empty(len(tp))
    for i in range(len(tp)):
        wi = w[i]
        A = Xin * wi[:, None]
        b, *_ = np.linalg.lstsq(A, tgt * wi, rcond=None)
        fit[i] = Xin[i] @ b
    if mode == "dr_target":
        fit = L(fit)
    return fit


def dcc(a, b):
    da, db = np.diff(a), np.diff(b)
    return float(np.corrcoef(da, db)[0, 1])


def apply_delay(y, IR):
    z = y.copy()
    for i in range(12, len(z)):
        z[i] = y[i] - IR * y[i - 12]
    return z


def main():
    yl = 365.2463
    names = sys.argv[1:] or ["amo", "pdo", "nino4"]
    t0 = max(np.loadtxt(f"{ROOT}/{i}/lte_results.csv", delimiter=",")[0, 0]
             for i in names)
    t1 = min(np.loadtxt(f"{ROOT}/{i}/lte_results.csv", delimiter=", ")[-1, 0]
             if False else
             np.loadtxt(f"{ROOT}/{i}/lte_results.csv", delimiter=",")[-1, 0]
             for i in names)
    tp = np.arange(round(t0 * 12) / 12, round(t1 * 12) / 12, 1 / 12)
    fam = []
    for i in names:
        p, ts, series = load_index(i)
        Ms = {}
        for j, m in enumerate(p["ltep"]):
            if 0.002 < abs(m) < 10:
                Ms[round(abs(m), 4)] = j
        f = manifold(p, yl, tp)
        x = np.interp(tp, ts, series); x = (x - x.mean()) / x.std()
        IR = float(p["IR"]); third = 0.0
        res = {}
        for mode in ("plain", "dr_target", "gls"):
            y = local_fit(f, tp, x, 15.0, Ms, IR=IR, mode=mode)
            res[mode] = y
        prod = np.interp(tp, ts, np.loadtxt(f"{ROOT}/{i}/lte_results.csv",
                             delimiter=",")[:, 1])
        prod = (prod - prod.mean()) / prod.std()
        line = [f"{i:6s} IR={IR:+.3f} windings={sorted(Ms)}"]
        for mode in ("plain", "dr_target", "gls"):
            y = res[mode]
            r = np.corrcoef(x, y)[0, 1]
            line.append(f"{mode}: r={r:+.3f} dCC={dcc(x,y):+.3f}")
        line.append(f"(prod r {np.corrcoef(x,prod)[0,1]:+.3f} "
                    f"dCC {dcc(x,prod):+.3f})")
        print("  ".join(line))
        fam.append((i, x, res["dr_target"], res["gls"], tp))
    fig, axes = plt.subplots(3 * len(names), 1, figsize=(12, 2.0 * 3 * len(names)),
                             sharex=True)
    for k, (i, x, y, yd, _) in enumerate(fam):
        base = k * 3
        axes[base].plot(tp, x, color="0.4", lw=0.9)
        axes[base].set_ylabel(f"{i}\nobs")
        axes[base + 1].plot(tp, y, color="crimson", lw=0.9)
        axes[base + 1].set_ylabel("DR fit\n(prod mode)")
        if yd is not None:
            axes[base + 2].plot(tp, yd, color="purple", lw=0.9)
            axes[base + 2].set_ylabel("GLS fit\n(basis-folded L)")
        else:
            axes[base + 2].set_visible(False)
    fig.suptitle(f"joint capture at yl={yl} — obs / fit / lag-12-delay fit (IR per index)")
    fig.tight_layout()
    fig.savefig(f"{GEN}/../figures/fig_joint_nino4.png", dpi=130)
    print("chart:", f"{GEN}/../figures/fig_joint_nino4.png")


if __name__ == "__main__":
    main()
