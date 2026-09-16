import json, sys
import numpy as np
sys.path.insert(0, "/home/paul/eval/winding_scalogram")
from lte_forward import tide_sum, impulse_delta, iir
from wavelet_scalogram import standardize
from winding_rank import rank_series  # for design reuse only if needed
YL = 365.2463
D = "/home/paul/eval/winding_scalogram"
p = json.load(open(D + "/qbo30/lt.exe.p")); L = np.array(p["lpap"])
per, ap2 = L[:, 0], L[:, 1:3]
t = np.loadtxt(D + "/qbo30/qbo30.dat")[:, 0]
x = np.loadtxt(D + "/qbo30/qbo30.dat")[:, 1]
B = {k: float(p[k]) for k in ("delA", "delB", "asym", "ma", "mp", "init", "shfT")}
mNfam = np.logical_or(np.logical_and(per >= 26.9, per <= 27.7),
                      np.logical_and(per >= 13.5, per <= 13.9))
idx = np.where(mNfam)[0]
tf = tide_sum(t, ap2[idx], per[idx], YL, integ=B["shfT"])
raw = tf * impulse_delta(t, B["delA"], B["delB"], B["asym"], 12)
F = iir(raw, lag_a=1.0 - B["ma"], lag_c=B["mp"], init=B["init"], start_date=t[0], dates=t)
F -= F.mean()

def local_fit(ts, xs, Fs, Ms, sigma=10.0, nmax=3):
    """shipped design: sin/cos(n*k*F) sidebands, n<=nmax, on +-sigma windows
    — here one global least-squares over all sidebands of the k*F carrier."""
    cols = [np.ones_like(ts)]
    for k in Ms:
        for n in range(1, nmax + 1):
            cols.append(np.sin(2 * np.pi * n * k * Fs))
            cols.append(np.cos(2 * np.pi * n * k * Fs))
    A = np.column_stack(cols)
    beta, *_ = np.linalg.lstsq(A, xs, rcond=None)
    fit = A @ beta
    return np.corrcoef(xs, fit)[0, 1], fit

def iaaft_flat(y, n_reps=20, seed=7):
    """spectrum-exact random-phase IAAFT rung on the target itself."""
    rng = np.random.default_rng(seed)
    N = len(y); n = np.fft.rfftfreq(N, d=1.0 / 12)
    Amag = np.abs(np.fft.rfft(y - y.mean()))
    out = []
    for _ in range(n_reps):
        ph = rng.uniform(0, 2 * np.pi, len(n))
        ph[0] = 0.0
        s = np.fft.irfft(Amag * np.exp(1j * ph), n=N)
        for _ in range(20):
            s = np.interp(np.linspace(0, 1, N), np.sort(s), np.sort(y))
            f = np.fft.rfft(s - s.mean())
            s = np.fft.irfft(Amag * np.exp(1j * np.angle(f)), n=N)
        out.append(s)
    return out

Ms = [0.42, 0.68]          # the two cont=1.00 draconic-manifold teeth
r_real, fit_real = local_fit(t, standardize(x), F, Ms, nmax=3)
dcc_real = np.corrcoef(np.diff(standardize(x)), np.diff(fit_real))[0, 1]
print(f"real qbo30: r(n<=3) = {r_real:.3f}  dCC = {dcc_real:.3f}")

nulls = iaaft_flat(x, 20)
rs = np.array([local_fit(t, standardize(s), F, Ms, nmax=3)[0] for s in nulls])
print(f"flat rung (spectrum-exact IAAFT x20): r = {rs.mean():.3f} +- {rs.std():.3f}")
print(f"honest r (real - flat) = {r_real - rs.mean():+.3f}  z = {(r_real - rs.mean()) / rs.std():+.1f}")
dnull = np.array([np.corrcoef(np.diff(standardize(s)), np.diff(local_fit(t, standardize(s), F, Ms)[1]))[0, 1] for s in nulls[:8]])
print(f"dCC: real {dcc_real:.3f} vs flat-null {dnull.mean():.3f} +- {dnull.std():.3f}")
json.dump({"r_real": round(float(r_real), 4), "dCC_real": round(float(dcc_real), 4),
           "flat_mean": round(float(rs.mean()), 4), "flat_std": round(float(rs.std()), 4),
           "honest_r": round(float(r_real - rs.mean()), 4),
           "z": round(float((r_real - rs.mean()) / rs.std()), 2),
           "dCC_flat_mean": round(float(dnull.mean()), 3)},
          open(D + "/qbo30_k0_fithonesty.json", "w"), indent=1)
print("saved qbo30_k0_fithonesty.json")
