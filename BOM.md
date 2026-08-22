# Bill of materials — cello and bass viol

One rig serving **cello and bass viol**. Generated from the model by
`tools/make_bom.py`, so every mass, length and bearing size below comes
from the same parameters the parts are built from.

The hammer pins at **192 mm, 222 mm** — move the pin and wind the crank to
change instrument. Everything else is the same hardware for both.

## Printed parts

| part | qty | volume | filament | print it |
|---|---|---|---|---|
| 01 Base | 1 | 46.9 cm³ | 58 g | flat on its underside |
| 02 Top | 1 | 26.2 cm³ | 33 g | flat, bearing seat upwards |
| 03 Slider | 1 | 75.5 cm³ | 94 g | flat on its underside, tubes up |
| 04 Microphone holder | 1 | 11.0 cm³ | 14 g | flat on the arch |
| 05 Microphone arm | 1 | 14.8 cm³ | 18 g | on its side, channel outwards |
| 06 Cable clip | 3 | 1.3 cm³ | 4.7 g | flat, mouth upwards |
| 07 Hammer | 1 | 1.7 cm³ | 2.1 g | on its side |
| 08 Knob | 1 | 8.7 cm³ | 11 g | flat, hex trap down |
| 09 Knob handle | 1 | 1.7 cm³ | 2.1 g | flat, pin upwards |
| 10 Knob handle knurl | 1 | 0.1 cm³ | 0.1 g | on end |
| 11 Handheld hammer | 1 | 1.8 cm³ | 2.2 g | on its side — optional |
| **Total** | | | **238 g** | ~80 m of 1.75 mm |

PLA at 1.24 g/cm³ and 100% infill — the figures are solid volume, so
real filament use at 20–30% infill will be well under half of this.

**Nothing needs support.** The cross-bolt holes are teardrops for that
reason, and the orientations above put a flat face on the bed. Part 11
is a handheld version of the hammer for tapping off the rig — skip it if
you do not want one.

## Hardware

| item | size | qty | notes |
|---|---|---|---|
| Guide rod, aluminium | ⌀16 × 300 mm | 2 | ground or drawn, straight matters more than the grade |
| Linear bearing | LM16UU (⌀16 bore, ⌀28 OD, 37 long) | 2 | press fit into the slider, no clearance |
| Threaded rod | M10 × 312 mm | 1 | the leadscrew; cut from stock |
| Thrust bearing | 6200 (⌀10 bore, ⌀30 OD, 9 wide) | 2 | one in the base, one in the top plate |
| Cap screw | M5 × 20 | 4 | rod clamps, two per plate; head seats in the ⌀8.5 counterbore |
| Nut | M5 | 4 | drops into the clamp slots from below |
| Nut | M10 | 2 | the drive nut in the slider, and one captive in the knob |
| Locking nut | M10 | 2 | either side of a thrust bearing, to stop the leadscrew moving axially |
| Cap screw | M4 × 25 + nut | 1 | hammer pivot, through the 16 mm fork |
| Screw | M3 × 16–20 | 3 | **bolts the base to a board** — see below |

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
| 0.14 mm² wire, ~200 mm lengths | 4 |
| Thin wire, e.g. 34 AWG, ~10 mm | 4 |

Consumables: solder, flux, heat-shrink, two-part epoxy.

## Two things this list assumes

**You will bolt it to a board.** The three M3 screws are not optional.
Free-standing this rig tips under about 120 g applied to the end of the
arm — a hand resting on it. The base's three counterbored holes take M3
screws into a board or the bench; bolted down it is nowhere near its
limit. Same is true of the original violin rig.

**No grub screws.** The original clamps the microphone arm with two
tapered grub screws. Here the arm is gripped by the fins on the holder
and slides in that slot to set the microphone position, so those two
screws are not needed. If your printer runs loose and the arm slides too
freely, adjust `fits.arm_slot` and reprint the holder rather than adding
a screw.

## What differs from the violin build

| | violin | this rig |
|---|---|---|
| guide rods | ⌀10 × 200 | ⌀16 × 300 |
| linear bearings | LM10UU | LM16UU |
| leadscrew | M8 | M10 × 312 |
| thrust bearings | 608 | 6200 |
| clamp hardware | M4 | M5 |
| filament | ~94 g | ~238 g |

The rods step up because a printed cantilever on ⌀10 rods deflects
enough at this reach to move the tap point between taps.

[upstream]: https://github.com/luca-jost-violins/General-Acoustic-Measurement-Setup
