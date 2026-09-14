# The Manifold Campaign — a pre-registered falsification program

## 0. What is being tested, and why this shape

Hypothesis under test (**H1**): the geophysical indices of the climate
system are organized by a low-dimensional latent coordinate — the LTE
tidal winding manifold F(t), calibrated externally to measured dLOD —
rather than by the effectively high-dimensional state spaces that GCMs
brute-force. If H1 is true, the economics of climate science invert:
discovering the coordinate dominates integrating the state space.

The campaign's job is not to defend H1. Its job is to **kill it**,
from as many independent directions as possible, and to report what
survives. This is cross-validation applied to a physical theory in the
same sense neural-net practice means it: held-out data, blind
replicators, no post-hoc threshold tuning, and a pre-registered
decision table written before any agent runs.

Two honesty constraints baked into the design:

1. **Independence is enforced numerically, not socially.** Two LLM
   agents reading the same spec and making the same mistake are not
   independent evidence. Agents in the Reconstruction track therefore
   work from primary sources (published equations, raw archives) and
   are *forbidden* from reading project artifacts; their outputs are
   compared by hash and by numbers, not by narrative agreement.
2. **Kill criteria are fixed in advance** (Section 4). An agent may
   not redefine a metric, move a threshold, or "explain away" a
   failure inside its own verdict — that role belongs to a separate
   Adjudication step, and explanations-away must be written as
   testable follow-ups, not as amendments.

## 1. Firewalls and workspace discipline

```
~/campaign/
  PREREG.md            <- the kill table, git-committed, sha256-locked; read-only
  shared_in/           <- primary sources only: Doodson 1921 equations,
                          IERS EOP files, PSMSL RLR files, PSL URLs
  blind/               <- Track A workspaces; NO access to gem-lte-core,
                          winding_scalogram repo, or experiments/ dirs
  armed/               <- Track B/C workspaces; full repo access
  verdicts/<agent>.json<- fixed schema, Section 5
```

Enforcement: each agent is spawned in its own directory with an
explicit denial list in its prompt AND no copies of the forbidden
artifacts on its path. Track A comparison with "our" numbers happens
only after verdict submission, in the Adjudication step.

## 2. Track A — Independent reconstruction (the "would it exist without us?" test)

**A1 — Reconstruct the manifold from published equations.**
From Doodson 1921 argument definitions and Meeus-grade astronomy
algorithms, rebuild F(t) monthly 1880–2025 from scratch (s, h, p, N, p1
combinations, Mm/Mf assembly, annual interaction). Compare against our
col-4: correlation, spectral agreement, sign-change census. *Kill
value:* if H1's manifold is just re-derivable astronomy, this is the
baseline that proves it; if it cannot be reconstructed without our
tuning constants, the "externally calibrated" qualification weakens.

**A2 — Reimplement the winding transform from the formula only.**
Spec = G(t0,M) = <w(t-t0) x(t) exp(-i2piM F(t))> + AR(1)-surrogate
floor + ridge triple test, written as math, not code. Feed the agent
synthetic ground-truth data (known M, known amplitude) — it must
recover M to <=1 grid cell, then run the Baltic data with the F from
A1. *Kill value:* a tool whose published spec does not reproduce our
numbers is a documentation bug at best, a fabrication at worst.

**A3 — Reproduce the dLOD calibration from raw observations.**
Download IERS EOP (Bulletin A / C series), build annual-mean dLOD,
correlate with A1's F(t). Must land at |r| > 0.99 *without ever seeing
lte_results.csv or dlod_compare.csv*. *Kill value:* this is the load-
bearing wall of the whole qualifications story. If it fails here,
everything downstream is circular no matter what the ridges say.

**A4 — Reproduce the Baltic and Brest MSL calibrations from raw gauges.**
PSMSL RLR downloads: the 211-site Baltic network and Brest (1807–).
Rebuild the composite (documented averaging rules), fit the ridge
pipeline (A2's implementation) against A1's manifold, report Mdom and
ridge stats for baltic and brest. *Kill value:* the two most load-
bearing empirical claims (baltic order-6 dominance; single-gauge
Brest, 212 years, no composite-averaging explanation available)
tested on data fetched by someone with no stake in the outcome.

## 3. Track B — The kill battery (armed agents; repo access)

**B1 — Null-model gauntlet.** Every one of the 14 indices through
AR(1) (matched rho), IAAFT, phase-randomized-with-annual-cycle, and
**manifold-scrambled** controls (permute F(t)'s segment order —
destroys phase-locking, preserves spectrum). A ridge that survives
segment-permutation of its own clock is not about the clock.

**B2 — Predictive CV (the item-6 protocol).** Optimize M and
amplitudes on interval I1 (e.g. 1880–1950) via the existing Ada/lt.exe
pipeline or lte_forward.py; predict the ridge location and power in
I2 (1950–2025) with zero refit. Metrics: ridge-location error, power
correlation across windows. *Kill value:* distinguishes "winding
numbers are stable physical coordinates" from "winding numbers are
in-sample basis functions." This is the single most informative test
in the campaign — schedule it first.

**B3 — Constituent ablation.** Remove/downweight each lunar
constituent (Mm, Mf, draconitic vs tropical split, node N, perigee p,
solar terms) from F(t); measure ridge survival at Mdom per index.
*Kill-value expectations pre-registered:* the narrative says Mm/Mf
against annual carry the structure — so ablation should DEMOLISH the
ridges when Mm/Mf are removed and barely move them when the long
precession terms are removed. Inverse result = narrative wrong.

**B4 — Rival-manifold specificity.** Run the same data through
alternative clocks: (a) solar-only forcing, (b) pure draconitic-month
winding, (c) synthetic non-monotone processes matched to F's spectrum
and slope distribution, (d) astronomically unrelated multi-periodic
sets. *H1 prediction:* ridges concentrate on real F, not on the
matched-spectrum synthetic; rivals produce diffuse structure. If any
plausible-but-physical-free rival scores within 1 bit of F, the
"tidal manifold" attribution is unearned and H1 downgrades to
"any richly oscillating coordinate works."

**B5 — Baseline head-to-heads.** Doodson harmonic analysis (fitting
the same records with a fixed constituent library), Fourier, Morlet
CWT (wavelet_scalogram.py already ships this), EOF/PCA on the index
panel, and a linear state-space/Kalman fit. Compare: parsimony
(parameters per degree of explained variance), held-out prediction
(same I1/I2 split as B2), and the beat-pair and AMO/TNA structure the
narrative claims only winding sees. *Rule:* winding methods must win
on prediction and parsimony, not merely on visual interpretability.

## 4. Track C — Generalization (the out-of-sample soul of the theory)

**C1 — Holdout indices.** ID.yml registers 112 indices; only 17 were
in the discovery set. Randomize-and-rank the rest (AO, NINO3, NINO12,
TSA, NPGO/M4, individual gauge ports like Cuxhaven/Wismar/Helsinki/
Warnemunde, the ~20 unused composites), and generate fresh PSL box
grids (psl_extract.py) across latitude bands. Discovery set = which
indices participated in the manifold's multi-index fine-tune — this
must be *documented* before C1 runs, or the holdout is contaminated.
*Pre-registered prediction (this is what makes C1 a real test):* H1
predicts ridges at M = n x 0.2075 (integer harmonics) for genuine
tidally-driven sites, and NONE for sites with no plausible mechanism.
Report the base-frequency convergence rate across the holdout; if it
stays ~0.2% it is a law; if it drifts it was the 7 the optimizer saw.

**C2 — Forward-simulated worlds with known answers.**
pyqg (or a hand-rolled 2-layer quasi-geostrophic model), forced
shallow-water, and a stratified column: impose a KNOWN winding
component on the boundary/forcing (sin(2pi M F(t)) with chosen M) plus
turbulent background at realistic SNR. Run the full pipeline
blind. Questions: does the ridge appear at the correct M? at what
background power does it vanish (detection curve)? does anything
*unforced* at M emerge (false-positive rate in genuine chaos)?
*Kill value:* this is the only track that tests the pipeline against
real nonlinear dynamics with ground truth instead of surrogates. A
turbulent cascade can generate narrow-band structure that would pass
B1–B5 on observations; simulation is where that confound is
falsifiable.

## 5. Verdict schema and Adjudication

Each agent submits `verdicts/<id>.json`:
{agent, claim_id, reproduced (bool), kill_outcome
(PASSED_KILL_ATTEMPT | KILLED | INCONCLUSIVE), metrics {…},
artifacts [paths], methods_hash (sha256 of its own scripts),
leakage_selfreport (files outside its allowance it touched)}.

Adjudication (a separate agent pass, after all verdicts are in):
1. Verify every reproduced=true claim by re-running one artifact from
   scratch before accepting it. Sub-agent self-reports are claims,
   not facts.
2. Compute the table below. H1 stands only if ALL kill rows come up
   green; any RED row means the public story is cut back to what
   survives, in writing, in the repo.

| # | Kill criterion (pre-registered) | Red if… |
|---|---|---|
| K1 | A3 dLOD from raw IERS | \|r\| < 0.99 |
| K2 | A4 baltic order-6 ridge, blind pipeline | FWHM > 0.15 or cont < 0.6 |
| K3 | B2 ridge location out-of-sample | median M error > 0.05 on holdout |
| K4 | B3 Mm/Mf ablation | dominant ridges survive with <1 bit power loss |
| K5 | B4 matched-spectrum synthetic clock | rival within 1 bit of real F on >= 5 of 14 indices |
| K6 | B5 parsimony/prediction | any standard baseline matches winding on held-out CC with <= 2x parameters |
| K7 | C1 harmonicity on holdout | <50% of new real indices show integer-harmonic ridges |
| K8 | C2 forced-simulation recovery | correct M not recovered at SNR where observed ridges exist |

## 6. Execution on this machine (Hermes)

- **Sequencing:** Wave 0 = write PREREG.md, hash it, lock C1
  discovery/holdout split (~1h). Wave 1 = A1–A4 + B2 in parallel
  (6 tasks). Wave 2 = B1, B3–B5 (5 tasks) once A's F(t) exists —
  they use it. Wave 3 = C1 (longest list of indices) and C2 (sim runs
  overnight). Adjudication last.
- **Parallelism:** `delegate_task` for wave members (<=10 children,
  isolated terminals per child). For anything >15 min wall-clock
  (C2 sims, per-index lt.exe ~1h each): background `terminal` jobs or
  spawned `hermes chat -q` in tmux, capped so this box never contends
  with the user's own lt.exe xterms (check `uptime` load before each
  wave launch; lt.exe-style jobs: max 2 concurrent).
- **Compute economics:** the transform itself is cheap (n x |M| x
  |t0| matmul, seconds); surrogate floors are the cost (~15s/index);
  full 17-index kill battery ~= one afternoon. Only C2 and per-index
  lt.exe re-fits are expensive. The plan's own thesis holds: the
  expensive resource is establishing the manifold, not computation —
  and that's exactly what Track A buys.
- **Failure modes to refuse:** an agent that "improves" a threshold to
  pass; an agent that reads blind/ paths; Track A agents consulting
  each other. Adjudication checks leakage_selfreport plus mtimes
  against the firewall listing.

## 7. What each outcome means

- **All green:** publishable as a verified framework — first time a
  tidal-manifold claim on climate indices carries a pre-registered
  falsification ledger. The C1/C2 numbers become the headline:
  harmonicity rate on unseen indices + recovery curve in simulated
  turbulence.
- **B2 green, K3 red (ridge power moves out-of-sample):** H1 survives
  as "locking exists, amplitudes are non-stationary" — a weaker but
  still novel claim; scalograms become the primary product, not the
  fixed-params narrative.
- **K5 or K8 red:** the manifold's particular physics is unearned —
  fall back to "some non-monotone clock works," which reframes the
  whole result and must be said publicly.
- **K1/K2 red:** the qualifications we verified this session are
  artifacts of our own pipeline. This is the catastrophic row; it is
  first in the table for a reason — do it before defending anything else.
