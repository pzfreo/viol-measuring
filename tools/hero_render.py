"""Build the README's hero scene: one rig for a violin, one for a cello.

Writes the scene split into printed parts and bought-in hardware, so a
renderer can colour the two differently, and exports the whole thing as a
single STEP for anyone who wants to look it over.

    python tools/hero_render.py          # writes export/hero_*.step
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from build123d import Compound, Location, export_step  # noqa: E402

from gams import INSTRUMENTS, Rig, assembly  # noqa: E402

# anything whose label names a bought-in part; the rest is printed
HARDWARE = ("rod", "bearing", "leadscrew", "nut", "bolt", "screw", "thrust", "pin")
GAP = 170.0


# The camera views the rig from behind so the arms face the viewer, which
# mirrors X — so the instrument named second is the one that ends up on the
# left of the picture.
def scene(left_name="cello", right_name="violin"):
    left, right = (assembly(Rig(INSTRUMENTS[n])) for n in (left_name, right_name))
    x = (left.bounding_box().size.X + right.bounding_box().size.X) / 2 + GAP
    printed, metal = [], []
    for asm, dx in ((left, -x / 2), (right, x / 2)):
        for child in asm.children:
            label = (child.label or "").lower()
            bucket = metal if any(k in label for k in HARDWARE) else printed
            bucket.append(child.moved(Location((dx, 0, 0))))
    return printed, metal


def main(out="export"):
    printed, metal = scene()
    d = pathlib.Path(out)
    d.mkdir(parents=True, exist_ok=True)
    for name, parts in (("printed", printed), ("hardware", metal)):
        c = Compound(children=parts)
        c.label = name
        export_step(c, str(d / f"hero_{name}.step"))
        print(f"{d/f'hero_{name}.step'}  {len(parts)} parts")
    whole = Compound(children=printed + metal)
    whole.label = "violin_and_cello"
    export_step(whole, str(d / "hero.step"))


if __name__ == "__main__":
    main(*sys.argv[1:])
