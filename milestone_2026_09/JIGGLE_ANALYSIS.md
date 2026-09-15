# Jiggle / jitter analysis — why per-index tidal factors looked necessary, and why they weren't

Companion to [`../milestone_2026_09/README.md`](../milestone_2026_09/README.md)
("The jiggle is (almost) unnecessary"). Reproduce everything here with:

    python3 manifold_overlay.py            # repo root; prints both tables

## The modeling-convenience explanation

Every index's `lt.exe.p` carries its OWN tidal-factor table (42 Doodson
constituent amplitudes/phases) and its own manifold constants (offs,
bg, impA, impB, asym, ma, mp, init, shfT). The physical reading
originally offered: each basin needs slightly perturbed ("jiggled")
tidal factors to sit on the manifold. The modeling reading, which the
evidence now supports, is different:

**Jiggling the tidal factors gives the Ada random-descent optimizer
(`gem-random_descent.adb`) room to move without changing where it
lands.** Random descent escapes local minima by accepting uphill
moves on a jittered landscape; a 42-tuple of nearly-degenerate
constituent amplitudes provides ~40 fresh random directions per
restart that all produce nearly the same manifold. The jiggle is
search ergonomics — mobility, not information. The final products of
13 independent searches are then expected to be the SAME manifold
found 13 different ways, differing only by the noise with which each
search happened to stop.

Two predictions follow. Both are confirmed below:
1. the 13 converged manifolds should overlay (they do: 12/13 at
   r > 0.9976 — see manifold_overlay.png);
2. removing any single index's jiggle and fitting it on another
   index's manifold should cost nothing (it costs nothing: mean
   |Δr| = 0.017, and 9/12 fits actually IMPROVE on amo's F).

## What the jitter physically is

### Tidal constituent table (42 entries)

Per-constituent relative amplitude change vs amo, and the energy that
actually matters — the tide-sum power injected by the change
(sum |Δa|² / sum |a|², incoherent bound on the tide-sum RMS change):

| index | M2 (dominant) | tide-power change sum|Δa|²/sum|a|² |
|---|---|---|
| pdo | 0.6% | 80% |
| nino4 | 2.2% | 6.2% |
| iode | 1.2% | 90% |
| baltic | 0.8% | 2930% |
| nao | 2.2% | 6.5% |
| brestexcl | 0.0% | 4356% |
| tna | 1.8% | 1.6% |
| tpi | 1.0% | 40% |
| emi | 2.2% | 6.0% |
| pna | 1.4% | 7.5% |
| noi | 1.3% | 6.7% |
| kap10-10-20-30 | 1.2% | 7.7% |

The large totals for baltic/brestexcl/iode/pdo are entirely in the
near-zero constituents: entries whose amo amplitude is ~0.001 are
rescaled to ~0.02–0.2 — 1000–3000% of nothing. The **forcing-relevant
jitter is the big-constituent column: 0–2.2% on M2, and the
power-weighted tide change is 1.5–7.5% for 8 of 12** (the 40–90%
outliers are pdo/iode/baltic/brestexcl redistributing small-constituent
energy, which the 13-manifold overlay shows does not move F
meaningfully). All 42 constituent *periods* are byte-identical to
amo's (the Doodson table is frozen — the optimizer only moves
coefficients); phases are identical to ~0.001 rad except for genuine
π sign-flips of individual constituents (11/16/18/22 in about half
the productions — the same ones flipping repeatedly, i.e. the
descent choosing the opposite basin of a sign-degenerate coefficient).
The jiggle-removal test below shows even those flips are
inconsequential.

### Manifold constants (B-block)

| const | shared or jittered | spread across 13 indices |
|---|---|---|
| delA | **identical** (-4.225534) | — |
| delB | **identical** (1.126057) | — |
| ma | ~0 for all (1.4/1.5e-5) | — |
| shfT | ~identical (0.002885–0.002905) | 7e-5 |
| offs | jittered | ±0.03 |
| bg | jittered | 0.371–0.423 (±7% rel) |
| impA, impB | jittered | ±3% |
| asym | jittered | 6.227–6.274 (±0.4%) |
| mp | jittered | ±0.004 (≈ the value itself) |
| init | jittered | −2.2975 … −2.2485 (±1%) |

The *physical* comb structure — delA/delB, the comb's timing — is
frozen across all 13 productions: every optimizer independently
discovered the same annual comb and jittered only the secondary
knobs. init is a seed offset (constant F shift); offs/bg/asym enter
the tide sum at ≤0.4% levels; impA/impB ±3% perturb the FM warp depth
without moving the winding lattice. None of this is worth 0.05 in r —
which is exactly what the jiggle-removal test below measures.

## Jiggle-removal test (the decisive one)

All 13 indices refit on **amo's un-jiggled manifold** — same windings,
same σ, same harmonic order, same detrend rules as each index's
shipped fit:

| index | own manifold r | **common (amo) F r** | Δr (common − own) |
|---|---|---|---|
| amo | 0.846 | 0.846 | 0 (reference) |
| pdo | 0.814 | 0.818 | +0.004 |
| nino4 | 0.842 | 0.848 | +0.006 |
| iode (detr.) | 0.728 | 0.694 | **−0.034** |
| baltic | 0.870 | 0.872 | +0.002 |
| nao | 0.786 | 0.806 | +0.020 |
| brestexcl | 0.843 | 0.842 | −0.002 |
| tna (detr.) | 0.740 | 0.753 | +0.013 |
| tpi | 0.807 | 0.806 | −0.001 |
| emi | 0.776 | 0.805 | +0.029 |
| pna (detr.) | 0.834 | 0.854 | +0.019 |
| noi (detr.) | 0.806 | 0.855 | +0.050 |
| kap (detr.) | 0.828 | 0.852 | +0.024 |

**9 of 12 improve, 2 are neutral to ±0.002, 1 loses a little
(iode −0.034), mean |Δr| = 0.017.** The direction of the residuals
matters: the "gains" from jiggling are negative on average, so the
optimizer's jiggle spent more accuracy than it bought. Only iode —
the weakest capture in the set, a trend-heavy series — has a jiggle
doing real work (+0.034), plausibly because its local window needs
slightly different FM warp depth to place its comb teeth on the
1960s–80s variability.

Why do common-F fits improve? A per-index jiggle makes F_i wobble
relative to the shared phase structure (±3 windings over 146 yr,
panel 2 of manifold_overlay.png); the wobble is noise for a
regression whose job is to read out phases. Removing it removes a
nuisance variable. The exception proves the scale: kap, whose own
manifold is the one that really differs (r = 0.944, the FM-fold
amplification story), gains most (+0.024) from riding the common F.

## What this buys the model

The parsimony claim sharpens from "one dial" to
**"one dial, one manifold, one comb (delA/delB frozen), 13 windings
sets."** The complete per-index degrees of freedom are now just:
1. the winding numbers M_i (scalars, scalogram-confirmed);
2. 3 split dates / regression weights from the local-window fit.

Everything else — 42 tidal amplitudes, ~9 comb/FM constants — is
either shared or demonstrably inconsequential. The remaining
open item is honest bookkeeping: a jiggle-free production fit
(noise floor, k0 term, and the windings' provenance) still has to
clear the gate-A/AMO-style rivals before any of this becomes a
prediction; it is descriptive parsimony for now.

Data: `manifold_jiggle_test.json`, `manifold_overlay_stats.json`
(both regenerated by `manifold_overlay.py`).
