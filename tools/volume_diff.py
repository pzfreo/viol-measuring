"""Localise where a built part differs from its reference, by volume.

Samples a 3D grid over the shared bounding box and reports the excess and
missing volume per Z layer, so the remaining error can be chased to a feature
rather than guessed at from cross-sections.
"""
import sys
import numpy as np
from diff_mesh import load_any
from occupancy import inside


def main(ref_path, part_path, n=110):
    rv, rt = load_any(ref_path)
    pv, pt = load_any(part_path)
    lo = np.minimum(rv.min(0), pv.min(0)) - 0.2
    hi = np.maximum(rv.max(0), pv.max(0)) + 0.2
    step = (hi - lo).max() / n
    axes = [np.arange(lo[i] + step / 2, hi[i], step) for i in range(3)]
    cell = step ** 3
    print(f"grid {[len(a) for a in axes]}  cell {step:.3f} mm -> {cell:.4f} mm3")
    tot_e = tot_m = 0.0
    rows = []
    for z in axes[2]:
        X, Y = np.meshgrid(axes[0], axes[1], indexing="ij")
        pts = np.c_[X.ravel(), Y.ravel(), np.full(X.size, z)]
        ri = inside(rv, rt, pts)
        pi = inside(pv, pt, pts)
        e = float((pi & ~ri).sum()) * cell
        m = float((ri & ~pi).sum()) * cell
        tot_e += e; tot_m += m
        rows.append((z, e, m, float(ri.sum()) * cell))
    print(f"\n{'Z':>7}  {'excess':>9}  {'missing':>9}  {'ref vol':>9}")
    for z, e, m, rvv in rows:
        bar = "#" * int(e / max(1e-9, max(r[1] for r in rows)) * 40)
        print(f"{z:7.2f}  {e:9.1f}  {m:9.1f}  {rvv:9.1f}  {bar}")
    print(f"\ntotal excess {tot_e:.1f} mm3, missing {tot_m:.1f} mm3, net {tot_e - tot_m:+.1f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 110)
