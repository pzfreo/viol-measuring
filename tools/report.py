"""Measure every part against Luca Jost's reference and print the numbers.

The generated fingerprint suites only print a value when a check fails, so a
part that passes tells you nothing about how much room it had.  This calls the
same measurement routines directly, so every part reports a number either way,
and reads each suite's own tolerances — which differ part to part, because
cad-fingerprint scales them by how well that part's reference mesh decimated.

Cross-sections and the radial profile are deliberately absent: both are
measuring the wrong thing (pzfreo/cad-fingerprint#5 and #6).

    python tools/report.py            # a table on stdout
    python tools/report.py --json     # ... and fingerprints/report.json
"""

import importlib.util
import json
import math
import pathlib
import re
import sys

from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

import gams  # noqa: E402
from gams import VIOLIN, Rig  # noqa: E402

PARTS = [
    ("01_base", "base", "Base"),
    ("02_top", "top", "Top"),
    ("03_slider", "slider", "Slider"),
    ("04_holder", "holder", "Microphone holder"),
    ("05_mic_arm", "mic_arm", "Microphone arm"),
    ("06_clip", "clip", "Cable clip"),
    ("07_hammer", "hammer", "Hammer"),
    ("08_knob", "knob", "Knob"),
    ("09_handle", "handle", "Knob handle"),
    ("10_grip", "grip", "Knurled sleeve"),
    ("11_handheld", "handheld_hammer", "Handheld hammer"),
]
PRINCIPAL = ("Ixx", "Iyy", "Izz")
OFF_DIAGONAL = ("Ixy", "Ixz", "Iyz")


def suite(name):
    """Import a generated fingerprint module for its measurement helpers."""
    path = pathlib.Path("tests/fingerprint") / f"test_{name}.py"
    spec = importlib.util.spec_from_file_location(f"fp_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def tolerances(name):
    """The two surface-deviation tolerances that suite asserts against."""
    src = (pathlib.Path("tests/fingerprint") / f"test_{name}.py").read_text()
    return (float(re.search(r'max\(([\d.]+), result\["floor"\]\)', src).group(1)),
            float(re.search(r'max\(([\d.]+), result\["floor"\] / 4', src).group(1)))


def inertia(part):
    """Volume moments about the origin, matching what the suites record."""
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(part.wrapped, props)
    m = props.MatrixOfInertia()
    com = props.CentreOfMass()
    return ({"Ixx": m.Value(1, 1), "Iyy": m.Value(2, 2), "Izz": m.Value(3, 3),
             "Ixy": m.Value(1, 2), "Ixz": m.Value(1, 3), "Iyz": m.Value(2, 3)},
            (com.X(), com.Y(), com.Z()))


def measure(name, builder, label, rig):
    ref = json.load(open(f"fingerprints/{name}.json"))
    part = getattr(gams, builder)(rig)
    mod = suite(name)
    va = ref["volume_and_area"]

    bb = part.bounding_box()
    corners = [bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z]
    box = max(abs(a - b) for a, b in
              zip(corners, ref["bounding_box"]["min"] + ref["bounding_box"]["max"]))

    got, com = inertia(part)
    ri = ref["moments_of_inertia"]
    # off-diagonal terms are near zero on a symmetric part, so an absolute
    # difference means nothing until it is put against the part's own scale
    scale = max(abs(ri[k]) for k in PRINCIPAL)

    h = mod._hausdorff_vs_reference(part)
    h_tol, m_tol = tolerances(name)
    h_tol, m_tol = max(h_tol, h["floor"]), max(m_tol, h["floor"] / 4)

    return {
        "name": name, "label": label,
        "volume": part.volume, "volume_ref": va["volume"],
        "volume_pct": 100 * (part.volume - va["volume"]) / va["volume"],
        "area": part.area, "area_ref": va["surface_area"],
        "area_pct": 100 * (part.area - va["surface_area"]) / va["surface_area"],
        "com_offset": math.dist(com, va["center_of_mass"]),
        "bbox_worst": box,
        "hausdorff": h["hausdorff"], "h_tol": h_tol,
        "p95": h["p95"], "mean": h["mean"], "rms": h["rms"], "m_tol": m_tol,
        "principal_pct": max(100 * abs(got[k] - ri[k]) / abs(ri[k]) for k in PRINCIPAL),
        "off_diag_pct": max(abs(got[k] - ri[k]) for k in OFF_DIAGONAL) / scale * 100,
        "ok": h["hausdorff"] < h_tol and h["mean"] < m_tol,
    }


def main():
    rig = Rig(VIOLIN)
    rows = [measure(n, b, l, rig) for n, b, l in PARTS]
    print(f"{'part':20s} {'vol%':>7s} {'area%':>7s} {'CoM':>6s} {'bbox':>6s} "
          f"{'Hausdorff/tol':>17s} {'mean/tol':>15s} {'I%':>5s} {'off%':>5s}")
    for r in rows:
        print(f"{r['label']:20s} {r['volume_pct']:+7.2f} {r['area_pct']:+7.2f} "
              f"{r['com_offset']:6.3f} {r['bbox_worst']:6.3f} "
              f"{r['hausdorff']:8.3f}/{r['h_tol']:<7.3f}{'' if r['hausdorff'] < r['h_tol'] else '!'} "
              f"{r['mean']:6.3f}/{r['m_tol']:<7.3f}{'' if r['mean'] < r['m_tol'] else '!'} "
              f"{r['principal_pct']:5.2f} {r['off_diag_pct']:5.2f}")
    print(f"\n{sum(r['ok'] for r in rows)} of {len(rows)} within every surface tolerance"
          f"   worst volume {max(abs(r['volume_pct']) for r in rows):.2f}%")
    if "--json" in sys.argv:
        out = pathlib.Path("fingerprints/report.json")
        out.write_text(json.dumps(rows, indent=1))
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
