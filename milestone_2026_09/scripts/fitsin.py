#!/usr/bin/env python3
"""FITSIN — sine-modulation fits of FROM-SCRATCH manifolds to climate indices.

Pipeline (campaign premise: manifold must not come from the Ada search):
  candidate F:  F_strict_v3 (Ray table, analytic level clock, zero tuning)
                F_scratch_v8 (Ray constituents re-estimated vs dlod3 rate
                              1962-2019, zero index data)   <- "calibrated"
                F_col4 (production, CONTROL ONLY - not a candidate)
  model:        x_hat(t) = trend(t) + sum_{n=1..N} a_n cos(2pi n M F) + b_n sin(...)
  M:            grid-searched per (index, F) on the TRAIN window only;
                ridge positions from the scalogram are used only as a
                reporting prior, never as a fit constraint.
  stats:        held-out CC (both half-record directions), param count,
                vs the K6 baseline (Fourier harmonics on calendar time
                with the SAME param count), and vs col4-control ceiling.

Usage:
  python3 fitsin.py smoke          # amo+pdo, fast grid
  python3 fitsin.py full           # all repo indices, fine grid
"""
import os as _os
_R = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
import sys
import numpy as np

REPO = _R
GEN = _R + "/milestone_2026_09/data"
sys.path.insert(0, REPO)
from wavelet_scalogram import load_columns  # noqa: E402  (repo copy)

BOUND = 1950.0
N_HARM = 4          # modulation order n=1..4
TREND_DEG = 2       # polynomial trend in calendar years

CANDIDATES = {
    "F_v3":  f"{GEN}/F_strict_v3.csv",
    "F_v8":  f"{GEN}/F_scratch_v8.csv",
    "F_col4": None,   # special: col 4 of the index's dlod_compare.csv
}


def load_F(path, year_target):
    a = np.loadtxt(path, delimiter=",", skiprows=1)
    return resample(a[:, 0], a[:, 1], year_target)


def resample(t_src, f_src, t_dst):
    return np.interp(t_dst, t_src, f_src)


def col4_F(idx, year):
    """Production manifold = col-4 forcing from the index's lte_results.csv
    (control only; same grid as load_columns output)."""
    try:
        y, dt, model, obs, forcing = load_columns(idx)
    except Exception:
        return None
    return np.interp(year, y, forcing)


def design(F, M, year):
    cols = [np.cos(2*np.pi*n*F) for n in range(1, N_HARM+1)] + \
           [np.sin(2*np.pi*n*F) for n in range(1, N_HARM+1)]
    tn = (year - year.mean()) / 100.0
    cols += [tn**d for d in range(TREND_DEG+1)]
    return np.column_stack(cols)


def lstsq_cc(A, y):
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    yhat = A @ beta
    if np.std(yhat) < 1e-12:
        return -2.0, beta
    return float(np.corrcoef(yhat, y)[0, 1]), beta


def fit_M_grid(year, x, F, train, m_grid):
    """Rank TRAIN-window CC over M grid. Returns list of (cc, M) sorted desc."""
    res = []
    yt = x[train]
    for M in m_grid:
        cc, _ = lstsq_cc(design(F, M, year)[train], yt)
        res.append((cc, float(M)))
    res.sort(reverse=True)
    return res


def fourier_baseline(year, x, train, m_grid, n_params_match):
    """K6 control: calendar-time harmonics, same param count, best subset
    of frequencies on TRAIN, then held-out CC."""
    # calendar freqs: 1/(1000yr) .. 1/(2yr)
    freqs = np.linspace(0.001, 0.5, 80)
    best = (-2.0, None)
    yt = x[train]
    tn = (year - year.mean()) / 100.0
    trend = np.column_stack([tn**d for d in range(TREND_DEG+1)])
    n_h = (n_params_match - trend.shape[1]) // 2
    for f0 in freqs:
        # single base freq + first (n_h-1) integer harmonics
        cols = []
        for k in range(1, n_h+1):
            w = 2*np.pi*f0*k
            cols += [np.cos(w*year), np.sin(w*year)]
        A = np.column_stack(cols + [trend])
        cc, _ = lstsq_cc(A[train], yt)
        if cc > best[0]:
            best = (cc, f0)
    # refit on train, score held-out
    f0 = best[1]
    cols = []
    for k in range(1, n_h+1):
        w = 2*np.pi*f0*k
        cols += [np.cos(w*year), np.sin(w*year)]
    A = np.column_stack(cols + [trend])
    _, beta = lstsq_cc(A[train], x[train])
    yhat = A @ beta
    hold = ~train
    return float(np.corrcoef(yhat[hold], x[hold])[0, 1])


F_rate_cache = {}


def run_index(idx, m_grid, verbose=True, dedup=0.05):
    year, dt, model, obs, forcing = load_columns(idx)
    x = obs
    x = (x - x.mean()) / x.std()
    tr1 = year <= BOUND
    out = []
    for name, path in CANDIDATES.items():
        F = col4_F(idx, year) if path is None else load_F(path, year)
        if F is None:
            continue
        F_rate_cache[year[0]] = np.gradient(F)
        npar = 2*N_HARM + TREND_DEG + 1
        row = {"index": idx, "F": name}
        for split, train in (("A1880>t1950", tr1), ("B1950>t2026", ~tr1)):
            hold = ~train
            ranked = fit_M_grid(year, x, F, train, m_grid)
            # top 5 distinct-ish M on train; fit beta TRAIN-only, score HOLD
            cands = []
            for cc_tr, M in ranked:
                if all(abs(M - m2) > 0.05 for _, _, m2 in cands):
                    A = design(F, M, year)
                    _, beta = lstsq_cc(A[train], x[train])
                    yhat = A @ beta
                    ch = float(np.corrcoef(yhat[hold], x[hold])[0, 1])
                    cands.append((cc_tr, ch, M))
                if len(cands) == 5:
                    break
            row[split] = [dict(M=round(M, 4), cc_train=round(ct, 3),
                               cc_hold=round(ch, 3))
                          for ct, ch, M in cands]
        out.append(row)
    if verbose:
        for r in out:
            for k, v in r.items():
                if k.startswith(("A", "B")) and isinstance(v, list):
                    s = "  ".join(f"M={d['M']:.3f}(tr{d['cc_train']:+.2f},"
                                  f"ho{d['cc_hold']:+.2f})" for d in v)
                    print(f"{r['index']:>10s} {r['F']:>7s} {k}  {s}")
    return out


INDICES_SMOKE = ["amo", "pdo"]


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "smoke"
    if mode == "smoke":
        coarse = np.concatenate([np.arange(0.002, 0.05, 0.002),
                                 np.arange(0.05, 1.0, 0.01)])
        for idx in INDICES_SMOKE:
            run_index(idx, coarse, dedup=0.05)
    else:
        import os
        idxs = [d for d in sorted(os.listdir(REPO))
                if os.path.isdir(f"{REPO}/{d}") and
                os.path.exists(f"{REPO}/{d}/{d}.dat")]
        print("indices:", idxs, flush=True)
        grid = np.concatenate([np.arange(0.004, 0.05, 0.004),
                               np.arange(0.05, 2.0, 0.005)])
        rows = []
        for idx in idxs:
            rows += run_index(idx, grid, dedup=0.015)
            print("done", idx, flush=True)
        import json
        with open(f"{GEN}/../data/fitsin_results.json", "w") as f:
            json.dump(rows, f, indent=1)
        print("wrote", f"{GEN}/fitsin_results.json")


if __name__ == "__main__":
    main()
