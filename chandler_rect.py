"""Chandler wobble as a forced-alias order line (Fyfe-style order tracking):
the rectified draconic torque 2q = 27.2122/2 = 13.60611 d sampled on the
annual clock gives frac(2*13.4221)=0.8443 c/yr -> 432.6 d, the CW period.
Winding teeth against nuisance-cleaned IERS pole x, with the QBO sibling
tooth 0.422 and the wrong-clock control 0.737 (Mf alias)."""
import json, sys
import numpy as np
sys.path.insert(0, "/home/paul/eval/winding_scalogram")
from lte_forward import tide_sum, iir
from wavelet_scalogram import standardize
from winding_rank import continuity
from winding_scalogram import winding_transform

YL, P_N = 365.2463, 27.21222
P_2N = P_N / 2.0
a1, a2 = YL / P_N % 1.0, YL / P_2N % 1.0
print(f"frac(q)={a1:.5f}->{YL/a1:.0f}d (QBO)   frac(2q)={a2:.5f}->{YL/a2:.2f}d (CW pred)")

def monthly_pole(fn, m0, m1):
    raw = np.loadtxt(fn, comments="#", usecols=(0, 1, 2, 5, 6))
    yrs = raw[:, 0] + (raw[:, 1] - 1) / 12 + (raw[:, 2] - 0.5) / 365.2422
    x = raw[:, 3]
    g = ~np.isnan(x); yrs, x = yrs[g], x[g]
    s = (yrs >= m0) & (yrs < m1); yrs, x = yrs[s], x[s]
    edges = np.arange(yrs[0], yrs[-1], 1 / 12.)
    idx = np.clip(np.searchsorted(edges, yrs) - 1, 0, len(edges) - 2)
    tg = (edges[:-1] + edges[1:]) / 2
    xv = np.array([x[idx == k].mean() if np.any(idx == k) else np.nan
                   for k in range(len(tg))])
    g = ~np.isnan(xv)
    return tg[g], xv[g]

def annual_clean(t, v, freqs=(1.0, 2.0)):
    y = t - t.mean()
    A = [np.ones_like(t), y, y**2]
    for f in freqs:
        A += [np.cos(2*np.pi*f*(t - t[0])), np.sin(2*np.pi*f*(t - t[0]))]
    A = np.stack(A, 1)
    b, *_ = np.linalg.lstsq(A, v, rcond=None)
    r = v - A @ b
    return r, float(np.std(r) / np.std(v))

p = json.load(open("/home/paul/eval/winding_scalogram/qbo30/lt.exe.p"))
L = np.array(p["lpap"]); per, amp = L[:, 0], L[:, 1:3]
B = {k: float(p[k]) for k in ("delA", "delB", "asym", "ma", "mp", "init", "shfT")}
mN = np.abs(per - P_N) < 0.001
mNfam = np.logical_or(np.logical_and(per >= 26.9, per <= 27.7),
                      np.logical_and(per >= 13.5, per <= 13.9))

def manifold(tt, subset, extra_lines=(), comb=True):
    idx = np.where(subset)[0]
    pp, aa = list(per[idx]), list(amp[idx])
    for P_, A_ in extra_lines:
        pp.append(P_); aa.append([A_, 0.0])
    pp = np.array(pp); aa = np.array(aa)
    tf = tide_sum(tt, aa, pp, YL, integ=B["shfT"])
    if comb:  # production annual sampler: delA at DPOS only (off-grid slots pass as 1)
        mo = np.rint((tt - tt[0]) * 12).astype(int) % 12
        dp = int(round(B["delB"] * 12)) % 12
        tf = tf * np.where(mo == dp, B["delA"], 1.0)
    f = iir(tf, lag_a=1.0 - B["ma"], lag_c=B["mp"], init=B["init"],
            start_date=tt[0], dates=tt)
    return f - f.mean()

# manifold line-content verification on a 178-yr grid
t0 = np.arange(1846.0, 2024.9, 1/12.)
for tag, kw in [("N only", dict(subset=mN)),
                ("N+N2", dict(subset=mN, extra_lines=[(P_2N, -3.319)])),
                ("Nfam+N2", dict(subset=mNfam, extra_lines=[(P_2N, -3.319)]))]:
    F = manifold(t0, **kw)
    w = np.hanning(len(F)); S = np.abs(np.fft.rfft(F * w)); fr = np.fft.rfftfreq(len(F), 1/12)
    a = lambda f0: S[int(np.argmin(abs(fr - f0)))] / S[fr > 0.05].max() * 100
    print(f"{tag:8s} manifold lines: 0.422={a(0.4221):5.1f}%  0.844={a(0.8443):5.1f}%  0.737={a(0.7368):5.1f}%")

def ar1_floor(tt_, F, mg, t0g, rho, n=25):
    rng = np.random.default_rng(2); acc = np.zeros((len(mg), len(t0g)))
    for _ in range(n):
        e = rng.standard_normal(len(tt_)); s = np.empty(len(tt_)); s[0] = e[0]
        for i in range(1, len(tt_)): s[i] = rho*s[i-1] + np.sqrt(1 - rho**2)*e[i]
        G, _, _ = winding_transform(tt_, standardize(s), F, mg, t0g, 10.0)
        acc += np.abs(G)**2
    return acc / n

def tooth(tag, tt_, F, x_, rho):
    mg = np.arange(0.0, 2.005, 0.01)
    t0g = np.arange(tt_[0] + 5, tt_[-1] - 5 + 1e-9, 2.5)
    G, _, _ = winding_transform(tt_, standardize(x_), F, mg, t0g, 10.0)
    lp = np.log2(np.maximum(np.abs(G)**2 / ar1_floor(tt_, F, mg, t0g, rho), 1e-9))
    out = {}
    for q, lab in [(a1, "0.422-QBO"), (a2, "0.844-CW"), (0.7368, "0.737-Mfctl")]:
        i = int(np.argmin(abs(mg - q)))
        out[lab] = (round(float(lp.mean(axis=1)[i]), 2),
                    round(float(continuity(lp, mg, q)), 2))
    print(f"{tag:32s} " + "  ".join(f"{k}:{v[0]:+.1f}b/{v[1]:.2f}c" for k, v in out.items()))
    return out

res = {}
for fn, lab, m0 in [("/home/paul/campaign/blind/AG1/eopc04_20.1962-now", "c04", 1962.0),
                    ("/home/paul/campaign/blind/AG1/eopc01.1846-now", "c01", 1846.0)]:
    t, x = monthly_pole(fn, m0, 2025.0)
    xc, keep = annual_clean(t, x)
    rho = float(np.corrcoef(xc[1:], xc[:-1])[0, 1])
    print(f"\n{lab}: n={len(xc)} rho={rho:.3f} annual+semiannual removed ({100*(1-keep):.0f}% of var)")
    res[lab] = {}
    res[lab]["N2"] = tooth(f"{lab} vs N+N2", t, manifold(t, mN, [(P_2N, -3.319)]), xc, rho)
    res[lab]["NfN2"] = tooth(f"{lab} vs Nfam+N2", t, manifold(t, mNfam, [(P_2N, -3.319)]), xc, rho)
    res[lab]["Nonly"] = tooth(f"{lab} vs N-only", t, manifold(t, mN), xc, rho)
json.dump(res, open("/home/paul/eval/winding_scalogram/chandler_rect_ridges.json", "w"))
print("\nsaved chandler_rect_ridges.json")
