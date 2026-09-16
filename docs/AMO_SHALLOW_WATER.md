# AMO as a shallow-water response: forcing pipeline and moving-gauge formulation

Companion to [`DERIVATION_AUDIT.md`](DERIVATION_AUDIT.md) (which audits the
general sin[kM(t)] chain) and [`QBO_K0.md`](../QBO_K0.md) (the wavenumber-0
contrast). This one does the same job specifically for the Atlantic Meridional
Overturning Oscillation index as the production model actually fits it:
`amo/lt.exe.p`, windings **ltep = [−0.01339, 0.20749]**, NM=2, harm {2,5,6,15},
IR = −0.457. Every number below is read from the production artifacts or
computed from them this session (2026-09-16); code lines quoted verbatim from
`gem-lte-core/src/`.

---

## 1. The physical question

AMO is a basin-scale, mid-latitude SST index. Laplace's Tidal Equations
(LTE) are the shallow-water equations of a rotating fluid with linearized
Coriolis — the standard long-wave dynamics of the ocean. The claim under
construction (GEM Ch. 12, as audited) is not that tides *heat* the Atlantic;
it is that the tidal **mechanical forcing** f(t) — known a priori from
celestial mechanics — drives a slow baroclinic mode whose material response
enters the observed index through a **winding** sin[kM(t)] nonlinearity,
where M(t) is the accumulated forcing manifold. Two ingredients need
formulation:

1. **Forcing**: how the 42-constituent lunar/solar tidal table becomes the
   scalar drive of the response equation;
2. **Moving gauge**: why the solution takes the form sin[kM(t)+φ] rather
   than a linear convolution Σᵢ H(ωᵢ)Fᵢ sin(ωᵢt).

The production code is the reference implementation of both.

---

## 2. The forcing pipeline (production, end to end)

`Calc_Forcing` (`src/gem-lte-primitives-solution.adb:840`) is four stages;
`lte_forward.py` reproduces it bit-for-bit (col-4 r = 0.9991).

### 2.1 Tidal constituents — the celestial input

`lpap` is a 42-row table (period_days, amplitude, phase) of **long-period**
constituents. Top lines for amo (this session, `amo/lt.exe.p`):

| line | period (d) | amp | phase | c_yr = 365.2463/P | monthly alias |
|---|---|---|---|---|---|
| Mf-like combination | 13.6608 | **+0.323** | +0.634 | 26.73682 | 0.2632 c/yr (3.80 yr) |
| 13.6334 | 13.6334 | +0.136 | +1.423 | 26.79057 | 0.2094 c/yr (4.78 yr) |
| 9.1330 | 9.1330 | +0.086 | −2.211 | 39.99193 | **0.00807 c/yr (123.9 yr)** |
| Mm 27.5545 | 27.55455 | +0.085 | +0.409 | 13.25539 | 0.2554 c/yr (3.92 yr) |
| Mf 14.7653 | 14.7653 | +0.032 | −2.801 | 24.73680 | 0.2632 c/yr (3.80 yr) |
| Ssa | 1616.303 | +0.012 | +1.654 | 0.22598 | 4.43 yr |
| Draconic Dc | 27.21222 | −0.003 | −2.487 | 13.42214 | 0.4221 c/yr (2.37 yr) |
| Anomalistic | 27.32166 | −0.004 | +2.192 | 13.36838 | 0.3684 c/yr (2.71 yr) |

Constants are the live ones in `src/gem-lte.ads:15–19` (Draconic
27.212220815 / Tropical 27.321661554 / Anomalistic 27.554549886; the code
names the beats itself: N = 1/(1/Dc − 1/Trop) = 27.2122×27.3217 → 18.6 yr
nodic; p = 1/(1/Trop − 1/An) = 8.85 yr apsidal). The **aliases column is the
whole game at monthly sampling**: a 13.66-day tide is observed 26.74 times
per month-folding; its residual fractional part 0.2632 c/yr is what the
ocean "sees". This is the same arithmetic that predicts QBO's 2.369-yr
alias at Draconic — no fitted parameter is involved in any alias period.

### 2.2 JERK rotation — production uses JERK=0

`Jerked_Tidal_Factors` (`solution.adb:811`) mixes each constituent with its
time derivative: amp·√((1−J)² + (J·13.6608/P)²), phase += atan2(derivative,
normal). With **JERK = 0.0** (confirmed in `experiments/Feb2026/amo/
lt.exe.resp`) this is the identity — the production forcing is the *raw
cosine tide*. (Physics note: J→1 converts displacement-forcing to
velocity-forcing; the response-side ω⁻² compliance below is then untouched.
This remains an open knob for the Filter9Pt/JERK follow-up.)

### 2.3 Tide_Sum with Integ = shfT — one integrator is already in the drive

`Tide_Sum` (see `lte_forward.py:264`): each line enters as
amp·cos θ − **Integ**·(yl/P)·sin θ with θ = 2π(yl/P)·t + ph, Integ = shfT =
**0.002885**. The −sin term is exactly a 90°-shifted, frequency-weighted
copy — a partial time-integral of the tide *before* any dynamics. Its
weight is tiny (0.29%), but its frequency weighting f·Integ tilts high
lines up — the deliberate opposite direction to the compliance argument,
worth remembering when auditing lpap slopes (§4).

### 2.4–2.5 Impulse comb × leaky IIR — annual sampling plus one ω⁻¹ stage

`Calc_Forcing` composes them as a **product then a recursion**
(`lte_forward.py:482`): `forcing = iir(tf * impulse_delta(...), lag_a =
1−ma, lag_c = mp, init)`. The delta train is a *sampler*: it zeroes the
tide in 11 months of 12 and passes tf at the firing slot. With
delB = **1.126**, DPos = int(round(1.126·12)) = 14 — off the 0..11 grid —
so the delA = **−4.2255** impulse never lands at monthly sampling and only
the half-year-removed second impulse fires: slot (14+6) mod 12 = **8**
(September), value **asym = 6.2444** — probe-verified this session as a
single annual spike. (The Ada `Integer()` rounding quirk is reproduced
exactly; at finer SAMPLING the delA line recovers its intended slot.)

The IIR is `y[i] = x[i] + Mem·y[i−1] − copysign(lag_c, y[i−1])`,
Mem = clamp(1−ma) = **0.9999856**, lag_c = mp = **−0.004205**, seeded
init = −2.2767 at IDATE 1880 with a backward pass for pre-history. Since
x is an annual kick of the instantaneous tide, the output is a geometric
cascade of September values — the leaky integrator supplies exactly **one
ω⁻¹** (measured last session: pure-sine gain·f = 1.92 ± 0.02 flat over
0.03–1 c/yr) while the copysign term is the Coulomb-friction deadband that
keeps the cascade from drifting. The climate reading: the index is an
annual-reporting instrument, so the continuous tide is *sampled annually*
and then smoothed by ocean memory — the alias structure of §2.1 passes
through intact because the comb shifts each line by ±1, ±2 c/yr without
changing fractional parts. That is why ridges appear at *the same*
fractional windings (0.42, 0.49, 0.21, 0.68…) on every manifold in the
scalograms.

### 2.6 Bessel FM — the winding warp

`bessel()` (`lte_forward.py:318`): F ← F + impA·sin(2πkF) + impB·cos(2πkF)
+ offs·impA·sin(4πkF) + bg·impB·cos(4πkF), k = the backbone winding
(ltep[1] = 0.2075). For AMO: impA = **−3.2648**, impB = **−5.0863**,
offs = 3.86e−4, bg = 0.398. This phase-modulates the manifold: it converts
the integrator output into the **M(t) whose sin(kM) is observed** — the
FM/warp that manufactures the high-order harmonics n∈{2,5,6,15} as teeth.
Without it, the r(yl) knife edge and harmonic combs do not exist
(quarter-turn: the same code path is what makes kap10's smooth R-drift
amplify into ±15-winding deviations; see manifold-overlay analysis).

Result: **M(t) = F_col4_amo**, the control manifold — 1777 monthly values,
the object the moving gauge below is defined on.

---

## 3. Moving-gauge formulation — why sin(kM), not H(ω)

### 3.1 The reduced response equation

After the ChatGPT two-layer audit (`docs/chatgpt_derivation.md` §2–3,
verified in DERIVATION_AUDIT.md), the slow/baroclinic parcel coordinate
q(t) obeys schematically

    q̈ + 2Γq̇ + ω₀² q = C·η_b(t) + F_φ(t)                    (3.1)

with η_b the fast barotropic tide of §2 passing through the comb, and the
material link dφ/dt = v_φ / a. For a harmonic constituent the double
integration gives φ_i ∝ −F_i/ω_i² — the **compliance**: at fixed force,
lower frequencies displace more (§5 of DERIVATION_AUDIT; sympy-checked
limit σ→0: H(σ) = 1/(ω₀² − σ² + 2iΓσ) → **1/ω₀² exact**).

### 3.2 The gauge transform, and its exactness

Set θ(t) = kM(t) + φ and look for solutions q = A(t)·sin θ. Two eliminations
make this *exact*, and this is the heart of the moving-gauge claim:

1. **Eliminate A(t), Γ** between the real and imaginary parts of the WKB
   balance, leaving the phase-only equation; equivalently,
2. **Reparametrize time by the manifold itself** — treat M as the
   independent variable (the gauge rides with the forcing):

       ζ ≡ q,  d/dt = M′(t)·d/dM:
       ζ″_M · M′² + ζ′_M · M″ = −A·ζ · M′²      ⇒

       **ζ̈ − (M̈/Ṁ)ζ̇ + A·Ṁ²·ζ = 0**                (3.2)

   with solution ζ = sin(√A·M(t) + φ) **for any smooth M(t)**. This is
   equation 12-13 of the chapter in substance. Verified this session with
   sympy: substituting ζ = sin(kM(t)) into (3.2) returns the coefficient
   identity **A = k² exactly** — no slow-manifold approximation survives
   inside (3.2) itself. The approximation is all in *why ζ should solve a
   constant-coefficient (3.2)*, i.e. in the two-layer reduction, not in the
   transform.

### 3.3 Where the physics lives: the singular points

(3.2) divides by Ṁ = M′(t). At every **turning point** (M′ = 0 — manifold
reversals) the equation is formally singular
while the solution sin(kM) stays smooth: the singularity is **removable** —
gauge, not physics. This is the precise sense of "moving gauge": the wave
equation is written in a coordinate that slides with the forcing; the
coordinate's reversals are not the wave's reversals. Census computed on
**AMO's own manifold** this session (pipeline of §2, 1880–2022, monthly):
F′ ≤ 0 in **46.3% of months**, 78 downward crossings, F range −53.1…+9.6
windings. The genuine
approximation content is the **adiabatic parameter** ε_M = |M̈|/(k·M′²):
median ε_M ≈ 0.21 at the AMO backbone (0.2075), 0.10 at the PDO tooth,
0.03 at the baltic-class 6× teeth — the teeth that lock in the scalogram
are the ones with the best adiabatic margin (DERIVATION_AUDIT §4, ε_M
census on the sibling pdo manifold; the same k·M′² scaling applies).

### 3.4 Standing-wave reading for AMO (NonLin, sin+cos pairs)

Regression_Factors fits [F, sin(2πmF), cos(2πmF)] pairs (m = ltep entries);
the sin/cos pair *is* the two quadratures of (3.2)'s general solution
(a·sin(√A M) + b·cos(√A M)), so the fitted standing wave **is** the moving
gauge's amplitude/phase form, with the FM warp of §2.6 supplying the
harm{2,5,6,15} harmonic sidebands. AMO's IR = −0.457 (delayed-response
regression weight) is the residual acknowledgment that a purely local
gauge is not enough — the basin needs phase lag.

---

## 4. The 1/ω² accounting, AMO-specific

The audited net weighting on the production AMO manifold is
**≈ ω⁻⁰·⁷⁵** (DERIVATION_AUDIT §3: fitted lpap slope +0.25/ω resists the
tilt; the IIR supplies −1.0). For AMO this is the resolution of what would
otherwise be a paradox: the observed index is *dominated* by a ~60-yr
line, so one might demand a huge low-frequency compliance at the forcing
stage. Instead the slow line arrives through the **alias + comb lattice**:
the 9.1330-day line is at 39.99193 c_yr — alias 0.00807 → **123.9 yr**;
three-tone combos of (6.859, 9.557, 13.777) land at 41, 61, and
**63.66 yr** (computed this session from the live lpap aliases); and the
nodic N line aliases to 18.61 yr. The 60-yr AMO tone is a *lattice
frequency* (comb of aliased minors), not a *forced compliance* — which is
consistent with the modest ω⁻⁰·⁷⁵: the ocean needs no extreme low-frequency
gain because the calendar already generates the low frequency. AMO's own
slow winding −0.01339 (period 74.7 yr) then reads as the response
selecting the 63–124-yr comb cluster.

**Contrast with QBO (the parallel k=0 category):** there the manifold was
rebuilt from draconic lines only and the dominant alias 0.4221 c/yr =
2.369 yr *was* the observed period with zero parameters. For AMO the
strongest aliases (3.8–4.8 yr) sit in the ENSO band instead; what the
Atlantic shows is their comb-difference envelope — the same lattice,
different tooth picked by the standing wave, which is exactly what a
wavenumber-specific (β-plane, IR ≠ 0) response should do.

---

## 5. Assumptions declared (where the derivation is questionable)

Per the standing brief — "where the derivation is questionable, assume
conditions to make it applicable" — the AMO chain additionally rests on:

| # | assumption | status |
|---|---|---|
| A1 | two-layer reduction (Ch.12 fast/slow split) gives (3.1) with C·η_b forcing | not re-derived from GEM_Chap12 (404); accepted from the audited transcripts; g′ = 0.02 m/s² check passes |
| A2 | M(t) ∈ C², Ṁ ≠ 0 except isolated | true of AMO's F (155 sign changes, 78 downward, all isolated — §3.3 census) |
| A3 | adiabaticity ε_M < 1 at teeth of interest | backbone median 0.21; *fails* at turning points — removable there, but see A4 |
| A4 | F′ ≤ 0 in 47% of months — temporal-WKB reading marginal; pullback (M-as-time) reading carries it | both readings agree at teeth; stated openly |
| A5 | basin geometry maps onto the standing-wave basis without additional modes | empirical: 12/13 manifolds overlay at r > 0.9976, kap exception diagnosed |
| A6 | AMO is *not* claimed as a standalone showcase: Gate B bare capture 0.726 vs calendar rival 0.738 (campaign ledger) | the evidence is alias-prediction + ridge continuity, never fit r |

## 6. Falsifiable predictions specific to this formulation

1. The **63.66-yr comb tone** (§4) should appear in century-scale Atlantic
   SST/stiff (e.g. Kaplan, HadSST extended, coral/SAMOC proxies) spectra
   within ±1 yr of 1/0.015708, with relative power set by |amp product|
   ≥ 5×10⁻³ — testable on data independent of the AMO index itself.
2. The 9.1330-day line's 123.9-yr alias (strongest single alias product
   0.0022 with the 13.6334 minor) should bracket the 60-yr tone as a
   **pair of satellites** at ~61/64 yr in high-resolution proxies.
3. Nodal 18.61-yr modulation of the 3.8–4.8-yr aliases: amplitude
   sidebands at 18.6 ± 4.2 yr in the index spectrum.
4. If A1's compliance is real at response stage, parcel displacement
   spectra (mooring/ARGO, equal-force lines) show 3.48× fortnightly-vs-
   monthly and ~2800× diurnal-vs-monthly — carried from DERIVATION_AUDIT
   §6; the AMO fit imposes no extra requirement.
5. Turning-point audit: kinks in any detrended AMO fit should coincide
   with F′ = 0 months (78 downward crossings on AMO's own manifold,
   1880–2022, §3.3) — the removable-singularity prediction of §3.3.

## 7. One-paragraph summary for the paper track

The AMO forcing manifold is a deterministic object: 42 celestial long-period
tides (JERK=0) → annual single-impulse sampler at year length 365.2463
(September slot) → one leaky-integrator stage (measured ω⁻¹ between
0.03 and 1 c/yr) → Bessel FM
warp at the backbone winding. The response ansatz sin[kM(t)+φ] is exact in
the moving-gauge ODE ζ̈ − (M̈/Ṁ)ζ̇ + k²Ṁ²ζ = 0 for any smooth M, with
approximation content confined to the two-layer reduction and the adiabatic
parameter; the ω⁻² compliance the chapter claims lives in the material
response, not the stored manifold (net ω⁻⁰·⁷⁵ there), and AMO's ~60-yr
dominance is a consequence of the alias×comb lattice (63.66-yr three-tone
combo, 123.9-yr single-line alias), which fixes falsifiable satellite
frequencies independent of any fitted index.
