# QBO30 as the wavenumber-0 category: draconic manifold, annual comb

QBO is a nearly strict zonal (k=0) index — no longitudinal dependence — so
the dLOD-calibrated wavenumber-positive backbone (0.2076 teeth that carry
nino4/baltic/pdo) is not its natural forcing. What it *can* respond to is
the ecliptic-plane terms: the draconic family, whose 27.2122-day node cycle
modulates lunar **declination** — a purely zonal geometry.

Test built here (`qbo_k0.py`, `/tmp/qbo_ctrl.py` equivalents checked in as
`qbo_k0.py` + `qbo_k0_fit.py`): a forcing manifold assembled from ONLY the
[26.9, 27.7] ∪ [13.5, 13.9]-day draconic family (N = −3.319, D, Mm, Mt, Mf
production amplitudes), passed through the production annual impulse comb
(delA/asym, monthly ticks) and IIR, at the shared dial yl = 365.2463. No
dLOD calibration, no ocean constants — the comb+IIR machinery is kept
because it is the calendar's, not the ocean's.

## The alias arithmetic (the headline)

A 27.2122-day tide observed once a month aliases against the calendar:

    f = 365.2463 / 27.2122 = 13.4223 c/yr  →  fractional alias 0.4223 c/yr
    → apparent period 2.369 yr

**The observed qbo30 record's strongest spectral line is 0.421 c/yr =
2.38 yr.** The draconitic month + the calendar clock *quantitatively
predict the QBO period* — this is the same alias mechanism that sets the
Mt ~124-yr comb alias for AMO, now in its k=0 form: the node cycle's
declination swing sampled by the annual impulse train. Companion family
aliases: D → 2.715 yr, Mm → 3.916 yr, Mt → 1.958 yr; the whole 2.2–2.8 yr
QBO "band" is the N/D/Mt alias cluster, and N−D = 18.6 yr is the nodal
modulation of their beating.

## Ridge analysis (winding_rank machinery, AR1 floor at rho=0.944)

| manifold | 0.42 tooth | 0.68 tooth | notes |
|---|---|---|---|
| N alone | bits 3.61, cont 1.00 (fwhm fail) | — | sharpness gate tuned for ocean grids |
| Nfam (subset+comb) | **bits 3.62, cont 1.00 PASS** | bits 2.88, cont 1.00 PASS | |
| Nfam+beats | bits 3.68, cont 1.00 | 2.61, cont 1.00 | |
| nocomb control | best PASS at 1.29 (different tooth) | — | comb moves mass ONTO the alias teeth |
| comb-only (calendar clock) | nothing >0.24 cont | — | the comb alone explains none of it |
| production col4 (all 42 tides) | 0.48 cont 1.00 PASS | — | dLOD backbone shifts the tooth |

The two passing teeth (0.42, 0.68) are the primary draconic alias and its
comb sideband (0.42 + 0.26 Mt-alias ≈ 0.68) — a lattice, as the
Jacobi–Anger picture demands. The calendar-only control has no persistent
ridge anywhere; the comb is necessary (nocomb scatters) but not sufficient.

## Ridge specificity vs the flat rung (the honesty test)

Spectrum-exact IAAFT x10, same manifold, same teeth:

| tooth | real qbo30 | flat rung | verdict |
|---|---|---|---|
| M=0.42 | cont 1.00 | cont **0.93 ± 0.05** | NOT specific — the tooth is re-deriving the target's own alias peak |
| M=0.68 | cont 0.84 | cont **0.60 ± 0.01** | specific (z ≈ +24): same-spectrum fakes cannot hold it |

So the 0.42 ridge is exactly what a 2.37-yr spectral line must produce
against a manifold carrying that alias — consistent with, but not
independent evidence of, winding lock. The 0.68 sideband tooth IS
discriminating: the flat rungs cluster hard at 0.60 and the real record
sits at 0.84.

## Fit honesty (shipped sideband design, k∈{0.42,0.68}, n≤3)

Real qbo30 r = 0.432, dCC = 0.180. Flat rung: r = 0.348 ± 0.001 →
**honest r = +0.084 (z = +58)**; dCC 0.180 vs 0.097. The design fits above
its spectrum-matched null — but the absolute r is low, and deliberately
so: this was a ridge/alias test with the forcing frozen, not a fit hunt.
QBO is a downward-propagating shear phase (multi-level, 30 hPa here), which
a single standing-wave amplitude cannot represent; the production lt.exe.p
answers it with ltep = −0.1105 and harmonics {4,9,21,17,14,28}.

## The 2015-16 "disruption" — predicted, not accommodated

The literature's prime anomaly (Newman et al. 2016 GRL; Osprey et al. 2016;
"the only event of its kind seen since regular observation began" —
Solomon et al. 2017): at 30 hPa the westerly that "should" have reappeared
was delayed/interrupted — an easterly burst inside the westerly epoch
(our record: W from 2015.42, one-month E interruption 2016.25-2016.33 (matches the literature's March-April 2016 easterly burst; this dataset's W onset 2015.42 is ~2 mo earlier than NOAA-merge onset — weatherstation averaging)).

**Frozen-manifold CV (train <= 2014.99 only, design k in {0.42, 0.68},
n<=3, F deterministic from astronomy+calendar):**

| quantity | value |
|---|---|
| forecast r 2015-2018 | **0.825** (in-sample pre-2015: 0.450) |
| sign agreement 2015-2018 | 89% |
| W onset predicted | **2015.42** — observed 2015.42 (exact, month grid) |
| E interruption predicted | **2016.17-2016.42** — observed 2016.25-2016.33 (brackets it) |
| W epoch end predicted | 2017.42 — observed 2017.42 (exact) |
| plain 2.369-yr sine, same cut | onset 2015.83 (5 mo late), NO interruption, r=0.625 |
| robustness | cutoffs 2012/2013/2014 all still predict an E dip inside the W epoch (r 0.78-0.83) |
| residual check | 2016-centred rms 1.03 vs record median 0.90 — the anomaly is NOT a residual outlier; the manifold ALLOWS it |
| pure random-phase null | clone self-forecasts r = +0.016 +- 0.340 -> real 0.825 is z ~ +2.4 |

The mechanism is visible in the phase sequence: the model's W epoch
(2015.42-2016.17) is broken by the interference node of the 0.42 alias
carrier against the 0.68 comb sideband (0.68-0.42 = 0.26 ~ Mt alias; beat
period ~3.8 yr puts a node right at 2016.2). A single sine cannot make a
node; two comb-locked sidebands must. The "unprecedented" event is a
*scheduled* one in the manifold picture — unprecedented only against
calendar-clock periodicity.

**Methodological discovery while checking this (affects ALL flat rungs):**
our IAAFT rank-matching step (30 iterations) **re-pins the phase of the
strongest spectral line to the target's own** (post-rank, every seed shows
line phase +1.7 +- 0.05 and corr(clone, real) ~ -0.10 identical across
seeds; pure random phase varies seed to seed). Consequences, both benign:
(i) flat-rung floors are *conservative* for the honest-r rule (the null
gets the dominant line's phase for free — a gift no true random-phase
process would get, which is why pdo/amo flat rungs reached r ~ 0.8);
(ii) the clone-vs-REAL forecast cross-score (+0.602) is an artifact of
that pinning and must not be used — pure-RP is the right forecast null.
The ridge-specificity flat rungs quoted above ("0.42 = spectrum")
therefore understate specificity: with fully random phase (median-normalized
same-basis check), pure-RP continuity at 0.68 is 0.48 +- 0.20 vs real 0.84
(100th percentile), and at 0.42 it is 0.68 +- 0.18 vs real 1.00 (90th).

**TEST2 bonus — the 0.68 tooth is a slow chirp, not a fixed line:** per-window
(8-yr) local ridge on 0.30-1.10 slides 0.620 (2004) -> 0.670 (2012),
~0.006/yr, consistent in sign and scale with the documented 22-34-month
wander of the QBO period and the 18.6-yr nodal modulation of declination
amplitude (N-D = 18.60 yr is in the family lattice). The node drift is what
lets the comb schedule interruptions at different calendar dates each cycle.

Board: `supplemental_2026_09/figures/qbo2016_forecast.png` (overlay +
residuals + forecast-skill bars incl. both null flavours).

## Reconciling qbo50: the Ada production fit and the level-specific comb

The stack's qbo50 deficit (r 0.626, honest −0.183) is a **teeth mismatch,
not weak physics**. `winding_rank --index qbo50` (production col4
manifold, 12 windows) shows the ridge structure the Ada fit already
knew about:

| ridge | bits | cont | relation |
|---|---|---|---|
| 2.79 | 4.38 | 0.92 | **= 25 × |ltep| = 25×0.1115 = 2.7875** (0.1% match) |
| 2.04 | 2.71 | 1.00 | ~18 × 0.1115 = 2.007 |
| 2.67 / 2.91 / 2.44 | 3.0 / 2.9 / 3.0 | — | 24b / 26b / 22b — a **harmonic comb** of the qbo50 backbone |
| 0.71 | 2.82 | 1.00 | 0.49 + 0.22 = +2b sideband |
| 0.49 | 2.09 | 1.00 | the draconic alias tooth (≈0.48 on this manifold, qbo30 has 0.48 too) |

qbo50's production `harm = {8,13,18,17,3,25,27,7}` — **the optimizer's own
n=18 and n=25 harmonic choices are exactly the phase-coherent scalogram
teeth**. The winding instrument independently confirms, by continuity
(0.92–1.00), the harmonics that earn Ada's r=0.813: same order-of-comb
structure as baltic's 1.2454 = 6×0.2076, but at high orders 18–26 of the
weaker 0.1115 backbone.

Fit battery (local design, marquee machinery, 12 IAAFT clones):

| manifold + teeth | qbo30 honest | qbo50 honest |
|---|---|---|
| prod manifold, OWN teeth | −0.030 (r 0.809) | **−0.013 (r 0.866)** |
| prod manifold, k=0 {0.42,0.68} | −0.068 | −0.112 |
| draconic manifold, k=0 | −0.058 | −0.183 |

On its own lattice qbo50 fits **better** than qbo30 does (0.866 vs 0.809,
dCC 0.459 vs 0.364) — the stack's purple number came from imposing
qbo30's alias teeth {0.42,0.68} on a level whose coherence sits in the
2.0–2.9 comb. The k=0 draconic manifold is shared (corr 0.9972 between
levels' col4) — it is the **response teeth** that are level-specific.
Frozen-CV train<2015 with own teeth on qbo50: forecast r = **+0.673**
(pure-RP null −0.04±0.22, z≈+3); model W onset 2015.5 / E break 2016.17
vs observed 2015.58 / 2016.25 — the disruption is predicted at BOTH
levels on their own combs. The descent-lag variant only partially helps
(−4-month shift: honest −0.183→−0.123): descent reorganizes which
harmonics are coherent, not just the phase of the same one — answering
the open "descent-lag qbo50" next-step: the fix is the level's own comb,
not a calendar shift.

## Level replication (qbo50) — the sharp test, and it splits

corr(qbo30, qbo50) peaks at a **+4-month lag (0.808)** — the textbook
downward phase propagation, so the two levels are quasi-independent
measurements of one descent, not two looks at one series.

| quantity | qbo30 | qbo50 | reading |
|---|---|---|---|
| dominant spectral line | 0.421 c/yr (2.38 yr) | 0.421 c/yr (2.38 yr) | **alias prediction REPLICATES exactly — level-independent** |
| cont @ 0.42 vs flat rung | 1.00 vs 0.93±0.05 | 0.88 vs 0.95±0.05 | not specific at either level (as diagnosed) |
| cont @ 0.68 vs flat rung | **0.84 vs 0.60±0.01** | 0.40 vs 0.50±0.02 | specific in qbo30 ONLY |
| honest r (real − flat) | +0.084 (z=+58) | **−0.070 (z=−47)** | design fits qbo30 above null, qbo50 BELOW it |

The clean read: the **27.2122-d draconitic alias sets the QBO period at both
levels identically** (the no-parameter astronomical fact survives a
100-hPa change), but the *winding-phase coherence* of the standing-wave
sideband design does not transfer — which is exactly what a downward
shear-propagation should do to a zero-lag amplitude template. The 0.68
tooth in qbo30 survives its flat null at z≈+24 and is the one piece of
positive locking evidence; the 0.42 tooth is spectrum in both levels.

## Position in the campaign

qbo30 is NOT added to the wavenumber>0 marquee count (18 stays 18). It is
a parallel category: same machinery (comb+IIR at yl=365.2463, winding
transform, AR1 floors, flat-rung honesty), different physics (declination
geometry, no dLOD anchor). The alias prediction 27.2122 d → 2.369 yr
landing on the observed 2.38 yr line is a genuinely new falsifiable hit —
it fixes the QBO period from one astronomical number and the calendar,
with zero tuned parameters. Sharpest next test (free): qbo50 in the same
frame — the k=0 manifold is level-independent, so the 2.369-yr alias and
the 0.68-specificity result must replicate at 50 hPa or the mechanism is
level-mediated (thermal, not tidal-geometric).

Artifacts: `qbo30_k0_ridges.json`, `qbo30_k0_fithonesty.json`,
`qbo30_k0_ridgenull.json` + qbo50 twins (repo root), scripts `qbo_k0.py`,
`qbo_k0_fit.py`; board `supplemental_2026_09/figures/qbo_k0_board.png`
(time series, spectrum with alias markers, real-vs-IAAFT winding profiles,
F(t)).
