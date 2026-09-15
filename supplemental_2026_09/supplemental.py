#!/usr/bin/env python3
"""SUPPLEMENTAL: stacked obs+fit overlays for nao, brestexcl, tna, tpi,
emi — same one-dial machinery as milestone_2026_09/marquee.py, plus:
  - brestexcl 1944-1954 blackout: samples masked from local-window
    support AND from r/dCC scoring (fit value shown, greyed band)
  - tna: trend nuisance (0.10) -> report detrended like iode
Per-index points tested in README: nao rich ridge comb, brestexcl gap,
tna~amo, tpi~pdo, emi~nino4 (cross-correlations printed too)."""
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
YL = 365.2463


def month_grid(ts):
    return np.arange(round(ts[0] * 12) / 12,
                     round(ts[-1] * 12) / 12 + 1e-9, 1 / 12)


def manifold(p, yl, tp):
    from lte_forward import tide_sum, impulse_delta, iir, bessel
    lpap = np.array(p["lpap"], float)
    per = np.abs(lpap[:, 0])
    B = {k: float(p[k]) for k in PK}
    tf = tide_sum(tp, lpap[:, 1:3], per, yl, 0.0, B["shfT"])
    comb = impulse_delta(tp, B["delA"], B["delB"], B["asym"], 12)
    R = iir(tf * comb, lag_a=1.0 - B["ma"], lag_c=B["mp"], init=B["init"],
            start_date=1880.0, dates=tp)
    return bessel(R, B["impA"], B["impB"], p["ltep"][-1], B["offs"],
                  B["bg"])


def local_fit(F, tp, x, sig, Ms, nmax=3, mask=None):
    """mask: bool array, True = usable sample. Missing samples get zero
    weight everywhere (never fabricated into the local regression)."""
    w = np.exp(-0.5 * ((tp[:, None] - tp[None, :]) / sig) ** 2)
    if mask is not None:
        w = w * mask[None, :]
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


def detrend_m(v, tp, m, deg=2):
    t = tp - tp.mean()
    V = np.vander(t, deg + 1)
    b, *_ = np.linalg.lstsq(V[m], v[m], rcond=None)
    return v - V @ b


def dcc(a, b):
    return float(np.corrcoef(np.diff(a), np.diff(b))[0, 1])


CFG = {  # idx: (sigma, nmax, detrend_report, blackout)
    "nao":      (10.0, 3, False, None),
    "brestexcl": (10.0, 3, False, (1944.3, 1954.3)),
    "tna":      (10.0, 3, True, None),
    "tpi":      (10.0, 3, False, None),
    "emi":      (10.0, 3, False, None),
}
COL = {"nao": "teal", "brestexcl": "saddlebrown", "tna": "crimson",
       "tpi": "tab:green", "emi": "darkorange"}

fig, axes = plt.subplots(len(CFG), 1, figsize=(12, 2.6 * len(CFG)),
                         sharex=False)
summary = {}
for k, (idx, (sig, nmax, dtr, gap)) in enumerate(CFG.items()):
    p = json.load(open(f"{REPO}/{idx}/lt.exe.p"))
    c = np.loadtxt(f"{REPO}/{idx}/lte_results.csv", delimiter=",")
    ts, series = c[:, 0], c[:, 2]
    tp = month_grid(ts)
    x = np.interp(tp, ts, series)
    x = (x - x.mean()) / x.std()
    mask = np.ones(len(tp), bool)
    if gap:
        mask &= ~((tp >= gap[0]) & (tp <= gap[1]))
    F = manifold(p, YL, tp)
    Ms = sorted({round(abs(m), 4) for m in p["ltep"] if 0.002 < abs(m) < 10})
    y = local_fit(F, tp, x, sig, Ms, nmax=nmax, mask=mask)
    if dtr:
        xd = detrend_m(x, tp, mask)
        yd = detrend_m(y, tp, mask)
        r = np.corrcoef(xd[mask], yd[mask])[0, 1]
        raw = np.corrcoef(x[mask], y[mask])[0, 1]
        lab = f"r={r:.3f} (detrended; raw {raw:.3f})  dCC={dcc(xd[mask], yd[mask]):.3f}"
        xplot, yplot = xd, yd
    else:
        r = np.corrcoef(x[mask], y[mask])[0, 1]
        lab = f"r={r:.3f}  dCC={dcc(x[mask], y[mask]):.3f}"
        xplot, yplot = x, y
    prod = np.interp(tp, ts, c[:, 1])
    prod = (prod - prod.mean()) / prod.std()
    if dtr:
        prod = detrend_m(prod, tp, mask)
    rp = np.corrcoef(xplot[mask], prod[mask])[0, 1]
    summary[idx] = (r, rp, float(np.std(x[mask])) )
    ax = axes[k]
    xplot2 = np.where(mask, xplot, np.nan)   # never fabricate obs across gap
    if gap:
        ax.axvspan(gap[0], gap[1], color="0.85", alpha=0.9, zorder=0)
    ax.plot(tp, xplot2, color="0.65", lw=1.0, zorder=1)
    ax.plot(tp, yplot, color=COL[idx], lw=1.1, alpha=0.85, zorder=2)
    ax.set_ylabel(f"{idx}\n{lab}\nprod r={rp:.3f}", fontsize=8.5)
    ax.text(0.995, 0.90, f"windings {Ms}  n\u2264{nmax}", transform=ax.transAxes,
            ha="right", fontsize=7.5, color=COL[idx])
fig.suptitle("SUPPLEMENTAL — five more indices on the same one year-length "
             "dial (365.2463 d); grey=obs, color=winding fit; "
             "baltic-band shading = brestexcl blackout (masked from fit)",
             y=0.995)
fig.tight_layout(rect=(0, 0, 1, 0.975))
out = f"{REPO}/supplemental_2026_09/figures/supplemental_stack.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
fig.savefig(out, dpi=130)
print(out)
for i, (r, rp, _) in summary.items():
    print(f"  {i:10s} r={r:+.3f}  prod r={rp:+.3f}")
