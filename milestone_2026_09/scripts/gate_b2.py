#!/usr/bin/env python3
"""GATE B2 — AMO capture on F_col4 with the PRODUCTION regression basis:
   x ~ level + k0*F + [sin,cos](2pi M F) + annual+semiannual (calendar)
   + trend + accel            (NonLin=1, third=0 per amo resp)
M=0.0134 (lowest winding). Compare against:
  - same basis WITHOUT the winding columns (what's left is trend+annual)
  - same basis with F replaced by matched-slope null clock (cumsum of
    col4-rate-matched random walk) [K5-style]
  - 12 phase-randomized surrogates of AMO -> empirical p-value.
Also report the production col2 CC as the 0.70+ reference.
"""
import os as _os
_R = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
import math
import sys

import numpy as np

sys.path.insert(0, _R)
from wavelet_scalogram import load_columns  # noqa: E402

year, dt, model, obs, forcing = load_columns("amo")
x = (obs - obs.mean()) / obs.std()
F = forcing


def basis(Fc, M, wind=True, cal=True, trnd=True):
    cols = [np.ones_like(Fc), Fc]
    if wind:
        cols += [np.sin(2*np.pi*M*Fc), np.cos(2*np.pi*M*Fc)]
    if cal:
        cols += [np.sin(2*np.pi*year), np.cos(2*np.pi*year),
                 np.sin(4*np.pi*year), np.cos(4*np.pi*year)]
    if trnd:
        cols += [year, (year - year[0])**2]
    return np.column_stack(cols)


def fit_cc(A, y, yy=None):
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    yh = A @ beta
    return float(np.corrcoef(yh, y)[0, 1]), beta, yh


M = 0.0134
full = basis(F, M)
cc_full, _, yh = fit_cc(full, x)
cc_nowind, _, _ = fit_cc(basis(F, M, wind=False), x)
cc_nocal, _, _ = fit_cc(basis(F, M, cal=False), x)
print(f"production-basis capture M={M}: CC={cc_full:+.3f}")
print(f"  without winding cols:      CC={cc_nowind:+.3f}")
print(f"  without calendar harmonics: CC={cc_nocal:+.3f}")
print(f"  (production col2 reference: {float(np.corrcoef(model, x)[0,1]):+.3f})")

# matched-slope null clock: random walk with col4's step-size distribution
rng = np.random.default_rng(3)
dFs = np.diff(F)
nulls = []
for k in range(12):
    z = rng.permutation(dFs)
    Fn = np.concatenate([[F[0]], F[0] + np.cumsum(z)])
    nulls.append(abs(fit_cc(basis(Fn, M), x)[0]))
print(f"phase-shuffled-F (same increments, random order) |CC|: "
      f"median {np.median(nulls):.3f} max {np.max(nulls):.3f}")

# surrogate AMO: preserve spectrum+power, scramble phase
def phaserand(v):
    f = np.fft.rfft(v)
    return np.fft.irfft(np.abs(f) * np.exp(1j*rng.uniform(0, 2*np.pi, len(f))),
                        n=len(v))


sur = [abs(fit_cc(full, phaserand(x))[0]) for _ in range(24)]
sur.sort()
rank = 1 + sum(1 for s in sur if s >= abs(cc_full))
print(f"phase-rand AMO |CC| floor: median {sur[len(sur)//2]:.3f} "
      f"95% {sur[int(0.95*len(sur))]:.3f}  -> p ~ {rank/25:.3f}")
# calendar-only winding: sine at same APPARENT period (autonomy control)
rate = np.mean(np.abs(dFs))
P = 1.0 / (M * rate)
cal_only = (year - year[0]) / P
Acal = np.column_stack([np.ones_like(F), np.cos(2*np.pi*cal_only),
                        np.sin(2*np.pi*cal_only),
                        np.sin(2*np.pi*year), np.cos(2*np.pi*year),
                        np.sin(4*np.pi*year), np.cos(4*np.pi*year),
                        year, (year - year[0])**2])
cc_cal, _, _ = fit_cc(Acal, x)
print(f"calendar-sine at apparent P={P:.1f}yr (no winding): CC={cc_cal:+.3f}")
