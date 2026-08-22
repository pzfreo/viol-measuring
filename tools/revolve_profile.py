"""Recover the profile of a rotationally symmetric part.

Walks up the axis and, at each height, finds the material runs along a radial
ray — averaged over several angles so knurling and flats show up as a spread
rather than as noise.
"""
import sys
import numpy as np
from probe_3mf import load
from occupancy import inside


def profile(src, z0, z1, axis_xy=(0.0, 0.0), rmax=20.0, steps=60, angles=8):
    _, objs = load(src)
    _, v, t = objs[0]
    cx, cy = axis_xy
    print(f"{src}\n{'Z':>8}  material runs along r (min..max over {angles} angles)")
    for z in np.linspace(z0, z1, steps):
        spans = []
        for k in range(angles):
            a = 2 * np.pi * k / angles
            n = 900
            r = np.linspace(0.0, rmax, n)
            pts = np.c_[cx + r * np.cos(a), cy + r * np.sin(a), np.full(n, z)]
            m = inside(v, t, pts)
            runs, cur, start = [], m[0], r[0]
            for i in range(1, n):
                if m[i] != cur:
                    if cur:
                        runs.append((start, r[i - 1]))
                    cur, start = m[i], r[i]
            if cur:
                runs.append((start, r[-1]))
            spans.append(runs)
        n_runs = max(len(s) for s in spans)
        desc = []
        for j in range(n_runs):
            los = [s[j][0] for s in spans if len(s) > j]
            his = [s[j][1] for s in spans if len(s) > j]
            desc.append(f"[{min(los):6.2f}..{max(his):6.2f}]"
                        if max(his) - min(his) < 0.05 and max(los) - min(los) < 0.05
                        else f"[{min(los):6.2f}/{max(los):6.2f}..{min(his):6.2f}/{max(his):6.2f}]")
        print(f"{z:8.2f}  " + "  ".join(desc))


if __name__ == "__main__":
    src = sys.argv[1]
    z0, z1 = float(sys.argv[2]), float(sys.argv[3])
    steps = int(sys.argv[4]) if len(sys.argv) > 4 else 60
    profile(src, z0, z1, steps=steps)
