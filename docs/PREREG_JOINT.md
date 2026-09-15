# PREREG — Manifold Campaign pre-registration (LOCKED)

Hash-locked at commit time; any post-wave amendment requires a new row in
the Amendment Log. Kill-table semantics: docs/CAMPAIGN_PLAN.md §5.

## Thresholds (fixed before any agent runs)

- dm=0.01, m_max=5.0 (9.0 where Mdom>5: darwin1880, npi, noi), sigma=15yr,
  t0_step=5yr; surrogate floor AR(1) rho=0.97 n_reps>=24.
- K1: |r| >= 0.99  (blind-reconstructed F vs raw IERS dLOD)
- K2: baltic ridge  FWHM <= 0.15, cont >= 0.60 (blind pipeline)
- K3: median out-of-sample |ΔM| <= 0.05 on fit-I1/predict-I2 (amo, pdo lead)
- K4: Mm/Mf ablation must cost >= 1 bit at Mdom on >= 5 of 14 indices
- K5: any matched-spectrum synthetic clock within 1 bit on >= 5 of 14 = RED
- K6: any standard baseline matches winding held-out CC with <= 2x params = RED
- K7: >= 50% of never-analyzed holdout indices show integer-harmonic ridges
- K8: forced-simulation M recovered at observed-record SNR

## Discovery / holdout split (contamination register)

DISCOVERY (manifold-fine-tune era, 2026-08/09; snapshot evidence):
  nino4 pdo amo tna nao baltic iode emi nino34 darwin1880 npi pna noi tpi
  qbo30 qbo50 + intermediates 88 111 brest brestexcl tsa iodw kap10-10-20-30
  atlbox5n15s  (+ negative control pdo_iaaft_detuned_surrogate)

HOLDOUT-C1 (never fit, never analyzed; need data pull first):
  ao, iod, m6 (Atlantic Nino), m4 (NPGO), nino3, nino12, denison, ic3tsfc,
  12 PSMSL composites (Britain-78, ecoast-91, nz, sea, gom-64, med-158,
  maritimes-33, australia-95, spacific-102, japan-187, wcoast-51, alaska-33),
  ~60 individual gauges in ID.yml with no local dir, fresh PSL boxes
  (psl_extract.py) over Arctic/Indian/S-American regions.

## Priority per PI directive (2026-09-13): dynamic range

Largest-variance records sample the manifold most fully -> run these FIRST
in every test (census std dev of raw .dat):
  tier0: 88/Fremantle 65.4 | 111/Ratan 47.3 | brest 42.9 | brestexcl 44.5 |
         baltic 36.5   (MSL, mm units)
  tier1: amo 2.09 | pdo 1.16 | darwin1880 1.06 | pna 1.04   (anomaly idx)
  tier2: nino34 tpi nino4 nao ... (already characterized)
B2 predictive-CV order: amo, pdo (PI-named), then baltic+brest, then nino4.

## Wave 1 assignments (launched 2026-09-13)

AG1 blind   A1+A3: rebuild F(t) 1880-2025 monthly from Doodson 1921
            published definitions (may read src/gem-lte.ads/
            gem-dlod.adb as definition, NOT params/csv); download raw IERS
            EOP; K1 correlation. Output: shared_in/F_AG1.csv + verdict.
AG2 blind   A2: reimplement winding transform from math spec ONLY
            (winding_scalogram.py forbidden); synthetic M recovery <=1
            grid cell; segment-permutation control; verdict.
AG3 blind   A4-fetch: PSMSL RLR downloads: Brest (rlr id 1) + 211-site
            Baltic gauge list (psmsl.org/data/locations) -> QC'd .dat +
            composite method note; ridge analysis deferred to Wave 2.
AG4 armed   B2: fit-M on 1880-1950 vs 1950-2025 via compute_winding CV
            override; K3 on amo, pdo, baltic, brest, nino4; also report
            ridge power correlation between halves.

Verdict schema: /home/paul/campaign/verdicts/AGx.json
{agent, claims:[{id, reproduced, kill_outcome, metrics}], artifacts:[],
 methods_sha256, leakage_selfreport}

## Amendment log
- A1 (adopted 2026-09-14, logged late 2026-09-15): K3-full = re-run the
  lt.exe optimizer on disjoint half-records (true m-blind search) beyond
  the frozen-m AG4 protocol. Thresholds unchanged.
- A2 (2026-09-15, PI directive): K3-full VOID and retracted — cold runs
  silently used a zero-LPAP degenerate forcing model (lt.exe cold-start +
  resp DLOD_REF=TRUE trap; see RESULTS_W1.md VOID section). Additionally
  PI rules cold/warm optimizer refits out of scope: refits continue from
  the production manifold, while the campaign premise requires the
  COMPLETE ANALYSIS FROM SCRATCH (published Doodson/Ray-Erofeeva library
  + dlod3 calibration + winding pipeline; armed/pump_v*.py, F_scratch).
  K3 thresholds and definition stand; K3-strong = UNTESTED, K3-warm =
  PARKED. No threshold moved; kill-table semantics intact.
