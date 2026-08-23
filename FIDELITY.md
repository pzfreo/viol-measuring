# How close is it, and how do I know?

This is the working behind the claim on the front page: that the `violin`
preset reproduces [Luca Jost's rig][upstream] rather than merely resembling it.
None of it is needed to build one. It is here so the claim can be checked, and
so the places it does not hold are written down rather than glossed.

## What was compared, and how

Each of his eleven `.3mf` files was moved into the frame its parametric
counterpart is built in, and then compared against it. There is a generated
geometric-equivalence suite per part in `tests/fingerprint/`, built with
[cad-fingerprint][fingerprint], holding an embedded copy of his mesh and
checking volume, surface area, centre of mass, the full inertia tensor,
cross-sections and point-by-point surface deviation.

```bash
python tools/report.py       # every part, measured, whether it passes or not
```

The suites only print a value when a check fails, which tells you nothing about
how much room a passing part had. `tools/report.py` calls the same routines
directly so every part reports a number either way.

## Where it stands

| part | volume | surface deviation | worst | centre of mass |
|---|---|---|---|---|
| Base | −0.37% | 0.383 mm mean | 0.804 / 3.07 | 0.027 mm |
| Top | −0.10% | 0.010 | 0.286 / 0.30 | 0.013 |
| Slider | −0.07% | 0.260 | 2.179 / 3.24 | 0.085 |
| Microphone holder | +0.04% | 0.007 | 0.060 / 0.30 | 0.021 |
| Microphone arm | +0.58% | 0.172 | 1.293 / 2.00 | 0.105 |
| Cable clip | +0.06% | 0.016 | 0.217 / 0.30 | 0.013 |
| Hammer | −0.14% | 0.098 | 0.536 / 1.24 | 0.023 |
| Knob | −0.02% | 0.004 | 0.040 / 0.30 | 0.003 |
| Knob handle | +0.03% | 0.001 | 0.024 / 0.30 | 0.002 |
| Knurled sleeve | +0.20% | 0.006 | 0.250 / 0.30 | 0.050 |
| Handheld hammer | −0.16% | 0.095 | 0.637 / 1.43 | 0.016 |

**All eleven are inside every tolerance.** Worst volume error 0.58%, worst
centre of mass 0.105 mm, every bounding box within 0.010 mm. The tolerances are
not comparable between parts — cad-fingerprint scales each from how well that
part's reference mesh decimated, which is why the slider is allowed 3.24 mm and
the knob 0.30.

The *fits* are asserted separately, by ordinary tests: the crank socket clears
the knob post, the sleeve spins on its pin but cannot come off, the hammer
swings free in the fork, the bearing bores are a zero-clearance press fit on a
⌀19 LM10UU, and no two parts interfere in any preset.

## Volume is the weak test

It was also the one this rebuild used for far too long, and it hid real errors.
The hammer sat at +1.1% by volume while having a fork where the reference has a
counterbored bore, a centred square core where it has an offset round channel,
and a sampled taper table where it has a single 200 mm arc. Three substantial
errors that nearly cancelled.

What catches that is surface deviation, and — for anything with a hole in it —
looking at the part. The knurled sleeve passed every metric with small tabs of
material hanging off its top rim, because a row of its diamond crossings landed
exactly on the edge. No number objected. That was spotted by eye in a CAD
viewer, and it is the honest limit of everything on this page.

## What the measurement turned up

Fitting primitives and reading the residual, rather than storing sampled
points, is what turns a good-enough curve into his actual number. Where a fit
comes back at two microns, that is a construction and not a coincidence.

- The **hammer's outline is three arcs** — a ⌀12 round head, a ⌀5 round tail,
  and an R200 arc tangent to both, fitting to 0.002 mm. Not a taper and not a
  spline. Its internal channel is round, offset 1 mm from the centre plane,
  straight to Z=36 and then out through one face on an R38 arc.
- The **microphone holder's arch is two very large arcs**, R54.7 outside and
  R45.4 in, struck from centres out on the rod axis and meeting at a point that
  is then rounded off. They fit to 0.01 mm, so the arch height falls out of them
  rather than being typed in.
- The **knob's knurl is nine circles that all pass through its axis**, struck at
  half the knob's radius from centres half the radius out. Their union is the
  body. It fits within 0.02 mm where the best single cutter managed 0.30.
- **Every teardrop is struck as tangents to its hole**, which is what puts the
  sides at exactly 45° — the steepest overhang a printer bridges without
  support. A triangle from the hole's diameter, which is what this rebuild had,
  gives whatever angle the apex constant happens to produce.
- The **clamp nut slots close as a 30° gable**, so the nut meets a wedge and
  settles onto the bolt axis instead of sitting anywhere across the slot.
- Both plates **relieve the thrust bearing's inner race**, stepping the bore
  22 → 12 → 9 mm. Without it the plate bears on the race the leadscrew turns in.
- The **microphone arm** is a rounded rectangle with an obround channel inside
  it — not the other way round, which costs 9% of the section area. Its S-bend
  is an arc, a straight and a second arc, tangent throughout. Its three side
  windows are spaced along the arm rather than along its reach, so the middle
  one spans barely 2 mm of reach for its 10 mm of arm.
- The **microphone seat is a plain ⌀6.00 hole**, fitting to 0.006 mm — which
  matches the 6 × 2.7 mm electret in his bill of materials.
- The **cable enters the slider through a cone of exactly 15°** in the
  carriage's front face, and runs out along the arm to the fork on a ⌀3.5 bore
  whose axis stays at mid-thickness the whole way.
- The **knurled sleeve is a diamond**: two families of eight helical grooves at
  13.3° of twist per millimetre. Where the crossings sit along its height is a
  separate thing to get right, and getting it wrong puts tabs on the rim.
- The **bearing seat** in both plates is not a round pocket but a disc flatted
  to exactly 22.0 mm across, so the flats locate the 608 — far easier to print
  to size than a bore.

## The hardware ladder, and why it is gone

This rebuild used to step the guide rods and leadscrew up with reach: ⌀12 above
the violin, ⌀16 for bass viol and cello, M10 instead of M8. That was my rule,
not his, on the argument that a printed cantilever on ⌀10 rods deflects enough
at a cello's reach to move the tap point between taps.

Working out where that movement actually comes from says otherwise:

```bash
python tools/stiffness.py
```

| cello rig, 300 mm column | movement at the tap point | |
|---|---|---|
| printed slider arm | 394 µm | 91% |
| ⌀10 rods | 40 µm | 9% |
| ⌀16 rods | 9 µm | 2% |

Going ⌀10 → ⌀16 buys 31 µm out of 434. In stiffness the arm is 1.9 N/mm at the
tap point and the ⌀10 rods 19.3 — springs in series, so the soft one decides,
and the rig's first mode moves only from **52 Hz to 55**. The leadscrew was
worse: it carries about 1 N, and an M8 at 300 mm buckles near 2000 N, so
stepping it to M10 was three orders of magnitude of nothing — and it pulled the
thrust bearing up with it. One invented rule dragged two more behind it.

The ladder is gone. Every preset now runs on his hardware, and the plates went
back to his 60 × 30 with it, which took 94 g of filament off the cello rig.

**The finding that matters is the one the ladder was obscuring:** at 52 Hz the
larger rigs sit below a cello's A0 at about 100 Hz, so the rig can ring inside
the band being measured. Fixing that means a deeper arm section, since stiffness
goes as the cube of depth. It has not been done.

## The two M4 grub screws

For a long time this was the one thing in his design I could not account for. I
looked for a threaded hole in the bearing tubes, found none, and wrote it up as
an unresolved gap. It is not a gap, and the answer is better than a fixing.

**They are the hammer's pivot.** One threads into each fork prong; their cone
points seat in the rim of the 1.5 mm hole through the hammer's tail, so the
hammer hangs on two cones rather than turning on a pin. The measurements:

| | |
|---|---|
| fork prong hole | ⌀3.925, right through — *under* M4's 4.0 major diameter, so the screw cuts its own thread |
| prong thickness | 4.705 mm, so an M4 × 5 stands 0.295 proud of the inner face |
| hammer's hole | ⌀1.496 through — far too small for a bolt; it is a seat for the cone tips |
| both | coaxial on X at Y = 106.5, Z = 5.0 |

Every detail that had puzzled me separately falls out of it: why the hammer's
hole is only 1.5 mm when I was hunting for a pivot bore; why there are exactly
two screws; why 5 mm, which is the length that gives cone engagement rather than
a clamp; why *tapered tip* and not flat or cup; and why his published parts list
has **no hammer pivot bolt** — four M4 × 10 for the rod clamps, four M4 nuts, two
M4 × 5 grubs, and nothing else.

It is also the right answer mechanically. Two cones is about as little friction
as a printed pivot can have, and a stiff pivot damps the impulse the rig exists
to measure.

This repo had modelled the prong hole as a ⌀4.0 clearance hole and the BOM had
invented an M4 × 25 bolt and nut to go through it. Both are corrected: the hole
is now the thread-forming 3.925 he uses, and the fastener is gone.

## Known gaps

**Above violin size, the scaling rules are mine** and none of those presets has
been printed. See the front page for what that means in practice.

## Tooling

Everything here is reproducible from the repository.

| | |
|---|---|
| `tools/report.py` | every part measured against his mesh |
| `tools/stiffness.py` | where the compliance lives, and the first mode |
| `tools/stability.py` | centre of gravity and what it takes to tip it over |
| `tools/interference.py` | no two parts occupying the same space |
| `tools/compare_sections.py` | his section and mine on the same plane |
| `tools/overlay.py` | the same, drawn on top of each other |
| `tools/xsection_ascii.py` | a filled section as text, when solid-or-void must be unambiguous |
| `tools/find_bores.py` | every cylindrical void in a reference mesh |
| `tools/make_locals.py` | his `.3mf` files moved into each part's own frame |

Two bugs in cad-fingerprint were found doing this and are filed upstream:
[#5][fp5], cross-section area adds holes instead of subtracting them; and
[#6][fp6], the radial profile compares the nearest surface against a reference
taken from the outer one, so every hollow part fails every ray that crosses a
cavity. Between them they accounted for 194 of 206 remaining check failures,
which is why `tools/report.py` leaves both out.

[fingerprint]: https://github.com/pzfreo/cad-fingerprint
[fp5]: https://github.com/pzfreo/cad-fingerprint/issues/5
[fp6]: https://github.com/pzfreo/cad-fingerprint/issues/6

[upstream]: https://github.com/luca-jost-violins/General-Acoustic-Measurement-Setup
