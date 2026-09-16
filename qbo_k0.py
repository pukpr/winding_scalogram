#!/usr/bin/env python3
"""QBO30 as the wavenumber-0 category: draconic/ecliptic manifold (27.2122-d
factors x annual impulse comb), no dLOD calibration, ridge-ranked.

Physics note: the draconic month is the lunar DECLINATION cycle -- a purely
zonal (k=0) modulation.  At monthly sampling the 27.2122-d tide aliases
against the calendar: 365.2463/27.2122 = 13.4223 -> fractional 0.4223/yr ->
a 2.368-yr beat, strikingly close to the observed 2.2-2.8-yr QBO band.
The annual comb (delA at tick dpos, asym at dpos+6) re-impulses that phase
walk, exactly as in Calc_Forcing but with ONLY the ecliptic subset.

Variants (tide sum -> comb -> IIR, production qbo30 knobs, yl=365.2463):
  N        : {27.2122} alone
  Nfam     : [26.9,27.7] plus [13.5,13.9] d  (N + D/Mm sidebands + fortnightly)
  NfamBeat : Nfam plus long nodal beats
  nocomb   : Nfam without the impulse comb (attribution control)
  full     : all 42 production constituents (control)
Ranking: winding_rank machinery, AR1 floor at rho=0.944 (qbo30 own).
"""
import json
import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, ".")
from lte_forward import tide_sum, impulse_delta, iir
from wavelet_scalogram import standardize
from winding_rank import find_ridges, continuity
from winding_scalogram import winding_transform

YL = 365.2463
ROOT = Path(".")
OUT = {}

p = json.load(open(ROOT / "qbo30/lt.exe.p"))
L = np.array(p["lpap"])
per, ap2 = L[:, 0], L[:, 1:3]
t = np.loadtxt(ROOT / "qbo30/qbo30.dat")[:, 0]
x = np.loadtxt(ROOT / "qbo30/qbo30.dat")[:, 1]
B = {k: float(p[k]) for k in ("delA", "delB", "asym", "ma", "mp", "init", "shfT")}

def mask_rng(lo, hi):
    return np.logical_and(per >= lo, per <= hi)

mN = np.abs(per - 27.21222) < 0.001
mNfam = np.logical_or(mask_rng(26.9, 27.7), mask_rng(13.5, 13.9))
mbeat = np.logical_or.reduce([mask_rng(2100, 2250), mask_rng(3200, 3450),
                              mask_rng(6100, 6900), mask_rng(1600, 1620),
                              mask_rng(1305, 1306)])
mfull = np.ones(len(per), bool)

def manifold(subset, comb=True):
    idx = np.where(subset)[0]
    tf = tide_sum(t, ap2[idx], per[idx], YL, integ=B["shfT"])
    raw = tf * impulse_delta(t, B["delA"], B["delB"], B["asym"], 12) if comb else tf
    f = iir(raw, lag_a=1.0 - B["ma"], lag_c=B["mp"], init=B["init"],
            start_date=t[0], dates=t)
    return f - f.mean()

def ar1_floor(t, forcing, m_grid, t0_grid, sigma, n_reps=40, rho=0.944):
    rng = np.random.default_rng(1)
    acc = np.zeros((len(m_grid), len(t0_grid)))
    for _ in range(n_reps):
        e = rng.standard_normal(len(t))
        s = np.empty(len(t)); s[0] = e[0]
        for i in range(1, len(t)):
            s[i] = rho * s[i-1] + np.sqrt(1 - rho**2) * e[i]
        G, _, _ = winding_transform(t, standardize(s), forcing, m_grid, t0_grid, sigma)
        acc += np.abs(G) ** 2
    return acc / n_reps

def scan(label, f, sigma=10.0, t0_step=2.5, m_max=5.0, dm=0.01):
    m_grid = np.arange(0.0, m_max + dm / 2, dm)
    t0_grid = np.arange(t[0] + sigma / 2, t[-1] - sigma / 2 + 1e-9, t0_step)
    G, _, _ = winding_transform(t, standardize(x), f, m_grid, t0_grid, sigma)
    floor = ar1_floor(t, f, m_grid, t0_grid, sigma)
    lp = np.log2(np.maximum(np.abs(G) ** 2 / floor, 1e-9))
    prof = np.abs(G).mean(axis=1)
    rid = []
    for M, pk, fw in find_ridges(m_grid, prof, lp, 2.0, 0.12):
        rid.append({"M": round(M, 4), "bits": round(pk, 2), "fwhm": round(fw, 3),
                    "cont": round(continuity(lp, m_grid, M), 2)})
    rid.sort(key=lambda r: -r["bits"])
    OUT[label] = {"ridges": rid[:6], "std_F": round(float(f.std()), 2),
                  "range": [round(float(f.min()), 1), round(float(f.max()), 1)]}
    print("\n== %s ==  F std=%.1f ntides=%d" % (label, f.std(), int((f != 0).sum())))
    for r in rid:
        q = "PASS" if (r["fwhm"] <= 0.12 and r["cont"] >= 0.70) else "fail"
        print("   M=%6.3f  bits=%5.2f  fwhm=%5.3f  cont=%4.2f  %s"
              % (r["M"], r["bits"], r["fwhm"], r["cont"], q))
    return lp, m_grid

scan("N",       manifold(mN))
scan("Nfam",    manifold(mNfam))
scan("NfamBeat",manifold(np.logical_or(mNfam, mbeat)))
scan("nocomb",  manifold(mNfam, comb=False))
scan("full",    manifold(mfull))
fprod = np.loadtxt(ROOT / "qbo30/lte_results.csv", delimiter=",", skiprows=1, usecols=3)
scan("prod_col4", np.interp(t, t[:len(fprod)], fprod) - fprod.mean())

json.dump(OUT, open(ROOT / "qbo30_k0_ridges.json", "w"), indent=1)
np.save("/tmp/qbo_fam.npy", manifold(mNfam))
print("\nsaved qbo30_k0_ridges.json")
