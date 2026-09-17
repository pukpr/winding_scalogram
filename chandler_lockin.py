"""Chandler wobble: forced-alias order line vs free resonance.

(1) Alias arithmetic: rectified draconic torque 2q = 13.60611 d on the
    annual clock -> 432.61 d (article mechanism, k=0 solid-body).
(2) Fyfe-style computed order tracking / lock-in demodulation: track the
    phase of the cleaned pole-x CW line against the predicted alias phase
    phi(t)=2pi*f_cw*(t-t0) in sliding windows. Free resonance (Q~30-60,
    Wilson 1969 / Lambert 2015) => phase wanders several cycles. Forced
    order line => phase stays flat within noise. This is the discriminator.
(3) Frequency chirp: windowed peak / parabolic refinement of the CW line.
Annual + semiannual wobble removed first (nuisance terms, user directive).
"""
import json, sys
import numpy as np
sys.path.insert(0, "/home/paul/eval/winding_scalogram")
from wavelet_scalogram import standardize
from winding_scalogram import winding_transform
from winding_rank import continuity
from lte_forward import tide_sum, iir

YL, P_N = 365.2463, 27.21222
P_2N = P_N / 2.0
a1, a2 = YL / P_N % 1.0, YL / P_2N % 1.0     # 0.42214, 0.84429
FCW = a2                                       # predicted CW freq c/yr
print(f"predicted CW: {FCW:.5f} c/yr = {YL/FCW:.2f} d")

def pole(fn):
    """returns yearly time, x for both IERS formats"""
    raw = np.loadtxt(fn, comments="#")
    if "eopc01" in fn:                        # MJD(1960-scaled, can be neg), x, y
        yrs = 1858.88 + raw[:, 0] / 365.2422
        x = raw[:, 1]
    else:                                     # eopc04: YR MM DD HH MJD x y
        yrs = raw[:, 0] + (raw[:, 1] - 1) / 12 + (raw[:, 2] - 0.5) / 365.2422
        x = raw[:, 5]
    g = ~np.isnan(x)
    return yrs[g], x[g]

def annual_clean(t, v, f0=1962.0, freqs=(1.0, 2.0, 0.9946, 1.0128)):
    y = t - t.mean()
    A = [np.ones_like(t), y, y**2]
    for f in freqs:
        A += [np.cos(2*np.pi*f*(t - f0)), np.sin(2*np.pi*f*(t - f0))]
    A = np.stack(A, 1)
    b, *_ = np.linalg.lstsq(A, v, rcond=None)
    return v - A @ b

def monthly(t, v, lo, hi):
    s = (t >= lo) & (t < hi)
    t, v = t[s], v[s]
    edges = np.arange(t[0], t[-1], 1/12.)
    idx = np.clip(np.searchsorted(edges, t) - 1, 0, len(edges) - 2)
    tg = (edges[:-1] + edges[1:]) / 2
    out = np.array([v[idx == k].mean() if np.any(idx == k) else np.nan
                    for k in range(len(tg))])
    g = ~np.isnan(out)
    return tg[g], out[g]

# ---- load + clean
t4, x4 = pole("/home/paul/campaign/blind/AG1/eopc04_20.1962-now")
tm, xm = monthly(t4, x4, 1962, 2025)
xmc = annual_clean(tm, xm, 1962.0)
tl, xl = pole("/home/paul/campaign/blind/AG1/eopc01.1846-now")
tL, xL = monthly(tl, xl, 1846, 2025)
xLc = annual_clean(tL, xL, 1846.0)
print(f"c04 monthly n={len(xmc)}  c01 1846- monthly n={len(xLc)} rho1={np.corrcoef(xLc[1:],xLc[:-1])[0,1]:.3f}")

# ---- observed CW line per era (sanity): FFT peak near 0.844
def peak_near(t, x, f0=0.844, hw=0.06):
    w = np.hanning(len(x)); S = np.abs(np.fft.rfft((x-x.mean())*w))
    fr = np.fft.rfftfreq(len(x), 1/12)
    m = (fr > f0-hw) & (fr < f0+hw)
    i = np.argmax(S[m])
    return fr[m][i], YL/fr[m][i]
print("obs CW c04:", ["%.4f" % v for v in peak_near(tm, xmc)], " c01:", ["%.4f" % v for v in peak_near(tL, xLc)])

# ---- (2) lock-in: windowed complex amplitude vs predicted alias phase
def lockin(t, x, f_pred, win=10.0, step=0.5):
    ph = 2*np.pi*f_pred*(t - t[0])
    rows = []
    for tc in np.arange(t[0]+win/2, t[-1]-win/2+1e-9, step):
        m = (t >= tc-win/2) & (t < tc+win/2)
        if m.sum() < win*10: continue
        A = np.stack([np.cos(ph[m]), np.sin(ph[m]), np.ones(m.sum()), t[m]-tc], 1)
        b, *_ = np.linalg.lstsq(A, x[m], rcond=None)
        amp = np.hypot(b[0], b[1]); phi = np.arctan2(-b[1], b[0])
        # ref phase at window centre relative to global t0
        rows.append((tc, amp, phi, np.unwrap(np.array([phi]))[0]))
    return np.array([(r[0], r[1], r[2]) for r in rows])

li4 = lockin(tm, xmc, FCW)
li1 = lockin(tL, xLc, FCW)

def phase_drift_stats(li, label):
    ph = np.unwrap(li[:, 2])
    tc = li[:, 0]
    # detrend the constant part by removing the mean slope forced to zero:
    # a perfect forced line has slope 0 in this frame
    c = np.polyfit(tc - tc.mean(), ph, 1)
    resid = ph - np.polyval(c, tc - tc.mean())
    print(f"{label:28s} phase slope {c[0]:+.4f} c/yr ({c[0]*(li[-1,0]-li[0,0]):+.2f} cyc over span)  "
          f"resid rms {resid.std():.2f} rad  amp mean {li[:,1].mean():.3f}")
    # free-resonance reference: Q=40 relaxation wander scale
    return c[0], resid.std()

s4 = phase_drift_stats(li4, "c04 1962-2024 (62 yr)")
s1 = phase_drift_stats(li1, "c01 1846-2024 (178 yr)")

# control: lock against wrong frequency
for df in (0.004, -0.004, 0.02):
    lic = lockin(tm, xmc, FCW + df, win=10.0)
    ph = np.unwrap(lic[:, 2]); c = np.polyfit(lic[:, 0]-lic[:, 0].mean(), ph, 1)
    print(f"  control f+{df:+.3f}: slope {c[0]:+.4f} c/yr resid rms {(ph-np.polyval(c, lic[:,0]-lic[:,0].mean())).std():.2f}")

# ---- (3) chirp: windowed frequency estimate near CW line
def chirp(t, x, win=12.0, step=1.0):
    out = []
    for tc in np.arange(t[0]+win, t[-1]-win, step):
        m = (t >= tc-win/2) & (t <= tc+win/2)
        if m.sum() < 100: continue
        seg = x[m]; tt = t[m]-tc
        best = (None, -1)
        for f in np.arange(0.72, 1.0, 0.002):
            A = np.stack([np.cos(2*np.pi*f*tt), np.sin(2*np.pi*f*tt), np.ones_like(tt), tt], 1)
            b, *_ = np.linalg.lstsq(A, seg, rcond=None)
            r = np.hypot(b[0], b[1])
            if r > best[1]: best = (f, r)
        out.append((tc, best[0], best[1]))
    return np.array(out)

ch = chirp(tL, xLc)
pred_days = YL/FCW
print(f"\nchirp c01 1846-2024: observed CW period {YL/ch[:,0+1].mean():.1f} d mean, "
      f"min {YL/ch[:,1].max():.1f} max {YL/ch[:,1].min():.1f}, predicted {pred_days:.1f} d")
print("chirp vs nodal phase (18.61 yr):")
nod = (ch[:, 0] % 18.61) / 18.61
for k in range(6):
    m = (nod >= k/6) & (nod < (k+1)/6)
    if m.sum(): print(f"  nodal phase {k/6:.1f}-{(k+1)/6:.1f}: mean P {YL/ch[m,1].mean():.1f} d  n={m.sum()}")
json.dump({"pred_d": pred_days, "obs_c04": peak_near(tm, xmc)[1], "obs_c01": peak_near(tL, xLc)[1],
           "lockin_slope_c04": s4[0], "lockin_resid_c04": s4[1],
           "lockin_slope_c01": s1[0], "lockin_resid_c01": s1[1]},
          open("/home/paul/eval/winding_scalogram/chandler_lockin.json", "w"), indent=1)
print("\nsaved chandler_lockin.json")
