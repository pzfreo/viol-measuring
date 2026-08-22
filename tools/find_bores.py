"""Find every cylindrical void in a reference mesh, on any of the three axes.

Sections the mesh perpendicular to each axis, keeps the inner loops that are
round to within a tolerance, and merges consecutive slices into a bore with a
diameter, an axis position and a depth. Written to hunt for the two M4 grub
screw holes, but it inventories every hole in a part.

    python tools/find_bores.py 3.0 4.6        # M4 tapped range
    python tools/find_bores.py 0 99 03_slider # everything in one part
"""
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from compare_sections import read_stl  # noqa: E402
from loops import loops  # noqa: E402
from section_mesh import slice_mesh  # noqa: E402

PARTS = [p.stem for p in sorted(pathlib.Path("ref/stl").glob("*.stl"))]


def round_loops(v, t, axis, value, dmin, dmax, tol=0.06):
    out = []
    ls = loops(slice_mesh(v, t, axis, value))
    if len(ls) < 2:
        return out
    big = max(range(len(ls)), key=lambda i: np.ptp(ls[i], 0).prod())
    for i, L in enumerate(ls):
        if i == big or len(L) < 16:
            continue
        c = L.mean(0)
        r = np.hypot(*(L - c).T)
        if r.std() < tol * max(r.mean(), 1) and dmin <= 2 * r.mean() <= dmax:
            out.append((c[0], c[1], 2 * r.mean()))
    return out


def main():
    dmin, dmax = float(sys.argv[1]), float(sys.argv[2])
    parts = sys.argv[3:] or PARTS
    for name in parts:
        v, t = read_stl(f"ref/stl/{name}.stl")
        lo, hi = v.min(0), v.max(0)
        found = []
        for ax, a in (("X", 0), ("Y", 1), ("Z", 2)):
            step = 0.5
            runs = {}
            for val in np.arange(lo[a] + 0.3, hi[a] - 0.3, step):
                for cu, cv, d in round_loops(v, t, ax, val, dmin, dmax):
                    key = (round(cu, 0), round(cv, 0), round(d, 0))
                    runs.setdefault(key, []).append((val, cu, cv, d))
            for key, hits in runs.items():
                if len(hits) < 3:                  # need real depth, not a blend
                    continue
                h = np.array(hits)
                found.append((ax, h[:, 1].mean(), h[:, 2].mean(),
                              h[:, 3].mean(), h[0, 0], h[-1, 0]))
        if found:
            print(f"### {name}")
            for ax, cu, cv, d, v0, v1 in sorted(found, key=lambda f: -(f[5] - f[4])):
                o1, o2 = [c for c in "XYZ" if c != ax]
                print(f"    axis {ax}  D={d:5.2f}  {o1}={cu:7.2f} {o2}={cv:7.2f}"
                      f"  {ax} {v0:7.2f}..{v1:7.2f}  (depth {v1 - v0 + 0.5:5.2f})")


if __name__ == "__main__":
    main()
