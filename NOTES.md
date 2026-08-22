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

## Status: complete

Every part is within 1.9% of the upstream reference by volume, against a 3%
target, and every one builds as a single valid solid at all five instrument
presets (55 builds).

| part | built | reference | diff |
|---|---|---|---|
| 01 Base | 16780.4 | 16749.2 | +0.19% |
| 02 Top | 10735.3 | 10650.4 | +0.80% |
| 03 Slider | 29416.0 | 29652.7 | -0.80% |
| 04 Microphone holder | 4471.9 | 4500.2 | -0.63% |
| 05 Microphone arm | 2198.8 | 2193.6 | +0.24% |
| 06 Cable clip | 558.9 | 558.5 | +0.07% |
| 07 Hammer | 1703.1 | 1684.7 | +1.09% |
| 08 Knob | 5759.3 | 5676.8 | +1.45% |
| 09 Knobhandle | 1419.6 | 1423.5 | -0.27% |
| 10 Knobhandleknurl | 80.7 | 79.2 | +1.90% |
| 11 Handheld hammer | 1752.0 | 1766.1 | -0.80% |

74 tests pass. They assert fits, not just shapes: the handle socket clears the
knob post, the grip spins on its pin but cannot come off, the hammer shaft
swings free in the slider fork, the microphone channel takes a 6 mm electret,
the bearing bores are a zero-clearance press fit.

### The microphone arm, and a correction

An earlier pass recorded that the arm "tapers" and was modelled at a constant
section as an approximation. **Both halves of that were wrong**, and the real
structure matters:

- The outer section is **constant**, and it is an **obround** — ends fully
  rounded at radius t/2, not a rounded rectangle. That distinction alone is
  ~9% of the arm's volume.
- What changes along the arm is that the **+X wall is cut away in two short
  windows** (Y 58.5..70.5 and 109.5..120.5), so the cable is laid into the
  channel from the side rather than threaded through it.
- Everywhere else — including the whole S-bend — the section stays a **closed
  box**. That is the important part: an open section is far softer in twist
  than a closed one, and the original deliberately keeps the box closed through
  the bend, where the arm is longest and least supported.

The first model had it as an open C for the whole run past the clamp with a
bore sized to make the volume come out right. It hit the number and got the
structure backwards.

## What the reference gave up, part by part

- **Base/Top**: bearing seat is a rim-sized disc flatted to exactly 22.0 across
  X — the flats locate the 608, which is far easier to print to size than a
  round pocket. Lightening is mirror-symmetric about both axes, not four-fold.
- **Slider**: the arm necks to a waist at 0.755 of reach, and each bearing post
  is L-shaped in section, wide at the bearing and stepping in at the rim.
- **Cable clip**: it is one ring twice, the second dropped by exactly one outer
  radius so the two touch.
- **Holder**: the arch is a superellipse, n = 1.66 outer and 1.64 inner.
- **Hammer**: 07 and 11 are the same part; 11 simply has no pivot slot.

## The microphone subsystem did not scale (fixed)

The first assembly looked right for the violin and was broken for every gamba:
the microphone arm sat at violin height (Z 12.5..56.2) on a 300 mm column, and
the holder was at Z 206 from a formula that had no business existing. Nothing
was literally absent — the arm and holder were simply floating, unconnected to
anything.

What was wrong, and what each is now derived from:

| was fixed at | now |
|---|---|
| `mic_arm_w` 6.25, `mic_arm_t` 3.66 | fractions of mic reach |
| channel size and offset | fractions of the arm section |
| `mic_arm_root_z` 54.35 | tap height + 9.35, i.e. just clear of the belly |
| `mic_arm_tip_z` 14.34 | the microphone height |
| `holder_z` = mic_height x 3.3 | set so the fins land on the arm's root |
| `arm_slot_w` 6.31 | arm width + 0.06 |
| `fin_h`, `fin_outer_x`, arch semi-axes | derived from the arm and the rod span |
| `handle_len` 45 | 1.607 x knob diameter |
| `clip_h`, `clip_mouth_y`, `holder_h` | multiples of rod diameter |

Two things only showed up once the gamba presets were actually built:

- **The traced bend table's Y values are absolute fractions of reach.** Making
  `mic_arm_bend_from` derived did nothing until the table was remapped onto
  each rig's own bend. Until then the bass arm's swept section folded through
  itself and the part came out as four solids.
- **The bend has to start clear of the holder.** The drop grows with rib depth
  (x3.3 from violin to bass viol) far faster than the reach does (x1.6), so the
  bend starts earlier and earlier — and on the bass rig it started *inside the
  fins gripping the arm*. `mic_arm_bend_from` now has a floor at the holder's
  forward reach.

The lesson is the same one as the slider's arm taper: **a parameter that is a
fixed number rather than a ratio does not announce itself on the preset it was
measured from.** Only building the extremes finds them.

## Next, if you want it

- The assembly, driven by the shared coordinate frame the .3mf files already
  agree on: base Z 0, slider Z 95, top Z 190, knob Z 202.
- A tap test on the bare rig to find where the arm rings, before trusting the
  bass viol preset at 192 mm reach.
