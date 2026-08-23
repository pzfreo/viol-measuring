"""Build the README's hero scene: one rig for a violin, one for a cello.

Writes the scene split into printed parts and bought-in hardware, so a
renderer can colour the two differently, and exports the whole thing as a
single STEP for anyone who wants to look it over.

Needs vtk, which is not required to build or export any part:

    uv pip install --python .venv/bin/python vtk
    python tools/hero_render.py          # writes docs/hero.png
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


# Printed PLA, drawn aluminium and plain steel, as PBR (colour, metallic,
# roughness).  Getting metallic right is most of what separates a rod from a
# printed boss in the picture.
MATERIAL = {
    "printed":   ((0.055, 0.125, 0.295), 0.00, 0.52),
    "aluminium": ((0.807, 0.826, 0.848), 0.92, 0.30),
    "steel":     ((0.585, 0.612, 0.647), 0.95, 0.42),
}
ALUMINIUM = ("rod", "bearing")


def main(out="docs/hero.png", work="export"):
    import numpy as np
    from build123d import export_stl
    from render_vtk import actor_from_stl, ground, render

    printed, metal = scene()
    d = pathlib.Path(work)
    d.mkdir(parents=True, exist_ok=True)

    groups = {"printed": printed,
              "aluminium": [c for c in metal
                            if any(k in (c.label or "").lower() for k in ALUMINIUM)],
              "steel": [c for c in metal
                        if not any(k in (c.label or "").lower() for k in ALUMINIUM)]}
    actors, bounds = [], None
    for name, parts in groups.items():
        if not parts:
            continue
        c = Compound(children=parts)
        c.label = name
        path = d / f"hero_{name}.stl"
        export_stl(c, str(path), tolerance=0.02, angular_tolerance=0.1)
        colour, metallic, rough = MATERIAL[name]
        actors.append(actor_from_stl(path, colour, metallic, rough))
        bb = c.bounding_box()
        b = [bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, bb.min.Z, bb.max.Z]
        bounds = b if bounds is None else [
            min(bounds[0], b[0]), max(bounds[1], b[1]),
            min(bounds[2], b[2]), max(bounds[3], b[3]),
            min(bounds[4], b[4]), max(bounds[5], b[5])]
        print(f"  {name:10s} {len(parts):2d} parts")

    span = max(bounds[1] - bounds[0], bounds[5] - bounds[4])
    # no ground plane: a finite one shows its edge and an infinite one just
    # flattens into the background.  The gradient does the job.
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    render(actors, bounds, out)
    try:                                  # keep it light enough for a README
        from PIL import Image
        im = Image.open(out).convert("RGB")
        w = 1600
        im.resize((w, round(w * im.size[1] / im.size[0])), Image.LANCZOS).save(
            out, optimize=True)
    except ImportError:
        pass
    print(out)

    whole = Compound(children=printed + metal)
    whole.label = "violin_and_cello"
    export_step(whole, str(d / "hero.step"))


if __name__ == "__main__":
    main(*sys.argv[1:])
