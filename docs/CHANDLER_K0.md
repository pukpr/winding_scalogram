# Chandler wobble: the k=0 solid-body sibling of the QBO alias

Exploratory excursion (scripts `chandler_k0.py`, `chandler_clean.py`,
`chandler_rect.py`, `chandler_lockin.py`; JSON results at repo root;
board `supplemental_2026_09/figures/chandler_lockin.png`). Grounding:
geoenergymath.com 2026-09-17 "Forced aliasing model of the Chandler
wobble" (f = 365.242 d annual inertia comb, q = 27.2122 d draconic
torque, two-pole halving of the 865.5-d alias). PI anchor (weighted
statistics): most likely CW period **433.0 ± 0.5 days** — the frequency
adjudication throughout uses this interval.

## 1. The alias arithmetic, sharpened against the production table

The article's chain: frac(365.242/27.2122) = 0.42198 → 865.5-d alias →
halve by "two-pole seasonal symmetry" → 432.8 d. Verified on the
production dial (yl = 365.2463, same anchor as QBO/AMO):

| quantity | value |
|---|---|
| frac(yl/P_N) = QBO tooth | 0.42214 c/yr → 865.2 d |
| frac(2·yl/P_N) = CW prediction | **0.84429 c/yr → 432.61 d** |
| weighted-statistics CW (PI anchor) | **433.0 ± 0.5 d** → prediction at **0.78σ**, inside the interval |
| observed CW (eopc04 x, 1962–2024, Hann FFT) | 0.8424 c/yr = 433.59 d (1.2σ above anchor center) |
| observed CW (eopc01 x, 1846–2024) | 0.8388 c/yr = 435.4 d (astrolabe-era contaminated) |
| lock-in mean line, window scan (§3) | 432.57–433.20 d across 1962–2010/2022 windows (0.05–0.4σ from anchor center) |

Independent estimators — alias prediction 432.61, modern FFT 433.59,
lock-in mean 432.6–433.2 (window-sensitive) — all land within 1.2σ of
the weighted 433.0 ± 0.5 anchor, straddling it from both sides. The
prediction is also robust to the year-length debate: across the whole
plausible yl window (365.2422–365.259) the alias moves only
432.76–432.15 d, entirely inside the anchor interval. Landing *exactly*
on 433.0 would require yl = 365.2360 — outside the physical window —
so a small centroid detuning is expected in any reading, consistent
with the comb-sideband candidate in §3.

The halving gets a cleaner statement than "two poles": **rectifying a
sinusoidal torque doubles its frequency**, so the operative line is the
rectified draconic 2N = 27.2122/2 = 13.60611 d — and it is a real
production constituent, in `qbo30/lt.exe.p` at amplitude −0.019 with
alias 0.8443 c/yr. The near-miss neighbours make the pick falsifiable
rather than tautological: the true fortnightly Mf line (13.66083 d)
aliases to **495.7 d**, the 13.63342-d line to 462.0 d, Mt to 715.1 d —
none of them the CW. The lattice selects 432.6 d specifically, from the
same draconic anchor as the QBO's 2.369 yr: **frac(2·yl/P_N) and
frac(yl/P_N) are the same phase walk, viewed at 433 days by the solid
Earth and at 2.37 years by the stratosphere.**

## 2. What the winding battery did and did not see (annual nuisance honored)

Nuisance discipline (user directive, and correct physics): the annual
wobble is ~60% of raw monthly pole-x variance (16.6 mas vs 28 mas CW line
before cleaning) one period away from the CW line — every target below is
cleaned of trend + annual + semiannual (regressed at 1, 2, 0.9946,
1.0128 c/yr to spare the CW band; 22% of variance removed, CW line
untouched). The winding teeth were then scanned on the draconic manifold
× annual sampler, monthly and daily grids, four comb modes (production,
single-pole, equal two-pole, square-wave), both IERS products, plus the
full-42-line manifold. **Result: no passing tooth at the predicted 0.844
anywhere** — best reading +0.9 bits / cont 0.50 (full-42-line manifold ×
rectified sampler, far under the 2.0-bit/0.70-cont gate); stray teeth
elsewhere all at cont ≤ 0.41.

That negative is informative, not embarrassing — and it is exactly the
Fyfe lesson. In *computed order tracking* (Fyfe & Munill 1977; Fyfe,
Fritzen & Rand 1997 — `docs/METHODS_BLURB.md`), an engine-order line is
found by tracking against the **shaft-angle phase itself**, not against a
reconstructed torque waveform. The winding manifold M(t) is the tidal
*waveform*; the alias line lives in the **frequency domain of the
rectified phase**, for which the carrier demodulation of §3 is the
native instrument. The scalogram correctly refuses to credit a waveform
projection whose tooth spacing doesn't match; the order line then shows
up with 58-year coherence when demodulated against the carrier directly.
(Also honest: the CW band is retrograde in the space frame,
−0.844 c/yr; the winding transform's |G|² kernel is blind to sign — no
rescue available from the tooth geometry itself.)

## 3. Lock-in / order-tracking test: forced line or ringing bell?

The discriminator — free resonance vs forced order line — is **phase
coherence against the astronomical carrier**. A free CW at Q ≈ 30–60
(resonance literature: Wilson & Haubrich 1969; Lambert et al. 2015) has
a natural frequency near the free-oscillation eigenfrequency, and its
observed phase must wander through the frame of any *fixed astronomical
carrier* at a rate set by whatever detuning the real Earth has. Lock-in
demodulation of nuisance-cleaned pole x at f_CW = 0.84429 c/yr
(sliding 8-yr windows, sin/cos + local linear trend regressors,
unwrapped phase). The estimator is calibrated on synthetics: a pure line
at f_CW + 0.0019 c/yr reads a frame slip of the same sign and scale, and
the window-noise floor at the modern SNR is ≈ 0.2 rad.

| era | frame slip (c/yr vs carrier) | phase resid (rad) | read |
|---|---|---|---|
| 1846–1900 | −0.0038 | 0.48 | astrolabe era, 10 obs/yr |
| 1900–1930 | +0.0029 | 0.68 | visual/astrolabe noise floor |
| 1930–1962 | +0.0051 | — | photographic transition |
| 1962–1978 | −0.0013 | **0.04** | space age, strong CW |
| 1978–1994 | +0.0010 | 0.11 | space age, peak CW |
| 1994–2010 | −0.0043 | **0.06** | CW decay phase |
| 2010–2022 | +0.0137 | 0.16 | deep minimum, amp 0.04 |
| **1962–2020 aggregate** | **+0.00007** | **0.20** | **0.00 cyc over 58 yr** |

The structure inside the space age is the tell. A **free oscillator**
whose natural frequency is the weighted 433.0-d reading (0.8434 c/yr)
must drift through the carrier frame **monotonically** at −0.0009 c/yr
if it sits at the anchor center, or −0.0019 c/yr at the modern FFT line
(433.59 d). It does not: the 16-yr slips **alternate sign**
(−0.0013, +0.0010, −0.0043, +0.0137) with per-block phase residuals of
0.04–0.16 rad, and they sum to +0.00007. The phase **wanders around the
carrier rather than away from it**, and the wander tightens in the
strong-CW blocks. That is the signature of a quasi-locked (pulled)
oscillator — drive nearby, feedback through the finite Q — not of a free
ring-down. And the aggregate is decisive against monotonic drift in
either direction: zero net slip, six decades, satellite-era noise floor.
Meanwhile the **amplitude** decays ~5× (lock-in envelope 0.15″ → 0.03″
through 2020, the documented 1999–2016 Chandler decay, and the last
sub-era's large slip coincides with the deep amplitude minimum where
SNR-bound phase noise is expected): the classic
forced-phase/transient-amplitude split. The pre-1962 slips of
0.003–0.005 c/yr are at the astrometric noise level of those eras, so
the defensible statement is era-bounded: **in the era where measurement
noise is below the line, the CW phase executes a zero-mean wander about
an astronomical order line, with no sustained drift over 58 yr** (net
slip 0.00007 c/yr = 8×10⁻⁵ of the carrier frequency).

The forced reading is textbook cyclostationarity (Antoni 2009): the
**amplitude is the transient** (a free mode ringing down, Q-life of
decades; the published historical record shows much larger early-20th-
century amplitudes, though our astrolabe-era lock-in numbers are
noise-contaminated and cannot confirm this directly), while **the phase
is the steady state** (driven at the rectified-nodal alias, which cannot
ring down). Both pictures coexist in the record: the free-oscillation
literature measures the transient and infers Q and excitation sources;
the order-tracking view measures the carrier that never leaves.

Frequency-domain complement: adjudicated against the PI's weighted
anchor (433.0 ± 0.5 d), the modern Hann-FFT peak (433.59 d) is a 1.2σ
reading above center, the astrolabe-heavy eopc01 peak (435.4 d) is
contaminated, and the lock-in mean line sits at 432.6–433.2 d depending
on window (the 2010–22 deep-minimum block carries the largest slip so
window choice matters at the 0.5-d level). The centroid is therefore
*straddled*, not offset: comb sidebands of the
2N line (0.844 ± 0.25/0.5/1 c/yr from the sampler slots) pull one way
and the nodal ± 0.0537-c/yr pair (± 2.4 d) the other, which is exactly
the ± 0.5 d scatter the weighted statistics measure. The yl-window
robustness (432.15–432.76 d across all plausible year lengths, §1)
means the alias prediction cannot be blamed for the residual; the
residual is sideband structure. And the carrier coherence has a
time-domain summary:
anchoring the carrier's phase in ONE 8-yr window (2000) and fitting
nothing else, a single cosine cos(φ₀ + 2π·0.84429·(t−2000)) reproduces
the nuisance-cleaned pole x at r = **0.95 for 1962–1995** and r = **0.85
over all 1962–2025** — the figure's panel 1. A detuning of only
0.005 c/yr slides ~0.3 cycles across that span, visible as fit decay; a
fixed astronomical carrier does not slide. Chirp scan (12-yr windows, 1846–2024): CW period wanders
409–445 d about a mean 431.5 d, with suggestive nodal organization
(432.5–432.9 d at nodal phases 0.0–0.2 / 0.8–1.0 vs 429.6–430.3 d at
0.3–0.7) — but window resolution σ_f ≈ 0.01 c/yr means the 3-d split is
~1σ per cell; exploratory, not a claim.

## 4. Position in the category taxonomy

| | forcing anchor | sampled line | tooth | response |
|---|---|---|---|---|
| ocean (18 idx) | dLOD-calibrated wavenumber>0 comb | backbone 0.2076 | n × b harmonics | SST/SLR standing waves, IR per index |
| QBO (k=0) | draconic P_N declination torque | frac(yl/P_N) = **0.422** | 2.369 yr | descending shear; level-specific combs |
| **Chandler (k=0)** | **rectified draconic 2N torque** | frac(2·yl/P_N) = **0.844** | **432.6 d** | solid-body pole; amplitude transient + locked phase |

One astronomical phase (the lunar node), two rectifications of it
sampled by the calendar, two of the most famous "unexplained periods" in
climate and geodesy, and the same doubling/halving arithmetic on both
sides. The CW joins qbo30/qbo50 in the k=0 category, with a
methodological footnote that matters for the campaign's own instrument:
*its* evidence is order-tracking phase coherence (the Fyfe-native
measurement), and the waveform-projection scalogram teeth — which
correctly found nothing — are the wrong shape for a line the calendar
samples once, not twice, per period. Where the manifold's teeth were
predicted at a priori positions and the target showed spectrum-level
texture (QBO 0.42 tooth), the CW's carrier showed *phase* where free
resonance predicts wander.

## 5. Declared caveats

- Against the PI's weighted anchor (433.0 ± 0.5 d) the frequency test
  PASSES at 0.78σ (prediction 432.61 d), with the modern FFT (433.59,
  1.2σ) and lock-in mean line (432.6–433.2 d, window-dependent)
  straddling it. What
  the anchor does NOT adjudicate is the *mechanism*: the free-mode
  literature attributes its ±0.5 d scatter to Q-weighted era mixing and
  elastic-loading shifts of a natural frequency; the forced reading
  attributes it to sideband structure on a fixed carrier. The two
  readings are frequency-indistinguishable at this precision — §3's
  slip-structure test (alternating vs monotonic drift) is the only
  discriminator available, and the slip statistic is insensitive to a
  constant offset by construction, so the headline is specifically
  *carrier-frame phase stationarity*, not frequency equality.
- Pre-1962 eopc01 values at 10–20 obs/yr carry astrometric noise ≥ the
  CW amplitude; their slips are reported but not credited.
- The slip-vs-alternative-reference numbers are frame-stationarity
  comparisons, not Bayes factors; a proper model comparison
  {phase-locked line} vs {AR ringing} on the modern record is the
  rigorous upgrade (next step if pursued).
- Amplitude-envelope numbers include window smoothing; the decay
  *trend* (5×, 1999–2020) matches the published CW-decay record
  (e.g. Koot et al. 2013 and successors), not our absolute scale.
- Nodal organization of the chirp is ~1–3σ, exploratory only.
