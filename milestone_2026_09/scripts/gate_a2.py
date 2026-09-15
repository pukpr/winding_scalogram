#!/usr/bin/env python3
"""GATE A2 — fair recovery scoring: calibrate 84 tide coeffs vs dlod3
LEVEL 1962-2019 only; score corr(F_hat, col4) (a) IN-WINDOW 1962-2019
(the only region with real daily LOD data) and (b) full record.
Grid: comb phase/months x asym x FM (eS,eC) x k spot. Report best."""
import os as _os
_R = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
import json
import math
import sys

import numpy as np

sys.path.insert(0, _R)
from lte_forward import YEAR_IN_DAYS, impulse_delta, iir, bessel

ROOT = _R
p = json.load(open(ROOT + "/amo/lt.exe.p"))
per = np.abs(np.array(p["lpap"], float)[:, 0])
B0 = {k: float(p[k]) for k in ("offs", "bg", "impA", "impB", "delA",
                               "delB", "asym", "ma", "mp", "init", "shfT")}
prov = np.loadtxt(ROOT + "/amo/lte_results.csv", delimiter=",")
tp, col4 = prov[:, 0], prov[:, 3]
k_prod = p["ltep"][1]
dl = np.loadtxt(ROOT + "/dlod3.dat")
tlo, ylo = dl[:, 0], dl[:, 1]
lv = np.concatenate([[0.0], np.cumsum(np.diff(tlo) * 0.5 * (ylo[1:] + ylo[:-1]))])
target = np.interp(tp, tlo, lv)
tmask = (tp > 1962) & (tp < 2019)

lines = []
for j in range(len(per)):
    f = YEAR_IN_DAYS / per[j]
    lines.append(np.cos(2 * math.pi * f * tp))
    lines.append(np.sin(2 * math.pi * f * tp))
TIN = np.column_stack(lines)


def iir_part(comb):
    out = np.empty_like(TIN)
    for j in range(TIN.shape[1]):
        out[:, j] = iir(TIN[:, j] * comb, lag_a=1.0 - B0["ma"],
                        lag_c=B0["mp"], init=B0["init"], start_date=1880.0,
                        dates=tp)
    return out


best_win = (0.0, None)
best_full = (0.0, None)
trials = 0
for delB in np.arange(0.0, 12.0, 0.5):
    for asym in (0.0, 3.122, 6.244):
        for delA in (-4.2255, -2.0, -6.5):      # nonzero only: delA=0 kills comb
            comb = impulse_delta(tp, delA, delB, asym, 12)
            if np.abs(comb).max() < 1e-9:
                continue
            D = iir_part(comb)
            A = np.column_stack([D, tp - tp.mean(), np.ones_like(tp)])
            coef, *_ = np.linalg.lstsq(A[tmask], target[tmask], rcond=None)
            R = A @ coef
            for eS in (-3.2648, 0.0, -1.5, -5.0):
                for eC in (-5.0863, 0.0, -2.5):
                    for kk in (k_prod, 0.2075, 0.0):
                        F = bessel(R, eS, eC, kk, B0["offs"], B0["bg"])
                        s_w = abs(float(np.corrcoef(F[tmask], col4[tmask])[0, 1]))
                        s_f = abs(float(np.corrcoef(F, col4)[0, 1]))
                        trials += 1
                        if s_w > best_win[0]:
                            best_win = (s_w, dict(delB=float(delB), asym=float(asym),
                                                  delA=delA, eS=eS, eC=eC, k=kk))
                        if s_f > best_full[0]:
                            best_full = (s_f, dict(delB=float(delB), asym=float(asym),
                                                   delA=delA, eS=eS, eC=eC, k=kk))
print(f"trials={trials}")
print(f"BEST in-window  |corr(F_hat,col4)| 1962-2019 = {best_win[0]:.4f}  {best_win[1]}")
print(f"BEST full-record|corr(F_hat,col4)| 1880-2023 = {best_full[0]:.4f}  {best_full[1]}")
