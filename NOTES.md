# Rebuild notes

Goal: a parameterisable build123d model of the GAMS rig, replacing the fixed
`.3mf` files from luca-jost-violins/General-Acoustic-Measurement-Setup.

## Method

The upstream parts are meshes only — no CAD source — so dimensions are
recovered from the meshes and the rebuild is verified against them:

1. `ref/upstream/` — vendored upstream `.3mf` (MIT).
2. `tools/probe_3mf.py` — bounding boxes.  All 11 parts share one assembly
   coordinate frame, so their positions give the assembly directly.
3. `tools/3mf_to_stl.py` → `ref/stl/` — STL for fingerprinting.
4. `tools/render_mesh.py` → `ref/render/` — 4-view renders.
5. `tools/section_mesh.py` / `tools/features.py` → cross-sections and fitted
   circles (centre + diameter) at any plane.
6. `cad-fingerprint <stl> -o tests/test_XX.py` — pytest geometric equivalence
   suite per part; the parametric code must pass it at default parameters.

## Assembly frame (from bounding boxes, mm)

| Part | X | Y | Z |
|---|---|---|---|
| 01 Base | -30..30 | -15..42.50 | 0..10 |
| 02 Top | -30..30 | -15..15 | 190..200 |
| 03 Slider | -35..35 | -15..110.90 | 95..124 |
| 04 Microphone holder | -26.25..26.25 | -3..45.63 | 49.5..67.5 |
| 05 Microphone arm | -3.125..3.125 | 14.68..133.67 | 12.5..56.2 |
| 06 Cable clip | 13.75..26.25 | -12.50..3 | 20..35 |
| 07 Hammer | -6..6 | 103.5..109.5 | 49.00..104.5 |
| 08 Knob | -14..14 | -14..14 | 202..218 |
| 09 Knobhandle | -6..6 | -48.00..6 | 215..229 |
| 10 Knobhandleknurl | -3..3 | -48..-42 | 218.5..227.5 |
| 11 Handheld hammer | same bbox as 07 | | |

Z is the column axis; the M8 leadscrew is on X=Y=0.

## Dimensions recovered so far

**01 Base** (Z 0..10, plate 10 thick)
- Outline 60 wide, Y -15..15 rounded rect, plus a lobe on +Y: arc centred
  (0, 30) reaching Y=42.50 (r = 12.50).
- Leadscrew bore on axis: r=4.50 at Z=0.5, opening to r=6.00 by Z=2, then a
  608 bearing pocket (bbox 22.13 x 26.00) from about Z=4 to the top face.
- Rod bores at (+/-20, 0) — merged with the clamp slots in section, radius
  still to confirm.
- Clamp slots: 3.5 wide at X = +/-(14.7..18.2), running in from Y=15.
- 3 x M3 holes: (+/-24, -9) and (0, 30), d=3.50, counterbored to d=5.50 at
  Z=9.5.
- 4 x curved lightening slots around the leadscrew.

## Next

- **03 Slider** needs a second pass: +11% by volume. The arm's internal
  geometry is the gap — there is a 3.5 mm core running *diagonally* along the
  arm at mid-height (centre X 6.67 at Y=20, drifting to 0.60 by Y=70), which is
  modelled, but something else in the carriage is still over-full. Run
  `tools/volume_diff.py` then `tools/diff_mesh.py` at the worst Z.
- Then 04/05 microphone holder + arm. The arm is a swept S-curve and will need
  spline reconstruction, not arc fitting.
- 06 clip, 07/11 hammers, 08-10 knob.
- Finally the assembly, driven by the shared coordinate frame the .3mf files
  already agree on: base Z 0, slider Z 95, top Z 190.

## Upstream issues raised

Filed against the helper projects while working:

- [cad-fingerprint#3](https://github.com/pzfreo/cad-fingerprint/issues/3) —
  the radial profile measures the candidate from the world origin but the
  reference from the bounding-box centre, so every radial test fails for any
  part not centred on the origin. `max_r` is also hard-coded at 20.0, below
  radii the analyser itself records.
- [cad-fingerprint#4](https://github.com/pzfreo/cad-fingerprint/issues/4) —
  `-o` throws `FileNotFoundError` if the output directory does not exist,
  after the analysis has already run.
- [build123d-mcp#436](https://github.com/pzfreo/build123d-mcp/issues/436) —
  commented rather than filed anew: a tangent junction reads as a 0.00 mm
  thin wall, with a three-way A/B/A+B result isolating it.
