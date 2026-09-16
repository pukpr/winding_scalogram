# Rejection battery: `pdo_iaaft_detuned_surrogate` as negative control

Scripts: [`rejection_surrogate.py`](rejection_surrogate.py),
[`../red_noise_floor.py`](../red_noise_floor.py)
Charts: [`figures/rejection_surrogate.png`](figures/rejection_surrogate.png),
[`../milestone_2026_09/figures/red_noise_floor.png`](../milestone_2026_09/figures/red_noise_floor.png)
Data: [`figures/red_noise_floor.json`](figures/red_noise_floor.json),
[`figures/red_noise_floor_n1.json`](figures/red_noise_floor_n1.json)

## What the surrogate is

An **IAAFT** (iterated amplitude-adjusted Fourier transform) surrogate of
PDO — randomised, so it preserves PDO's amplitude distribution and power
spectrum but has no physical coherence — then *detuned* onto
**baltic's** winding triple {0.1223, 0.2076, 0.9247} at the production
year length, and run through the full Ada optimizer. Its own production
scored r = **0.317** against its own data (real baltic scores 0.705).
It is listed in `docs/PREREG_JOINT.md` as the campaign's negative
control, and `docs/METHODS_BLURB.md` calls the surrogate rejection "the
strongest single card because it shows the instrument can answer no."

## The rejected exhibit, in full

[`figures/rejection_board.png`](figures/rejection_board.png)
([`../rejection_board.py`](../rejection_board.py)) shows the three
things a fair rejection must display:

- **(A) Model overlaid on the (synthetic) data — it fits beautifully.**
  Own baltic-triple design n≤6: r=0.866. PDO's own manifold + PDO's own
  windings n≤3 poured onto the surrogate: r=0.865 — and the same design
  on real PDO gives only 0.814. Rejection here is not about visual fit
  quality: the curves track. This is exactly why in-sample overlays
  cannot convict.
- **(B) Winding-ridge spectra** vs real PDO and the AR(1) floor: the
  surrogate shows **no strong ridge anywhere near the claimed PDO
  windings** — its spectrum is a smooth continuum riding its own
  autocorrelation (left: power / floor, right: raw power). Numeric
  verdict at M=0.4488 below: real continuity 1.00 vs surrogate 0.27.
- **(C) Manifold vs AMO's**: rms deviation **0.8 windings**, r = 0.999 —
  the detuned surrogate constants generate essentially the same
  manifold as everything else. Consistent with JIGGLE_ANALYSIS.md: the
  constants don't matter, the dial does. Which is precisely why the
  manifold/fit route alone could not reject it and the ridge criterion
  could.

## Test 1 — winding ridge qualification: PASSES (surrogate rejected)

`winding_rank.py`, identical settings for both series (dm=0.004,
σ=15 yr, t0=5 yr, AR(1) surrogate floor, 24 reps, thresholds SNR≥2 bits,
FWHM≤0.12, continuity≥0.7). Targeted band scans (window ±0.10 around
each claimed position) are the cleanest read:

| series | claimed PDO band [0.35, 0.55] | baltic detune tooth [0.85, 1.05] |
|---|---|---|
| real PDO | **M=0.446: 2.77 bits, FWHM 0.052, cont 1.00 → PASS** | M=0.950: 2.09 bits, FWHM 0.088, cont 0.65 → fail |
| surrogate | **no ridge above 2-bit SNR at all** (band-max SNR 0.27 bits at the window edge; direct continuity read at 0.4488: **0.31**) | M=0.854: 2.14 bits, FWHM 0.120, cont 0.38 → fail |

At the one position the instrument claims for PDO, the real series is
**steady in time** (ridge sits on M in 100% of windows) and the
surrogate has nothing there (27–31% at best, sub-SNR peak). The
rejection works — but only at claimed positions, and note the honest
asymmetry: an AR(1)-noise ridge scan run through the same filter passes
0–1 candidates per rep (8 reps, peak up to 3.57 bits), so *single*
ridge passes are not rare enough to be conclusive on their own.

**Bonus validation (full-range scan, [0, 1.5]).** The surrogate's own
candidate list is: **0.952 PASS (2.82 bits, FWHM 0.064, cont 0.88)** +
1.372/1.144/0.704/0.824 all failing. The one ridge that passes sits
exactly on the baltic order-6-adjacent tooth the surrogate was *detuned
to imitate* (its `lt.exe.p` windings are baltic's {0.1223, 0.2076,
0.9247}). So the ridge instrument is doubly validated here: it passes
the tooth genuinely stamped into the synthetic data (0.952) and rejects
the PDO-band tooth that was *not* stamped in — while the fit-r metric
does the opposite (fits the smooth surrogate best). A rejection with a
built-in positive control.

## Test 2 — in-sample fit r: FAILS (surrogate beats real PDO)

Fitting the *same* winding design to both series, one dial, σ=10:

| series | design | r | dCC |
|---|---|---|---|
| real PDO | PDO manifold + PDO windings, n≤3 | 0.814 | 0.254 |
| **surrogate** | **the same PDO fit, unchanged** | **0.865** | 0.255 |
| **surrogate** | PDO manifold + PDO windings, n≤6 | **0.904** | — |
| surrogate | its own baltic-winding manifold, n≤6 | 0.866 | 0.265 |

The surrogate fits **better than the real index**. Reason, from the
autocorrelation panel of `rejection_surrogate.png`: the surrogate is
*smoother* than reality (lag-1 ρ = 0.995 vs 0.967, and its ACF stays
high where real PDO's collapses), and a 40-column local regression on
monthly data of that smoothness captures anything of the same shape.
r is measuring smoothness, not locking.

## Test 3 — red-noise floor battery (12 indices × 2 nulls × 3 designs)

Each index's own shipped design scored against 8–10 AR(1)-ρ-matched
surrogates and 8–10 phase-randomised (spectrum-preserving) surrogates of
itself. `red_noise_floor.py`; forest plot in
`milestone_2026_09/figures/red_noise_floor.png`. z = (real −
mean_floor)/σ_floor:

| index | n≤1 real | z(AR1) | z(PhaseRand) | n≤6 real | z(AR1) | z(PhaseRand) |
|---|---|---|---|---|---|---|
| amo | 0.806 | **+1.5** | **+2.5** | 0.880 | +0.2 | −0.6 |
| pdo | 0.722 | −2.1 | +1.2 | 0.877 | −1.9 | −0.6 |
| nino4 | 0.719 | −2.2 | **+2.1** | 0.905 | −1.4 | **+2.9** |
| iode | 0.626 | −3.7 | −1.1 | 0.815 | −3.9 | −2.7 |
| baltic | 0.662 | −5.0 | +1.4 | 0.870 | −3.9 | +0.9 |
| nao | 0.629 | **−6.5** | −0.5 | 0.873 | −2.3 | −0.0 |
| brestexcl | 0.712 | −2.8 | +0.8 | 0.910 | −2.1 | +0.6 |
| tpi | 0.662 | −5.6 | +0.3 | 0.880 | −2.6 | +0.8 |
| emi | 0.646 | −2.4 | +0.7 | 0.853 | −2.3 | +0.7 |
| pna | 0.608 | +1.1 | **+1.6** | 0.834 | −0.5 | +0.4 |
| noi | 0.573 | −1.3 | +0.1 | 0.825 | −2.3 | −1.4 |
| kap10-10-20-30 | 0.588 | −0.5 | +0.4 | 0.839 | −1.4 | +0.1 |

**This is the campaign's most important negative result and it cuts the
showcase.** Against the red-noise floor, essentially *nothing* in the
one-dial capture battery clears significance. AR(1) noise matched to
each index's persistence scores 0.58–0.93 on the same designs —
r-values in the same range as the real captures. The only cells above
z ≈ +2 are amo and nino4 (n≤1 vs phase-randomised; nino4 n≤6 at +2.9),
i.e. the two indices whose capture is dominated by the AMO-band
0.0134-style slow tooth and the ENSO annual cycle — precisely the
components a spectrum-preserving null cannot fake, because the null
destroys phase-locking to the calendar while keeping the power.

Why AR1 beats the real series so often: the surrogate null has the
*same* long swing but its high-frequency wiggle is random, so a rich
design (24–92 columns) fits the noise series *more* cleanly than the
noisier real one. More harmonics = higher floor = worse evidence. That
is what the n≤1 → n≤6 columns show: real r rises ~0.06 with harmonic
order, and the AR(1) floor rises ~0.08.

## Verdict

**The instrument does answer "no" — and it just answered "no" to our
own headline statistics.** Recorded consequences:

1. **In-sample r is retired as evidence.** The marquee numbers
   (0.846/0.870/0.834…) stand as descriptive fits only, exactly as the
   Honest-limits section already conceded; the floor battery shows they
   are *inside* the red-noise envelope, so they cannot be cited as
   support for locking.
2. **Two statistics survive.** (a) Ridge **continuity** at claimed
   positions (real PDO 1.00 vs surrogate 0.27) — time-localisation, not
   amplitude. (b) **Phase-randomised** rejection of the specific slow
   tooth (amo +2.5σ, nino4 +2.9σ) — the calendar-locked component.
3. **What must come next** (unchanged priority, now mandatory rather
   than prudent): the C1 blind holdout battery, and a *paired*
   design-matched null (fit surrogate and real with identical design,
   compare r differences rather than levels). Without those, the
   defensible claim is the year-length fingerprint + the dLOD
   validation + ridge continuity, **not** the capture correlations.

The surrogate did its job. Keep it in the battery permanently.

## The sharpness ladder (v2): nulls that can't coast on smoothness

The AR(1) floor raised a design question: an AR(1) with matched ρ₁ is
actually *smoother* than real climate at the 1–5 yr band (its spectrum
has no knee where the real one drops), so "r < AR1 floor" can mean the
null is too sharp OR too soft. To settle it we need a ladder, not a
rung. `sharp_surrogates.py` builds one from the target's OWN spectrum:

1. amplitude spectrum A(f) of the real (detrended) monthly target,
   tilted `A(f) *= (f/f_ref)^alpha` — alpha=0 keeps the old IAAFT flat
   spectrum; alpha=+1/+2 drain the low-frequency power that inflates CC;
2. random phase per member (a phase-randomized null deliberately —
   locking means phase structure, and these must not fake it);
3. 20 IAAFT passes so final spectrum ≈ tilted target and the marginal
   shape = the real samples;
4. AR1(ρ=real ρ₁) as the "single-parameter" comparator rung.

Measured sharpness (curvature = var(Δ²x)/var(x), the wiggle-energy
count that fit-band inflation is all about):

| rung | ρ₁ | curvature |
|---|---|---|
| real pdo | 0.967 | 0.039 |
| flat (α=0) | 0.967 | 0.040 (by construction) |
| a1 (α=+1) | 0.687 | 0.73 |
| a2 (α=+2) | 0.370 | 2.25 |
| AR1@ρ_pdo | 0.973 | 0.11 |

**Fit battery** (`sharp_fit_battery2.py`, 8 seeds/rung, ladder rebuilt
from each index's own detrended target, design = shipped
manifold + `lt.exe.p` windings + σ=10, n≤3/n≤6):

| index | real r (n≤3) | flat z | a1 z | a2 z | AR1 z |
|---|---|---|---|---|---|
| pdo | 0.814 | +0.4 | +22.6 | +77 | −2.6 |
| amo | 0.846 | +0.3 | +68 | +217 | +1.5 |
| baltic | 0.797 | +1.1 | +16 | +72 | −3.1 |
| nino4 | 0.842 | +3.3 | +24 | +85 | −3.9 |
| iode (detrended) | 0.728 | +0.4 | +20 | +70 | −5.7 |

Reading (figure: `figures/sharp_ladder.png`, JSON:
`figures/sharp_battery_v2.json`):

- **Against a same-spectrum, random-phase null, in-sample r is worth
  ~nothing** (z = +0.3…+3.3): the regression earns its r from the
  target's *spectral shape*, not from locking. The nino4 +3.3 is the
  only index poking above 2 — consistent with the calendar-tooth
  survivor in Test 3.
- **Against the sharp rungs every index is massively significant**
  (z = +16…+217 at n≤3). The fits genuinely know something these
  targets lack.
- **The AR1 floor is the WRONG shape of null**: ρ₁-matched AR1 is
  *smoother at fitting-relevant bands* (curvature 0.11 vs 0.039: AR1
  piles up power at 1–5 yr where the real spectrum has already broken),
  which is why real captures score z<0 against it. "Beat AR1" was never
  the right bar; the right bar is a spectrum-matched null, and then a
  sharpness ladder to show *which* band of variance is doing the work.
- Practical rule going forward: **a capture's honest r is
  r_real − r_flat(α=0, same design)**, and the a1/a2 z's are the
  locking evidence. This retires the AR1 floor as the primary gate
  (it survives only as a convenience screen) and makes the flat IAAFT
  rung the headline null for C1.

## The spectrum-exact sharp synthesis, 1880–2025 (the user's test)

Question: synthesize a monthly series spanning 1880–2025 with **the
same spectral spread** as the soft surrogate but **nowhere near as
smooth**, then fit it through the manifold and run the winding-ridge
analysis. Recipe (`sharp2025.py`): take the amplitude spectrum of real
monthly PDO (IAAFT conserves it — the soft surrogate has it too),
interpolate to the new 1752-point grid, random phase, 20 IAAFT passes
to the full pdo marginal. Two rungs: `flat_a0` (α=0, spread-identical,
sharpness restored by the random phase) and `sharp_a05` (α=+0.5 tilt,
a deliberately over-sharp control).

Texture check (the soft surrogate's tell was curvature ≈ 0.0002–0.0003,
~100× below real; lowfrac = fraction of power at periods > 10 yr):

| series | ρ₁ | curvature | lowfrac(>10yr) |
|---|---|---|---|
| real pdo (1880–2022) | 0.9668 | 0.0386 | 0.406 |
| soft surrogate | 0.9946 | 0.0003 | 0.336 |
| **flat_a0** | **0.9666** | **0.0401** | **0.412** |
| sharp_a05 | 0.8490 | 0.2681 | 0.063 |

`flat_a0` matches real PDO on every statistic that matters (ρ₁, ρ₂,
curvature, spectral spread) with zero locking by construction.

**Fits, shipped PDO design (pdo manifold, `lt.exe.p` windings, σ=10):**

| target | r (n≤3) | dCC (n≤3) | r (n≤6) | dCC (n≤6) |
|---|---|---|---|---|
| real pdo | 0.814 | 0.254 | 0.877 | — |
| soft surrogate | 0.865 | 0.256 | 0.904 | — |
| **flat_a0** | **0.820** | **0.288** | 0.871 | 0.379 |
| **sharp_a05** | **0.636** | 0.299 | 0.750 | 0.399 |

Exactly as the ladder predicted: the smoothness gift is removed — r
collapses from the surrogate's inflated 0.865 to 0.820, **statistic-for-
statistic indistinguishable from the real capture's 0.814**. A random-
phase spectrum-exact series fits the manifold as well as real PDO
does. In-sample r: dead as evidence, now on a sharp, realistic-texture
target too. (dCC note: the fit tracks flat_a0's monthly wiggles *better*
than real's — 0.288 vs 0.254 — micro-texture correlation is also partly
texture-fitting, not locking.) sharp_a05 at 0.636 shows the opposite
failure mode: over-sharp targets fall below the real-capture level.

**Winding ridge analysis** (production-manifold forcing extended to
2026, AR1 floor per rung, σ=15 yr, dm=0.004): `flat_a0` yields 2
candidates, best 0.444 (2.57 bits) but **continuity 0.56 → FAIL**, and
at the claimed position band-bits 1.19 / cont 0.63 — versus real PDO's
2.8 bits / **cont 1.00 PASS** at 0.448 on the same grid. `sharp_a05`
yields **no candidates at all** (band sits 2.7 bits *under* floor,
cont 0.00). The ridge instrument answers NO on both new fakes even
though one of them reproduces the real index's r perfectly.

Board: [`figures/sharp2025_board.png`](figures/sharp2025_board.png)
(4 obs/fit rows + ridge band spectra); JSON
[`figures/sharp2025_results.json`](figures/sharp2025_results.json);
series files [`sharp2025_flat_a0.dat`](sharp2025_flat_a0.dat),
[`sharp2025_sharp_a05.dat`](sharp2025_sharp_a05.dat).

