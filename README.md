# winding_scalogram

Winding-number scalograms: time-localized spectral analysis of climate
indices against a fixed, externally calibrated tidal forcing manifold —
the non-autonomous alternative to EOF/PCA-style variance decomposition.

A mode with winding number `M` contributes `A sin(2*pi*M*F(t) + phi)` to a
record, where `F(t)` is the Laplace's tidal equation (LTE) forcing
manifold: a latent tidal phase coordinate, calibrated by regression on the
measured Earth-rotation RATE d(LOD)/dt over the satellite era (1962-2019,
daily, n=20,829) before any climate data is touched (in-sample |r| ~ 0.97;
split-sample out-of-sample CC ~ 0.96 at daily resolution; by conservation
of angular momentum the annual-impulse convolution integrates
the fitted rate back to the LOD level at r ~= 0.8; see
`docs/WINDING_SCALOGRAM_FEASIBILITY.md` and
`docs/RESULTS_W1.md` for the campaign corrections). Because `F(t)` is strongly
non-monotone (~160 direction reversals per century; linear-in-time
R^2 = 0.02), calendar-frequency transforms cannot be relabeled into
winding number: winding content is measured directly,

    G(t0, M) = < w(t - t0) * x(t) * exp(-i*2*pi*M*F(t)) >,

a Gaussian-windowed correlation against the manifold's own native basis,
normalized by a persistence-matched (AR(1)) surrogate floor through the
identical basis. Sharp, horizontally persistent ridges in `(t0, M)` are
the signature of genuine phase locking; an arbitrary time series (IAAFT
surrogate control included) produces none.

Intellectual lineage: computed order tracking (Fyfe et al. 1977/1997) and
lock-in demodulation generalized to a non-monotone multiply-periodic
phase reference; and, 100 years of precedence earlier, Doodson's tidal
harmonic analysis and his 1928 reduction method for monthly mean sea
level — the operation this package inverts: PSMSL-style MSL composites,
instead of having their tidal content subtracted, are shown to be built
from windings at integer harmonics of the calibrated base frequency
(e.g. baltic, a 211-gauge PSMSL composite: one ridge at M = 6.00 x 0.2076
dominating its spectrum by ~3x). See `docs/METHODS_BLURB.md`.

## Contents

    winding_scalogram.py   plot Data/Model winding-power scalograms (the paper figure)
    winding_rank.py        automated ranked winding numbers with AR(1)-surrogate
                           significance (peak/FWHM/continuity triple test)
    winding_beats.py       near-degenerate beat-pair analysis (PDO vs NINO4 case)
    wavelet_scalogram.py   standard Morlet cross-wavelet scalograms (the baseline
                           this approach is deliberately NOT)
    param_survey.py        fitted-winding extraction (compute_winding) + periodograms
    lte_forward.py         pure-Python LTE forward model (params -> Model/Forcing)
    psl_extract.py         NOAA PSL gridded-dataset timeseries extraction
                           (Kaplan SST V2, NCEP Reanalysis, ...) -> analysis subdir
    ID.yml                 index metadata (name, lat/lon, source)
    <index>/               analysis subdirs: <index>.dat (input), lte_results.csv
                           (Year, Model, Data, Forcing), lt.exe.p (fit params),
                           lt.exe.resp (config), winding_scalogram.png
    docs/                  WINDING_NARRATIVE.md (7-index findings),
                           WINDING_SCALOGRAM_FEASIBILITY.md (17-index ridge survey,
                           qualifications, controls), METHODS_BLURB.md

Indices: nino4, nino34, pdo, amo, tna, nao, iode, emi, npi, pna, noi, tpi
(SST/pressure anomaly indices), baltic + darwin1880 (PSMSL sea-level
composites), qbo30/qbo50 (the wavenumber-0 categorical contrast), and
pdo_iaaft_detuned_surrogate (the negative control — no ridge, correctly
rejected).

## Quick start

    pip install numpy matplotlib scipy pyyaml
    python3 winding_rank.py --index nino4
    python3 winding_rank.py --index pdo_iaaft_detuned_surrogate   # -> NONE
    python3 winding_scalogram.py amo nino4 --m-max 5
    python3 psl_extract.py atlbox5n15s --ntype 4 --lat 15 -5 --lon -20 -50
    python3 winding_rank.py --dat atlbox5n15s/atlbox5n15s.dat --manifold-from nino4

(Indices live in same-named subdirectories alongside the scripts; `ROOT`
in each script is that directory — the layout of the source project.)

## Status

Baseline of a continuing analysis. Key verified results so far:

- 11 of 14 winding-number indices show sharp, whole-record ridges
  (FWHM <= 0.08 in M, temporal continuity >= 0.85) over the AR(1) null.
- Seven independently optimized indices converge on the same base
  winding frequency M(NM) ~ 0.2073-0.2077 (0.2% spread).
- Ground-truth recovery on synthetics to within one grid cell.
- Calendar-clocked (autonomous) signals of matched apparent period land
  at M ~ 0.03, not on winding ridges: the transform separates
  non-autonomous from autonomous content.
- White-noise normalization is anti-conservative for red climate data;
  `winding_rank.py` uses AR(1) persistence surrogates instead.

## Related

Part of the GEM-LTE project (Ada optimizer + Python pipeline). The
manifold column (`lte_results.csv` col 4) originates from the LTE model
calibrated in `src/gem-dlod.adb` of the parent repository.

## License

To the extent possible under law, this repository — code, docs, and data
— is dedicated to the public domain (CC0 1.0; see `LICENSE`). Reuse
without conditions; attribution welcomed, never required.
