"""Recover circles and outlines from a reference mesh cross-section.

Segments from a plane cut are chained into loops, and each loop is tested
against a circle fit. Circular loops report centre and radius directly, which
is what most of the features on these parts are.
"""
import sys
import numpy as np
from probe_3mf import load
from section_mesh import slice_mesh, AX


def chain(segs, tol=1e-4):
    """Chain (2,2) segments into ordered loops."""
    pts = {}
    for i, s in enumerate(segs):
        for e in (0, 1):
            key = (round(s[e][0] / tol), round(s[e][1] / tol))
            pts.setdefault(key, []).append((i, e))
    used = set()
    loops = []
    for i0 in range(len(segs)):
        if i0 in used:
            continue
        used.add(i0)
        loop = [segs[i0][0], segs[i0][1]]
        cur, end = i0, 1
        while True:
            key = (round(loop[-1][0] / tol), round(loop[-1][1] / tol))
            nxt = [(i, e) for i, e in pts.get(key, []) if i not in used]
            if not nxt:
                break
            i, e = nxt[0]
            used.add(i)
            loop.append(segs[i][1 - e])
            if np.allclose(loop[-1], loop[0], atol=tol * 10):
                break
        loops.append(np.array(loop))
    return loops


def fit_circle(p):
    """Algebraic circle fit; returns (cx, cy, r, max_residual)."""
    x, y = p[:, 0], p[:, 1]
    A = np.c_[2 * x, 2 * y, np.ones(len(p))]
    b = x ** 2 + y ** 2
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy = sol[0], sol[1]
    r = np.sqrt(sol[2] + cx ** 2 + cy ** 2)
    res = np.abs(np.hypot(x - cx, y - cy) - r).max()
    return cx, cy, r, res


def describe(src, axis, value, circ_tol=0.06, min_pts=8):
    _, objs = load(src)
    _, v, t = objs[0]
    segs = slice_mesh(v, t, axis, value)
    loops = chain(segs)
    o = [k for k in "XYZ" if k != axis]
    print(f"\n--- {src}  {axis}={value:g}   {len(loops)} loops  (axes {o[0]},{o[1]})")
    rows = []
    for lp in loops:
        if len(lp) < min_pts:
            continue
        cx, cy, r, res = fit_circle(lp)
        lo, hi = lp.min(0), lp.max(0)
        span = hi - lo
        rows.append((-span.max(), lp, cx, cy, r, res, lo, hi, span))
    rows.sort(key=lambda t: t[0])
    for _, lp, cx, cy, r, res, lo, hi, span in rows:
        if res < circ_tol:
            print(f"  CIRCLE  c=({cx:8.3f},{cy:8.3f})  r={r:7.3f}  d={2*r:7.3f}"
                  f"   pts={len(lp):4d}  res={res:.4f}")
        else:
            print(f"  outline bbox {o[0]} {lo[0]:8.3f}..{hi[0]:8.3f} ({span[0]:7.3f})  "
                  f"{o[1]} {lo[1]:8.3f}..{hi[1]:8.3f} ({span[1]:7.3f})  pts={len(lp):4d}")


if __name__ == "__main__":
    src, axis = sys.argv[1], sys.argv[2]
    for val in [float(x) for x in sys.argv[3].split(",")]:
        describe(src, axis, val)
