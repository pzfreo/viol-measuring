"""Render two presets side by side, to show what changes with the instrument."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from build123d import Compound, Location, export_step  # noqa: E402

from gams import BASS_VIOL, VIOLIN, Rig, assembly  # noqa: E402


def main(out="export/hero"):
    left, right = assembly(Rig(VIOLIN)), assembly(Rig(BASS_VIOL))
    gap = 130.0
    lw = left.bounding_box().size.X
    rw = right.bounding_box().size.X
    x = (lw + rw) / 2 + gap
    scene = Compound(children=[
        left.moved(Location((-x / 2, 0, 0))),
        right.moved(Location((x / 2, 0, 0))),
    ])
    scene.label = "violin_and_bass_viol"
    export_step(scene, f"{out}.step")
    bb = scene.bounding_box()
    print(f"scene {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm -> {out}.step")


if __name__ == "__main__":
    main()
