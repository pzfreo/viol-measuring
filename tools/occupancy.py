"""Sample material/void on a plane through a reference mesh.

Section outlines alone are ambiguous — a loop may bound material or a hole.
This ray-casts each sample point to say which, and prints an ASCII map.
"""
import sys
import numpy as np
from probe_3mf import load

AX = {"X": 0, "Y": 1, "Z": 2}


# An oblique direction avoids the degeneracies an axis-aligned ray hits on
# axis-aligned faces, which this geometry is full of.
RAY = np.array([0.3117, 0.7231, 0.6161])
RAY = RAY / np.linalg.norm(RAY)


def inside(verts, tris, pts, axis=2):
    """Point-in-mesh by counting ray crossings (Moller-Trumbore)."""
    tv = verts[tris]
    o = [i for i in range(3) if i != axis]
    v0, v1, v2 = tv[:, 0], tv[:, 1], tv[:, 2]
    e1, e2 = v1 - v0, v2 - v0
    d = RAY
    pv = np.cross(d, e2)
    det = (e1 * pv).sum(1)
    ok = np.abs(det) > 1e-12
    inv = np.zeros_like(det); inv[ok] = 1.0 / det[ok]
    out = np.zeros(len(pts), dtype=bool)
    for i, p in enumerate(pts):
        tvec = p - v0
        u = (tvec * pv).sum(1) * inv
        qv = np.cross(tvec, e1)
        v = (d * qv).sum(1) * inv
        t = (e2 * qv).sum(1) * inv
        hit = ok & (u >= 0) & (u <= 1) & (v >= 0) & (u + v <= 1) & (t > 1e-9)
        out[i] = hit.sum() % 2 == 1
    return out


def amap(src, axis, value, r0, r1, n=68):
    _, objs = load(src)
    _, v, t = objs[0]
    a = AX[axis]
    o = [i for i in range(3) if i != a]
    names = [k for k in "XYZ" if k != axis]
    A = np.linspace(r0[0], r0[1], n)
    B = np.linspace(r1[0], r1[1], max(8, n // 3))
    pts = []
    for b in B:
        for x in A:
            p = np.zeros(3); p[a] = value; p[o[0]] = x; p[o[1]] = b
            pts.append(p)
    res = inside(v, t, np.array(pts)).reshape(len(B), len(A))
    print(f"\n{src}  {axis}={value:g}   rows={names[1]} {r1[0]}..{r1[1]}  "
          f"cols={names[0]} {r0[0]}..{r0[1]}   (# = material)")
    for b, row in list(zip(B, res))[::-1]:
        print(f" {b:7.2f} |" + "".join("#" if c else "." for c in row))
    print("         +" + "-" * len(A))
    ticks = "".join(f"{A[i]:.0f}".ljust(1) if i % 10 == 0 else " " for i in range(len(A)))
    print("          " + ticks)


if __name__ == "__main__":
    src, axis, val = sys.argv[1], sys.argv[2], float(sys.argv[3])
    r0 = tuple(float(x) for x in sys.argv[4].split(","))
    r1 = tuple(float(x) for x in sys.argv[5].split(","))
    amap(src, axis, val, r0, r1)
