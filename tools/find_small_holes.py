"""Find every small circular feature in the reference parts.

Used to audit the rebuild against the original: anything here that the
parametric model does not have is something that was dropped, deliberately or
otherwise.
"""
import glob
import os
import sys

import numpy as np
from probe_3mf import load
from section_mesh import slice_mesh
from features import chain, fit_circle


def scan(path, dmin=2.5, dmax=5.5, planes=9, tol=0.08):
    _, objs = load(path)
    _, v, t = objs[0]
    lo, hi = v.min(0), v.max(0)
    found = {}
    for ax in "XYZ":
        i = "XYZ".index(ax)
        for s in np.linspace(lo[i] + 0.4, hi[i] - 0.4, planes):
            for lp in chain(slice_mesh(v, t, ax, float(s))):
                if len(lp) < 8:
                    continue
                cx, cy, r, res = fit_circle(lp)
                if res < tol and dmin / 2 < r < dmax / 2:
                    key = (ax, round(cx, 1), round(cy, 1), round(2 * r, 1))
                    found.setdefault(key, 0)
                    found[key] += 1
    return found


if __name__ == "__main__":
    for f in sorted(glob.glob("ref/upstream/*.3mf")):
        hits = scan(f)
        name = os.path.basename(f)
        if not hits:
            print(f"{name:32s} none")
            continue
        print(f"{name:32s}")
        for (ax, a, b, d), n in sorted(hits.items()):
            other = "".join(c for c in "XYZ" if c != ax)
            print(f"    axis {ax}  {other}=({a:8.2f},{b:8.2f})  d={d:4.1f}  seen on {n} planes")
