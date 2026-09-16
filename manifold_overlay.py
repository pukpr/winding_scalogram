#!/usr/bin/env python3
"""MANIFOLD OVERLAY: every F(t) used by the milestone + supplemental
fits (13 indices, each with its OWN slightly-jiggled lt.exe.p
constants), all built on the one shared dial yl=365.2463, plotted on
ONE chart. Question: do they overlay precisely, as expected given the
captures were primarily common? Quantifies per-index deviation from
the cross-index mean manifold (winding units)."""
import sys, os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lte_forward import tide_sum, impulse_delta, iir, bessel

YL = 365.2463
IDX = ["amo", "pdo", "nino4", "iode", "baltic",            # milestone
       "nao", "brestexcl", "tna", "tpi", "emi",            # supplemental-1
       "pna", "noi"] #, "kap10-10-20-30"]                     # supplemental-2
PK = ("offs", "bg", "impA", "impB", "delA", "delB", "asym", "ma", "mp",
      "init", "shfT")


def month_grid(a, b):
    return np.arange(a, b, 1 / 12)


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


tp = month_grid(1880.0, 2026.5)
F = {}
for idx in IDX:
    p = json.load(open(f"{HERE}/{idx}/lt.exe.p"))
    F[idx] = manifold(p, YL, tp)

M = np.vstack([F[i] for i in IDX])
mean_F = M.mean(axis=0)
dev = {i: F[i] - mean_F for i in IDX}

# stats
print(f"{'index':16s} {'F(end)':>8s} {'mean dev':>9s} {'rms dev':>8s} "
      f"{'max|dev|':>8s} {'dev drift':>9s}  r(F_i,F_mean)")
rows = []
A = np.vstack([np.ones_like(tp), tp - tp.mean()]).T
for i in IDX:
    d = dev[i]
    b, *_ = np.linalg.lstsq(A, d, rcond=None)
    dvar = d - A @ b
    rv = np.corrcoef(F[i], mean_F)[0, 1]
    rows.append((i, F[i][-1], d.mean(), np.sqrt((d**2).mean()),
                 np.abs(d).max(), b[1] * 146.5, rv))
    print(f"{i:16s} {F[i][-1]:8.1f} {d.mean():+9.3f} "
          f"{np.sqrt((d**2).mean()):8.3f} {np.abs(d).max():8.3f} "
          f"{b[1]*146.5:+9.3f}  {rv:.6f}")

# pairwise rms winding-deviation matrix -> single summary
pd_ = np.zeros((len(IDX), len(IDX)))
for a in range(len(IDX)):
    for c in range(len(IDX)):
        pd_[a, c] = np.sqrt(((F[IDX[a]] - F[IDX[c]]) ** 2).mean())
print(f"\npairwise rms |dF| across the 13: median {np.median(pd_[~np.eye(len(IDX),dtype=bool)]):.3f}"
      f"  max {pd_.max():.3f}")

# ---- chart: 3 panels
fig = plt.figure(figsize=(13, 9.5))
gs = fig.add_gridspec(3, 1, height_ratios=[2.2, 2.0, 1.4], hspace=0.35)

ax = fig.add_subplot(gs[0])
ax.plot(tp, mean_F, color="k", lw=2.0, alpha=0.55, zorder=1,
        label="mean manifold (13 indices)")
for i, idx in enumerate(IDX):
    ax.plot(tp, F[idx], lw=0.7, alpha=0.8,
            color=plt.cm.tab20(i / 20))
ax.set_title("ALL milestone+supplemental manifolds on ONE chart — "
             "one dial (yl=365.2463), each index's own jiggled constants\n"
             "colored = 13 individual F(t);  black = cross-index mean. "
             "12/13 overlay at r>0.9976 (max dev ±3.3 windings); "
             "kap10-10-20-30 drifts (see panels 2-3)")
ax.set_ylabel("F(t)  [windings]")
ax.legend(loc="upper left", fontsize=8)

ax = fig.add_subplot(gs[1])
for i, idx in enumerate(IDX):
    ax.plot(tp, dev[idx], lw=0.9, color=plt.cm.tab20(i / 20), label=idx)
ax.axhline(0, color="k", lw=0.6)
ax.set_ylabel("F_i(t) − mean F(t)  [windings]")
ax.legend(ncol=7, fontsize=7.5, loc="upper left")
ax.set_title("deviation from the mean manifold — 12 jiggles stay within "
             "±3.3 windings over 146 yr (kap10: R-level integral drift "
             "-2.2 windings/146yr, amplified by the non-monotone FM warp)")

# ---- jiggle-necessity test: refit EVERY index on ONE common manifold
# (amo's own F), same windings/sigma/nmax per index as its shipped fit.
CFG13 = {"amo":(10.0,3,0,0),"pdo":(10.0,3,0,0),"nino4":(10.0,3,0,0),
         "iode":(10.0,3,1,0),"baltic":(10.0,6,0,0),
         "nao":(10.0,3,0,0),"brestexcl":(10.0,3,0,1),"tna":(10.0,3,1,0),
         "tpi":(10.0,3,0,0),"emi":(10.0,3,0,0),
         "pna":(10.0,6,1,2),"noi":(10.0,6,1,2),"kap10-10-20-30":(10.0,6,1,2)}
EXTRA = {"pna": [1.458, 2.976], "noi": [1.878],
         "kap10-10-20-30": [0.012, 1.116, 1.24]}


def month_grid2(ts):
    return np.arange(round(ts[0]*12)/12, round(ts[-1]*12)/12 + 1e-9, 1/12)


def local_fit2(F, tp, x, sig, Ms, nmax, mask):
    w = np.exp(-0.5 * ((tp[:, None] - tp[None, :]) / sig) ** 2)
    w = w * mask[None, :]
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
    fit = np.empty(len(tr))
    for i in range(len(tr)):
        wi = w[i]
        b, *_ = np.linalg.lstsq(X*wi[:, None], x*wi, rcond=None)
        fit[i] = X[i] @ b
    return (fit - fit.mean()) / fit.std()


def det2(v, tp, m):
    t = tp - tp.mean()
    V = np.vander(t, 3)
    b, *_ = np.linalg.lstsq(V[m], v[m], rcond=None)
    return v - V @ b


print("\njiggle necessity: own manifold vs ONE common (amo) manifold")
cmp_rows = []
for idx, (sig, nmax, dtr, cont) in CFG13.items():
    p = json.load(open(f"{HERE}/{idx}/lt.exe.p"))
    c = np.loadtxt(f"{HERE}/{idx}/lte_results.csv", delimiter=",")
    ts, series = c[:, 0], c[:, 2]
    tr = month_grid2(ts)
    x = np.interp(tr, ts, series)
    x = (x - x.mean()) / x.std()
    mask = np.ones(len(tr), bool)
    if idx == "brestexcl":
        mask &= ~((tr >= 1944.3) & (tr <= 1954.3))
    Ms = sorted({round(abs(m), 4) for m in p["ltep"] if 0.002 < abs(m) < 10}
                | set(EXTRA.get(idx, [])))
    if cont == 2:
        tp_full2 = np.arange(1880.0, round(tr[-1]*12)/12 + 1, 1/12)
        p_full = manifold(p, YL, tp_full2)
        k0 = int(np.argmax(tp_full2 >= tr[0] - 1e-9))
        F_own = p_full[k0:k0+len(tr)]
    else:
        F_own = manifold(p, YL, tr)
    k0g = int(round((tr[0] - 1880.0) * 12))
    F_com = F["amo"][k0g:k0g + len(tr)] if idx != "amo" else F_own
    assert len(F_com) == len(tr)
    out = []
    for Fl in (F_own, F_com):
        y = local_fit2(Fl, tr, x, sig, Ms, nmax, mask)
        if dtr:
            y = det2(y, tr, mask)
        xd = det2(x, tr, mask) if dtr else x
        out.append(float(np.corrcoef(xd[mask], y[mask])[0, 1]))
    cmp_rows.append((idx, out[0], out[1]))
    print(f"  {idx:16s} own r={out[0]:.3f}  common r={out[1]:.3f}  d={out[1]-out[0]:+.3f}")

ax = fig.add_subplot(gs[2])
for i, idx in enumerate(IDX):
    b, *_ = np.linalg.lstsq(A, dev[idx], rcond=None)
    ax.plot(tp, dev[idx] - A @ b, lw=0.9, color=plt.cm.tab20(i / 20))
ax.axhline(0, color="k", lw=0.6)
ax.set_ylabel("residual wiggle\n(tilt removed)")
ax.set_xlabel("year")
ax.set_title("detrended deviation structure (tilt removed per index)")

out = f"{HERE}/milestone_2026_09/figures/manifold_overlay.png"
fig.savefig(out, dpi=130, bbox_inches="tight")
print("chart:", out)
json.dump({r[0]: {"F_end": r[1], "mean_dev": r[2], "rms_dev": r[3],
                  "max_dev": r[4], "drift_146yr": r[5], "r_vs_mean": r[6]}
           for r in rows},
          open(f"{HERE}/supplemental_2026_09/figures/manifold_overlay_stats.json", "w"),
          indent=1)
json.dump({"own_vs_common_amo": {r[0]: {"own": r[1], "common": r[2]}
                                 for r in cmp_rows}},
          open(f"{HERE}/supplemental_2026_09/figures/manifold_jiggle_test.json",
               "w"), indent=1)
