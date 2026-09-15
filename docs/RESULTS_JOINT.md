# RESULTS — Wave 1 adjudication (2026-09-14)

Kill-table rows adjudicated. Parent-agent re-verification per plan §5
(nothing accepted on subagent self-report). Ledger:
verdicts/AG{1,2,3,4}.json + armed/adjudicate_w1.py, armed/adjudicate_oos.py,
armed/position_fpr.py (all sha256-able).

## Headline: 2 KILL, 1 PASS, 1 PASS-with-protocol-caveat

| row | claim | verdict | after re-check |
|-----|-------|---------|----------------|
| K1  | blind F(t) reconstruct + dLOD r>=0.99 | AG1: KILLED | CONFIRMED — but claim was mis-stated; see K1' below |
| A2  | transform reimpl reproduces ridges | AG2: KILLED | PARTIAL — kill is floor-convention-dependent; position-locked FPR says ridges are real (see d) |
| A4-fetch | PSMSL raw obtainable | AG3: PASSED | CONFIRMED: 115 RLR files, sha256 manifest, Brest 2310 mo (1807-2025) |
| K3  | fit-half vs predict-half M stability | AG4: PASSED | PASSED-AS-RUN, but protocol was weaker than intended (m never refit); true test needs lt.exe half-runs |

## K1 — the real finding

AG1 rebuilt F(t) = sum of 42 unit-amplitude Doodson cosines from the Ada
definitions alone (correct periods to <=0.0001 d). Result:
- F_AG1 vs raw IERS dLOD (1973-2024 annual, n=52): max |r| ~ 0.31-0.75
  depending on pairing/lag — NOT >=0.99.
- F_AG1 vs our col-4 forcing: r = 0.046 — the naive definition-sum is not
  the operational manifold (my re-check).
- Decisive: fitting 89 params (42 amps + phases) to 52 annual dLOD points
  gives in-sample r=1.0 BY CONSTRUCTION; split-sample out-of-sample r=0.52
  and 0.61.
- AG1 leakage: none. Also: eop.data.1846.2 is 404; pre-1956 UT1/LOD
  unavailable in C01 (n=17 for the 1956-72 blend — short-window r=0.93
  there is noise-fragile).

KILLED: "the manifold shape is predictable from published astronomy
without fitting" (strong independence reading).
SURVIVES (K1'): "F is a Doodson-argument manifold whose 89 amplitudes/
phases were regressed on measured dLOD; r=0.99+ is that in-sample fit,
out-of-sample ~0.55-0.61, i.e. REAL but MODERATE predictive skill."
CRUCIAL: the non-circularity-vs-CLIMATE claim is untouched — the fit was
to LOD, not to any index. But public language must change: say "calibrated
by regression to dLOD (OOS skill r~0.55-0.61 on 52-yr annual series),"
never "independently verified at r>0.99." Our dlod_compare.csv r check was
the same in-sample statistic — I reported it as verification of a stronger
claim than it supports. Corrected in this ledger and flagged for repo docs.

## A2 — transform reproduction

AG2 from-spec reimpl: synthetic recovery PASSES (0.449->0.45, 10/10 seeds).
AMO under amplitude-matched floor: no ridge passes triple test; and under
a white-ish floor, 0.0134 "passes" while its time-reversed control passes
equally (cont 0.86 vs 0.90). Parent re-check (position_fpr.py, our AR(1)
floor, 24 phase-scrambled + reversal per case, ridge must sit AT the
claimed M +-0.05):

    idx     M0      real   ph-rand hits/24  reversed  p<=
    amo   0.0134   fail        0             0       0.040
    amo   0.2075   fail        0             0       0.040
    pdo   0.4489   PASS        0             0       0.040
    nino4 0.4491   fail        0             0       0.040
    nino4 3.109    fail        0             0       0.040
    baltic 1.2454  PASS        0             0       0.040
    nao   0.8307   fail        0             0       0.040

Reading: at SPECIFIC claimed positions, surrogates score 0/24 EVERYWHERE —
the headline ridges are not spectrum artifacts. But random OTHER ridges DO
pass the triple test under phase-scrambling (e.g. amo 1.95 cont 0.92), and
the fixed-position triple test is convention-sensitive (nino4 3.11/0.45
pass in winding_rank's 24-rep run, fail in the stricter band logic here).
=> AG2's kill is REAL for the threshold-style statistic, NOT for the
position-locked one. Amendment A2 adopted: position-locked surrogate p is
now the primary ridge statistic; triple test demoted to descriptive.

## K3 — as run vs as needed

AG4 (frozen m from lt.exe.p, EXCLUDE=false half-window regression):
5/5 same Mdom at 1950 split, zero harmonic-family jumps at 1940/50/60
(one brest harm9<->base-of-same-family drift event). PASS as-run.

Parent semantic finding (why this is weaker than intended): the m-vector
is NOT refit by forward() — it is read from lt.exe.p, which was searched
using the WHOLE record. So no protocol here yet tests "winding numbers
predict out-of-sample"; only amplitude/phase stability given the modes.

True OOS (EXCLUDE=true: train outside window, score model INSIDE held-out
years; modes still full-record — upper bound on real predictive skill):

    index  holdout 1880-1950  holdout 1950-2026
    amo       0.67                0.85
    pdo       0.45                0.31   << weak link
    nino4     0.55                0.76
    baltic    0.62                0.64

Note the irony for the dynamic-range priority: AMO predicts well
out-of-sample (0.67/0.85 — its in-sample cc 0.70 is honest), PDO does
badly (0.31-0.45 despite in-sample cc ~0.70). If PDO's decadal character
is the narrative's showcase, it is the least predictive half-record.

Amendment A1 adopted: K3-full = re-run lt.exe optimizer on disjoint
halves (true m-blind search), 5 indices x 2 halves = 10 runs, ~1h each
under 2-job cap overnight. Until then K3 status = PENDING-FULL, not PASS.

## Housekeeping

- Working copy diverges from repo: user edited experiments/Feb2026/
  winding_scalogram.py today 12:12 (added gap_mask handling + valid=
  arg); repo copy (1e9ee9da) predates it. Sync + repackage before Wave 2
  publishes any scalograms.
- Repo docs WINDING_SCALOGRAM_FEASIBILITY.md wording on dLOD calibration
  needs the K1' correction before public push.

## K1 adjudication, second pass (2026-09-14): calibration target is dLOD/dt, not the dLOD level

PI correction accepted and verified three ways:

1. SOURCE CONFIRMATION. gem-dlod.adb:115: "Integration step commented out -
   dLOD is already a rate (derivative). If analyzing absolute LOD would need:
   Amplitude *= 26.736/f_i; Phase += Pi/2" -- a pi/2 phase advance + 1/omega
   scaling IS sinusoidal integration, and 26.736 = 365.25/13.66 = annual
   convolution of fortnightly Mf. The regressed quantity is the rate
   d(LOD)/dt (torque); the impulse-convolved LTE model produces its integral
   (angular momentum -> LOD). Conservation of angular momentum.

2. DATA CONFIRMATION (armed/derivative_definitive.py, monthly, n=684,
   dlod3.dat 1962-2019 vs eopc04 col12 LOD, lag-scanned +-12mo):
     corr(ref,  LOD level)      max 0.196   <- ref is NOT the level
     corr(ref,  d LOD/dt)       max 0.558   <- derivative signature
     corr(cumsum(ref), LOD lvl) raw 0.878, detrended 0.786
                                           <- INVERTING the operator works
   Integration recovers the level at r ~ 0.8; that closes the loop. AG1's
   K1 test paired level-vs-level (their annual-max was 0.31-0.75) -> tested
   the wrong physical quantity for the strong form.

3. LIMIT, stated honestly: with the corrected target, AG1's blind
   definition-sum F_AG1 vs monthly d(LOD)/dt is r = -0.045 and our col-4
   forcing vs d(LOD)/dt is r = 0.04. So the derivative correction does NOT
   rehabilitate the strong reading ("astronomy alone predicts LOD"); it
   fixes WHAT is predicted, not how much skill the blind reconstruction has.
   The r>0.99 in dlod_compare remains what K1 said: the in-sample LTE-fit
   regression skill of the manifold basis against the RATE series; OOS
   0.52-0.61. AG1's kill stands; the claim being killed is now stated
   correctly.

Docs (blurb/README/feasibility) corrected to: manifold calibrated by
regression to measured dLOD RATE d(LOD)/dt; model output is its integral
via annual-impulse convolution (conservation of angular momentum); in-sample
r>0.99, split-sample OOS ~0.55-0.61; LOD-level reconstruction via
integration r ~ 0.79-0.88.

## K1 adjudication, third pass (2026-09-14): satellite-era dLOD/dt confirmed
   -- and AG1's OOS estimate was an aggregation artifact

PI verification request, done from scratch (armed/verify_dlod_fit.py):

POST-1962 / SATELLITE-ERA: CONFIRMED. The calibration target dlod3.dat
spans 1962.005-2019.030, step ~1 day, n=20,829 -- and C04's own file
begins 1962-01-01 (start of the satellite/laser ranging era; C01 has NO
UT1/LOD column until 1956). The fit target is the daily rate series
d(LOD)/dt, full satellite era only. Pre-1962 data cannot support the
regression at daily cadence; AG1's 'n=17 blended series' was the
consequence.

REGRESSION REPRODUCED (42 LP tidal constituents + level/K0/trend/accel,
88 params vs 20,829 points):
  in-sample CC = 0.9719 (their dlod_compare reports 0.9951; same mechanism,
  likely extra annual-harmonic terms in the Ada regression)
  SPLIT-SAMPLE OOS: fit 1962-1976 -> predict 1976-2019: CC 0.9601
                    fit 1962-1990 -> predict 1990-2019: CC 0.9595
  (reverse direction 0.978-0.992)
=> CORRECTION TO MY OWN EARLIER CORRECTION: AG1's OOS r~0.55-0.61 was an
artifact of ANNUAL aggregation (52 points vs 89 params -- degenerate).
At the native daily resolution the tidal-manifold fit to d(LOD)/dt has
genuine out-of-sample skill ~0.96 over the satellite era. The strong form
of K1 is substantially rehabilitated: the manifold predicts the observed
rotation RATE out-of-sample at r~0.96, on 43 years held out in the
forward split. K1 final status: PASSED (daily-resolution, satellite-era
dLOD/dt target; public wording: 'regression on satellite-era dLOD/dt,
split-sample prediction CC ~0.96 at daily resolution').

Remaining honest caveats: (a) tidal constituents are exactly periodic, so
long-horizon OOS is easier than for stochastic models -- the skill
measures whether the RATE's tidal structure is what the basis encodes,
which is precisely the claim; (b) dlod3 vs C04-derivative r=0.51 (daily)
-- dlod3 is some smoothed/blended product, provenance of the target file
itself still deserves a footnote; (c) my reproduction used lstsq on the
42-frequency library, not the Ada engine's exact search -- 0.9719 vs
0.9951 gap unexplained but not load-bearing.

## Wave 1.5 (2026-09-14): Ray and Erofeeva 2014 library — claim verification

Source secured: Ray, R.D. and Erofeeva, S.Y. (2014) "Long-period tidal
variations in the length of day", JGR Solid Earth 119, 1498-1509,
doi:10.1002/2013JB010830 (full text cached under campaign/shared_in;
Table 3 "Long-Period Tidal Earth Rotation Rate Coefficients" parsed to
shared_in/ray_erofeeva_2014_table3.csv: 72/80 lines recovered, node line
and ~8 minors lost to OCR; all majors present).

INTERNAL VALIDATION of the derivative relation (PI's conservation point):
the table's own UT(cos/sin) and DL(cos/sin) columns satisfy
UT_amp = DL_amp * T / 2pi at median relative error 0.0003 — Ray's two
reported quantities are literally the rate and its integral.

FIT (dlod3.dat, 1962-2019 daily, 42-period library + 4 trend terms):
- in-sample CC = 0.9719 (reproduces verify_dlod_fit exactly; units
  settled: lpap periods are DAYS; our-as-YEARS variant gives 0.006)
- 36/42 of our library lines coincide with Ray table lines to <1%.
- A_fit vs Ray RATE amplitudes DL: log-amp corr 0.705; median ratio
  0.84, IQR 0.47-1.31.
- The big lines: Mf(13.661d) fit 0.3159 ms vs Ray 0.3594 (0.88x);
  Mf sidelobe 13.633d: 0.1303 vs 0.1490 (0.87x); Mt 0.0857 vs 0.0672
  (1.28x); Mm 0.0857 vs 0.1938 (0.44x); MSf 0.0253 vs 0.0316 (0.80x);
  Ssa 0.0238 vs 0.1735 (0.14x).
CLAIM VERDICT: PROPORTIONALITY CONFIRMED for the lunar fortnightly/monthly
family (Mf, Mf sidelobes, MSf, Mt, MSt within 0.8-1.3x; median 0.84x).
The PI's "divide by period" equals the UT->DL conversion (columns differ
by exactly 2pi/T); against Ray's level column divided by T the same fits
sit at a common ~5.5x (2pi) scale — consistent. NOT confirmed for Ssa
(solar semiannual: fit absorbs it into trend terms — the annual-impulse
aliasing the PI flagged) and Mm (0.44x, possibly the ocean dynamic term).
Correlation 0.705 with a 24x IQR spread is remarkable shape agreement
with real unit-scale/aliasing structure — NOT yet the quantitative
identity a paper figure requires.

LIBRARY DECISION (adopted for Wave 2): the hand-picked 42-line set is
retired as the calibration basis. Wave 2 fits use the full Ray-Erofeeva
line set (80 lines; their threshold-justified selection UT>2us or
LOD>0.4us, J2000 epoch; machine-readable EOP-IE coefficients file to be
fetched from the IERS conventions server; parsed paper table until then).
Ablation B3 reruns against this library. Annual/semi-annual retained only
as nuisance regressors with aliasing documented, per PI — not counted as
tidal evidence.

## Wave 2-pre (2026-09-14): 'prime the pump' — from-scratch manifold attempt, RESULT: NOT YET CLOSED

Target recipe (PI): col4 := integral of [dLOD/dt sampled by annual(+semiannual
fraction) impulse train] tempered by Bessel-type (nodical/perigee) phase
modulation; AMO as pump-prime index (obvious lowest winding = frequency-
doubled 120-yr cycle).

Structural facts established first (why the recipe cannot be a literal
reproduction of col4 from dlod3):
1. col4's 120-yr line = 91.3% of its AC power; longest constituent in the
   fitted library is 18.6 yr. col4's slow structure is an EMPIRICAL clock
   fitted to the index family, NOT tidal-band.
2. dlod3 spans 1962-2019 (57 yr) — cannot contain a 120-yr line at all;
   col4 1880-1962 std 17.5 == post-1962 std 15.3, i.e. col4 was built by
   model EXPLANATION (forward) across the pre-satellite gap, not from data.
3. Fitting the convolution template to d(col4)/dt with 121 (A,b1,b2) grid
   combinations reaches only r=0.02 — my implementation of the stated
   recipe does not describe col4 as built.

Zero-tuning alternative built: F_strict = Ray & Erofeeva 2014 Table 3 UT
lines (the RATE, exactly as published) integrated once -> LOD level ->
cumulative phase, Ssa annual-alias family dropped per PI rule. 72 lines,
no climate-index input.
  - AMO: F_strict PASSes triple test at M=0 (4.11 bits, cont 0.87) but the
    backbone 0.2075 and M=0.449 structures do NOT transfer (FWHM blow to
    0.28-0.38). PDO 0.4489 ridge (col4: PASS, 24/24 position-locked):
    collapses on F_strict to pk 0.28. => The 0.449-family ridges are
    specific to the TUNED col4 clock; the pure Ray clock does not carry
    them at those M.
  - Honest caveat: ridge M scales with clock rate; F_strict's rate differs
    from col4's by ~O(2.5x), so an M-rescaled comparison is required before
    any strong claim either way.

KILL VALUE — null-clock test on AMO low-M ridge (the 'obvious frequency-
doubling' claim), strict triple test at M=0.0134 +- 0.05, phase-random
surrogates 12 each:
  col4        PASS pk3.9 fw0.03 ct0.96  surrogates 0/12
  120-yr sine PASS pk3.5 fw0.05 ct0.87  surrogates 0/12
  40-yr sine  PASS pk3.3 fw0.04 ct0.74  surrogates 0/12
  random walk fail(pk3.8 fw0.09 ct0.70) surrogates 0/12
The AMO low-M ridge is CLOCK-ROBUST: any slow clock finds it. Within-clock
phase-scramble p-values do NOT discriminate between clocks — they only
bound spectral leakage. This is the first concrete demonstration that
position-locked surrogate significance is a NECESSARY but NOT SUFFICIENT
test: low-M ridges require a CROSS-CLOCK invariance control (if the
physics is tidal-clock locking, M must map through clock-rate changes as
M' = M*(Fdot/F'dot) in a predictable way; if it is the index's own
60-yr oscillation, it reappears at every slow clock).

Artifacts: armed/manifold_from_scratch.py, armed/gen/F_gen.csv,
armed/f_strict_test.py, armed/gen/F_strict.csv, armed/null_clock_test.py,
armed/pump_probe2.py (partial: pdo,nino4 done; baltic/amo rows pending),
armed/verify_pump.py. Scripts now under campaign git (see latest commit).

## Wave 2-pre, second pass (2026-09-14): F_strict v1 WAS WRONG (PI caught it on the figure)

Unit bug: Ray & Erofeeva Table 3's UT column is the INTEGRATED tidal UT1
(level, microseconds of time: verified identity UT = DL*T/2pi on every
line), not the rate. v1 integrated it again -> the 18.6-yr nodal line
(DL=159.9 us level at T=6798 d) was amplified 1082x by spurious second
integration -> 'large 18.6-yr cycle' that the PI identified as physically
impossible from memory of the table. PI rule confirmed in data: in the
42-line dLOD/dt fit of dlod3, node/Mf amplitude ratio = 0.016 -- the
direct nodal line is essentially absent from the RATE; nodal information
enters physically only as sidebands of Mf/Mm (envelope, not line).

v2 rebuild (fstrict_v2.py): rate = 2*pi/T * DL for lines T<500 d, Ssa
excluded, integrate once -> level clock. 18.6-yr power in v2: 0.00%.
AMO/PDO/nino4/baltic ridge tests on v2 vs col4 (strict triple test,
position-locked):
  pdo 0.4489: col4 PASS (pk2.86 ct0.88)  v2 fail (pk1.60 ct0.15)
  baltic 1.2454: col4 PASS (pk4.03 ct1.00) v2 fail (pk2.88 ct0.52)
  amo 0.0134: col4 marginal in this floor config, v2 fail (ct0.04)
=> Same conclusion as v1 minus the artifact, and now robust: the correctly
built, zero-tuning Ray clock does NOT carry col4's ridge structure at
those M (rate-scale caveat stands: v2 swings dF/dt ~+-400/yr vs col4
+-70/yr; M-rescaled remap test still open).
Figures: gen/fig_fstrict_v2.png (v1 vs v2 vs col4), gen/fig_series.png,
gen/fig_col4_spec.png (stacked time series of all objects + col4 spectrum).
Scripts: armed/fstrict_diag.py, armed/fstrict_v2.py.

### Amendment (same day): second unit/logic bug in v2 build caught by parent
(a) 'Ssa dropped' exclusion matched ZERO lines (OCR csv has blank name
column) - solar annual+semiannual lines were still in v2. Re-excluded by
PERIOD (365.25/182.62/121.75/91.31/73.05d +-1.5): 11 solar lines + 6 long
lines dropped, 55 lunar/luni-solar lines used.
(b) v2-vs-col4 clock-rate ratio C = mean|dF/dt| ratio = 27.4. Rescaled test:
pdo col4 ridge 0.4489 maps to v2 M=0.016 -> peak there = 3.03 bits, the
#2 ridge in the whole v2 map (top: 0.73/0.03/1.43/0.25/0.44 at
3.27/3.03/2.99/2.88/2.83). SUGGESTIVE that v2 clock ridges sit at
M/C - i.e. tidal lines DO phase-lock pdo at a rate-rescaled winding - but
mean|dF/dt| is a crude warp for non-monotone clocks and 0.016 sits in the
red-noise-prone low-M regime; NOT claimable until a proper time-warp
matched-rescaling control is run (registered as Wave-3 item: M-rescaling
discrimination test with DTW or phase-monotone segments).

## Wave 2-pre third pass (2026-09-14): PI mechanism checks - 40:1 alias +
   sample-and-hold convolution; v2 sawtooth diagnosis

(1) 40:1 CONFIRMED arithmetically: Mt = 9.1330 d -> 365.2422/9.1330 =
    39.99148 cycles/yr; drift -0.00852/yr -> annual sampling of Mt aliases
    to a 117-yr rolling envelope. Pure-Mt hold-convolution synthetic
    (pump_v3b) gives dominant long period 72 yr @49% AC (half-alias;
    record is 145 yr = 1.2 cycles so peak splits), steps quantized by
    the year - the PI's mechanism reproduces as stated.

(2) v2's 'semi-annual convolution look' DIAGNOSED: my monthly cumsum of a
    rate containing Mf (13.661 d = 26.736 cpy) ALIASES the fortnight under
    1/12-yr sampling: 26.736 mod 12 = 2.736 cpy = 133.5 d - exactly the
    64.9% peak in both v2 and the analytic-level v3 monthly spectra. So
    the visual was a sampling artifact of the FORTNIGHTLY, not a real
    semiannual impulse. (Ray level column used directly in v3 does NOT
    fix the monthly-grid alias - 133.48 d is the true aliased appearance
    of a 13.66-d line read at 1/12 yr; on a fine grid F_strict_v3 is
    correct.)

(3) PHYSICAL hold-convolution fit to col4 with the back-extrapolated
    dlod3-rate (hold_convolve.py, 3 free: month x12, f_semi x7, damp
    0.5-1.0 x101 = full coverage): BEST r=+0.223 (month=Dec, f_semi=0,
    damp=0.79); post-1962 0.47, pre-1962 0.24. The correct
    sample-and-hold manifold from pure dLOD/dt physics explains ~0.2-0.5
    of col4 - NOT the 0.92 of the smooth leaky version, and nowhere near
    the 0.964 curve ceiling. Damping optimum 0.79 (strong leak) means the
    PI's 'slight damping to keep integration from drifting' is exactly
    what's needed, but the resulting staircase is too weak to be col4.
    => col4's pre-1962 120-yr sawtooth is STILL not reproduced by any
    zero-index-tuned construction; the honest status of the manifold
    origin claim: rate fit good (r 0.92-0.97 post-1962 by smooth path),
    staircase mechanism real (117-yr alias confirmed), but col4 as
    provided contains index-fitted clockwork the physical path cannot
    yet reach.

(4) Ridge battery on clocks: F_strict_v3 (analytic level, no cumsum):
    baltic 1.2454 pk3.41 ct0.33 (fail; was 1.99/0.00 in v2); pdo 0.4489
    pk0.99 (fail). Generated F_hold clock: AMO top ridge M=0.40 (vs col4
    0.66), nino4 0.58 (col4 0.62), pdo 0.94 (col4 0.44) - ridges EXIST on
    the generated clock at comparable power but M positions do not map
    through the simple rate-ratio warp (C=27 for v2; F_hold swing is
    different again). Cross-clock M-rescaling discrimination remains the
    registered Wave-3 test; simple linear rescaling is now ruled out as
    the mapping for at least pdo/amo.
Artifacts: armed/pump_v3.py, armed/pump_v3b.py, armed/hold_convolve.py,
armed/fstrict_v3.py, gen/F_strict_v3.csv, gen/F_hold.csv,
gen/fig_mt_impulse.png, gen/fig_v2_vs_v3.png.

## Wave 2-pre fourth pass (2026-09-14): lte_forward.py schematic CLOSED the
   loop -- comb+IIR+FM pipeline REPRODUCES col4 (r=0.9991); Ray-only
   calibration through it: 0.666; ridges do NOT transfer. The decisive
   finding: col4 = index-fitted constants x dLOD-calibrated structure.

PI relaxed the peer-review constraint and pointed at lte_forward.py as the
schematic. It was the missing key. Structured probes (pump_v4..v8):

1. ARCHITECTURE NOW EXACT. lte_forward Calc_Forcing = tide_sum(42 Doodson
   lines, lpap amps/phases; JERK=0 per resp) x impulse_delta(MONTHLY comb:
   delA=-4.2255 at delB -> DPos=13/12 rounds to Jan; asym=6.244 semiannual
   at +6 slots) -> iir(mem=1-1.4e-5~1, signed leak mp=-0.0042, init
   seeded at IDATE=1880, backward pre-history pass) -> bessel FM
   (impA=-3.26, impB=-5.09, k=M[NM-1]=0.20749! 2nd harm offs/bg).
   Pushing the FITTED lpap constants through this chain reproduces col4
   at r=0.9991 (the known forward-verify result, now used as a control).

2. THE PI's 40:1 MECHANISM VALIDATED STRUCTURALLY. v5 (zero-structure:
   Ray rate x pure annual comb -> cumsum): corr with col4 only 0.147,
   monotone ramp (decreasing frac 0.00) -- yearly sampling phase-pins
   EVERY lunar line (40.0, 26.7, 13.4 cycles/yr: near-integers), so only
   the drift envelope survives integration: exactly the aliasing the PI
   predicted, and why the REAL pipeline needs (a) the leaky/seeded IIR
   pre-history and (b) the Bessel FM warp to wind at all. v6 (comb->ramp->
   FM, k/eS/eC grid): corr 0.63, dec% 10 vs col4's 45, ridges fail.

3. THE CLOSED LOOP (pump_v8): same fitted comb/IIR/FM constants; ONLY the
   84 tide coefficients re-estimated vs the integrated-dlod3 LOD LEVEL on
   1962-2019 (zero index data). Result: corr(pipe(Ray-calib), col4) =
   0.666 in the calibrated window (vs 0.9991 with the index-fitted lpap).
   Ridge battery at col4 positions: amo 2.45/0.15/0.00 fail, pdo fail,
   baltic fail. Interpretation: the MANIFOLD MACHINERY is dLOD-real
   (66.6% of col4's variance is recoverable by the physically-calibrated
   input through the real structure; the pre-FM span check 0.72), but
   col4's exact clockwork -- and its position-locked ridges -- require the
   INDEX-FITTED constituent constants (lpap is fitted to the climate
   index by the Ada search, not to dlod3).

4. CONSEQUENCE (this is the answer to 'prime the pump'): the pump CANNOT
   be primed from dLOD/dt alone into a manifold that carries the observed
   ridge positions. Verified dead ends: raw Ray-sum (r=0.147), curve-fit
   ceiling vs Ray-only input (0.22 hold-convolution; 0.63 FM-ramp;
   0.666 full-structure-calibrated), definition-sum (AG1, r<=0.75).
   The surviving positive: on the SATELLITE ERA the pipeline input stage
   IS dLOD-calibratable (0.666 with fixed structure) and the RATE fit has
   genuine OOS skill (0.96, K1 third pass). So the honest reading is
   HYBRID, and now exactly localized: structure (comb/IIR/FM) fitted to
   the index, tide constants fitted to the index, calibration-vs-dLOD
   establishing that the fitted object is dLOD-consistent to r~0.67-0.995
   in-sample at the RATE level. K1' final form: manifold is dLOD-CONSISTENT
   (regression-verified on rotation rate, in-sample>0.995 on the level
   through the full chain), not dLOD-DERIVABLE (blind: <=0.67 through the
   real structure; <=0.15 blind structure-free; definition-sum fails
   entirely). Docs already phrase calibration as regression; the
   'derivable' over-claim, where it lurks, must read 'consistent'.

Files: armed/pump_v4.py (calib grid vs integrated dlod3), v5 (pure-comb
alias ramp), v6 (ramp+FM), v7 (full structure, Ray amps+fitted phases),
v8 (full structure + dlod3-re-estimated coefficients: 0.666 control);
gen/F_scratch_v5..v8.csv. The AMO M=0.0134 ridge pk=2.45 (v8) with
continuity 0.00: the low-M content is present but not stationary --
stationarity claims still rest on col4 and await K3-full.

### Post-audit notes (same day)
- pump_v4 fit_rate had a phase-sign bug (atan2(c_sin,c_cos) instead of
  atan2(-c_sin,c_cos)); corrected numbers there are only in v8's design
  (v8 used the correct decomposition in the w-weights check). Logged so
  nobody re-derives from v4's printed 0.597.
- Phase audit (armed/phase_audit.py): fitted lpap phases, epoch-converted
  to J2000 (the convention Ray uses; a missing -i and an epoch slip both
  wrecked earlier versions of this check), vs Ray line phases:
  amp-weighted concentration R = 0.31, mean offset -125 deg (Mf -79,
  Mm +110, Mt -67). The index-fitted constants sit PART-WAY between pure
  published tide and whatever the CC search preferred -- quantitatively
  consistent with the 0.666-vs-0.9991 gap. Mean offset ~= -90 deg family
  hints at a residual level/rate convention mix inside lpap itself;
  registered for Wave 3, no claim made.

## K3-FULL preliminary (5/6 runs, 2026-09-15): cold-start refits DO NOT
   reach the production basin -- K3-STRONG KILLED, with honest confounder

Protocol: true cold searches (no seeded lt.exe.p), EXCLUDE=false so TRAIN
window = literal fit window, SOLUTION=40, default resp seeds (NM=2 amo /
NM=3 pdo, IDATE=1880). Each run completed exit=0 after the 10-round
solution loop (~2h51m per wave at 1300% CPU). Final metrics:

  run              train-window        fitted m            (production ref)
  amo/first   1880-1951.25   +0.4728   [5.36, 116.84]      prod amo finalCC
  amo/second  1951.25-2023   +0.3691   [5.15,  42.38]       = +0.9458, m =
  amo/full    1880-2023      +0.2886   [2.76,  42.39]       [-0.0134, 0.2075]
  pdo/first   1880-1951.25   +0.2034   [0.80, 70.27, 12.58] prod pdo finalCC
  pdo/full    1880-2023      +0.1569   [0.86,  6.81, 29.74]  = +0.8510, m =
  (pdo/second still running at commit time)                 [0.593,0.449,0.207]

READINGS:
- Half-vs-half median |dm| for AMO = 37.3 >> 0.05 pre-registered threshold.
- The FULL-RECORD cold control lands at CC 0.29 with m=[2.76, 42.4] -- it
  CANNOT reproduce the production solution either (0.29 vs 0.95). So the
  search space is multi-basin and the production basin is NOT
  cold-discoverable within the standard 10-round budget. The cold optimizer
  escapes to large-order windings (M=42..117) that fit poorly.
- Consequence: K3-STRONG ("an independent 2004-2014-era analysis would have
  landed on this manifold") is KILLED within this budget. But because the
  full control also fails, this run measures DISCOVERABILITY, not
  identifiability of the production solution. It does not retroactively
  affect: the position-locked surrogate ridges (model-fit quality), the
  K1' dLOD-consistency findings, or the production-window CV (AG4), which
  held m FIXED and tested ridge stability of the given model.

INTERPRETIVE LINK to wave-2: consistent with the growing picture that the
production manifold (m, FM constants, pre-1962 clockwork) is an
interactive-warm-start construction -- reachable and stable from its own
history, not findable de novo in standard budget. Physical evidence remains
where it was: post-1962 rate calibration (OOS 0.96), Mf amplitude ratio
0.88, comb+IIR+FM structure reproducing col4 at r=0.9991.

REMAINDER: K3-WARM closes the identifiability question properly: seed the
PRODUCTION lt.exe.p into half-record dirs, refit, measure |dm|. If m stays
near production in BOTH halves, the defensible stationarity claim is LOCAL
identifiability (production = local attractor of both halves' likelihood),
which is what the scalogram ridges actually require. Scripts:
armed/k3_full.py (cold, done) + warm variant to add SEED_PROD=1.

(campaign session, 2026-09-15 05:05 CDT, parent re-verified all CC values
by direct recompute from lte_results.csv)

ADDENDUM 2026-09-15 07:30 CDT: the host rebooted overnight (uptime 2 min at
07:25). pdo/second died mid-search with no lt.exe.p -> cell lost; partial
dir preserved as k3_pdo_second.LOST-TO-REBOOT and the run relaunched cold
from scratch (pid 2939, same protocol; ETA ~3h single-run). Driver fixes
committed: SEED_PROD=1 now routes to separate k3w_* dirs (prefix() in
run_dir_for/status/collect -- previously warm would have collided with the
cold dirs), and re-runs skip dirs with RUN_DONE instead of aborting, so one
crash no longer blocks the queue. K3-WARM remains PA pending go.

## VOID — K3-FULL section above is retracted (2026-09-15, PI correction)

Protocol autopsy after PI caught that LPAP was never set: ALL five
finished cold runs saved 42/42 tidal amplitudes = 0.000000
(verified programmatically vs production's max|amp|=0.323). Mechanism:
cold (no lt.exe.p) -> JSON read fails silently -> resp carries
DLOD_REF=TRUE -> "Referencing dLOD" branch stores LPRef but loads NO
amplitudes into LPAP. The cold searches therefore optimized a
degenerate zero-forcing model; their CC/m values (0.16-0.47, M=42-117)
characterize THAT bug, not basin reachability. Consequences:
- "production basin not cold-discoverable / K3-strong killed" = VOID
  (artifact). True status of K3-strong: UNTESTED.
- K3-WARM as designed (seed production lt.exe.p, refit halves) is
  circular for the campaign purpose: it re-establishes the production
  manifold from itself; it does not test from-scratch derivability.
  PARKED, not queued.
- All processes killed 07:5x (pids 2919/2938/2939/3134/3866/3885);
  k3_* dirs retained as bug evidence only.
- Status-line note: NLOOPS=1 DOES emit periodic "Status:" (smoke test,
  k3_status_smoke/) but it releases only on strict best-metric
  improvement — near-useless for liveness. The smoke's first Status
  (0.47282/0.36892) matching old amo/first finals is what exposed the
  zero-forcing bug.

Correct K3 direction per campaign premise: the from-scratch analysis
(pump_v8 structure calibrated on dlod3; F_scratch v2), NOT refits
inside the production Ada pipeline seeded at its own manifold. If a
true cold optimizer test is ever wanted, it needs `-r` (dLOD amplitude
load) or DLOD_REF=FALSE — logged as a known lt.exe cold-start trap.

## WAVE 3 (2026-09-15): sine-modulation fits of FROM-SCRATCH manifolds —
   production ridge positions DO NOT transfer. K2-line = RED.

PI goal restated: x(t) = sine modulations of a manifold built from
published astronomy + dlod3 calibration only; production col4 demoted to
control. Three manifolds: F_v3 (Ray table -> analytic level clock, zero
tuning), F_v8 (pump_v8: same structure, 84 tide coeffs re-estimated vs
dlod3 rate 1962-2019, zero index data), F_col4 (control).
Scripts armed/fitsin.py (global harmonic-of-MF fits, train/hold halves),
armed/diag_fitsin.py, armed/fitsin_ridges.py (winding_rank scan 17 idx x
2 scratch Fs), armed/fitsin_rescale.py (M/C anchor mapping, C_v3=27.9).
Artifacts gen/fitsin_results.json, gen/fitsin_ridges.json.

1. GLOBAL FITS: regression on {cos,sin}(2pi n M F), n<=4, M-grid searched
   train-only: mean held-out CC ~ +0.02 on v3, +0.03 on v8, +0.01 on col4
   — NO out-of-sample predictive skill from any manifold via global
   harmonics. col4's scalogram skill is local-window phase-locking, not
   global regression: this test neither grants nor denies it, but it kills
   any paper claim phrased as "the index IS a sine modulation of F".
2. V3 ALIASING (fatal to its ridge scan): mean|dF/dt|=166/yr -> resolvable
   M<=~0.4 on monthly data; its 42 "qualified" ridges sit at M=2-5 (aliased
   noise), spread randomly, and the pdo_iaaft_detuned negative control
   PASSES 2 of them -> v3 passes are not index-discriminating. The
   rate-legit low-M test is the M-rescaled anchor map (M_col4/27.9):
   amo/pdo/nino4/baltic anchors all FAIL or no-candidate (except the
   PI-flagged AMO low-M clock-robust artifact, which is uninformative by
   construction — Paul: "starting with amo is guaranteed to generate a
   strong low frequency ridge").
3. V8: 0 qualified ridges across ALL 17 indices; anchor map (C=0.7) also 0.
   Clean, decisive: the dlod3-calibrated from-scratch clock carries none of
   the production ridge structure at any position.
4. CONTROL INTEGRITY: F_col4 (amo's manifold) correctly FAILS to produce
   ridges for the detuned surrogate (0 pass) — the triple test works when
   the manifold is the fitted one. Note noi passes 6 ridges on F_col4:
   high-M triple-test selectivity is not FPR-calibrated (K5-family caveat
   stands).

ADJUDICATION vs PREREG: K2 (baltic order-6 ridge under blind pipeline on
A1-style F) = RED: baltic's 1.2454 does not exist on v3 or v8 at any
rescaled position. K3 from-scratch = RED for the transfer form (ridges are
manifold-specific to index-fitted constants). Per CAMPAIGN_PLAN §7 this is
the "K1/K2 red" branch: the qualifications verified inside our pipeline do
NOT survive export to a from-scratch manifold. What SURVIVES unchanged:
K1' rate calibration (OOS 0.96), structure closure r=0.9991, pump_v8
dLOD-consistency 0.666, and the ridge positions AS PROPERTIES OF THE
INDEX-FITTED MODEL ONLY. Public story must be cut to the hybrid claim:
"sine modulations of an index-fitted manifold whose constituent constants
are dLOD-consistent" — never "sine modulations of the dLOD-calibrated
astronomical clock".

## GATE A/B (2026-09-15, PI two-gate test on the wave-3 result)

PI gates: (A) recover F_col4 by calibrating LOD params from scratch +
fitting the annual impulse comb; if impossible, state physical
implausibility. (B) apply lowest-winding sine to F_col4 and capture AMO
at CC>0.70 immediately; if not, state implausibility.
Scripts armed/gate_a.py, gate_a2.py, gate_b.py, gate_b2.py.

GATE A — FAIL against a >0.9 recovery bar; honest ceiling 0.69.
dLOD-only calibration of the 84 tide coeffs through the real chain
(comb/IIR/FM fixed at production values in pump_v8; comb phase/asym/FM
swept in gate_a2), scored vs col4: best IN-WINDOW |corr| = 0.6935
(1962-2019, the only span with daily LOD data), best FULL-RECORD =
0.5257; pump_v8's single config = 0.666 / 0.172. Two apparent "wins"
(0.94 in-window, 0.756 full) were caught and EXCLUDED: both grid points
had delB/asym combos making the comb identically zero (max|comb|=0), so
lstsq matched smooth IIR ramps against col4's smooth ramp — scale-free
correlation of trend artifacts, not shape. >0.9 FULL-RECORD recovery is
physically IMPOSSIBLE, two independent reasons: (1) dlod3 begins
1962.005 (IERS C04; C01 has no daily UT1 pre-1956.3) — the pre-1962
clockwork of col4 is not constrained by ANY measured LOD, so
recovering it "from dLOD" means knowing unmeasured data;
back-extrapolation was separately measured at r=0.26 pre-1962 vs 0.92
post. (2) the comb/FM warp constants themselves were fitted to the
climate index (they ARE what carries ridge positions; pump_v8
localized this). So col4 = hybrid, exactly as wave-3 said: dLOD-real
structure in-window, index-fitted elsewhere.

GATE B — the capture exists at production's own basis, NOT bare.
- Bare single sine, lowest M=0.0134 on F_col4: CC=+0.625 (M-scan best
  over all low M: 0.627; 2-harmonic: 0.630) — below 0.70, so the
  literal "immediately CC>0.70" FAILS for a bare modulation.
- Production regression basis (modes + k0*F + annual/semiannual +
  trend, nonlin=1): mode0 only 0.648; mode0+mode1(0.2075) 0.726 > 0.70
  PASS; production col2 itself 0.789.
- MECHANISM CONTROLS (the hard part): AMO's own 66.5-yr sine ceiling
  0.667, 3-harmonic calendar wave 0.694; calendar sine at the winding's
  apparent period (150 yr) 0.497-0.052; winding sine BEATS that
  particular rival (0.625 vs 0.497) — col4's non-monotone warp helps.
  BUT a matched-parameter rival (2 free calendar freqs + harmonics +
  same calendar block, 12 params, grid-fit) reaches 0.738 > winding's
  0.726. Per PREREG K6 ("baseline matches winding held-out CC with
  <=2x params = RED"), global-capture superiority on AMO is RED:
  AMO's global fit is its ~66-yr oscillation wearing whatever clock is
  offered — exactly the clock-robustness finding, and the PI's
  "starting with AMO guarantees a low-frequency ridge" warning, now
  quantified against matched rivals.
- What survives untouched: the ridge evidence was never global capture;
  it is LOCAL-window phase-locking on the index-fitted manifold
  (position-locked surrogates 0/24; gate_b2 phase-shuffled-F control
  median |CC| 0.407, max 0.598 vs observed 0.657 — col4's increment
  ORDER does matter for the global fit, p~0.04-0.08).

SYNTHESIS for the paper's claims: Gate A sets the honest manifold
statement (structure dLOD-consistent in-window ~0.67-0.76 ceiling
without index data; full recovery impossible for stated reasons);
Gate B sets the honest AMO statement (CC>0.70 needs >=2 modes +
calendar terms on the fitted manifold, and matched calendar rivals
score equal — so AMO supports "phase-locked local structure", not
"global sine capture"). pdo/nino4/baltic ridges remain the
discriminating evidence; AMO is excluded as a showcase (PI rule).

## YEAR-LENGTH KNIFE EDGE (2026-09-15, PI physics point + chart mandate)

PI: the assumed year length (365.2422-365.259) slides the annual-sampling
alias of the 9.133-d Mt line (40 cpy boundary), which is the ~60-150yr
comb structure — and what matters is the chart, not the number.
Charts: armed/fig_yl_sweep.py -> gen/fig_yl_sweep.png (4 rows, obs vs
fit + dF/dt envelope); armed/fig_yl_curve.py -> gen/fig_yl_curve.png
(continuous r(yl) sweep, 0.0001-d resolution).
VERIFIED: r(AMO winding fit) oscillates 0.31-0.70 across the physical
yl range. Tropical 365.2422: r=0.311 (alias 117 yr, red curve flat —
misses the swing entirely); production yl 365.2463 = tropical
+0.00405 (the fitted startup-year candidate): r=0.704, the GLOBAL MAX
of the whole sweep, alias 124 yr, tracks the multidecadal timing with
good amplitude; Julian 365.25: 0.523; sidereal 365.2564: ~0.5;
365.2590: 0.434 (alias 150 yr, phase-shifted ~15 yr early).
Meaning: the 0.70 AMO capture rides on a +0.004-day tuning of the year
definition that parks the Mt comb alias on the AMO band. Short-term
excursions are NOT captured at any yl (visible in fig_yl_sweep: fit =
envelope only) — consistent with local-window ridge evidence being the
substantive content, global capture being envelope + calendar block.
Honest read for the paper: state the yl dial openly as a fitted
parameter with alias-period interpretation (117->124 yr), show the
sweep figure; the sensitivity is the mechanism, not a nuisance.

## SIMULTANEOUS AMO+PDO CAPTURE (2026-09-15, PI stage-2 directive)

PI: PI-reveled AMO fit (yl=365.2463 = tropical + fitted startup
candidate; both indices' own lt.exe.p independently converged year
fields: -4.4400e-6 vs -4.3381e-6 days — 1e-5-day agreement) generalizes
to PDO concurrently on the same dial, windings from winding_scalogram,
tidal factors jiggled slightly. Charts mandated over numbers.
Scripts armed/joint_capture{,2,3,4,5}.py; charts gen/fig_joint_amo_pdo.png,
fig_joint_local.png (6-row: obs/joint-fit/production per index),
fig_joint_final.png, fig_fingerprint_yl.png, fig_joint_yl.png.

METHOD THAT WORKS (v5): ONE year-length dial (365.2463), per-index
manifold from own lt.exe.p ("slight jiggle" = 7.9% median rel amplitude,
0.015 rad median phase vs AMO's — verified quantitatively), windings
amo [0.0134, 0.2075] pdo [0.5934, 0.4489, 0.2073] (both sets
scalogram-discovered), LOCAL-WINDOW MLR fit (sigma=15 yr Gaussian,
one-sided edges) on basis [1, k0*F, sin/cos(2pi M F), annual/semiannual,
trend, accel]. NEW METRIC for the micro lines: dCC = corr of first
differences (PI was right that excursions are captured; r alone missed
it; production col2 anchors: amo dCC=+0.243, pdo dCC=+0.282).

RESULTS (r / dCC):
  AMO joint  +0.782 / +0.259   vs production col2 +0.789 / +0.243
      -> EXCEEDS production on micro-lines, matches macro within 0.007
  PDO joint  +0.640 / +0.164   vs production col2 +0.757 / +0.282
      -> captures all five regime flips (vision-checked 1900/1940/1970/
         1980/2000 timings correct), amplitude muted; gap = the 27
         extra regression cols of full production (per-mode amps,
         jerk=0 both resp, FM k fixed: k=0.2075 amo / 0.2073 pdo)
  PDO on UNjiggled AMO manifold: +0.610/+0.128 -> jiggle earns
      +0.03/+0.036 (modest but real; the fingerprint is the SHARED dial)
Global (non-local) fits cap at 0.70/0.28 — local-window is the right
regime, consistent with wave-3: the winding evidence IS local locking.
Fingerprint surface: r_amo(yl) and r_pdo(yl) oscillate IN PHASE
(common ~0.005-d comb period) — one dial drives both indices' fits;
joint max at production yl.
NOTE: earlier claim "short-term excursions not captured at any yl" is
CORRECTED by the dCC metric + charts — the yl-sweep fits DO reproduce
excursion timing (smoothed amplitude); the vision read of the sparse
fig_yl_sweep was wrong, the 6-row chart shows micro structure present.

## NINO4 + AUTONOMOUS DELAY FEATURE (2026-09-15, PI: "nino4 next; test
autonomous features such as the 12-month delayed differential")

armed/joint_capture6.py generalizes the joint local fit to any index
that has an lt.exe.p, and implements production's lag-12 delay
differential from the Ada source (gem-lte-primitives.adb:1337-1650):
saved Model = L applied (Model[I] -= IR*Model[I-12], reverse order =
exact basis transform); default regression targets DR = Data +
IR*Data[I-12]; UNCOMPENSATED mode instead regresses L*X against raw
Data (GLS/pre-whitening; the source's own comment calls the DR path
"provably non-optimal"). Per-index IR from lt.exe.p: amo -0.457,
pdo -0.711, nino4 +0.160.

Results at yl=365.2463, windings from each index's own ltep (plain /
DR-prod-mode / GLS):
  amo   r = 0.814 / 0.818 / 0.828   dCC = 0.238 / 0.241 / 0.250 (prod 0.243)
  pdo   r = 0.734 / 0.666 / 0.783   dCC = 0.204 / 0.157 / 0.187 (prod 0.282)
  nino4 r = 0.762 / 0.752 / 0.759   dCC = 0.258 / 0.243 / 0.257 (prod 0.318)
- NINO4 on the SAME dial with its own discovered windings
  {0.2073, 0.4491, 0.5604, 1.3851}: r=0.76 >= production's own 0.758.
  ENSO events (72/73, 82/83, 97/98, 15/16 El Ninos + the La Nina dips)
  captured right sign+timing, amplitude compressed (vision-checked).
- DELAY FINDING: GLS basis-folded fit beats production's DR
  approximation where IR is large (pdo 0.783 vs 0.666, +0.12; amo
  +0.010) and ties where IR is small (nino4) — the Ada source's own
  optimality comment, confirmed numerically. pdo GLS 0.783 now
  EXCEEDS production pdo (0.757).
- FINGERPRINT, quantitative: all six original indices' independently
  fitted 'year' offsets land at 365.25059-365.25060 (spread 3e-6 day):
  amo -4.44e-6, pdo -4.34e-6, nino4 -4.43e-6, nino34 -2.79e-6, emi
  -4.42e-6, baltic -5.05e-6. Independent searches, one dial.
- JOINT OBJECTIVE r(mean amo/pdo/nino4) over yl grid: argmax AT the
  production yl (365.2460 vs production 365.2463; mean 0.772); maximin
  peaks there too. Per-index argmaxes scatter (amo 365.2594, pdo
  365.2518, nino4 365.2446) on the coarse 0.002 grid — consistent with
  the ~0.005-d comb oscillation; the SHARED optimum, not the single-
  index maxima, is the fingerprint claim. Charts: fig_joint_nino4.png
  (obs/DR/GLS x 3 indices), fig_yl_multindex.png, fig_joint_objective.png.
Battery sweep over all ~24 index dirs at the yl grid running as
armed/yl_battery.py (results appended when done).

## yl BATTERY — 15 INDEPENDENT PRODUCTIONS (2026-09-15)

armed/yl_battery.py: every index dir with its own lt.exe.p (amo baltic
brest brestexcl emi iode iodw nao nino34 nino4 npi pdo tna tpi tsa),
each fit with ITS OWN windings/IR/constants, swept over yl.
AT yl=365.2463 (production dial, never tuned to these 12 new indices):
mean r=0.760, 14/15 indices r>=0.70 (only nino34 0.629), range 0.629
(nino34) - 0.888 (npi), iodw 0.865, brestexcl 0.828.
Joint objective over the 15: MAXIMIN (min r across indices) argmax =
365.2460 = production yl (min 0.6295) — the worst index is best served
AT the production dial; mean-r is flat (0.741-0.763, oscillation
period ~0.005 d as expected) with a shallow local max at production
and endpoint noise at 365.256/365.260. Per-index argmaxes scatter
across the comb lobes (3/15 within +-0.001 of prod) — the single-index
peak is NOT the fingerprint claim, the SHARED maximin optimum and the
3-microday agreement of the independently fitted 'year' offsets are.
Chart: gen/fig_battery.png (15 curves + joint mean/min).
HONEST LIMITS: (a) these are IN-SAMPLE fits with each index's own
Ada-fitted windings/IR/constants — the battery shows a shared dial
serves every production, not blind prediction (that's the still-open
C1 holdout battery); (b) mean-r flat => yl sensitivity per index lives
in the 0.005-d comb lobes, and the production yl is where the WORST
index peaks, which is the strongest defensible phrasing.

## IODE + TREND DISCRIMINATION (2026-09-15, PI: "upward trend inflates
r; discriminate linear/accelerating trend from the variations")

armed/iode_capture.py: fit = same one-dial manifold (iode own windings
{0.2073,0.4455,0.5555}, IR=+0.028, year_off -4.49e-6). The trend IS
real and captured: r_trend=+0.610, quadratic accelerating rise (flat
to ~1920, monotone concave-up after). Decomposition:
  r_raw 0.838 (local sig=15) / 0.803 -> WITH trend = inflated
  r_var 0.663 -> 0.728 after optimization (sigma 15->10; grid over
        windings x nmax x sigma; best honest config kept WITHOUT
        borrowing AMO's 0.0134 clock-robust mode: +0.746 rejected)
  production col2, detrended identically: r_var 0.548 -> our honest
  fit now EXCEEDS production on detrended iode (+0.18).
Global (non-local) fit iode: r_raw 0.671 vs r_var 0.349 = nuisance
+0.322 -> the local window is what holds the trend.
Battery re-scored detrended (quadratic) at yl=365.2463, sigma=10,
n<=3 (gen/battery_detrended.json): 12/15 r_var>=0.70, mean 0.762.
Trend nuisance is confined to the warming-trend SST series exactly as
PI predicted: iodw +0.34, tsa +0.23, iode +0.11, tna +0.10; all others
<=0.02. Honest headline set now: amo 0.832, nino4 0.833, npi 0.900,
brestexcl 0.847, pdo 0.808 (detrended). Chart: fig_iode_trend.png
(4 rows: raw obs | extracted trend | detrended obs/fit/prod | d/dt).

## BALTIC — THE ORDER-6 RIDGE (2026-09-15, PI: "baltic featured a
predominant strong ridge at winding 1.245")

armed/baltic_capture.py. Baltic's scalogram signature is a single
dominant order-6 harmonic at M=1.2454 (amp 30.95, ~3x next-largest,
triple-test PASS; AG-surrogates 0/24 at that position). Its own
lt.exe.p windings are {0.1223, 0.2076, 0.9247}.

1. RIDGE = 6th HARMONIC OF THE BACKBONE: 6 x 0.2076 = 1.2456,
   matches the scalogram ridge to dM=+0.0002. The 1.2454 "winding"
   is not an independent base mode — it is backbone order 6.
2. The fit CONFIRMS the dominance structurally: capture r rises
   monotonically with harmonic allowance nmax=1..6 (0.662, 0.744,
   0.797, 0.833, 0.850, 0.870) — the 6th order is exactly where the
   scalogram says the energy is; no truncation below 6 suffices.
   Ablations (nmax=6): dropping backbone 0.2076 = -7.9 raw pts,
   0.1223 = -7.2, 0.9247 = -2.8. All three matter; backbone chain
   matters most.
3. r=0.870 at yl=365.2463, sigma=10, n<=6 — EXCEEDS production col2
   (0.705) by +0.165 on the same dial with baltic's own windings.
   Trend nuisance zero (quad frac var 0.001): r_raw = r_var = 0.870.
   dCC micro = +0.379 (highest in battery).
4. OOS DISCIPLINE (armed, this pass): train<1955/holdout split with
   M-fits on train support gives holdout r = -0.01..-0.08 — zero
   forecast skill; causal walk-forward (fit past-only) gives +0.867
   at margin 0 (trivial self-extrapolation of a smooth curve) but
   +0.045 at margin 0.1yr. Same on amo (0.880 -> +0.009). npi
   retains 0.23-0.43 even at 3yr margin (genuine persistence,
   separate finding). => All capture numbers here are DESCRIPTIVE
   retrospective fits, consistent with campaign position (no claim
   of prediction). Baltic's 0.870 stands as: one dial + own windings
   + order-6 chain reconstructs the MSL record better than the
   production fit that was optimized for it.
Chart: gen/fig_baltic_capture.png (obs/fit/prod, variations, d/dt).
