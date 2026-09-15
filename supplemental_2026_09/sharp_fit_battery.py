#!/usr/bin/env python3
"""SHARPNESS-LADDER FIT BATTERY.  For each shipped index design
(pdo, amo, baltic, nino4, iode), fit 8 fresh realizations of each
ladder family (flat-alpha0 IAAFT, sharp a1, sharp a2, AR1@rho_pdo)
and compare real r to the member floor.  Two readings per floor:
  flat  = 'low-freq power alone' null (same spectrum as target)
  sharp = 'texture must be real' null (no low-freq gift)
"""
import json
import sys
import numpy as np

sys.path.insert(0, "/home/paul/eval/winding_scalogram")
ROOT = "/home/paul/eval/winding_scalogram"
SRC = open(f"{ROOT}/supplemental_2026_09/supplemental2.py").read()
exec(SRC.split("CFG = {")[0])
import sharp_surrogates as SS     # builds ladder members from real pdo

DETREND = {"iode", "baltic"}
DESIGNS = {}
for _i in ("pdo", "amo", "baltic", "nino4", "iode"):
    _p = json.load(open(f"{ROOT}/{_i}/lt.exe.p"))
    DESIGNS[_i] = sorted({round(abs(m), 4) for m in _p["ltep"]
                          if 0.002 < abs(m) < 10})

def fit_r(F, tp, x, Ms, nmax, sig=10.0):
    mask = np.ones(len(tp), bool)
    y = local_fit(F, tp, x, sig, Ms, nmax=nmax, mask=mask)
    xd = detrend_m(x, tp, mask) if fit_r.detrend else x
    yd = detrend_m(y, tp, mask) if fit_r.detrend else y
    return float(np.corrcoef(xd[mask], yd[mask])[0, 1])

def stats(v):
    return (np.corrcoef(v[:-1], v[1:])[0, 1],
            float(np.var(np.diff(v, 2)) / np.var(v)))

print("building ladder families (8 seeds each)...")
fams = {}
for alpha, name in ((0.0, "flat"), (1.0, "a1"), (2.0, "a2")):
    tilt = SS.tilt(alpha)
    fams[name] = [SS.iaaft_pass(100 + i, tilt) for i in range(8)]
fams["ar1"] = [SS.ar1(0.9668, 200 + i) for i in range(8)]
for k, vs in fams.items():
    r1 = [stats(v)[0] for v in vs]
    cv = [stats(v)[1] for v in vs]
    print(f"  {k:5s} rho1 {np.mean(r1):.4f}+-{np.std(r1):.4f}  "
          f"curvature {np.mean(cv):7.3f}")

res = {}
for idx, Ms in DESIGNS.items():
    c = np.loadtxt(f"{ROOT}/{idx}/lte_results.csv", delimiter=",")
    tp = month_grid(c[:, 0])
    x = np.interp(tp, c[:, 0], c[:, 2])
    x = (x - x.mean()) / x.std()
    p = json.load(open(f"{ROOT}/{idx}/lt.exe.p"))
    F = manifold(p, YL, tp)
    fit_r.detrend = idx in DETREND
    r1r, cvr = stats(x)
    row = {"real_r": fit_r(F, tp, x, Ms, 3), "rho1": float(r1r),
           "curvature": float(cvr)}
    row["real_r6"] = fit_r(F, tp, x, Ms, 6)
    print(f"\n{idx}: real r(n<=3)={row['real_r']:.3f} "
          f"r(n<=6)={row['real_r6']:.3f}  rho1={r1r:.4f} "
          f"curv={cvr:.3f}")
    for fam, vs in fams.items():
        vs2 = [np.interp(tp, SS.t, v) for v in vs]   # ladder -> this grid
        rr = [fit_r(F, tp, v, Ms, 3) for v in vs2]
        rr6 = [fit_r(F, tp, v, Ms, 6) for v in vs2]
        m, s = float(np.mean(rr)), float(np.std(rr))
        m6, s6 = float(np.mean(rr6)), float(np.std(rr6))
        z = (row["real_r"] - m) / max(s, 1e-6)
        z6 = (row["real_r6"] - m6) / max(s6, 1e-6)
        row[fam] = {"mean": m, "std": s, "z": z,
                    "mean6": m6, "std6": s6, "z6": z6,
                    "curv_mean": float(np.mean([stats(v)[1] for v in vs2]))}
        print(f"  {fam:5s} curv={row[fam]['curv_mean']:7.3f}  "
              f"n<=3 floor={m:.3f}+-{s:.3f} z={z:+5.1f}   "
              f"n<=6 floor={m6:.3f}+-{s6:.3f} z={z6:+5.1f}")
    res[idx] = row
json.dump(res, open(f"{ROOT}/supplemental_2026_09/figures/"
                    "sharp_battery.json", "w"), indent=1)
print("\nsaved figures/sharp_battery.json")
