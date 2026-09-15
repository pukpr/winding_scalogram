# Supplemental: five more indices on the same one dial (2026-09)

Companion to [`../milestone_2026_09/README.md`](../milestone_2026_09/README.md).
Same machinery, same year length **365.2463 d**, no re-tuning of the dial:
each index uses only its own `lt.exe.p` constants and windings. Marquee
figure: [`figures/supplemental_stack.png`](figures/supplemental_stack.png)
(obs grey, fit colored, blackout shaded), harmonic-order analysis:
[`figures/supplemental_harmonics.png`](figures/supplemental_harmonics.png).

| index | windings (own `lt.exe.p`) | fit r (n≤3) | r (n≤6) | prod r | PI point — test result |
|-------|---------------------|-------------|---------|--------|------------------------|
| nao       | 0.2077, 0.3552, 0.546        | 0.786 | **0.873** | 0.668 | **(1) richer ridges: CONFIRMED** |
| brestexcl | 0.0571, 0.086, 0.2076, 0.9227, 0.9662 | 0.843 | 0.910 | 0.759 | **(2) blackout 1944–1954: handled** |
| tna       | 0.0167, 0.2075 (detrended)   | 0.740 | 0.804 | 0.591 (detrended) | **(3) trend + amo-like: CONFIRMED** |
| tpi       | 0.2072, 0.4473, 0.632        | 0.807 | 0.880 | 0.760 | **(4) pdo-relative: PARTIAL** |
| emi       | 0.2073, 0.4488, 0.5612       | 0.776 | 0.853 | 0.622 | **(5) nino4-relative: CONFIRMED** |

All five exceed their own production fits in-sample (tna compared on
the identical detrended basis: 0.740 vs 0.591). This extends the
milestone battery from 15 to 20 indices, all served by one dial.

## (1) NAO — a richer comb, quantitatively

The `harmonics.json` sweep (r vs max harmonic order, σ=10) separates
the indices by how much structure sits above the base windings:

| index | n=1 | n=2 | n=3 | n=4 | n=6 | gain 1→6 |
|-------|-----|-----|-----|-----|-----|----------|
| nao | 0.629 | 0.734 | 0.786 | 0.830 | **0.873** | +0.244 |
| brestexcl | 0.712 | 0.802 | 0.843 | 0.881 | 0.910 | +0.198 |
| emi | 0.646 | 0.732 | 0.776 | 0.818 | 0.853 | +0.207 |
| tpi | 0.662 | 0.769 | 0.807 | 0.843 | 0.880 | +0.218 |
| tna | 0.661 | 0.700 | 0.740 | 0.758 | 0.804 | +0.143 |

NAO pays the most for high orders — consistent with its documented
comb-like ridge profile (similar-height teeth, vs one/two dominant
spikes elsewhere). Note its windings {0.2077, 0.3552, 0.546} contain
no near-harmonics of each other, so the harmonic energy is genuinely
per-winding, not aliases. (For comparison, baltic's headline ridge is
itself backbone order 6; here nao's whole spectrum is order-rich.)

## (2) Brestexcl — 1944.3–1954.3 blackout

Ten years with no data (verified as a gap in `brestexcl.dat`, not a
zero-fill: the CSV rows there are interpolation artifacts of the
pipeline's grid). Treatment: those samples carry **zero weight in the
local-window regression** (a window centered anywhere in the gap fits
only from pre/post-gap support), are excluded from r/dCC scoring, and
the observed trace is left blank in the figure (the fit is still drawn
through — it is model output, not fabricated data). With that, r=0.843
(n≤3; 0.910 at n≤6) is gap-honest. The gap lands inside a WWII-era
tide-gauge service interruption; PSMSL-style composites commonly carry
exactly this kind of hole.

## (3) TNA — trend nuisance, AMO sibling

TNA's rising SST-trend series behaves like iode/amo: raw fit r=0.837
but the quadratic trend (corr with obs = +0.585, 34% of obs variance)
inflates it; **detrended honest r=0.740** (reported in the stack). Its windings {0.0167, 0.2075} are the AMO
pattern ({0.0134, 0.2075}) — and the observations agree: corr(tna,
amo) = **+0.754**. TNA and AMO are the same multidecadal mode seen
through two basins, captured by the same backbone 0.2075 with
near-identical low winding (0.0167 vs 0.0134 — both ≈1/60-yr-scale
winding of the 124-yr comb alias; see milestone README for why these
low windings are clock-robust and not discriminating).

## (4) TPI — PDO relative, partial

corr(tpi, pdo) = **+0.646** — same Pacific-decadal family, weaker
coupling than tna-amo. TPI's own windings {0.2072, 0.4473, 0.632}
share backbone 0.207 and a second winding 0.4473 with pdo
{0.2073, 0.4488, 0.5934}; the third mode differs (0.632 vs 0.5934).
So the family relation is visible in the winding sets themselves, not
just the time series. Caveat flagged for the optimizer thread: tpi's
fitted delay coefficient **IR = −1.142** is the only |IR| > 1 in the
battery — per the Ada source, the inverse recursion
`Model_orig = Σ IR^k Model_final(·−12k)` diverges for |IR| ≥ 1, so
tpi's saved model is only well-defined in the forward direction. Our
plain-mode fits never apply the delay, so the reported r values are
unaffected; but this parameter should be watched in any DR/GLS
re-analysis (the milestone's GLS experiment does exercise it: it just
hasn't been run for tpi yet).

## (5) EMI — Nino4 relative, confirmed

corr(emi, nino4) = **+0.730**. EMI's windings {0.2073, 0.4488, 0.5612}
match nino4's {0.2073, 0.4491, 0.5604, 1.3851} on backbone and two
mid windings (ΔM ≤ 0.0004) — two ENSO expressions of the same winding
family, each exceeding its own production fit here (0.776 vs 0.622).

## Reproducing

```bash
python3 supplemental_2026_09/supplemental.py      # -> figures/supplemental_stack.png
# harmonic sweep + chart: see figures/supplemental_harmonics.{png,json}
```

Reads only repo-tracked files: `<idx>/lt.exe.p`, `<idx>/lte_results.csv`,
`lte_forward.py`. Note `brestexcl/` params were copied from the
experiments tree to this repo for this milestone (first time tracked
here); the blackout is defined by the gap in `brestexcl/brestexcl.dat`.

## Same limits as the milestone

Descriptive retrospective fits, not forecasts (see milestone README
"Honest limits": holdout/causal tests kill predictive claims); manifold
dLOD-consistent, not dLOD-derived; r values here are n≤3 for
comparability with the marquee — n≤6 numbers are shown only as the
ridge-richness diagnostic (point 1), where all five indices improve and
nao improves most.
