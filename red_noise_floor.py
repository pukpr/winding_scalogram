#!/usr/bin/env python3
"""RED-NOISE FLOOR BATTERY: is the one-dial local-fit r above what
smooth noise achieves on the SAME design?
For every milestone/supplemental index: fit its shipped design (its
windings, sigma, yl=365.2463) to 8 AR1(rho-matched) and 8
phase-randomized (spectrum-preserving) surrogates of itself; compare
the real r_var to the surrogate floor. Motivated by the
pdo_iaaft_detuned_surrogate rejection test (REJECTION figure): that
negative control fits at r ABOVE real pdo -> r alone is not evidence.
"""
import sys, os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lte_forward import tide_sum, impulse_delta, iir, bessel

YL = 365.2463
PK = ("offs", "bg", "impA", "impB", "delA", "delB", "asym", "ma", "mp",
      "init", "shfT")
EXTRA = {"pna": [1.458, 2.976], "noi": [1.878],
         "kap10-10-20-30": [0.012, 1.116, 1.24]}
DET = {"iode", "tna", "pna", "noi", "kap10-10-20-30"}   # r_var basis
IDX = ["amo", "pdo", "nino4", "iode", "baltic",
       "nao", "brestexcl", "tpi", "emi",
       "pna", "noi", "kap10-10-20-30"]


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


def design(F, tp, Ms, nmax):
    cols = [np.ones_like(F), F]
    for M in Ms:
        th = 2*np.pi*M
        for n in range(1, nmax+1):
            cols += [np.sin(n*th*F), np.cos(n*th*F)]
    cols += [np.sin(2*np.pi*tp), np.cos(2*np.pi*tp),
             np.sin(4*np.pi*tp), np.cos(4*np.pi*tp)]
    t = tp - tp[0]
    cols += [t, t**2]
    return np.column_stack(cols)


def local_fit_vec(X, w, x):
    """w: (N,N) weight matrix rows. Returns fitted curve."""
    fit = np.empty(X.shape[0])
    for i in range(X.shape[0]):
        wi = w[i]
        b, *_ = np.linalg.lstsq(X * wi[:, None], x * wi, rcond=None)
        fit[i] = X[i] @ b
    return fit


def det2(v, tp, m):
    t = tp - tp.mean()
    V = np.vander(t, 3)
    b, *_ = np.linalg.lstsq(V[m], v[m], rcond=None)
    return v - V @ b


def score(x, X, w, tp, mask, detr):
    y = local_fit_vec(X, w, x)
    if detr:
        xd, yd = det2(x, tp, mask), det2(y, tp, mask)
    else:
        xd, yd = x, y
    yd = (yd - yd.mean()) / yd.std()
    return float(np.corrcoef(xd[mask], yd[mask])[0, 1])


rng = np.random.default_rng(20260915)
out = {}
for idx in IDX:
    p = json.load(open(f"{HERE}/{idx}/lt.exe.p"))
    c = np.loadtxt(f"{HERE}/{idx}/lte_results.csv", delimiter=",")
    ts, series = c[:, 0], c[:, 2]
    tp = month_grid(ts)
    x = np.interp(tp, ts, series)
    x = (x - x.mean()) / x.std()
    mask = np.ones(len(tp), bool)
    if idx == "brestexcl":
        mask &= ~((tp >= 1944.3) & (tp <= 1954.3))
    F = manifold(p, YL, tp)
    Ms = sorted({round(abs(m), 4) for m in p["ltep"] if 0.002 < abs(m) < 10}
                | set(EXTRA.get(idx, [])))
    sig = 10.0
    w = np.exp(-0.5 * ((tp[:, None] - tp[None, :]) / sig) ** 2) * mask[None, :]
    rho = float(np.corrcoef(x[1:, ], x[:-1])[0, 1])
    import numpy.fft as fft
    mag = np.abs(fft.rfft(x))
    rec = {"rho": round(rho, 4)}
    for nmax in (3, 6):
        X = design(F, tp, Ms, nmax)
        real = score(x, X, w, tp, mask, idx in DET)
        s_ar, s_pr = [], []
        s_ = np.sqrt(max(1 - rho**2, 1e-9))
        for k in range(8):
            z = rng.standard_normal(len(tp)); a = np.zeros(len(tp))
            for i in range(len(tp)):
                a[i] = rho * a[i-1] + z[i] * s_ if i else z[0] * s_
            s_ar.append(score((a - a.mean()) / a.std(), X, w, tp, mask,
                              idx in DET))
            ph = rng.uniform(0, 2*np.pi, len(mag))
            b = fft.irfft(mag * np.exp(1j * ph), n=len(tp))
            s_pr.append(score((b - b.mean()) / b.std(), X, w, tp, mask,
                              idx in DET))
        rec[f"n{nmax}"] = {
            "real": round(real, 3),
            "ar1_mean": round(float(np.mean(s_ar)), 3),
            "ar1_std": round(float(np.std(s_ar)), 3),
            "ar1_max": round(float(np.max(s_ar)), 3),
            "pr_mean": round(float(np.mean(s_pr)), 3),
            "pr_std": round(float(np.std(s_pr)), 3),
            "pr_max": round(float(np.max(s_pr)), 3),
            "z_ar1": round((real - np.mean(s_ar)) / max(np.std(s_ar), 1e-3), 1),
            "z_pr": round((real - np.mean(s_pr)) / max(np.std(s_pr), 1e-3), 1),
        }
        print(f"{idx:16s} nmax={nmax} real={real:.3f}  AR1 {np.mean(s_ar):.3f}"
              f"+-{np.std(s_ar):.3f} (z={rec[f'n{nmax}']['z_ar1']:+.1f})  "
              f"PhaseRand {np.mean(s_pr):.3f}+-{np.std(s_pr):.3f} "
              f"(z={rec[f'n{nmax}']['z_pr']:+.1f})")
    out[idx] = rec

json.dump(out, open(f"{HERE}/supplemental_2026_09/figures/red_noise_floor.json", "w"), indent=1)

# ---- forest plot
fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.5), sharey=True)
for ax, nmax in zip(axes, (3, 6)):
    ys = np.arange(len(IDX))
    reals = [out[i][f"n{nmax}"]["real"] for i in IDX]
    arm = [out[i][f"n{nmax}"]["ar1_mean"] for i in IDX]
    ars = [out[i][f"n{nmax}"]["ar1_std"] for i in IDX]
    prm = [out[i][f"n{nmax}"]["pr_mean"] for i in IDX]
    prs = [out[i][f"n{nmax}"]["pr_std"] for i in IDX]
    ax.errorbar(arm, ys, xerr=ars, fmt="none", ecolor="0.55", elinewidth=1.0,
                capsize=2, label="AR1(rho-matched) ±1σ")
    ax.errorbar(prm, ys, xerr=prs, fmt="none", ecolor="tab:blue",
                elinewidth=1.0, capsize=2, label="phase-random ±1σ")
    ax.scatter(reals, ys, color="crimson", zorder=3, s=30, label="real series")
    ax.axvline(0.7, color="0.8", lw=0.8)
    ax.set_yticks(ys); ax.set_yticklabels(IDX, fontsize=8.5)
    ax.set_title(f"local-winding fit r, harmonics n≤{nmax}")
    ax.set_xlabel("detrended r (r_var)")
axes[0].invert_yaxis(); axes[0].legend(fontsize=8, loc="lower right")
axes[1].invert_yaxis()
fig.suptitle("RED-NOISE FLOOR: does the one-dial fit beat smooth noise on the "
             "same design?  (prompted by pdo_iaaft_detuned_surrogate fitting "
             "ABOVE real pdo)", y=1.02)
fig.tight_layout()
fig.savefig(f"{HERE}/milestone_2026_09/figures/red_noise_floor.png",
            dpi=130, bbox_inches="tight")
print("chart: milestone_2026_09/figures/red_noise_floor.png")
