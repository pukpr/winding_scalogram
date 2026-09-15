# Milestone: one year-length dial, five indices (2026-09)

Marquee figure: [`figures/marquee_stack.png`](figures/marquee_stack.png)

Five climate indices — **AMO, PDO, Nino4, IODE, Baltic** — each overlaid
(obs = grey, model = color) on the **same** winding manifold generated at
the **same** assumed year length **365.2463 days**. The overlays are the
argument: the model curve rides the observed curve through multidecadal
swings, PDO regime flips, individual ENSO spikes, detrended IODE
wiggles, and Baltic's sea-level order-6 texture. Correlation values
alone say nothing; the visual overlap at r ≥ 0.73 across five
independent systems on one dial is what matters.

| index | windings (own `lt.exe.p`) | fit r | dCC (micro-lines) | production col2 r | notes |
|-------|---------------------------|-------|--------------------|-------------------|-------|
| amo    | 0.0134, 0.2075, n≤3        | **0.846** | 0.261 | 0.789 | detrended r_var = 0.832 |
| pdo    | 0.2073, 0.4488, 0.5934, n≤3 | **0.814** | 0.254 | 0.757 | GLS-delayed variant 0.783 plain/DR 0.666 |
| nino4  | 0.2073, 0.4491, 0.5604, 1.3851, n≤3 | **0.842** | 0.246 | 0.758 | ENSO events right sign + timing |
| iode   | 0.2073, 0.4455, 0.5555, n≤3 | **0.728** (detrended; raw 0.838) | 0.246 | 0.705 raw / 0.548 detrended | trend nuisance +0.11 separated |
| baltic | 0.1223, 0.2076, 0.9247, n≤6 | **0.870** | 0.371 | 0.705 | ridge 1.2454 = 6 × backbone 0.2076 |

`dCC` = correlation of first differences — the metric that quantifies
the short-term excursions the r value alone hides. Baltic exceeds
production's own optimized fit by +0.16; IODE exceeds it by +0.18 on
the honestly detrended series; AMO/PDO/Nino4 all exceed production
in-sample on the shared dial.

## The dial

The manifold is built from published tidal constituents (Doodson
definitions, Ray & Erofeeva 2014 amplitudes) through the Ada pipeline's
physical chain: tide sum → monthly impulse comb → leaky IIR integrator
→ Bessel FM winding (`lte_forward.py`, reproducing the pipeline at
r = 0.9991). The assumed **year length enters as the comb's sampling
period**: at 365.2463 days the 9.133-day Mt tide-sampling structure
aliases at 1/(40 − 365.2463/9.133) ≈ **124 years** — placing the annual
comb alias exactly on the AMO/PDO multidecadal band.

The sensitivity is knife-edge and it is a fingerprint, not a nuisance:

- `figures/fig_yl_sweep.png` — AMO obs-vs-fit at yl = 365.2422 (r = 0.31,
  fit visibly fails), 365.2463 (r = 0.70), 365.25, 365.259 (r = 0.43,
  visibly phase-shifted ~15 yr early).
- `figures/fig_yl_curve.png` — continuous r(yl) sweep: oscillates
  0.31–0.70 across the physical range; global maximum **exactly at
  365.2463**.
- `figures/fig_fingerprint_yl.png` — r(yl) for AMO and PDO oscillate
  **in phase** (common 0.005-day comb period): one dial, two instruments.
- `figures/fig_battery.png` — 15 indices, one dial: 14/15 reach r ≥ 0.70;
  the maximin (worst-index) objective argmax is **at** 365.2460 ≈ production.
- Every index's independently converged `lt.exe.p` `year` offset lands
  at 365.25059–365.25060 — agreement across six separate optimizer
  searches to **3×10⁻⁶ days**.

## The manifolds themselves overlay

`figures/manifold_overlay.png` (reproduce: `python3 manifold_overlay.py`
at repo root): all 13 index manifolds used by the milestone +
supplemental fits — each built from that index's OWN jiggled
`lt.exe.p` constants, all on the shared dial — plotted together.

- **12/13 overlay precisely**: r(F_i, mean F) > 0.9976 for all twelve,
  pairwise rms |ΔF| max 1.79 windings (median 0.96) on a signal that
  sweeps ~60 windings over 146 years; each jiggle stays within
  ±3.3 windings of the mean across the whole record. The captures were
  "primarily common" — the manifolds show it directly: the optimizer,
  given 12 unrelated climate records and free rein over ~20 constants,
  converged 12 times onto essentially ONE manifold.
- **kap10-10-20-30 is the exception** (r=0.944, rms dev 6.2): its R
  (IIR output) drifts from the common one at −0.015 windings/yr
  (−2.2 over the record) — a smooth drift, no jumps; the FM warp is
  non-monotone in R (impA=−3.29 with k≈0.2077), so a small R offset
  gets amplified into ±15-winding deviations near FM fold points.

## The jiggle is (almost) unnecessary — ONE manifold suffices

Full write-up with the physical jitter accounting:
**[`JIGGLE_ANALYSIS.md`](JIGGLE_ANALYSIS.md)** — the modeling-
convenience explanation (tidal-factor jitter gives the random-descent
optimizer mobility to escape local minima, per
`gem-random_descent.adb`: "explore parameter space and escape local
minima … probabilistic perturbations"), and the evidence that the
amount of jitter added was inconsequential.

Refit every index on **amo's own manifold** (no jiggle at all), same
windings/σ/harmonics per index (same block, same detrend rules;
continued slicing for the short records): **9 of the other 12 fit
BETTER** on the common F (pdo +0.004, nino4 +0.006, baltic +0.002,
nao +0.020, tna +0.013, emi +0.029, pna +0.019, noi +0.050, kap
+0.024), 2 neutral (brestexcl −0.002, tpi −0.001), and **only iode
actually earns its jiggle** (+0.034 own over common). Mean |Δr| over
the 12 non-amo indices = 0.017. The per-index jiggled constants
therefore carry almost no information beyond the shared manifold —
the jiggles were mild overfitting by the optimizer, with one
exception: iode (the weakly-captured trend series) benefits slightly.
The 0.85-0.87 captures on a SINGLE un-jiggled F are the headline:
one manifold, 13 indices, one dial. Windings remain index-specific —
that is the per-index degree of freedom the scheme genuinely needs.
(table: supplemental_2026_09/figures/manifold_jiggle_test.json;
printed by manifold_overlay.py)

## Honest limits (pre-registered, not after-the-fact)

- **In-sample r is NOT evidence of locking.** Superseding update of
  2026-09-15: the pre-registered negative control
  `pdo_iaaft_detuned_surrogate` fits at r=0.865 — ABOVE real PDO
  (0.814) on the identical design — and the full red-noise floor
  battery (`red_noise_floor.py`,
  [`../supplemental_2026_09/REJECTION.md`](../supplemental_2026_09/REJECTION.md))
  shows AR(1)-matched noise scores in the same range on every index's
  own design. Only two statistics reject the null: ridge continuity at
  claimed positions, and phase-randomised rejection of the calendar-
  locked slow tooth (amo, nino4 only). The r values below and in the
  marquee stand as descriptive fits, not supporting evidence.
- **Descriptive, not predictive.** Train/holdout split (baltic,
  train < 1955): holdout r = −0.01…−0.08. Causal walk-forward with any
  nonzero margin collapses (AMO: 0.867 at margin 0 → 0.009 at 0.1 yr;
  the margin-0 number is trivial self-extrapolation). No forecast
  claim is made or supported. npi is the one partial exception
  (persistence 0.23–0.43 at 3-yr margins) — flagged, not claimed.
- **Manifold is dLOD-consistent, not dLOD-derived.** Calibrating the
  84 tide coefficients against dlod3 (1962–2019, zero index data)
  recovers col4's in-window shape to 0.694 (full record 0.526; a
  > 0.9 full-record recovery is physically impossible because IERS
  daily UT1 starts 1962 and the comb/FM warp constants are themselves
  index-fitted). The defensible sentence: *sine modulations of an
  index-fitted manifold whose constituent constants are
  dLOD-consistent*. Never: "of the dLOD-calibrated astronomical clock."
- **The 0.0134 AMO low-winding is clock-robust** — it reproduces on any
  slow-drifting manifold because AMO's own ~centennial oscillation
  dominates it; AMO is therefore excluded as *discriminating* evidence
  (PI rule), though its macro capture is the marquee headline.
- **Trend inflation is separated.** IODE r_raw = 0.838 decomposes into
  quadratic trend r = 0.610 plus variations r_var = 0.728 (the number
  in the marquee; global fits make the nuisance worse: +0.32). Battery
  detrended: nuisance > 0.1 only on the warming-trend SST series
  (iodw +0.34, tsa +0.23, iode +0.11, tna +0.10).
- The year length is a **fitted dial**: the 12 "new" indices were each
  produced by independent optimizer runs whose year offsets agree with
  AMO's to microdays, but the dial itself was not derived from
  first-principles astronomy — the fingerprint claim is about the
  *coincidence* of the converged values and the joint objective peak,
  not about astronomical necessity.

## Reproducing

```bash
pip install numpy matplotlib scipy            # python >= 3.10
python3 milestone_2026_09/marquee.py          # -> figures/marquee_stack.png
python3 milestone_2026_09/scripts/baltic_capture.py
python3 milestone_2026_09/scripts/iode_capture.py iode
python3 milestone_2026_09/scripts/joint_capture6.py amo pdo nino4
python3 milestone_2026_09/scripts/yl_battery.py    # ~3 min, 15 indices
python3 milestone_2026_09/scripts/fig_yl_curve.py  # continuous yl sweep
```

All scripts read only files tracked in this repo (`<idx>/lt.exe.p`,
`<idx>/lte_results.csv`, `lte_forward.py`). Each index's model uses its
**own** windings / IR / comb / FM constants — the shared ingredient is
the year length, and nothing else about the dial is re-tuned per index.

## File inventory (milestone_2026_09/)

- `marquee.py` — this figure (paths relative to repo root).
- `scripts/joint_capture{5,6}.py` — joint local fit machinery; v6 adds
  the lag-12 delay differential (plain / DR / GLS basis-folded) — the
  GLS variant beats production's DR approximation exactly where |IR|
  is large, confirming the Ada source's own optimality comment.
- `scripts/iode_capture.py` — trend-discriminated capture + chart.
- `scripts/baltic_capture.py` — order-6 ridge decomposition + capture.
- `scripts/gate_{a2,b,b2}.py`, `scripts/fitsin.py` — the from-scratch
  manifold gates (K2-line RED: v8 from-scratch manifold qualifies 0/17
  ridges; v3 aliased) that bound what the marquee can claim.
- `scripts/yl_battery.py`, `scripts/fig_yl_curve.py`,
  `scripts/fig_yl_sweep.py` — the dial evidence.
- `figures/` — marquee + all stage charts; `data/` — battery JSONs and
  the from-scratch manifold grids (F_strict_v3, F_scratch_v8).
- `docs/RESULTS_JOINT.md` (in repo docs/) — the full campaign ledger
  including the VOIDED K3 runs (zero-LPAP cold trap: cold runs without
  a seed + DLOD_REF=TRUE silently fit a degenerate zero-forcing model)
  and every adjudicated kill.

*Prepared 2026-09-15 under the campaign's pre-registration
(docs/PREREG_JOINT.md). Model source: `src/` constants shipped per
index in `<idx>/lt.exe.p`.*
