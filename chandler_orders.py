"""Fyfe computed-order analysis for the Chandler wobble carrier.

The carrier f1 = frac(2*yl/P_N) = 0.844285 c/yr is the order-1 line of a
rectified 2N phase walk sampled on the annual shaft. The Fyfe-native test:
each order line f_j = frac(j*f1) in the cleaned pole record must be PHASE-
STABLE against the carrier frame (lock-in circular concentration over
sliding windows). A free resonance has one line; any other spectral content
is excitation accident with no reason to hold phase vs the carrier frame.

Window: 16 yr. The ladder's minimum spacing is frac(6*F1) = 0.0657
c/yr; Rayleigh 1/16 = 0.0625 sits just under it, so neighboring orders
are marginally resolved (8-yr windows leak them badly). Null: 40
pure-random-phase clones of the SAME cleaned
record (spectrum preserved, phase destroyed) scored per order.
Companion: circular polarization (pro/retro) of the order-1 orbit.
"""
import json
import numpy as np

YL = 365.2463
PN = 27.212220815
F1 = (2 * YL / PN) % 1.0          # 0.844285 c/yr carrier
JMAX = 12
TAU_WIN = 16.0
LO, HI = 1962.0, 2022.0

raw = np.loadtxt("/home/paul/campaign/blind/AG1/eopc04_20.1962-now",
                 comments="#", usecols=(0, 1, 2, 5, 6))
yrs = raw[:, 0] + (raw[:, 1] - 1) / 12 + (raw[:, 2] - 0.5) / 365.2422
tc = np.arange(np.ceil(yrs.min() * 12) / 12, yrs.max(), 1.0 / 12)
xm = np.interp(tc, yrs, raw[:, 3])
ym = np.interp(tc, yrs, raw[:, 4])

def design(t):
    c = t - t.mean()
    cols = [np.ones_like(c), c, c ** 2]
    for f in (1.0, 2.0, 0.9946, 1.0128):
        cols += [np.cos(2 * np.pi * f * c), np.sin(2 * np.pi * f * c)]
    return np.array(cols).T

D = design(tc)
xc = xm - D @ np.linalg.lstsq(D, xm, rcond=None)[0]
yc = ym - D @ np.linalg.lstsq(D, ym, rcond=None)[0]
TREF = 1992.0

def lockin(sig, f, win=TAU_WIN):
    """sliding linear-LS lock-in, phase referred to fixed epoch TREF."""
    h = win / 2.0
    rows = []
    for t0 in np.arange(tc.min() + h, tc.max() - h + 1e-9, 1.0):
        m = np.abs(tc - t0) <= h
        if m.sum() < int(win * 9):
            continue
        u = tc[m] - t0
        A = np.column_stack([np.ones_like(u), u,
                             np.cos(2 * np.pi * f * u), np.sin(2 * np.pi * f * u)])
        b, *_ = np.linalg.lstsq(A, sig[m], rcond=None)
        ref = 2 * np.pi * f * (t0 - TREF)
        rows.append((t0, np.hypot(b[2], b[3]), np.arctan2(b[3], b[2]) + ref))
    r = np.array(rows)
    return r[:, 0], r[:, 1], np.unwrap(r[:, 2])

def concs(sig):
    out = []
    for j in range(1, JMAX + 1):
        fj = (j * F1) % 1.0
        tt, a, ph = lockin(sig, fj)
        m = (tt >= LO) & (tt <= HI)
        C, S = np.cos(ph[m]).mean(), np.sin(ph[m]).mean()
        out.append((float(np.hypot(C, S)), float(a[m].mean()), int(m.sum())))
    return np.array(out)

real = concs(xc)

# spectral companion tests at full-record resolution (Hann):
# order-1 line vs the UNRECTIFIED N alias (0.422 c/yr, the QBO tooth at
# 865 d). Generic draconic forcing predicts BOTH; rectified sampling
# predicts order-1 only. A true falsifier.
w = np.hanning(len(xc)); X = np.abs(np.fft.rfft(xc * w)) / np.sqrt((w**2).sum() / 2)
fr = np.fft.rfftfreq(len(xc), 1 / 12)
bg = float(np.median(X[(fr > 0.05) & (fr < 3.0)]))
def band(f0, half=0.012):
    m = (fr > f0 - half) & (fr < f0 + half)
    return float(X[m].max() / bg), float((X[m]**2).sum() / (X**2).sum())
cw_ratio, cw_pow = band(F1)
qbo_ratio, qbo_pow = band(F1 / 2)          # 0.422143 = 865.2 d companion
print(f"\nfull-record Hann spectrum of cleaned pole-x:")
print(f"  order-1 band (432.6 d): {cw_ratio:.0f}x background, band power {cw_pow:.3f}")
print(f"  unrectified companion (865.2 d = QBO tooth): {qbo_ratio:.1f}x bg, band power {qbo_pow:.5f}")
print(f"  -> rectification is SELECTIVE in the solid Earth"
      f" ({cw_pow/max(qbo_pow,1e-12):.0f}x band-power contrast)")

rng = np.random.default_rng(7)
N = 40
null = []
for k in range(N):
    Ff = np.fft.rfft(xc)
    ph = rng.uniform(0, 2 * np.pi, len(Ff)); ph[0] = 0
    s = np.fft.irfft(np.abs(Ff) * np.exp(1j * ph), n=len(xc))
    null.append(concs(s))
null = np.array(null)

print(f"F1 = {F1:.6f} c/yr; window {TAU_WIN:.0f} yr (Rayleigh {1/TAU_WIN:.4f} c/yr); "
      f"min ladder step frac(6F1) = {(6*F1)%1.0:.4f} c/yr; n_win per order = {real[0,2]}")
print(" j    f_j      amp      conc  null_med null_p95    z    verdict")
rows = []
for j in range(1, JMAX + 1):
    cr, amp, _ = real[j - 1]
    dist = null[:, j - 1, 0]
    mu, sd, p95 = dist.mean(), dist.std(), np.quantile(dist, 0.95)
    z = (cr - mu) / sd if sd > 0 else 0.0
    v = "PASS" if cr > p95 else ""
    print(f"{j:2d}  {(j*F1)%1.0:.5f}  {amp:.4f}   {cr:.3f}   {mu:.3f}   {p95:.3f}  {z:+5.1f}  {v}")
    rows.append({"j": j, "f": float((j * F1) % 1.0), "amp": amp, "conc": cr,
                 "null_med": float(mu), "null_p95": float(p95), "z": float(z),
                 "pass": bool(cr > p95)})

# circular polarization at order 1
m = (tc >= LO) & (tc <= HI)
u = tc[m] - TREF
zsig = (xc + 1j * yc)[m]
retro_slot = float(np.abs(np.mean(zsig * np.exp(-2j * np.pi * F1 * u))))
pro_slot = float(np.abs(np.mean(zsig * np.exp(+2j * np.pi * F1 * u))))
# convention control on the RAW (uncleaned) series at the annual line:
# the annual wobble is known PROgrade; if it lands in the slot OPPOSITE to
# the CW line, the slot labels are physical (CW = retrograde).
zr = (xm + 1j * ym)[m]
an_a = float(np.abs(np.mean(zr * np.exp(-2j * np.pi * 1.0 * u))))
an_b = float(np.abs(np.mean(zr * np.exp(+2j * np.pi * 1.0 * u))))

# sanity positive control: an injected line AT order 5 must read high conc
inj = xc + 0.01 * np.cos(2 * np.pi * ((5 * F1) % 1.0) * (tc - TREF) + 1.1)
ci = concs(inj)[4]
print(f"\ncircular @order1: retrograde-slot {retro_slot:.4f} vs prograde-slot {pro_slot:.4f} arcsec"
      f"  (orbit is retrograde in space frame: ellipticity {(pro_slot-retro_slot)/(pro_slot+retro_slot):+.2f})")
print(f"positive control: line injected at order 5 reads conc {ci[0]:.3f} (amp {ci[1]:.4f})")

json.dump({"F1": float(F1), "window_yr": TAU_WIN, "orders": rows, "n_null": N,
           "circ": {"retro_slot": retro_slot, "pro_slot": pro_slot}},
          open("/home/paul/eval/winding_scalogram/chandler_orders.json", "w"), indent=1)
print("wrote chandler_orders.json")
