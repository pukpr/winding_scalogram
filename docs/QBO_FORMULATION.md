# QBO as the wavenumber-0 case: formulation

Formal counterpart to [`AMO_SHALLOW_WATER.md`](AMO_SHALLOW_WATER.md)
(§2 forcing, §3 moving gauge) and [`DERIVATION_AUDIT.md`](DERIVATION_AUDIT.md).
Discovery log with raw tables: [`../QBO_K0.md`](../QBO_K0.md). Scripts:
`qbo_k0.py` (manifold + ridges), `qbo_k0_fit.py` (honest battery),
`supplemental_2026_09/qbo_stack.py` (figure). Data: `qbo30/`, `qbo50/`
(monthly zonal wind anomalies, ~1953–2026, 856 rows).

## 1. Why QBO is a different problem from the ocean indices

The quasi-biennial oscillation is a zonal-mean, nearly longitudinally
symmetric shear flow: **wavenumber 0 by construction**. The Atlantic/Pacific
captures (amo, pdo, nino4, baltic, …) are wavenumber>0 features — SST
patterns with longitude structure — whose production forcing is calibrated
through length-of-day (dLOD), an angular-momentum exchange dominated by
that same longitude structure (mountains, ocean tides on topography).

For k = 0 the dLOD calibration is not the relevant anchor. What a zonal
flow *does* respond to is the **ecliptic geometry**: the Moon's node cycle
tilts its declination, and declination is a purely zonal quantity. The
draconic month, 27.2122 d, is the period of that modulation. This is the
physical justification for treating QBO as its own category with its own
forcing table rather than borrowing the ocean backbone.

Formally, start from the same two-layer response chain as AMO
(AMO_SHALLOW_WATER §1–3): with zonal dependence removed (∂/∂λ ≡ 0, so the
Coriolis term couples u to no meridional pressure gradient at the equator
in the k=0 limit — the residual balance is vertical shear, ∂²u/∂z², against
the imposed tidal body force g·∇ζ evaluated at the forcing's own zonal
decomposition). The k=0 component of the equilibrium tide is the
**long-period tide**: terms in (H_m)^n with no longitude factor. Of the
production 42-line lpap table, the k=0-relevant family is exactly

| line | period (d) | amplitude (amo lpap) | character |
|---|---|---|---|
| N (draconic) | 27.2122 | **−3.319 (dominant)** | node cycle → declination |
| Dc (trop. month) | 27.3217 | −0.085 | sidereal |
| Mm (anomalistic) | 27.5545 | −0.033 | perigee |
| Mt / Mf | 13.777 / 13.6608 | −0.18 / −0.046 | fortnightly declination |

Everything else in the table carries a longitude factor e^{imλ}, m>0, and
projects out of a strictly zonal response. (Assumption A-Q1 below: the
declination factors survive as *amplitude modulators* even for m>0 lines —
the table's negative amplitudes already encode declination weighting; the
k=0 subset used is empirical, [26.9, 27.7] ∪ [13.5, 13.9] d.)

## 2. The forcing: draconic family × annual comb

`qbo_k0.py` assembles M(t) from ONLY the family above, through the
production impulse comb and IIR (`product then recursion`, as in
AMO_SHALLOW_WATER §2.4–2.5 — the comb machinery belongs to the calendar,
so QBO keeps it; the dLOD/Bessel stages do not), at the shared dial
**yl = 365.2463 d**. The whole parameter content is the 12-line alias
arithmetic:

    f_monthly = yl / P   →  fractional part = the alias seen by a monthly
                             (or annually-sampled) zonal response

| family line | raw freq (c/yr) | monthly alias (c/yr) | apparent period |
|---|---|---|---|
| N 27.2122 d | 13.42 | **0.4221** | **2.369 yr** |
| Dc 27.3217 | 13.37 | 0.3684 | 2.715 yr |
| Mm 27.5545 | 13.26 | 0.2554 | 3.916 yr |
| Mt 13.777 | 26.51 | 0.5113 | 1.956 yr |
| Mf 13.6608 | 26.74 | 0.7368 | 1.357 yr |

Three facts with no free parameters:

1. **The period.** The observed dominant spectral line of *both* qbo30 and
   qbo50 is **0.421 c/yr = 2.38 yr**. The draconitic month aliased against
   the calendar year predicts **2.369 yr**. Error 0.4%. One astronomical
   number + the calendar gives the QBO period; the Dc/Mt aliases (2.7,
   1.96 yr) bracket the historically quoted 2.2–2.8 yr band, and the
   0.4221+0.2554 = **0.6775 c/yr** cross-sum matches the second,
   specificity-bearing ridge tooth (0.68, §4) to 0.4%.
2. **The modulation.** N − Dc = 18.60 yr is the nodal cycle: the same
   18.6-yr line in the lattice modulates declination amplitude, i.e. the
   QBO amplitude and period wander, with the documented sign and scale of
   the 22–34-month wander of the observed period (TEST2 chirp: local ridge
   slides 0.620→0.670 over 2004–2012, ~0.006 c/yr per yr, QBO_K0.md).
3. **The sampler, not the clock.** comb-only control: no persistent ridge
   anywhere (max cont 0.24). nocomb control: mass scatters off the alias
   teeth. The calendar supplies the sampling that converts draconic
   sub-monthly forcing into the 2.37-yr line, but generates no coherence
   by itself.

## 3. Moving gauge in the k=0 setting

The response identity is the same one verified symbolically for AMO
(AMO_SHALLOW_WATER §3, sympy-exact):

    ζ = sin(k·M(t))  ⟹  ζ̈ − (M̈/Ṁ)ζ̇ + k²Ṁ² ζ = 0,  A(t) = k² exactly.

Two QBO-specific readings:

* **The winding number is the response, the manifold is the forcing.**
  M(t) is built with zero knowledge of the 2.37-yr line: the alias
  arithmetic above says the *sampled forcing* already carries frequency
  k·Ṁ ≈ 0.4221 c/yr at tooth k = 0.42. That the standing-wave coordinate
  then solves the wave equation at that A(t) is the same pullback
  structure as the ocean case; the k=0 manifold's Ṁ is dominated by the
  comb/IIR tail rather than tidal jerk, so turning points (Ṁ = 0, where
  the gauge is singular in form but removable in solution) are calendar-
  scheduled, and their annual spacing is what gives the *comb* in the
  sideband lattice.
* **Propagation is a gauge choice.** A descending shear phase is
  ζ(z,t) = sin(k·M(t) − n·z): the same manifold at every level, phase
  lagging with depth. Production encodes this as **negative ltep**
  (−0.1105 at qbo30): the standing-wave template picks the retrograde
  branch. The qbo50 reconciliation (QBO_K0.md) shows what descent does to
  the winding spectrum: the shared forcing (corr 0.9972 between levels)
  but the coherent harmonics **reorganize from {0.42, 0.68} at 30 hPa to
  the 18–25 × |ltep| comb (2.04–2.79) at 50 hPa** — descent is not a
  calendar shift of one template (a −4-month lag recovers only −0.06 of
  the honest deficit) but a change of which lattice teeth are
  phase-coherent at each level. That is the k=0 analogue of the ocean
  result that different indices sit on different multiples of the backbone
  (baltic = 6×0.2076).

## 4. What the ridge instrument actually convicted (per campaign rules)

Two-level battery (winding_rank + spectrum-exact IAAFT; the honest-r rule
and the IAAFT phase-pinning trap as documented in
`supplemental_2026_09/REJECTION.md`):

| claim | qbo30 | qbo50 | status |
|---|---|---|---|
| 0.421 line = draconic alias | yes | yes | **predicted, replicates across 20 km** |
| 0.42 tooth continuity | 1.00 | 0.88 | **spectrum, not locking** (flat rungs 0.93±0.05) |
| 0.68 (=0.42+0.255 comb sum) tooth | **0.84 vs flat 0.60±0.01 (z≈+24)** | 0.40 vs 0.50 | the one positive locking datum — qbo30 only |
| own-comb fit on production manifold | r 0.809, honest −0.030 | r 0.835, honest −0.023 | capture parity across levels |
| imposed k=0 teeth on qbo50 | — | honest −0.183 | **teeth mismatch artifact, retired** |

Frozen-manifold out-of-sample test across the 2015/16 "disruption" (the
model never saw ≥2015): forecast r = **0.825** at qbo30 (z ≈ +2.4 vs pure
random-phase null 0.016 ± 0.34), W onset predicted and observed
**2015.42**, easterly interruption predicted 2016.17–2016.42, observed
2016.25–2016.33, and replicated at qbo50 on its own teeth (r 0.673, z≈+3).
A plain 2.369-yr sine trained to the same cut misses the onset by 5 months
and predicts no interruption at all: **the anomaly is an interference
node of the {0.42, 0.68} pair (beat 0.255⁻¹ = 3.9 yr), which a single
periodicity cannot produce** — the strongest existence-proof in this
document that the lattice, not the line, is the model.

## 5. Declared assumptions

| # | assumption | risk if wrong |
|---|---|---|
| A-Q1 | the draconic/fortnightly period-window subset ≈ the k=0 projection of the production table | empirical, not derived from a formal spherical-harmonic cut; a rigorous P₂(δ)-based filter might shift family members (the trop-month Dc is arguably m>0 dressed) |
| A-Q2 | monthly-sampled annual comb is the right sampler for a continuous atmosphere | tested: comb-only and nocomb controls both fail to reproduce teeth, so sampler+family act jointly; a finer sampling might move tooth weights, not existence |
| A-Q3 | qbo30/qbo50 datasets are homogenous single-station merges (weatherstation records) | onset dates carry ±1–2 mo record-construction noise; noted the 2015.42 onset is ~2 mo earlier than NOAA-merge estimates |
| A-Q4 | GEM_Chap12's two-layer route as quoted in DERIVATION_AUDIT (doc still 404) | if Chap12's k=0 reduction differs, §3's propagation-as-gauge reading changes; §2 alias arithmetic is independent of it |
| A-Q5 | response teeth are level-specific while forcing is shared | supported by corr 0.9972 forcing identity + 0.808@+4mo shear lag; needs a full 5-level ladder to confirm the reorganization law |

## 6. Falsifiable predictions (QBO-specific)

1. **Ladder replication.** Any independent stratospheric wind level
   (70 hPa, or MERRA-2 reanalysis at fixed level) must show its dominant
   line at 0.4221 c/yr ± 0.005, while its *coherent-tooth set* migrates
   with level exactly as qbo50's did. Level-independence of the line +
   level-dependence of the lattice is the signature; a uniform lattice
   across levels would falsify §3's propagation reading.
2. **Nodal amplitude gate.** The nodal line survives monthly sampling
   exactly: alias(N) − alias(Dc) = 13.4221 − 13.3684 = 0.0537 c/yr =
   **18.61 yr**, the node period unaliased. The QBO amplitude envelope and
   period wander must lock to it: enhanced shear in 1969.4/1987.7/2006.3
   ± 1-yr phases, suppressed ~9.3 yr away. (Partially visible; needs a
   formal multitaper test on a longer record.)
3. **Beat-node recurrence, dated.** The {0.42, 0.68} cross-sum beats at
   0.6775 − 0.4221 = 0.2554 c/yr: node period **3.915 yr**, so
   interruption candidates are scheduled at 2016.2 + 3.915n =
   **2020.1, 2024.0, 2027.9, 2031.8**. The 2016 node was the predicted
   and observed disruption; the **2020.1 candidate coincides with a
   marginal 4-month easterly flicker (2020.17–2020.33, |u| ≤ 0.07)
   splitting adjacent W epochs** — same sign of node, weak amplitude; the
   2024.0 candidate falls mid-E-epoch (2023.50–2024.25), where a node
   suppresses rather than interrupts. Prospective test: a W-epoch
   compression or flicker at 2027.9 ± 0.3 in whatever the operational
   record then is. Nodes drift with the TEST2 chirp (0.006 c/yr/yr on
   0.68 → node spacing lengthens ~1%/decade), which the forecast must
   track.
4. **Cross-sum lattice.** Every tooth of the k=0 lattice must be an
   integer ± combination of {0.4221, 0.3684, 0.2554, 0.5113, 0.7368} plus
   0.25-yr comb sidebands (a lattice census, like AMO §4's but on the
   draconic set). Any strong observed line not representable that way is a
   counterexample.

## 7. One-paragraph summary

QBO is the wavenumber-0 member of the same forcing problem the ocean
indices represent at wavenumber>0: a two-layer response in a moving gauge
whose manifold is built not from length-of-day-calibrated angular-momentum
tides but from the purely zonal ecliptic terms — above all the draconic
node cycle at 27.2122 d. Sampled by the annual impulse comb, that sub-
monthly line aliases to 0.4221 c/yr: the observed 2.38-yr QBO period,
identically at both measured levels, from one astronomical number and the
calendar, zero tuned parameters. The 18.6-yr nodal line and the
comb-sideband lattice {0.42, 0.6775, …} then do the non-trivial work:
their beat nodes — impossible for any single periodicity — predicted the
2015/16 disruption's onset, interruption window, and end under a frozen
cut, and the sideband tooth at 0.68 is the one datum with flat-rung
specificity. What descends through the stratosphere is the phase; what
changes with level is which lattice teeth are coherent — the exact
k=0 analogue of the ocean comb structure, and the reason one manifold
carries both categories while no single sine carries either.
