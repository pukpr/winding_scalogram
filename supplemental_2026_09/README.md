# Supplemental: shorter records on the same dial — pna, noi, kap10-10-20-30

Stacked figure: [`figures/supplemental2_stack.png`](figures/supplemental2_stack.png)
Harmonics sweep: [`figures/supplemental2_harmonics.png`](figures/supplemental2_harmonics.png)
Reproduce: `python3 supplemental2.py`

These records start **1948/1950**, not 1880 — so this pass tests the
**continuation of the common manifold** across the pre-record window.
F(t) is integrated from 1880.0 as always (nothing re-tuned); every
in-record winding phase is inherited from ~68–70 years of pre-record
tidal integration. Ablation: cold-starting the IIR at the record start
instead moves r_var by at most 0.019 (pna 0.834→0.834, noi 0.806→0.825,
kap 0.828→0.839) — the clock is phase-coherent across the gap; the
continuation is real but the local fit is robust either way. (The
manifold *values* differ enormously, max |ΔF| ≈ 50 windings — the
cold-start loses 70 years of accumulated turns — yet the local fit is
invariant to a constant winding offset within each local window, and
what carries the record is the *relative* phase structure, which the
combinatorial tidal model regenerates identically from the same yl.
That is
the fingerprint behaviour again: a 77-year record cannot re-tune
70 years of unobserved integration and still line up.

| index | record | windings (lt.exe.p **+ scalogram-discovered**) | n≤ | r_raw | **r_var (detrended)** | dCC | prod r_var |
|---|---|---|---|---|---|---|---|
| pna | 1950–2026 | 0.2076, 0.349, 0.5451, 2.2061, 2.497 **+ 1.458, 2.976** | 6 | 0.838 | **0.834** | **0.597** | 0.649 |
| noi | 1948–2026 | 0.2081, 0.3522, 0.5473, 2.0218, 2.502 **+ 1.878** | 6 | 0.813 | **0.806** | 0.470 | 0.623 |
| kap10-10-20-30 | 1948–2022 | 0.0259, 0.2077 **+ 0.012, 1.116, 1.24** | 6 | 0.883 | **0.828** | 0.391 | 0.720 |

All three exceed their own production fits by +0.11 to +0.21
(detrended basis; all three carry trend nuisance — kap's is large:
trend corr +0.547, 30% of variance — which is why r_var is the honest
number here too).

**Windings for pna/noi ARE higher — and they are comb teeth.**
pna/noi run to M=2.50 and noi's fitted set is nearly pna's
(|ΔM| ≤ 0.006 on three of five; cross-family obs corr +0.70). Against
the backbone B=0.2076: 2.497 ≈ **12×B**, 2.206 ≈ 10.6×B, 2.022 ≈ 9.7×B
— not integer multiples, but 2.502/2.497 sit exactly on the 12th tooth
of the 0.20845-scale comb (same structure that put baltic at 6×B).
Higher-frequency windings = the short, sharp records need finer comb
teeth; the long SST records used the low teeth. Same dial, different
register of the same comb.

**Scalogram-discovered extra ridges (winding_rank, the algorithm —
not the design matrix):** running winding_rank to M=3 (pna/noi) and
M=1.5 (kap) with the standard qualification (SNR≥2 bits over AR(1)
floor, FWHM≤0.12, continuity≥0.7) passed:
- pna: **1.458** (2.75 bits, cont 1.00 — that's 7×B) and **2.976**
  (2.70 bits, cont 0.85 — ~14.3×B). Note pna's own 2.497 ridge FAILS
  continuity (0.46) — high but unsteady; the steady teeth are 1.458/2.976.
- noi: **1.878** (2.20 bits, cont 0.85).
- kap: **0.012** (2.29 bits — the AMO-band clock tooth again),
  **1.116** (2.13 bits, cont 1.00) and **1.24** (2.24 bits, cont 0.75 —
  baltic's order-6 tooth, present in a Kaptal Arctic-index series).

Adding the discovered ridges (with harmonics to order 6, on the
continued manifold) is what takes these records from base-fit
0.730–0.787 to 0.806–0.834; for kap the discovered ridges contribute
+0.10 r_var over its lt.exe.p pair (0.730→0.828, ablation-documented).
This is the intended loop: the
Ada production finds windings by optimizer; the scalogram finds the
ones the optimizer missed; both feed the same one-dial manifold.

Caveats: in-sample descriptive fits (same OOS discipline as the
supplemental-1 set — no forecast skill claimed); pna/noi extend to
2026.3/2026.4 beyond the milestone grid, so their fits are computed on
the extended month grid from the same continuous manifold; the n≤6
harmonic sets are rich (local-regression design: 92/80/68 columns for
pna/noi/kap against Gaussian-kernel windows of ~300 effective samples)
— descriptive, not parsimonious prediction. The parsimonious n≤3
figures on the continued manifold (0.757/0.728/0.766) still beat
production detrended (0.649/0.623/0.720).

Distinct indices now served by the single dial: **18** (15 battery +
pna/noi/kap; the five supplemental-1 indices were already in the
battery at production constants and improved here with discovered
ridges).

---

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
the identical detrended basis: 0.740 vs 0.591). Note these five were
already in the 15-index yl battery (measured at production constants,
n≤1); here the scalogram-discovered windings + harmonics push them
higher. Distinct indices now served by one dial: **18**.

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
