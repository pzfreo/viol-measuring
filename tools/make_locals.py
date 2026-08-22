"""Write each reference part as an STL in the part's own build frame.

The .3mf files are all in assembly coordinates. The parametric parts are built
in their own frames, so a like-for-like comparison needs the reference moved to
match. The offsets here are the assembly placements, inverted.
"""
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from probe_3mf import load          # noqa: E402
from importlib.util import module_from_spec, spec_from_file_location  # noqa: E402

_spec = spec_from_file_location("s2", str(pathlib.Path(__file__).with_name("3mf_to_stl.py")))
_m = module_from_spec(_spec); _spec.loader.exec_module(_m)

# part file -> (name, offset to subtract to reach the part's own frame)
PARTS = {
    "01 Base":                  ("01_base",        (0, 0, 0)),
    "02 Top":                   ("02_top",         (0, 0, 190)),
    "03 Slider":                ("03_slider",      (0, 0, 95)),
    "04 Microphone holder":     ("04_holder",      (0, 0, 49.5)),
    "05 Microphone arm":        ("05_mic_arm",     (0, 0, 0)),
    "06 Cable Management Clip": ("06_clip",        (20, 0, 20)),
    "07 Hammer":                ("07_hammer",      (0, 106.5, 49)),
    "08 Knob":                  ("08_knob",        (0, 0, 202)),
    "09 Knobhandle":            ("09_handle",      (0, 0, 215)),
    "10 Knobhandleknurl":       ("10_grip",        (0, -45, 218.5)),
    "11 Handheld Hammer":       ("11_handheld",    (0, 106.5, 49)),
}


def main(out="ref/stl"):
    d = pathlib.Path(out)
    d.mkdir(parents=True, exist_ok=True)
    for src, (name, off) in PARTS.items():
        _, objs = load(f"ref/upstream/{src}.3mf")
        _, v, t = objs[0]
        v = v.copy() - np.array(off, float)
        path = d / f"{name}.stl"
        _m.write_stl(str(path), v, t)
        lo, hi = v.min(0), v.max(0)
        print(f"{name:12s} {len(t):6d} tris   "
              f"X {lo[0]:8.2f}..{hi[0]:7.2f}  Y {lo[1]:8.2f}..{hi[1]:7.2f}  "
              f"Z {lo[2]:7.2f}..{hi[2]:7.2f}")


if __name__ == "__main__":
    main()
