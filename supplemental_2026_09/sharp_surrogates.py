#!/usr/bin/env python3
"""SHARPNESS LADDER: synthetic nulls whose fit-CC cannot be inflated by
low-frequency smoothness.  Recipe per member:
  1. amplitude spectrum from REAL monthly PDO, tilted: A(f) *= (f/f_ref)^alpha
     (alpha=0 -> old IAAFT-like flatness, alpha>0 -> sharper).
  2. preserve the REAL series' phase autocorrelation: new phases
     phi' = phi + (random uniform) * (1 - rho2_target^member) ... or fully
     random for alpha>0 members (they must not fake the tooth lock).
  3. amplitude-match: rank-transform samples to the target spectrum's
     marginal (mimic gaussian, but preserve sample order by quantile),
     then one IAAFT pass (FFT amplitude swap + rank) so the FINAL spectrum
     is right and the marginal is right.
  4. optionally rescale the low-freq part: after synthesis subtract
     beta * lowpass(x, 10yr) and renormalise variance -> kills CC floor.
Members on the ladder (all 1706 pts, 1880.0-2022.08 monthly):
  flat_alpha0   : alpha=0, random phase (old surrogate's replacement)
  sharp_a1      : alpha=+1 linear emphasis
  sharp_a2      : alpha=+2
  sharp_a2_lp   : alpha=+2 AND low-freq energy halved (beta=0.5)
  ar1_rho_pdo   : simple AR(1) with rho matched to REAL PDO (0.967)
  ar1_rho95     : AR(1) rho=0.95 (sharper white-ish control)
"""
import json
import numpy as np

rng_global = np.random.default_rng(20260915)
c = np.loadtxt("/home/paul/eval/winding_scalogram/pdo/lte_results.csv",
               delimiter=",")
t = c[:, 0]
x = (c[:, 2] - c[:, 2].mean()) / c[:, 2].std()
N = len(x)
freqs = np.fft.rfftfreq(N, d=1.0 / 12)        # cycles per year
X = np.fft.rfft(x)
A0 = np.abs(X)
f_ref = 1.0 / 5.0                              # 5-yr reference period
f_lo = freqs > 0

def tilt(alpha):
    w = np.ones_like(A0)
    w[f_lo] = (freqs[f_lo] / f_ref) ** alpha
    return A0 * w

def iaaft_pass(phase_seed, target_spec, n_iter=20):
    """Iterative amplitude-adjusted FT surrogate (spectral matched,
    marginal matched to the ORIGINAL gaussian sample set)."""
    rng = np.random.default_rng(phase_seed)
    target_vals = np.sort(x)                   # keep real pdo marginal shape
    z = rng.standard_normal(N)
    for _ in range(n_iter):
        Z = np.fft.rfft(z)
        Z = target_spec * np.exp(1j * np.angle(Z))
        zf = np.fft.irfft(Z, n=N)
        order = np.argsort(np.argsort(zf))     # ranks
        z = target_vals[order]
    return (z - z.mean()) / z.std()

def ar1(rho, seed):
    rng = np.random.default_rng(seed)
    e = rng.standard_normal(N)
    y = np.zeros(N)
    a = np.sqrt(1 - rho ** 2)
    for i in range(1, N):
        y[i] = rho * y[i - 1] + a * e[i]
    return (y - y.mean()) / y.std()

def lowpass(v, cut_years=10.0):
    V = np.fft.rfft(v)
    V[freqs > 1.0 / cut_years] = 0
    return np.fft.irfft(V, n=N)

def shrink_low(v, beta):
    """Remove a fraction beta of the <0.1 cyc/yr (decadal+) variance,
    renormalize to unit variance.  Applied BEFORE any z-scoring so the
    curvature/rho1 stats actually move."""
    lp = lowpass(v)
    out = lp * (1 - beta) + (v - lp)
    return (out - out.mean()) / out.std()

members = {}
members["flat_alpha0"]  = iaaft_pass(11, tilt(0.0))
members["sharp_a1"]     = iaaft_pass(12, tilt(1.0))
members["sharp_a2"]     = iaaft_pass(13, tilt(2.0))
members["sharp_a2_lp"]  = shrink_low(members["sharp_a2"], 0.5)
members["ar1_rho_pdo"]  = ar1(0.9668, 21)
members["ar1_rho95"]    = ar1(0.95, 22)

def stats(v):
    return dict(rho1=float(np.corrcoef(v[:-1], v[1:])[0, 1]),
                rho2=float(np.corrcoef(v[:-2], v[2:])[0, 1]),
                curvature=float(np.var(np.diff(v, 2)) / np.var(v)))

print(f"{'member':14s} {'rho1':>7s} {'rho2':>7s} {'curvature':>9s}")
print(f"{'REAL pdo':14s} {stats(x)['rho1']:7.4f} {stats(x)['rho2']:7.4f} "
      f"{stats(x)['curvature']:9.3f}")
for k, v in members.items():
    s = stats(v)
    print(f"{k:14s} {s['rho1']:7.4f} {s['rho2']:7.4f} {s['curvature']:9.3f}")

out = "/home/paul/eval/winding_scalogram/supplemental_2026_09/"
for k, v in members.items():
    np.savetxt(f"{out}/sharp_{k}.dat",
               np.vstack([t, v]).T, fmt="%.6f")
json.dump({k: stats(v) for k, v in members.items()},
          open(f"{out}/figures/sharp_stats.json", "w"), indent=1)
print("wrote sharp_<member>.dat files")
