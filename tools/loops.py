"""Chain section segments into ordered loops and print them as coordinates.

The slicer emits unordered segments; joining them end-to-end turns a section
into something you can read off as a profile — corner coordinates, radii,
which side a flat is on.
"""
import sys
import pathlib

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from compare_sections import BUILDERS, read_stl, tessellate  # noqa: E402
from section_mesh import slice_mesh  # noqa: E402


def loops(segs, tol=1e-4):
    """Chain (n,2,2) segments into closed point loops."""
    segs = [tuple(map(tuple, s)) for s in np.round(segs, 4)]
    out = []
    while segs:
        chain = list(segs.pop(0))
        grew = True
        while grew and segs:
            grew = False
            for i, (a, b) in enumerate(segs):
                if np.allclose(chain[-1], a, atol=tol):
                    chain.append(b)
                elif np.allclose(chain[-1], b, atol=tol):
                    chain.append(a)
                elif np.allclose(chain[0], b, atol=tol):
                    chain.insert(0, a)
                elif np.allclose(chain[0], a, atol=tol):
                    chain.insert(0, b)
                else:
                    continue
                segs.pop(i)
                grew = True
                break
        out.append(np.array(chain))
    return sorted(out, key=len, reverse=True)


def show(tag, verts, tris, axis, value, decimate=1):
    ls = loops(slice_mesh(verts, tris, axis, value))
    print(f"  {tag}: {len(ls)} loop(s)")
    for k, L in enumerate(ls):
        # drop collinear runs so the printout is corners, not tessellation
        keep = [0]
        for i in range(1, len(L) - 1):
            d1, d2 = L[i] - L[keep[-1]], L[i + 1] - L[i]
            if abs(d1[0] * d2[1] - d1[1] * d2[0]) > 2e-3:
                keep.append(i)
        keep.append(len(L) - 1)
        pts = " ".join(f"({L[i][0]:.2f},{L[i][1]:.2f})" for i in keep[::decimate])
        print(f"    [{k}] {len(L)} pts, {len(keep)} corners: {pts[:2000]}")


if __name__ == "__main__":
    name, axis, value = sys.argv[1], sys.argv[2].upper(), float(sys.argv[3])
    dec = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    rv, rt = read_stl(f"ref/stl/{name}.stl")
    print(f"{name} at {axis}={value}")
    show("ref ", rv, rt, axis, value, dec)
    import gams
    from gams import VIOLIN, Rig
    mv, mt = tessellate(getattr(gams, BUILDERS[name])(Rig(VIOLIN)))
    show("mine", mv, mt, axis, value, dec)
