"""Slice a reference mesh with planes and plot the outlines in 2D.

Cross-sections are what you actually model from: they give hole centres,
outline radii and wall thicknesses directly off a grid.
"""
import sys, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from probe_3mf import load

AX = {"X": 0, "Y": 1, "Z": 2}


def slice_mesh(verts, tris, axis, value):
    """Return list of (2,2) segments where the mesh crosses the plane."""
    a = AX[axis]
    other = [i for i in range(3) if i != a]
    tv = verts[tris]                       # (n,3,3)
    d = tv[:, :, a] - value
    sign = d > 0
    cross = sign.any(1) & ~sign.all(1)
    tv, d = tv[cross], d[cross]
    segs = []
    for tri, dd in zip(tv, d):
        pts = []
        for i in range(3):
            j = (i + 1) % 3
            if (dd[i] > 0) != (dd[j] > 0):
                t = dd[i] / (dd[i] - dd[j])
                p = tri[i] + t * (tri[j] - tri[i])
                pts.append((p[other[0]], p[other[1]]))
        if len(pts) == 2:
            segs.append(pts)
    return np.array(segs) if segs else np.empty((0, 2, 2))


def plot(src, axis, values, out, grid=5.0):
    _, objs = load(src)
    _, v, t = objs[0]
    other = [k for k in "XYZ" if k != axis]
    n = len(values)
    cols = min(n, 4)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(5.2 * cols, 5.2 * rows), squeeze=False)
    lo = v.min(0); hi = v.max(0)
    o0, o1 = AX[other[0]], AX[other[1]]
    for k, val in enumerate(values):
        ax = axes[k // cols][k % cols]
        segs = slice_mesh(v, t, axis, val)
        for s in segs:
            ax.plot(s[:, 0], s[:, 1], "-", color="#1f4e9c", lw=1.0)
        ax.set_title(f"{axis} = {val:g}   ({len(segs)} segs)", fontsize=10)
        ax.set_xlabel(other[0]); ax.set_ylabel(other[1])
        ax.set_aspect("equal")
        ax.set_xlim(lo[o0] - 3, hi[o0] + 3); ax.set_ylim(lo[o1] - 3, hi[o1] + 3)
        ax.set_xticks(np.arange(np.floor(lo[o0] / grid) * grid, hi[o0] + grid, grid))
        ax.set_yticks(np.arange(np.floor(lo[o1] / grid) * grid, hi[o1] + grid, grid))
        ax.grid(True, lw=0.4, alpha=0.5)
        ax.tick_params(labelsize=7)
    for k in range(n, rows * cols):
        axes[k // cols][k % cols].axis("off")
    fig.suptitle(f"{os.path.basename(src)} — sections along {axis}", fontsize=13)
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    print(out)


if __name__ == "__main__":
    src, axis = sys.argv[1], sys.argv[2]
    values = [float(x) for x in sys.argv[3].split(",")]
    out = sys.argv[4]
    grid = float(sys.argv[5]) if len(sys.argv) > 5 else 5.0
    plot(src, axis, values, out, grid)
