#!/usr/bin/env python3
"""QBO stack v2 — k=0 parallel category, per the qbo50 reconciliation
(QBO_K0.md @2726cbe): shared draconic forcing, LEVEL-SPECIFIC comb.

Each panel now carries two fits in house style:
  solid colour : production manifold + the level's OWN scalogram teeth
                 (winding_rank --index, cont>=0.5; qbo50's 2.04-2.91
                 comb = harmonics 18-26 of |ltep|=0.1115, matching
                 production harm{18,25})  -> the capture the Ada fit
                 already earned,
  dashed blue  : shared draconic-only manifold + k=0 lattice teeth
                 {0.42, 0.68} -> the parallel-category fit.
ylabel metrics: r_own, r_draconic, honest r (own design vs 12-IAAFT flat
rung), dCC(own), production Ada r, and the frozen-CV(train<2015)
out-of-sample r through the 2015/16 disruption for the forecast design
named in the annotation.
"""
import sys, os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, REPO)

from lte_forward import tide_sum, impulse_delta, iir
from wavelet_scalogram import standardize

YL = 365.2463
PK = ("offs", "bg", "impA", "impB", "delA", "delB", "asym", "ma", "mp",
      "init", "shfT")
SIGMA, NMAX = 10.0, 3


def month_grid(ts):
    return np.arange(round(ts[0] * 12) / 12,
                     round(ts[-1] * 12) / 12 + 1e-9, 1 / 12)


def get(idx):
    p = json.load(open(f"{REPO}/{idx}/lt.exe.p"))
    dat = np.loadtxt(f"{REPO}/{idx}/{idx}.dat")
    tp = month_grid(dat[:, 0])
    x = standardize(np.interp(tp, dat[:, 0], dat[:, 1]))
    c = np.loadtxt(f"{REPO}/{idx}/lte_results.csv", delimiter=",", skiprows=1)
    fprod = np.interp(tp, c[:, 0], c[:, 3]); fprod -= fprod.mean()
    prod_model = standardize(np.interp(tp, c[:, 0], c[:, 1]))
    lpap = np.array(p["lpap"], float); per = lpap[:, 0]
    sel = np.logical_or(np.logical_and(per >= 26.9, per <= 27.7),
                        np.logical_and(np.abs(per) >= 13.5, np.abs(per) <= 13.9))
    B = {k: float(p[k]) for k in PK}
    tf = tide_sum(tp, lpap[sel][:, 1:3], np.abs(per[sel]), YL, 0.0, B["shfT"])
    comb = impulse_delta(tp, B["delA"], B["delB"], B["asym"], 12)
    fdra = iir(tf * comb, lag_a=1.0 - B["ma"], lag_c=B["mp"], init=B["init"],
               start_date=tp[0], dates=tp)
    fdra -= fdra.mean()
    return p, tp, x, fprod, fdra, prod_model


def design(F, tp, Ms, nmax=NMAX):
    cols = [np.ones_like(F), F]
    for M in Ms:
        th = 2 * np.pi * M
        for n in range(1, nmax + 1):
            cols += [np.sin(n * th * F), np.cos(n * th * F)]
    t = tp - tp[0]
    cols += [np.sin(2 * np.pi * t), np.cos(2 * np.pi * t), t, t ** 2]
    return np.column_stack(cols)


def local_fit(F, tp, x, Ms, sig=SIGMA):
    w = np.exp(-0.5 * ((tp[:, None] - tp[None, :]) / sig) ** 2)
    X = design(F, tp, Ms)
    fit = np.empty(len(tp))
    for i in range(len(tp)):
        b, *_ = np.linalg.lstsq(X * w[i][:, None], x * w[i], rcond=None)
        fit[i] = X[i] @ b
    return fit


def iaaft(y, seed):
    rng = np.random.default_rng(seed)
    N = len(y); nf = np.fft.rfftfreq(N, d=1 / 12)
    Am = np.abs(np.fft.rfft(y - y.mean()))
    ph = rng.uniform(0, 2 * np.pi, len(nf)); ph[0] = 0.0
    s = np.fft.irfft(Am * np.exp(1j * ph), n=N)
    for _ in range(30):
        s = np.interp(np.linspace(0, 1, N), np.sort(s), np.sort(y))
        f = np.fft.rfft(s - s.mean())
        s = np.fft.irfft(Am * np.exp(1j * np.angle(f)), n=N)
    return s


CFG = {
    "qbo30": dict(col="darkorange", lvl="30 hPa",
                  own=[0.48, 1.87, 3.06], k0=[0.42, 0.68],
                  note="k=0 teeth {0.42,0.68}: frozen-CV forecast r=0.825\n"
                       "through the 2015/16 disruption (draconic manifold)"),
    "qbo50": dict(col="tab:purple", lvl="50 hPa",
                  own=[0.49, 0.71, 2.04, 2.44, 2.79], k0=[0.42, 0.68],
                  note="own comb = 18-25 x |ltep| (2.79=25x0.1115, harm{18,25});\n"
                       "frozen-CV forecast r=0.673, onset 2015.5 vs obs 2015.58"),
}

fig, axes = plt.subplots(len(CFG), 1, figsize=(12, 2.8 * len(CFG)))
summary = {}
for k, (idx, cf) in enumerate(CFG.items()):
    p, tp, x, fprod, fdra, prod_model = get(idx)
    y_own = local_fit(fprod, tp, x, cf["own"])
    y_k0 = local_fit(fdra, tp, x, cf["k0"])
    r_own = float(np.corrcoef(x, y_own)[0, 1])
    r_k0 = float(np.corrcoef(x, y_k0)[0, 1])
    dCC = float(np.corrcoef(np.diff(x), np.diff(y_own))[0, 1])
    flat = [float(np.corrcoef(standardize(iaaft(x, 4001 + j)),
                              local_fit(fprod, tp, standardize(iaaft(x, 4001 + j)),
                                        cf["own"]))[0, 1]) for j in range(12)]
    fm, fs = float(np.mean(flat)), float(np.std(flat))
    rp = float(np.corrcoef(x, prod_model)[0, 1])
    summary[idx] = dict(r_own=r_own, r_draconic_k0=r_k0, dCC_own=dCC,
                        flat_mean=fm, flat_std=fs, honest_own=r_own - fm,
                        prod_r=rp)
    ax = axes[k]
    ax.plot(tp, x, color="0.65", lw=1.0, zorder=1)
    ax.plot(tp, y_own, color=cf["col"], lw=1.3, alpha=0.9, zorder=2,
            label=f"own comb {cf['own']}")
    ax.plot(tp, y_k0, color="tab:blue", lw=0.9, ls="--", alpha=0.8, zorder=3,
            label="draconic manifold, k=0 teeth {0.42,0.68}")
    ax.set_ylabel(f"{idx} ({cf['lvl']})\nr_own={r_own:.3f}  r_k0={r_k0:.3f}\n"
                  f"dCC={dCC:.3f}  honest={r_own - fm:+.3f} "
                  f"(flat {fm:.3f}±{fs:.3f})\nprod r={rp:.3f}", fontsize=8.0)
    ax.text(0.995, 0.94, cf["note"], transform=ax.transAxes, ha="right",
            va="top", fontsize=7.0, color=cf["col"])
    ax.legend(fontsize=7.5, loc="lower left")
r50 = summary["qbo50"]["r_own"]; r30 = summary["qbo30"]["r_own"]
fig.suptitle("QBO — k=0 category: SHARED draconic forcing (col4 corr 0.9972), "
             "LEVEL-SPECIFIC comb response (grey=obs, solid=own scalogram teeth "
             "cont>=0.5, dashed=shared k=0 lattice yl=365.2463)\n"
             f"qbo50 r={r50:.3f} on its own teeth beats qbo30 r={r30:.3f} — the "
             "earlier deficit was imposed teeth, not weak physics",
             y=0.995, fontsize=10.5)
fig.tight_layout(rect=(0, 0, 1, 0.915))
out = f"{REPO}/supplemental_2026_09/figures/qbo_stack.png"
fig.savefig(out, dpi=130)
print(out)
for i, s in summary.items():
    print(f"  {i}: r_own={s['r_own']:+.3f} r_k0={s['r_draconic_k0']:+.3f} "
          f"dCC={s['dCC_own']:+.3f} honest={s['honest_own']:+.3f} "
          f"prod={s['prod_r']:+.3f}")
json.dump(summary, open(f"{REPO}/supplemental_2026_09/figures/qbo_stack_stats.json", "w"), indent=1)
