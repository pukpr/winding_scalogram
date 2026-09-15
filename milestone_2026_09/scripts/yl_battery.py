#!/usr/bin/env python3
"""Battery: shared-yl dial r(yl) for ALL indices with an lt.exe.p
(coarse grid 0.002 days), print per-index peak + value at 365.2463,
save JSON. Chart: heat-strip of r vs yl vs index + joint mean."""
import os as _os
_R = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
import sys, json, glob, os, time
import numpy as np
sys.path.insert(0, _os.path.dirname(__file__))
sys.path.insert(0, _R)
from joint_capture6 import ROOT, GEN, load_index, manifold, local_fit

SKIP = ("k3_", "pdo_iaaft", "111", "88", "kap")
names = []
for d in sorted(os.listdir(ROOT)):
    if any(s in d for s in SKIP):
        continue
    if os.path.exists(f"{ROOT}/{d}/lt.exe.p") and \
       os.path.exists(f"{ROOT}/{d}/lte_results.csv"):
        try:
            p, ts, s = load_index(d)
            if len(ts) > 1000:
                names.append(d)
        except Exception:
            pass
print(f"battery: {len(names)} indices: {' '.join(names)}", flush=True)

t0g = max(load_index(i)[1][0] for i in names)
t1g = min(load_index(i)[1][-1] for i in names)
tp = np.arange(round(t0g * 12) / 12, round(t1g * 12) / 12, 1 / 12)
yls = np.arange(365.240, 365.2601, 0.002)
out = {}
t0 = time.time()
for i in names:
    p, ts, series = load_index(i)
    Ms = sorted({round(abs(m), 4) for m in p["ltep"] if 0.002 < abs(m) < 10})
    x = np.interp(tp, ts, series); x = (x - x.mean()) / x.std()
    rs = []
    for yl in yls:
        F = manifold(p, yl, tp)
        y = local_fit(F, tp, x, 15.0, Ms)
        rs.append(np.corrcoef(x, y)[0, 1])
    rs = np.array(rs)
    k = int(np.argmax(rs))
    r_pro = rs[np.argmin(abs(yls - 365.2463))]
    out[i] = {"rs": rs.tolist(), "peak_r": float(rs[k]),
              "peak_yl": float(yls[k]), "r_at_prod": float(r_pro)}
    print(f"{i:12s} n_M={len(Ms)} peak {rs[k]:+.3f}@{yls[k]:.4f} "
          f"| at-prod {r_pro:+.3f}  [{time.time()-t0:.0f}s]", flush=True)
json.dump({"yls": yls.tolist(), "res": out}, open(f"{GEN}/../data/yl_battery.json", "w"))
arr = np.array([out[i]["r_at_prod"] for i in names])
print(f"AT yl=365.2463: mean {arr.mean():.3f}  n>=0.7: {(arr>=0.7).sum()}/{len(arr)}")
print("peaks at prod+-0.001:",
      sum(abs(out[i]['peak_yl']-365.2463)<0.001 for i in names), "/", len(names))
