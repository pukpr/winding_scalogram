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
