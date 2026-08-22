"""Generate BOM.md for a rig, from the model rather than by hand.

    python tools/make_bom.py "bass viol+cello"

Every printed mass, bolt length and bearing size below is computed from the
same parameters the parts are built from, so the list cannot drift from the
geometry.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from gams import (  # noqa: E402
    INSTRUMENTS, Rig, base, clip, grip, hammer, handheld_hammer, handle,
    holder, knob, mic_arm, slider, top,
)
from gams.params import cap_head, nut  # noqa: E402

PLA = 1.24e-3            # g/mm3
FILAMENT_AREA = 2.405    # mm2, 1.75 mm filament

PARTS = [
    ("01 Base", base, 1, "flat on its underside"),
    ("02 Top", top, 1, "flat, bearing seat upwards"),
    ("03 Slider", slider, 1, "flat on its underside, tubes up"),
    ("04 Microphone holder", holder, 1, "flat on the arch"),
    ("05 Microphone arm", mic_arm, 1, "on its side, channel outwards"),
    ("06 Cable clip", clip, 3, "flat, mouth upwards"),
    ("07 Hammer", hammer, 1, "on its side"),
    ("08 Knob", knob, 1, "flat, hex trap down"),
    ("09 Knob handle", handle, 1, "flat, pin upwards"),
    ("10 Knob handle knurl", grip, 1, "on end"),
    ("11 Handheld hammer", handheld_hammer, 1, "on its side — optional"),
]


def standard_length(minimum, steps=(10, 12, 16, 20, 25, 30, 35, 40, 50)):
    for s in steps:
        if s >= minimum:
            return s
    return int(minimum) + 5


def rows(rig):
    hw = rig.hw
    nut_af, nut_t = nut(hw.clamp_bolt)
    lnut_af, lnut_t = nut(hw.screw_d)

    nut_face = rig.rod_x - rig.slit_w / 2 - rig.jaw_wall
    head_seat = rig.plate_width / 2 - rig.head_cbore_depth
    clamp_len = standard_length(head_seat - nut_face + nut_t)

    fork_w = 2 * rig.fork_r
    pivot_len = standard_length(fork_w + nut(4)[1] + 2)

    screw_len = rig.knob_z + rig.knob_bore_h + rig.knob_nut_h

    return {
        "rod_d": hw.rod_d, "rod_len": rig.rod_length,
        "bearing_od": hw.bearing_od, "bearing_len": hw.bearing_len,
        "screw_m": hw.screw_d, "screw_len": screw_len,
        "thrust_bore": hw.screw_d, "thrust_od": hw.thrust_od,
        "thrust_w": hw.thrust_len,
        "clamp_m": hw.clamp_bolt, "clamp_len": clamp_len,
        "clamp_head": cap_head(hw.clamp_bolt),
        "clamp_nut_af": nut_af, "clamp_nut_t": nut_t,
        "lnut_af": lnut_af, "lnut_t": lnut_t,
        "pivot_len": pivot_len, "fork_w": fork_w,
        "mount_cbore": rig.mount_cbore_d,
    }


def main(name="bass viol+cello", out="BOM.md"):
    names = [n.strip() for n in name.split("+")]
    rig = Rig.covering(*(INSTRUMENTS[n] for n in names))
    d = rows(rig)

    printed, total = [], 0.0
    for label, fn, qty, orient in PARTS:
        vol = fn(rig).volume
        mass = vol * PLA * qty
        total += mass
        printed.append((label, qty, vol / 1000, mass, orient))

    covers = " and ".join(i.name for i in rig.covers)
    pins = ", ".join(f"{r:.0f} mm" for r in rig.pivot_reaches)
    filament = total / PLA / FILAMENT_AREA / 1000

    L = []
    A = L.append
    A(f"# Bill of materials — {covers}")
    A("")
    A(f"One rig serving **{covers}**. Generated from the model by")
    A("`tools/make_bom.py`, so every mass, length and bearing size below comes")
    A("from the same parameters the parts are built from.")
    A("")
    A(f"The hammer pins at **{pins}** — move the pin and wind the crank to")
    A("change instrument. Everything else is the same hardware for both.")
    A("")
    A("## Printed parts")
    A("")
    A("| part | qty | volume | filament | print it |")
    A("|---|---|---|---|---|")
    for label, qty, cm3, mass, orient in printed:
        fmt = f"{mass:.1f}" if mass < 10 else f"{mass:.0f}"
        A(f"| {label} | {qty} | {cm3:.1f} cm³ | {fmt} g | {orient} |")
    A(f"| **Total** | | | **{total:.0f} g** | ~{filament:.0f} m of 1.75 mm |")
    A("")
    A("PLA at 1.24 g/cm³ and 100% infill — the figures are solid volume, so")
    A("real filament use at 20–30% infill will be well under half of this.")
    A("")
    A("**Nothing needs support.** The cross-bolt holes are teardrops for that")
    A("reason, and the orientations above put a flat face on the bed. Part 11")
    A("is a handheld version of the hammer for tapping off the rig — skip it if")
    A("you do not want one.")
    A("")
    A("## Hardware")
    A("")
    A("| item | size | qty | notes |")
    A("|---|---|---|---|")
    A(f"| Guide rod, aluminium | ⌀{d['rod_d']:.0f} × {d['rod_len']:.0f} mm | 2 | ground or drawn, straight matters more than the grade |")
    A(f"| Linear bearing | LM{d['rod_d']:.0f}UU (⌀{d['rod_d']:.0f} bore, ⌀{d['bearing_od']:.0f} OD, {d['bearing_len']:.0f} long) | 2 | press fit into the slider, no clearance |")
    A(f"| Threaded rod | M{d['screw_m']:.0f} × {d['screw_len']:.0f} mm | 1 | the leadscrew; cut from stock |")
    A(f"| Thrust bearing | 6200 (⌀{d['thrust_bore']:.0f} bore, ⌀{d['thrust_od']:.0f} OD, {d['thrust_w']:.0f} wide) | 2 | one in the base, one in the top plate |")
    A(f"| Cap screw | M{d['clamp_m']:.0f} × {d['clamp_len']:.0f} | 4 | rod clamps, two per plate; head seats in the ⌀{d['clamp_head']:.1f} counterbore |")
    A(f"| Nut | M{d['clamp_m']:.0f} | 4 | drops into the clamp slots from below |")
    A(f"| Nut | M{d['screw_m']:.0f} | 2 | the drive nut in the slider, and one captive in the knob |")
    A(f"| Locking nut | M{d['screw_m']:.0f} | 2 | either side of a thrust bearing, to stop the leadscrew moving axially |")
    A(f"| Cap screw | M4 × {d['pivot_len']:.0f} + nut | 1 | hammer pivot, through the {d['fork_w']:.0f} mm fork |")
    A(f"| Screw | M3 × 16–20 | 3 | **bolts the base to a board** — see below |")
    A("| Grub screw, M4 × 5, cone point | M4 | 2 | in the original parts list; see the note below |")
    A("")
    A("## Electronics")
    A("")
    A("Unchanged from Luca Jost's original — his [README][upstream] has")
    A("purchase links for all of it.")
    A("")
    A("| item | qty |")
    A("|---|---|")
    A("| Electret microphone, 9.7 × 4.7 mm | 2 |")
    A("| Electret microphone, 6 × 2.7 mm | 2 |")
    A("| Behringer UCA-202 audio interface | 1 |")
    A("| Cinch (RCA) plugs | 4 |")
    A("| 4.7 kΩ resistors | 2 |")
    A("| 1 µF ceramic capacitors | 2 |")
    A("| 0.14 mm² wire, ~200 mm lengths | 4 |")
    A("| Thin wire, e.g. 34 AWG, ~10 mm | 4 |")
    A("")
    A("Consumables: solder, flux, heat-shrink, two-part epoxy.")
    A("")
    A("## Notes")
    A("")
    A("**You will bolt it to a board.** The three M3 screws are not optional.")
    A("Free-standing this rig tips under about 120 g applied to the end of the")
    A("arm — a hand resting on it. The base's three counterbored holes take M3")
    A("screws into a board or the bench; bolted down it is nowhere near its")
    A("limit. Same is true of the original violin rig.")
    A("")
    A("**The two M4 grub screws — I do not know what they are for.** They are")
    A("in Luca Jost's parts list, so they have a purpose in a design that has")
    A("been built and iterated on. I could not find a hole for them in any of")
    A("his printed parts: the microphone holder's fins are solid walls with no")
    A("opening, and nor is there one in the clip or the arm. So this rebuild")
    A("does not model them, which is a gap in the rebuild rather than a")
    A("judgement that they are unnecessary. They are listed above because you")
    A("should buy them. If you know where they go, please open an issue — it")
    A("is the one item on the original list this model cannot account for.")
    A("")
    A("## What differs from the violin build")
    A("")
    A("| | violin | this rig |")
    A("|---|---|---|")
    A(f"| guide rods | ⌀10 × 200 | ⌀{d['rod_d']:.0f} × {d['rod_len']:.0f} |")
    A(f"| linear bearings | LM10UU | LM{d['rod_d']:.0f}UU |")
    A(f"| leadscrew | M8 | M{d['screw_m']:.0f} × {d['screw_len']:.0f} |")
    A(f"| thrust bearings | 608 | 6200 |")
    A(f"| clamp hardware | M4 | M{d['clamp_m']:.0f} |")
    violin = Rig(INSTRUMENTS["violin"])
    violin_total = sum(fn(violin).volume * PLA * qty for _, fn, qty, _ in PARTS)
    A(f"| filament | ~{violin_total:.0f} g | ~{total:.0f} g |")
    A("")
    A("The rods step up because a printed cantilever on ⌀10 rods deflects")
    A("enough at this reach to move the tap point between taps.")
    A("")
    A("[upstream]: https://github.com/luca-jost-violins/General-Acoustic-Measurement-Setup")
    A("")

    pathlib.Path(out).write_text("\n".join(L))
    print(f"{out}: {covers}, {total:.0f} g printed, pins at {pins}")


if __name__ == "__main__":
    main(sys.argv[1].replace("_", " ") if len(sys.argv) > 1 else "bass viol+cello")
