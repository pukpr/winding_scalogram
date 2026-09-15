#!/usr/bin/env python3
"""MARQUEE: stacked obs+fit overlay for amo, pdo, nino4, iode, baltic.
Same one year-length dial (365.2463), each index with its own windings,
IR/constants from lt.exe.p; local-window winding fit (sigma per stage
report). Overlay draws obs (grey) under fit (color, alpha) at IDENTICAL
y-scale per row so the high-r structure is visually explicit; r and
dCC annotated. This is the milestone showcase figure.

Self-contained: import paths fixed at runtime to the repo layout:
  repo/wavelet_scalogram.py, repo/lte_forward.py,
  repo/<idx>/lte_results.csv, repo/<idx>/lt.exe.p"""
import sys, os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, REPO)

PK = ("offs", "bg", "impA", "impB", "delA", "delB", "asym", "ma", "mp",
      "init", "shfT")


def load_params(idx):
    return json.load(open(f"{REPO}/{idx}/lt.exe.p"))


def month_grid(ts):
    return np.arange(round(ts[0] * 12) / 12,
                     round(ts[-1] * 12) / 12 + 1e-9, 1 / 12)


def manifold(p, yl, tp):
    from lte_forward import tide_sum, impulse_delta, iir, bessel, YEAR_IN_DAYS
    lpap = np.array(p["lpap"], float)
    per = np.abs(lpap[:, 0])
    B = {k: float(p[k]) for k in PK}
    tf = tide_sum(tp, lpap[:, 1:3], per, yl, 0.0, B["shfT"])
    comb = impulse_delta(tp, B["delA"], B["delB"], B["asym"], 12)
    R = iir(tf * comb, lag_a=1.0 - B["ma"], lag_c=B["mp"], init=B["init"],
            start_date=1880.0, dates=tp)   # production chain start date
    return bessel(R, B["impA"], B["impB"], p["ltep"][-1], B["offs"],
                  B["bg"])


def local_fit(F, tp, x, sig, Ms, nmax=3):
    w = np.exp(-0.5 * ((tp[:, None] - tp[None, :]) / sig) ** 2)
    cols = [np.ones_like(F), F]
    for M in Ms:
        th = 2 * np.pi * M
        for n in range(1, nmax + 1):
            cols += [np.sin(n * th * F), np.cos(n * th * F)]
    cols += [np.sin(2*np.pi*tp), np.cos(2*np.pi*tp),
             np.sin(4*np.pi*tp), np.cos(4*np.pi*tp)]
    t = tp - tp[0]
    cols += [t, t**2]
    X = np.column_stack(cols)
    fit = np.empty(len(tp))
    for i in range(len(tp)):
        wi = w[i]
        b, *_ = np.linalg.lstsq(X * wi[:, None], x * wi, rcond=None)
        fit[i] = X[i] @ b
    return fit


def detrend(v, tp, deg=2):
    t = tp - tp.mean()
    V = np.vander(t, deg + 1)
    b, *_ = np.linalg.lstsq(V, v, rcond=None)
    return v - V @ b


def dcc(a, b):
    return float(np.corrcoef(np.diff(a), np.diff(b))[0, 1])


YL = 365.2463
# per-stage validated settings (see RESULTS_W1.md stage sections)
CFG = {  # idx: (sigma, nmax, detrend_report)
    "amo":   (10.0, 3, False),
    "pdo":   (10.0, 3, False),
    "nino4": (10.0, 3, False),
    "iode":  (10.0, 3, True),   # trend nuisance +0.11: report detrended
    "baltic": (10.0, 6, False),
}
COL = {"amo": "crimson", "pdo": "tab:green", "nino4": "darkorange",
       "iode": "tab:purple", "baltic": "tab:blue"}

fig, axes = plt.subplots(len(CFG), 1, figsize=(12, 2.6 * len(CFG)),
                         sharex=True)
rows = {}
for k, (idx, (sig, nmax, dtr)) in enumerate(CFG.items()):
    c = np.loadtxt(f"{REPO}/{idx}/lte_results.csv", delimiter=",")
    ts, series = c[:, 0], c[:, 2]
    p = load_params(idx)
    tp = month_grid(ts)
    x = np.interp(tp, ts, series)
    x = (x - x.mean()) / x.std()
    F = manifold(p, YL, tp)
    Ms = sorted({round(abs(m), 4) for m in p["ltep"] if 0.002 < abs(m) < 10})
    y = local_fit(F, tp, x, sig, Ms, nmax=nmax)
    if dtr:
        xd, yd = detrend(x, tp), detrend(y, tp)
        r = np.corrcoef(xd, yd)[0, 1]
        rraw = np.corrcoef(x, y)[0, 1]
        lab = f"r={r:.3f} (detrended; raw {rraw:.3f})  dCC={dcc(xd, yd):.3f}"
    else:
        r = np.corrcoef(x, y)[0, 1]
        lab = f"r={r:.3f}  dCC={dcc(x, y):.3f}"
    rows[idx] = float(r)
    ax = axes[k]
    ax.plot(tp, x, color="0.65", lw=1.0, zorder=1)
    ax.plot(tp, y, color=COL[idx], lw=1.1, alpha=0.85, zorder=2)
    ax.set_ylabel(f"{idx}\n{lab}", fontsize=9)
    ax.text(0.995, 0.92, f"windings {Ms}  n≤{nmax}", transform=ax.transAxes,
            ha="right", fontsize=7.5, color=COL[idx])
axes[-1].set_xlabel("")
fig.suptitle("MARQUEE — five indices, ONE year-length dial (365.2463 d): "
             "grey=obs, color=winding fit on the shared manifold", y=0.995)
fig.tight_layout(rect=(0, 0, 1, 0.98))
out = f"{REPO}/milestone_2026_09/figures/marquee_stack.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
fig.savefig(out, dpi=130)
print(out)
for i, v in rows.items():
    print(f"  {i:7s} r={v:+.3f}")
