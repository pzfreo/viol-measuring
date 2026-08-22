"""Check that no two printed parts occupy the same space.

Exact booleans on every pair are slow, and most pairs are nowhere near each
other, so pairs whose bounding boxes miss are discarded first. That takes the
check from minutes to seconds and makes it cheap enough to run on every
instrument preset rather than just one.
"""

import pathlib
import sys
from itertools import combinations

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from gams import INSTRUMENTS, Rig, assembly  # noqa: E402

# The microphone arm is still very slightly curving where it beds onto the
# holder's flat plate, so the two share a contact sliver a few hundredths of a
# millimetre deep. That is a bearing contact, not interpenetration.
CONTACT_TOLERANCE = 2.0   # mm3


def boxes_miss(a, b, gap=0.0):
    x, y = a.bounding_box(), b.bounding_box()
    return (x.min.X > y.max.X + gap or y.min.X > x.max.X + gap
            or x.min.Y > y.max.Y + gap or y.min.Y > x.max.Y + gap
            or x.min.Z > y.max.Z + gap or y.min.Z > x.max.Z + gap)


def overlaps(rig: Rig):
    """Every printed pair that shares volume, worst first."""
    parts = list(assembly(rig, hardware=False).children)
    found = []
    for a, b in combinations(parts, 2):
        if boxes_miss(a, b):
            continue
        vol = getattr(a & b, "volume", 0.0)
        if vol > 0.0:
            found.append((a.label, b.label, vol))
    return sorted(found, key=lambda f: -f[2])


def main(names=None):
    worst_overall = 0.0
    for name in names or list(INSTRUMENTS):
        found = overlaps(Rig(INSTRUMENTS[name]))
        worst = found[0][2] if found else 0.0
        worst_overall = max(worst_overall, worst)
        verdict = "clear" if worst <= CONTACT_TOLERANCE else "INTERFERENCE"
        detail = "" if not found else "  " + ", ".join(
            f"{a}/{b} {v:.2f}" for a, b, v in found[:3])
        print(f"{name:14s} worst {worst:6.3f} mm3  {verdict}{detail}", flush=True)
    return worst_overall


if __name__ == "__main__":
    main(sys.argv[1:] or None)
