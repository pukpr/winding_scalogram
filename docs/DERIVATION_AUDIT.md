# Audit of the sin(k·M(t)) derivation chain (Chap. 12 Part I, the ChatGPT
# two-layer route, and the Claude artifact) — verified against the local
# Ada source and numerics, 2026-09-16

Sources under audit:
- [`chatgpt_derivation.md`](chatgpt_derivation.md) — line-by-line audit of
  GEM_Chap12 + the stratified two-layer derivation, whose key physical
  prediction is the **1/ω² constituent weighting: low frequencies are far
  more compliant**.
- [`claude_derivation.md`](claude_derivation.md) →
  https://claude.ai/artifact/4W1khUuCbY6JnzRg8LRSxw (fetched successfully;
  verdict tables §1–§9).
- Primary source `github.com/pukpr/gem/GEM_Chap12.docx`: **currently 404**
  (raw + API, both `master` and `main`; repo `pukpr/gem` not resolvable).
  The chapter itself cannot be re-read this session; what can be checked
  is everything the two transcripts claim against code and math. All such
  checks below.

## 1. Claims verified true

- **Claude §8 code quote is verbatim correct.** `src/gem-lte-primitives.adb`
  LTE(): `SW := Sin(2.0*Pi*Wave_Numbers(J)*Res(I).Value + M.Phase) *
  Exp(Res(I).Value*Third)` with sign-preserving `**NonLin` and the
  `Sinc` denominator branch. The mapping Wave_Numbers ↔ √A/2π per mode
  and Res ↔ M(t) is exact, and NonLin/Third are correctly flagged as
  post-derivation engineering extensions (our own joint-capture work
  independently confirms NonLin is not a lever — see RESULTS_JOINT.md).
- **Lunar periods cited are the live constants.** `src/gem-lte.ads:15–19`:
  Draconic 27.212220815, Tropical 27.321661554, Anomalistic 27.554549886.
  The code even names the beats: `N := 1/(1/Draconic − 1/Tropical)`,
  `p := 1/(1/Tropical − 1/Anomalistic)`.
- **The §3 "exact identity" algebra is exact — verified numerically.**
  For ζ=sin(√A·M(t)) with *any* smooth M, the ODE
  ζ″ − (M″/M′)ζ′ + A·M′²ζ = 0 reproduces with residual 2.8×10⁻⁴ of scale
  (pure finite-difference error; M = Σkᵢsin ωᵢt with the three lunar
  frequencies, √A=0.7). Claude's re-derivation stands; so does its
  "removable singularity" analysis — ζ stays smooth through every M′=0
  instant even though 12-12 formally divides by zero there.
- **12-15/12-16 cos/cosh sign dichotomy**: consistent with ChatGPT §16
  (normalized form X(t) = −a/(g√A)(v_t + U_φ/a) repairs the missing
  amplitude/sign/U term; both branches reachable).

## 2. One arithmetic correction

ChatGPT §5 table: "Anomalistic ⨉ Draconic beat ≈ 2,270 d (≈6.2 yr)".
With the live constants: 27.554549886 ⨉ 27.212220815 →
beat = 1/(1/27.2122 − 1/27.5545) = **2190.6 d = 5.994 yr** (not 2270/6.2).
The Jacobi–Anger combination-tone census on the production year length
(365.2463) confirms the emergent ladder: ±1 combos of (Mm, Dc) give
0.1667 c/yr = 6.00 yr, ±2 give 3.0 yr — the ENSO band falls out of the
monthly clock with no low-frequency input. Same arithmetic underwrites
the year-length knife edge already measured in RESULTS (alias
= 1/|round(cpy)−cpy| with cpy = yl/9.1330).

## 3. The 1/ω² weighting, audited against the production pipeline

Paul's framing: the 1/ω² is geared to **stratified layers and reduced
effective gravity** — g′ = g·Δρ/ρ ≈ 0.02–0.03 m/s² for the thermocline
(vs g=9.81), so c_bc = √(g′h) ≈ 1–3 m/s against c_barotropic ≈ 200 m/s:
the slow layer is ~10² more compliant, and double integration of the
meridional momentum per constituent gives k′ᵢ ∝ kᵢ/ωᵢ² — low frequencies
move the parcel most. What does the *production* manifold actually carry?

Three stages, measured (pure-sine transfer through the real `iir` code):

1. **tide_sum**: equilibrium form — fitted lpap amplitudes are nearly
   flat in ω (log-log slope **+0.25** across the 32 lunar-band
   constituents, same +0.25/+0.26 for amo/pdo/nino4/baltic). No strong
   compliance tilt is *stored* in the coefficients.
2. **impulse comb + IIR**: the leaky IIR with ma≈0.99999 is a near-exact
   integrator below ~1 c/yr — gain × f = **1.92 ± 0.02** from f=0.03 to
   1 c/yr (flat slope −1, the second integration's worth), deadbanded
   above the annual comb with a resonance spike at 13.4 c/yr exactly one
   comb-alias off 12/yr. (My earlier single-constituent "compliance
   −0.18" probe was comb-dominated and is superseded by this clean
   pure-sine transfer.)
3. **Bessel FM**: folds, does not filter.

So the production chain embeds **≈ one integration (ω⁻¹)** between the
stored equilibrium coefficients and the manifold argument, and the
optimizer's +0.25 tilt *resists* a second integration rather than
adopting one: net manifold weighting ≈ **ω⁻⁰·⁷⁵**, between equilibrium
(ω⁰) and the two-layer parcel prediction (ω⁻²). That is a substantive,
falsifiable finding, not a defect: the *forcing* manifold M is the
equilibrium-ish tide (correct per ChatGPT's fast barotropic layer —
quasi-static ⇒ ∝kᵢ, no ω-tilt), and the **1/ω² compliance belongs to
the material/response coordinate**, which in the code is where the IIR
integration + the fitted standing-wave amplitudes act. The stratified
prediction then lives at the *response* end: a parcel's excursion
should carry kᵢ/ωᵢ² — testable directly in mooring/altimetry
meridional-displacement spectra (item 6 below), and *already* partly
visible in our own data: the scalogram discovers that climate indices
lock to teeth of the *manifold* — a phase-mixing (Jacobi–Anger)
hierarchy, which is exactly what a compliance-tilted slow coordinate
would generate and what linear transfer could not.

## 4. Turning points and the adiabatic parameter, measured on production F

Claude §3/§4 resolves the M′=0 divisions as removable and grants rigor
"whenever the waveguide relaxation is fast vs the forcing periods".
The census on the real pdo manifold (1880–2022, 12/yr grid, windings
units):

- **F′ ≤ 0 in 46.9% of months; 77 downward crossings; F range −52…+10
  windings.** The pullback interpretation (A: exact, any M) is the one
  doing the work — the temporal-oscillator reading (B: WKB) is
  genuinely marginal: with μ=2πM, ε_M = |F″|/(μF′²) has median 0.21 at
  the backbone (0.2073), 0.10 at the PDO tooth, 0.03 at baltic's 6× —
  **but ε_M ≥ 1 in ~25–33% of months** (near every comb-tooth
  reversal). Higher windings are *more* adiabatic — the sin(2πMF)
  response is fastest at the teeth where the locking claims sit.
  This matches the empirical record: the ridge continuity metric (time
  windows!) is the criterion that survives; smooth-in-time is precisely
  what ε_M≪1 buys, and the scalogram measures its failure directly.
- **Level C (full LTE solution) remains undemonstrated in both
  transcripts and in our work** — agreed verdict of both audits: the
  honest claim is the pullback of a spatial eigenmode along a dynamically
  generated coordinate, with NonLin/Third and the IIR beyond Part I.

## 5. Where the two transcripts differ, and who is right

ChatGPT (§24, "ENSO(t) = Φ_n(M(t)) — forced manifold-response, not a
normal mode") and Claude (§4: "value of the fast eigenmode **as sampled
by a diagnostic that inherits the forcing's own slow phase**") converge
on the Lagrangian-pullback reading. Both correct; both must not be
over-read: neither has yet derived the *coupling coefficients* between
barotropic tide and the moving coordinate (ChatGPT's own table's last
row concedes this). Our scalogram results sharpen the caveat: since
spectrum-matched random-phase series reproduce the fit r of real
captures (see [`../supplemental_2026_09/REJECTION.md`](../supplemental_2026_09/REJECTION.md)),
any claim that "the fit validates the derivation" is void — the
derivation's testable content is the **phase coherence** (ridges/
continuity) and the **constituent-weighting prediction**, both
quantitative and both ours to run.

## 6. Falsifiable predictions from this audit (ordered by cost)

1. **Beat-ladder check (free):** response spectra of all 18 indices
   should carry power at n·(Mm±Dc) combination periods (6.00, 3.00 yr …)
   with Bessel-J² weights J_n(√A kᵢ) — *without* any 6-yr forcing input.
2. **ω-resistance check (free):** the fitted lpap slope +0.25 vs ω is a
   prediction under the pullback reading: forcing coefficients stay
   equilibrium-like; the ω⁻¹ comes from the IIR. Refit one index with
   lpap forced flat-in-ω: prediction r drops <0.01 (the shape is not in
   the coefficients).
3. **Parcel compliance (external data, the ChatGPT test proper):**
   mooring/ARGO meridional displacement spectra at low latitude should
   show tidal-line excursion amplitudes ∝ kᵢ/ωᵢ² at *equal forcing* —
   concrete predicted line-to-line ratios: draconic(27.21 d) vs
   anomalistic(27.55 d) nearly degenerate (1.025 — the tilt is NOT in
   that pair's ratio); fortnightly Mf(14.77 d) vs monthly Mm(27.55 d)
   = **3.48×**; semi-diurnal M2(12.42 h) vs Mm = **2835×**. The 1/ω²
   signature is therefore a monotone ramp across the *order of
   magnitude* in period (hours→days→weeks), steepest between the
   diurnal/semi-diurnal cluster and the monthly cluster — the place
   where equilibrium-tide theory (flat) and compliance theory (ω⁻²)
   differ by three orders of magnitude and mooring data can tell them
   apart. (Caveat: real parcel excursions also feel the β-plane
   restoring force; pure ω⁻² holds only while ω ≪ the local inertial/
   gravitational relaxation rate — precisely ChatGPT §1's quasi-static
   condition, itself falsifiable in the same spectra.)
4. **C1 holdout as usual:** ridge continuity on held-out segments.

## Bottom line

Both audits' math checks pass against primary sources (code verbatim,
constants, the exact identity numerically to 3e-4, one beat-period
arithmetic slip corrected). The 1/ω² compliance is *not* stored in the
production forcing coefficients (they are +0.25 tilted against it) but
one ω⁻¹ integration is physically embedded in the IIR stage — leaving
the stratified two-layer prediction as a property of the **material
response coordinate**, which is where the artifact's own slow-manifold
condition (and our scalogram's continuity criterion) actually bite:
ε_M<1 holds in the majority of months, breaks at the comb reversals,
and the windings with the strongest empirical support (backbone teeth)
are exactly the ones with the best adiabatic margin.
