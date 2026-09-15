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
