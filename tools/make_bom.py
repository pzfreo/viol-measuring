"""Generate BOM.md for a rig, from the model rather than by hand.

    python tools/make_bom.py "bass viol+cello"

Every printed mass, bolt length and bearing size below is computed from the
same parameters the parts are built from, so the list cannot drift from the
geometry.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from gams import (  # noqa: E402
    INSTRUMENTS, Rig, base, clip, grip, hammer, handheld_hammer, handle,
    holder, knob, mic_arm, slider, top,
)
from gams.params import cap_head, nut  # noqa: E402
from stability import cog, tipping_loads  # noqa: E402

PLA = 1.24e-3            # g/mm3
FILAMENT_AREA = 2.405    # mm2, 1.75 mm filament

def standard_length(minimum, steps=(8, 10, 12, 16, 20, 25, 30, 35, 40)):
    """Smallest stock length that reaches `minimum`."""
    for n in steps:
        if n >= minimum:
            return n
    return int(minimum) + 5


PARTS = [
    ("01 Base", base, 1, "flat on its underside"),
    ("02 Top", top, 1, "flat, bearing seat upwards"),
    ("03 Slider", slider, 1, "flat on its underside, tubes up - PAUSE to embed the nut"),
    ("04 Microphone holder", holder, 1, "flat on the arch"),
    ("05 Microphone arm", mic_arm, 1, "on its side, channel outwards"),
    ("06 Cable clip", clip, 3, "flat, mouth upwards"),
    ("07 Hammer", hammer, 1, "on its side"),
    ("08 Knob", knob, 1, "flat, hex trap down - PAUSE to embed the nut"),
    ("09 Knob handle", handle, 1, "flat, pin upwards - PAUSE to slide the knurl on"),
    ("10 Knob handle knurl", grip, 1, "on end - print this one first"),
    ("11 Handheld hammer", handheld_hammer, 1, "on its side — optional"),
]


def rows(rig):
    hw = rig.hw
    nut_af, nut_t = nut(hw.clamp_bolt)
    lnut_af, lnut_t = nut(hw.screw_d)

    clamp_len = rig.clamp_bolt_len

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

    mass, (cx, cy, _cz), _ = cog(rig)
    tip_g = tipping_loads(rig, mass, (cx, cy))["down on the arm tip"] / 9.81e-3
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
    A("**Three parts need a print pause**, as in Luca Jost's build video:")
    A("")
    A("- **Slider** and **knob** each capture a leadscrew nut. Pause when the")
    A("  hex pocket is open but not yet roofed over, drop the nut in, resume.")
    A("  There is no way to fit them afterwards.")
    A("- The **knurl** prints first, on its own. The **knob handle** print is")
    A("  then paused and the knurl slid onto its pin before the retaining")
    A("  flange prints over it. The flange is wider than the knurl bore, so")
    A("  again there is no fitting it later.")
    A("")
    A("## Hardware")
    A("")
    A("| item | size | qty | notes |")
    A("|---|---|---|---|")
    A(f"| Guide rod, aluminium | ⌀{d['rod_d']:.0f} × {d['rod_len']:.0f} mm | 2 | ground or drawn, straight matters more than the grade |")
    A(f"| Linear bearing | LM{d['rod_d']:.0f}UU (⌀{d['rod_d']:.0f} bore, ⌀{d['bearing_od']:.0f} OD, {d['bearing_len']:.0f} long) | 2 | press fit into the slider, no clearance |")
    A(f"| Threaded rod | M{d['screw_m']:.0f} × {d['screw_len']:.0f} mm | 1 | the leadscrew; cut from stock |")
    A(f"| Thrust bearing | 6200 (⌀{d['thrust_bore']:.0f} bore, ⌀{d['thrust_od']:.0f} OD, {d['thrust_w']:.0f} wide) | 2 | one in the base, one in the top plate |")
    A(f"| Cap screw | M{d['clamp_m']:.0f} × {d['clamp_len']:.0f} | 4 | rod clamps, two per plate. **The length must be exactly this** — shorter misses the nut, longer bottoms out against the print |")
    A(f"| Nut | M{d['clamp_m']:.0f} | 4 | drops into the clamp slots from below |")
    A(f"| Nut | M{d['screw_m']:.0f} | 1 | the drive nut, embedded in the slider mid-print |")
    A(f"| Locking nut | M{d['screw_m']:.0f} | 3 | one captive in the knob, two setting the leadscrew's end float |")
    A(f"| Cap screw | M4 × {d['pivot_len']:.0f} + nut | 1 | hammer pivot, through the {d['fork_w']:.0f} mm fork |")
    A(f"| Screw | M3 × 16–20 | 3 | **bolts the base to a board** — see below |")
    A("| Grub screw, M4 × 5, cone point | M4 | 2 | **retain the linear bearings in the slider** — see the note below |")
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
    A("| 0.14 mm² wire, ~200 mm lengths | 8 |")
    A("| Thin wire, e.g. 34 AWG, ~10 mm | 4 |")
    A("")
    A("Consumables: solder, flux, heat-shrink, two-part epoxy.")
    A("")
    A("## Notes")
    A("")
    A("**You will bolt it to a board.** The three M3 screws are not optional.")
    A(f"Free-standing this rig tips under about {tip_g:.0f} g applied to the end of the")
    A("arm — a hand resting on it. The base's three counterbored holes take M3")
    A("screws into a board or the bench; bolted down it is nowhere near its")
    A("limit. Same is true of the original violin rig.")
    A("")
    A("**The two M4 grub screws are not modelled, and I do not know where")
    A("they go.** In Luca Jost's build video they are threaded into the")
    A("slider after the linear bearings are fitted, tightened so they cannot")
    A("work loose. I have not been able to find a hole for them: the bearing")
    A("tube walls are solid at every height, and the one screw-sized bore in")
    A("the slider turns out to be the cable channel from the arm, not a")
    A("threaded hole.")
    A("")
    A("So this is an unresolved gap in the rebuild, not a finding that the")
    A("screws are unnecessary. Buy them; if you work out where they go,")
    A("please open an issue.")
    A("")
    A("**The microphone lead runs through the slider.** A 3.5 mm bore enters")
    A("the carriage's front face through a cone of exactly 15 degrees, so the")
    A("lead is led in rather than chafed on an edge, and runs out along the")
    A("arm to the fork with its axis at mid thickness the whole way. Earlier")
    A("versions of this rebuild stopped that bore short of the face, leaving")
    A("the lead nowhere to go.")
    A("")
    A("## What differs from the violin build")
    A("")
    violin_rig = Rig(INSTRUMENTS["violin"])
    vd = rows(violin_rig)
    violin_total = sum(fn(violin_rig).volume * PLA * qty
                       for _, fn, qty, _ in PARTS)
    A("| | violin | this rig |")
    A("|---|---|---|")
    for label, key, fmt in (("guide rods", "rod_len", "⌀{rod_d:.0f} × {rod_len:.0f}"),
                            ("linear bearings", "rod_d", "LM{rod_d:.0f}UU"),
                            ("leadscrew", "screw_len", "M{screw_m:.0f} × {screw_len:.0f}"),
                            ("thrust bearings", "thrust_od", "608 (⌀{thrust_od:.0f})"),
                            ("clamp hardware", "clamp_len", "M{clamp_m:.0f} × {clamp_len:.0f}"),
                            ("column height", "rod_len", "{rod_len:.0f} mm")):
        a, b = fmt.format(**vd), fmt.format(**d)
        mark = "" if a == b else " **"
        A(f"| {label} | {a} | {b}{mark.rstrip()} |" if a == b
          else f"| {label} | {a} | **{b}** |")
    A(f"| filament | ~{violin_total:.0f} g | ~{total:.0f} g |")
    A("")
    A("Bold marks the only things that change. This rebuild used to step")
    A("the rods and leadscrew up with reach; working out where the movement at")
    A("the tap point actually comes from (`tools/stiffness.py`) showed the")
    A("printed arm accounts for 91% of it and the rods for 9%, so the step")
    A("bought almost nothing and has been removed.")
    A("")
    A("[upstream]: https://github.com/luca-jost-violins/General-Acoustic-Measurement-Setup")
    A("")

    pathlib.Path(out).write_text("\n".join(L))
    print(f"{out}: {covers}, {total:.0f} g printed, pins at {pins}")


if __name__ == "__main__":
    main(sys.argv[1].replace("_", " ") if len(sys.argv) > 1 else "bass viol+cello")
