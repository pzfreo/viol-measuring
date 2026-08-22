"""Print a filled cross-section as text, so solid and void are unambiguous.

Outline plots leave you guessing which side of a curve is material. This
ray-casts every grid point, so '#' is solid and '.' is air, full stop.

    python tools/xsection_ascii.py 07_hammer X 0 0.25
"""
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from compare_sections import read_stl  # noqa: E402
from section_mesh import AX  # noqa: E402


def inside(verts, tris, pts, axis):
    """Möller-Trumbore ray cast; odd crossing count means solid.

    The ray is deliberately oblique. A ray running exactly along a bore axis
    or parallel to a flat face grazes shared triangle edges and gets counted
    twice, which paints a phantom spine straight down the middle of a hole.
    """
    a = AX[axis]
    d = np.zeros(3)
    d[a] = 1.0
    d[(a + 1) % 3] = 0.0173
    d[(a + 2) % 3] = 0.0209
    d /= np.linalg.norm(d)

    tv = verts[tris]
    v0, e1, e2 = tv[:, 0], tv[:, 1] - tv[:, 0], tv[:, 2] - tv[:, 0]
    h = np.cross(d, e2)
    det = np.einsum("ij,ij->i", e1, h)
    ok = np.abs(det) > 1e-12
    inv = np.where(ok, 1.0 / np.where(ok, det, 1.0), 0.0)

    out = np.zeros(len(pts), bool)
    for i, p in enumerate(pts):
        s_ = p - v0
        u = np.einsum("ij,ij->i", s_, h) * inv
        q = np.cross(s_, e1)
        w = (q @ d) * inv
        t = np.einsum("ij,ij->i", e2, q) * inv
        hit = ok & (u >= 0) & (w >= 0) & (u + w <= 1) & (t > 1e-9)
        out[i] = np.count_nonzero(hit) % 2 == 1
    return out


def main():
    name, axis, value = sys.argv[1], sys.argv[2].upper(), float(sys.argv[3])
    step = float(sys.argv[4]) if len(sys.argv) > 4 else 0.25
    src = sys.argv[5] if len(sys.argv) > 5 else f"ref/stl/{name}.stl"
    v, t = read_stl(src)
    a = AX[axis]
    o1, o2 = [i for i in range(3) if i != a]
    lo, hi = v.min(0), v.max(0)
    us = np.arange(lo[o1], hi[o1] + step, step)
    ws = np.arange(lo[o2], hi[o2] + step, step / 2)
    grid = np.zeros((len(ws), 3))
    print(f"{src}  {axis}={value}   across={'XYZ'[o1]} {us[0]:.1f}..{us[-1]:.1f}"
          f"   down={'XYZ'[o2]} {ws[-1]:.1f}..{ws[0]:.1f}")
    rows = []
    for w in ws:
        pts = np.zeros((len(us), 3))
        pts[:, a] = value
        pts[:, o1] = us
        pts[:, o2] = w
        rows.append("".join("#" if s else "." for s in inside(v, t, pts, axis)))
    for w, r in zip(ws[::-1], rows[::-1]):
        print(f"{w:7.2f} |{r}|")


if __name__ == "__main__":
    main()
