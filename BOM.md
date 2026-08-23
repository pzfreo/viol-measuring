# Bill of materials — cello and bass viol

One rig serving **cello and bass viol**. Generated from the model by
`tools/make_bom.py`, so every mass, length and bearing size below comes
from the same parameters the parts are built from.

The hammer pins at **192 mm, 222 mm** — move the pin and wind the crank to
change instrument. Everything else is the same hardware for both.

## Printed parts

| part | qty | volume | filament | print it |
|---|---|---|---|---|
| 01 Base | 1 | 24.8 cm³ | 31 g | flat on its underside |
| 02 Top | 1 | 10.6 cm³ | 13 g | flat, bearing seat upwards |
| 03 Slider | 1 | 47.9 cm³ | 59 g | flat on its underside, tubes up - PAUSE to embed the nut |
| 04 Microphone holder | 1 | 4.9 cm³ | 6.1 g | flat on the arch |
| 05 Microphone arm | 1 | 15.2 cm³ | 19 g | on its side, channel outwards |
| 06 Cable clip | 3 | 0.6 cm³ | 2.1 g | flat, mouth upwards |
| 07 Hammer | 1 | 1.7 cm³ | 2.1 g | on its side |
| 08 Knob | 1 | 5.7 cm³ | 7.0 g | flat, hex trap down - PAUSE to embed the nut |
| 09 Knob handle | 1 | 1.4 cm³ | 1.8 g | flat, pin upwards - PAUSE to slide the knurl on |
| 10 Knob handle knurl | 1 | 0.1 cm³ | 0.1 g | on end - print this one first |
| 11 Handheld hammer | 1 | 1.8 cm³ | 2.2 g | on its side — optional |
| **Total** | | | **144 g** | ~48 m of 1.75 mm |

PLA at 1.24 g/cm³ and 100% infill — the figures are solid volume, so
real filament use at 20–30% infill will be well under half of this.

**Nothing needs support.** The cross-bolt holes are teardrops for that
reason, and the orientations above put a flat face on the bed. Part 11
is a handheld version of the hammer for tapping off the rig — skip it if
you do not want one.

**Three parts need a print pause**, as in Luca Jost's build video:

- **Slider** and **knob** each capture a leadscrew nut. Pause when the
  hex pocket is open but not yet roofed over, drop the nut in, resume.
  There is no way to fit them afterwards.
- The **knurl** prints first, on its own. The **knob handle** print is
  then paused and the knurl slid onto its pin before the retaining
  flange prints over it. The flange is wider than the knurl bore, so
  again there is no fitting it later.

## Hardware

| item | size | qty | notes |
|---|---|---|---|
| Guide rod, aluminium | ⌀10 × 300 mm | 2 | ground or drawn, straight matters more than the grade |
| Linear bearing | LM10UU (⌀10 bore, ⌀19 OD, 29 long) | 2 | press fit into the slider, no clearance |
| Threaded rod | M8 × 312 mm | 1 | the leadscrew; cut from stock |
| Thrust bearing | 6200 (⌀8 bore, ⌀22 OD, 7 wide) | 2 | one in the base, one in the top plate |
| Cap screw | M4 × 10 | 4 | rod clamps, two per plate. **The length must be exactly this** — shorter misses the nut, longer bottoms out against the print |
| Nut | M4 | 4 | drops into the clamp slots from below |
| Nut | M8 | 1 | the drive nut, embedded in the slider mid-print |
| Locking nut | M8 | 3 | one captive in the knob, two setting the leadscrew's end float |
| Screw | M3 × 16–20 | 3 | **bolts the base to a board** — see below |
| Grub screw, M4 × 5, **cone point** | M4 | 2 | **the hammer's pivot** — one into each fork prong, see below |

## Electronics

Unchanged from Luca Jost's original — his [README][upstream] has
purchase links for all of it.

| item | qty |
|---|---|
| Electret microphone, 9.7 × 4.7 mm | 2 |
| Electret microphone, 6 × 2.7 mm | 2 |
| Behringer UCA-202 audio interface | 1 |
| Cinch (RCA) plugs | 4 |
| 4.7 kΩ resistors | 2 |
| 1 µF ceramic capacitors | 2 |
| 0.14 mm² wire, ~200 mm lengths | 8 |
| Thin wire, e.g. 34 AWG, ~10 mm | 4 |

Consumables: solder, flux, heat-shrink, two-part epoxy.

## Notes

**You will bolt it to a board.** The three M3 screws are not optional.
Free-standing this rig tips under about 56 g applied to the end of the
arm — a hand resting on it. The base's three counterbored holes take M3
screws into a board or the bench; bolted down it is nowhere near its
limit. Same is true of the original violin rig.

**The two M4 grub screws are the hammer's pivot.** One threads into
each fork prong, and their cone points seat in the rim of the 1.5 mm
hole through the hammer's tail — so the hammer hangs on two cones
rather than turning on a pin. That is about as little friction as a
printed pivot can have, which is the point: a stiff pivot damps the
impulse you are trying to measure. Wind them in until the hammer just
swings freely, which is also what stops them working loose.

The prong holes are printed at 3.93, undersize for M4, so each screw
cuts its own thread. Buy the tapered-tip ones — a flat or cup point
has nothing to seat in.

**The microphone lead runs through the slider.** A 3.5 mm bore enters
the carriage's front face through a cone of exactly 15 degrees, so the
lead is led in rather than chafed on an edge, and runs out along the
arm to the fork with its axis at mid thickness the whole way. Earlier
versions of this rebuild stopped that bore short of the face, leaving
the lead nowhere to go.

## What differs from the violin build

| | violin | this rig |
|---|---|---|
| guide rods | ⌀10 × 200 | **⌀10 × 300** |
| linear bearings | LM10UU | LM10UU |
| leadscrew | M8 × 212 | **M8 × 312** |
| thrust bearings | 608 (⌀22) | 608 (⌀22) |
| clamp hardware | M4 × 10 | M4 × 10 |
| column height | 200 mm | **300 mm** |
| filament | ~94 g | ~144 g |

Bold marks the only things that change. This rebuild used to step
the rods and leadscrew up with reach; working out where the movement at
the tap point actually comes from (`tools/stiffness.py`) showed the
printed arm accounts for 91% of it and the rods for 9%, so the step
bought almost nothing and has been removed.

[upstream]: https://github.com/luca-jost-violins/General-Acoustic-Measurement-Setup
