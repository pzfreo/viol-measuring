"""Does every part fit on the printer, for every preset?

The slider's arm and the microphone arm both grow with reach, so the large
presets are the ones at risk.  A part that only fits turned diagonally on the
bed is worth knowing about before you slice it, not after.

    python tools/printability.py                 # Bambu P1S / X1C, 256 cube
    python tools/printability.py 220 220 250     # any other bed
"""

import itertools
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from gams import (  # noqa: E402
    INSTRUMENTS, Rig, base, clip, grip, hammer, handheld_hammer, handle,
    holder, knob, mic_arm, slider, top,
)

PARTS = {
    "01 base": base, "02 top": top, "03 slider": slider,
    "04 holder": holder, "05 mic arm": mic_arm, "06 clip": clip,
    "07 hammer": hammer, "08 knob": knob, "09 handle": handle,
    "10 knurl": grip, "11 handheld": handheld_hammer,
}
# a margin off each bed axis: the purge line, the skirt, and the fact that the
# corners of a Bambu bed are not all usable
MARGIN = 6.0


def fits(size, bed):
    """Upright, laid over, or turned on the bed — the best of those."""
    w, d, h = sorted(size, reverse=True)
    bx, by, bz = bed
    for a, b, c in itertools.permutations((w, d, h)):
        if c > bz:
            continue
        if a <= bx and b <= by:
            return "flat"
        # rotated about Z: the footprint's diagonal has to clear the bed
        for deg in range(1, 90):
            t = math.radians(deg)
            if (a * math.cos(t) + b * math.sin(t) <= bx and
                    a * math.sin(t) + b * math.cos(t) <= by):
                return f"turned {deg}°"
    return None


def main(*bed):
    bx, by, bz = (float(v) for v in bed) if bed else (256.0, 256.0, 256.0)
    usable = (bx - MARGIN, by - MARGIN, bz)
    print(f"bed {bx:.0f} x {by:.0f} x {bz:.0f}, usable {usable[0]:.0f} x "
          f"{usable[1]:.0f} x {usable[2]:.0f} after margin\n")
    worst = 0.0
    for name in INSTRUMENTS:
        rig = Rig(INSTRUMENTS[name])
        notes = []
        for label, fn in PARTS.items():
            bb = fn(rig).bounding_box()
            size = (bb.size.X, bb.size.Y, bb.size.Z)
            how = fits(size, usable)
            worst = max(worst, max(size) / min(usable[0], usable[1]))
            if how is None:
                notes.append(f"  ✗ {label}: {size[0]:.0f} x {size[1]:.0f} x "
                             f"{size[2]:.0f} — DOES NOT FIT")
            elif how != "flat":
                notes.append(f"  ! {label}: {size[0]:.0f} x {size[1]:.0f} x "
                             f"{size[2]:.0f} — fits only {how}")
        state = "all fit flat" if not notes else ""
        print(f"{name:14s} reach {rig.reach:6.1f}  {state}")
        for n in notes:
            print(n)
    print(f"\nlongest part is {worst * 100:.0f}% of the usable bed")


if __name__ == "__main__":
    main(*sys.argv[1:])
