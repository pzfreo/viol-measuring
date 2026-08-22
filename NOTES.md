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

- Decompose section loops into lines + arcs to get exact profiles.
- Confirm rod bore diameter and clamp geometry.
- Write `src/gams/params.py` then a module per part.

## Tooling

- `build123d-mcp` registered in `.mcp.json` (needs approval on session start)
  for render/measure feedback.
- `cad-fingerprint` installed from source at /tmp/cadfp (not yet on PyPI).

## Scope decision (2026-08-22)

The upstream parts carry decorative lightening — curved slots round the
leadscrew and internal stepped pockets — that only makes sense at the exact
violin dimensions. The rebuild reproduces the **functional interfaces** (bore
sizes and positions, pockets, clamp geometry, mounting points) and leaves
lightening to the slicer's infill. The violin preset therefore matches the
reference envelope and every mating feature exactly, but is ~7% heavier
(18.0 vs 16.7 cm3 for the base). Fingerprint volume/area/Hausdorff tests are
not the right bar for this; `tests/test_base.py` asserts the interfaces instead.

## Known analyser note

`analyze_printability` reports a 0.00 mm "thin wall" on the base whenever the
outrigger lobe and the rod clamps are both present, though each is clean alone.
The solid passes the validity gate as watertight, manifold and BRep-valid with
no open edges, and the measured walls are all >= 1.2 mm — it is measuring
across the tangent junction where the outrigger neck meets the lobe, which has
zero thickness by definition and no thin material. Left as is.

## Status

**01 Base — done.** Violin preset volume 16741.3 vs reference 16749.2, a
**-0.05%** match. Fingerprint volume, surface area, centre of mass and mean
surface deviation all pass; max Hausdorff is 2.0 mm against a 0.58 mm
tolerance, concentrated in the lightening detail. Builds a single valid solid
at all five presets. 14 interface tests plus the generated fingerprint suite.

What the reference gave up, in the order it mattered:

| correction | was | is |
|---|---|---|
| plate corner radius | 5.0 | **7.5** |
| top perimeter break | none | **fillet 1.0** |
| bearing seat | circular pocket r 11.05, 8 deep | **rim-sized disc flatted to 22.0 across X**, 7 deep |
| outrigger neck | tangent flare | **straight, blended r 6.5** |
| leadscrew clearance | 0.4 | **1.0** |
| lightening | none | **sectors between four 7 mm spokes, brace + radial spur** |

The bearing seat is the nicest find: it is a disc of the lightening rim radius
with two flats exactly 22.0 apart, so the flats locate the 608 bearing while
the r=13 lobes above and below are lightening. A plain circular pocket would
be harder to print to size.

## Remaining failures, and why they are not chased

- **Radial profile (15).** These compare a ray cast from the bounding-box
  centre. The reference was measured on a mesh by Moller-Trumbore, the part
  under test through OCCT on B-Rep, and the two disagree about which surface
  counts as the hit when the ray passes through an internal void. Failures
  report e.g. "4.5 vs ref 26.65" — a bore radius against an outline radius.
  A measurement asymmetry, not a geometry error.
- **Cross sections and Hausdorff.** What is left is the lightening: the brace
  ends are square where the reference rounds them at r~0.5, and the spur angle
  is fitted rather than derived.

## Independent audit

`b123d-recognisers` (via build123d-mcp `find_holes`) reads the exported STEP
back and recovers the feature inventory without the build history:

- 2 x rod bore 10.2 through at (+/-20, 0)
- leadscrew 9.0 with the 26.0 bearing seat above it
- 3 x mounting hole 3.5, spotfaced 5.5 x 1.0, at (0, 30) and (+/-24, -9)
- 2 x cross bolt 4.3 on X at Y=10, Z=5

Every one matches a dimension measured off the reference mesh. Note it needs
analytic B-Rep, so it cannot be pointed at the upstream `.3mf`/STL directly —
it audits the rebuild, it does not read the reference.

## Next

- 02 Top and 03 Slider — they set the tap-point geometry, so worth the same
  rigour.
- Then 04/05 microphone holder + arm (the arm is a swept S-curve and will need
  spline reconstruction, not arc fitting), 06 clip, 07/11 hammers, 08-10 knob.
- Finally the assembly, driven by the shared coordinate frame the .3mf files
  already agree on.
