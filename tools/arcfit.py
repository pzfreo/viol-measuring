"""Decompose an ordered section loop into lines and circular arcs.

Walks the loop greedily: extend the current run while a single line or circle
still fits every point in it to `tol`, then emit that primitive and start again.
This turns a reference mesh outline back into the primitives it was drawn from.
"""
import numpy as np


def _line_err(p):
    d = p[-1] - p[0]
    n = np.hypot(*d)
    if n < 1e-9:
        return np.inf
    d = d / n
    q = p - p[0]
    return np.abs(q[:, 0] * d[1] - q[:, 1] * d[0]).max()


def _circle(p):
    x, y = p[:, 0], p[:, 1]
    A = np.c_[2 * x, 2 * y, np.ones(len(p))]
    b = x ** 2 + y ** 2
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy = sol[0], sol[1]
    r = np.sqrt(max(sol[2] + cx ** 2 + cy ** 2, 0))
    err = np.abs(np.hypot(x - cx, y - cy) - r).max()
    return (cx, cy, r), err


def decompose(loop, tol=0.05, min_pts=4):
    """Yield ('line', p0, p1) and ('arc', centre, radius, p0, p1) primitives."""
    n = len(loop)
    out, i = [], 0
    while i < n - 1:
        j = i + min_pts
        best = None
        while j <= n:
            seg = loop[i:j]
            if _line_err(seg) < tol:
                best = ("line", seg[0], seg[-1], None, None)
            else:
                (cx, cy, r), err = _circle(seg)
                if err < tol and r < 1e4:
                    best = ("arc", seg[0], seg[-1], (cx, cy), r)
                else:
                    break
            j += 1
        if best is None:
            i += 1
            continue
        out.append(best)
        i = j - 2
    return out


def report(loop, tol=0.05):
    for kind, p0, p1, c, r in decompose(loop, tol):
        if kind == "line":
            print(f"   LINE ({p0[0]:8.3f},{p0[1]:8.3f}) -> ({p1[0]:8.3f},{p1[1]:8.3f})"
                  f"   len {np.hypot(*(p1 - p0)):7.3f}")
        else:
            a0 = np.degrees(np.arctan2(p0[1] - c[1], p0[0] - c[0])) % 360
            a1 = np.degrees(np.arctan2(p1[1] - c[1], p1[0] - c[0])) % 360
            print(f"   ARC  c=({c[0]:8.3f},{c[1]:8.3f}) r={r:7.3f}"
                  f"   {a0:7.2f}deg -> {a1:7.2f}deg"
                  f"   ends ({p0[0]:7.3f},{p0[1]:7.3f})..({p1[0]:7.3f},{p1[1]:7.3f})")
