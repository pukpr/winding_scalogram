#!/usr/bin/env python3
"""GATE B — lowest winding number sine modulation on F_col4 vs AMO.

model: x_hat = c + a*cos(2pi M F) + b*sin(2pi M F)   (3 params; M fixed)
reported for M = 0.0134 (AMO's lowest ridge) and 0.2075 (backbone), on
F_col4 / F_v8 / F_v3, full record and both halves.
CONTROLS (decide whether the capture is about the manifold at all):
 (1) calendar sine: same 3-param fit with F -> (year-1880)/P, P set to the
     apparent period of M*F (mean rate); CC should be ~equal per the
     clock-robust finding -> then "capture" = AMO's own oscillation.
 (2) production model col2 CC for reference (full 9+ param fit).
"""
import os as _os
_R = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
import sys
import numpy as np

REPO = _R
GEN = _R + "/milestone_2026_09/data"
sys.path.insert(0, REPO)
from wavelet_scalogram import load_columns  # noqa: E402


def load_F(path, year):
    a = np.loadtxt(path, delimiter=",", skiprows=1)
    return np.interp(year, a[:, 0], a[:, 1])


def sine_cc(clock, x, mask=None):
    A = np.column_stack([np.ones_like(clock), np.cos(2*np.pi*clock),
                         np.sin(2*np.pi*clock)])
    if mask is None:
        mask = np.ones(len(clock), bool)
    beta, *_ = np.linalg.lstsq(A[mask], x[mask], rcond=None)
    y = A @ beta
    return float(np.corrcoef(y, x)[0, 1]), float(np.corrcoef(y[mask], x[mask])[0, 1])


year, dt, model, obs, forcing = load_columns("amo")
x = (obs - obs.mean()) / obs.std()
Fs = {"F_col4": forcing,
      "F_v8": load_F(f"{GEN}/F_scratch_v8.csv", year),
      "F_v3": load_F(f"{GEN}/F_strict_v3.csv", year)}
tr = year <= 1950

for M in (0.0134, 0.2075):
    for name, F in Fs.items():
        rate = np.mean(np.abs(np.gradient(F, year)))   # cycles per year avg
        P = 1.0 / (M * rate)
        clock = M * (F - F.mean())
        cc_f, _ = sine_cc(clock, x)
        cc_a, _ = sine_cc(clock, x, tr)
        cc_b, _ = sine_cc(clock, x, ~tr)
        cal = (year - year[0]) / P
        cc_cal, _ = sine_cc(cal, x)
        print(f"M={M:.4f} {name:>7s}: full CC={cc_f:+.3f}  "
              f"train1880-50={cc_a:+.3f} train1950-23={cc_b:+.3f}   "
              f"calendar-sine(P={P:.1f}yr)={cc_cal:+.3f}")

# reference: production col2 vs obs, full and halves
def ccv(v, m=None):
    if m is None:
        m = np.ones(len(year), bool)
    return float(np.corrcoef(v[m], x[m])[0, 1])
print(f"\nref production model col2 vs obs: full {ccv(model):+.3f} "
      f"A {ccv(model, tr):+.3f} B {ccv(model, ~tr):+.3f}")
print("ref corr(col4, obs) full (autonomy sanity): "
      f"{float(np.corrcoef(forcing, x)[0,1]):+.3f}")
