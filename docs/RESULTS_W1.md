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
