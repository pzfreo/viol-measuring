"""Show where a built part differs from its upstream reference.

Samples both meshes on the same grid in a plane and prints a map:
  '#' both agree material, '.' both agree void,
  '+' the part has material the reference does not (excess),
  '-' the reference has material the part does not (missing).
"""
import sys
import numpy as np
from probe_3mf import load
from occupancy import inside, AX


def load_any(path):
    if path.endswith(".3mf"):
        _, objs = load(path)
        return objs[0][1], objs[0][2]
    import struct
    with open(path, "rb") as f:
        f.read(80)
        n = struct.unpack("<I", f.read(4))[0]
        data = np.frombuffer(f.read(n * 50), dtype=np.uint8).reshape(n, 50)
    tri = data[:, 12:48].copy().view("<f4").reshape(n, 3, 3)
    verts = tri.reshape(-1, 3)
    tris = np.arange(len(verts)).reshape(-1, 3)
    return verts, tris


def diff(ref_path, part_path, axis, value, r0, r1, n=76):
    rv, rt = load_any(ref_path)
    pv, pt = load_any(part_path)
    a = AX[axis]
    o = [i for i in range(3) if i != a]
    names = [k for k in "XYZ" if k != axis]
    A = np.linspace(r0[0], r0[1], n)
    B = np.linspace(r1[0], r1[1], max(8, int(n * (r1[1] - r1[0]) / (r0[1] - r0[0]) / 2.1)))
    pts = []
    for b in B:
        for x in A:
            p = np.zeros(3); p[a] = value; p[o[0]] = x; p[o[1]] = b
            pts.append(p)
    pts = np.array(pts)
    ri = inside(rv, rt, pts).reshape(len(B), len(A))
    pi = inside(pv, pt, pts).reshape(len(B), len(A))
    print(f"\n{axis}={value:g}   rows={names[1]} {r1[0]}..{r1[1]}  cols={names[0]} {r0[0]}..{r0[1]}")
    print("   '+' part has excess    '-' part is missing material")
    for b, rr, pp in list(zip(B, ri, pi))[::-1]:
        row = "".join("#" if (r and p) else "." if not (r or p) else "+" if p else "-"
                      for r, p in zip(rr, pp))
        print(f" {b:7.2f} |{row}")
    ex = int((pi & ~ri).sum()); mi = int((ri & ~pi).sum())
    print(f"   excess cells {ex}, missing cells {mi}, of {ri.size}")


if __name__ == "__main__":
    ref, part, axis, val = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
    r0 = tuple(float(x) for x in sys.argv[5].split(","))
    r1 = tuple(float(x) for x in sys.argv[6].split(","))
    diff(ref, part, axis, val, r0, r1)
