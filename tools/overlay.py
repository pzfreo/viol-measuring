"""Draw reference and rebuilt section outlines on the same axes.

Numbers say how far apart two parts are; this says which feature is wrong.
The reference is black, the rebuild red, so anything that shows in only one
colour is a feature present in one part and absent from the other.

    python tools/overlay.py 07_hammer X 0        # one plane
    python tools/overlay.py 07_hammer Z 5,30,45  # several
"""
import pathlib
import sys

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from compare_sections import BUILDERS, SCRATCH, read_stl, tessellate  # noqa: E402
from section_mesh import AX, slice_mesh  # noqa: E402


def draw(ax, segs, colour, label, lw):
    if not len(segs):
        return
    for i, s in enumerate(segs):
        ax.plot(s[:, 0], s[:, 1], color=colour, lw=lw,
                label=label if i == 0 else None)


def main():
    name, axis = sys.argv[1], sys.argv[2].upper()
    vals = [float(v) for v in sys.argv[3].split(",")]
    rv, rt = read_stl(f"ref/stl/{name}.stl")
    import gams
    from gams import VIOLIN, Rig
    mv, mt = tessellate(getattr(gams, BUILDERS[name])(Rig(VIOLIN)))

    o1, o2 = [c for c in "XYZ" if c != axis]
    fig, axes = plt.subplots(1, len(vals), figsize=(5.2 * len(vals), 6.4),
                             squeeze=False)
    for ax, v in zip(axes[0], vals):
        draw(ax, slice_mesh(rv, rt, axis, v), "black", "reference", 1.6)
        draw(ax, slice_mesh(mv, mt, axis, v), "crimson", "rebuild", 1.0)
        ax.set_aspect("equal")
        ax.grid(True, lw=0.3, alpha=0.5)
        ax.set_title(f"{axis} = {v:g}", fontsize=10)
        ax.set_xlabel(o1)
        ax.set_ylabel(o2)
        ax.legend(fontsize=8)
    fig.suptitle(f"{name} — reference (black) vs rebuild (red)")
    fig.tight_layout()
    out = SCRATCH / f"overlay_{name}_{axis}.png"
    fig.savefig(out, dpi=110)
    print(out)


if __name__ == "__main__":
    main()
