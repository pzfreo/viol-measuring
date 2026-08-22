"""Convert the upstream .3mf reference meshes to binary STL.

The .3mf parts are already positioned in a shared assembly frame, so the STLs
keep those coordinates and can be compared against the assembly directly.
"""
import sys, os, glob, struct
import numpy as np
from probe_3mf import load


def write_stl(path, verts, tris):
    v = verts[tris]                                   # (n, 3, 3)
    n = np.cross(v[:, 1] - v[:, 0], v[:, 2] - v[:, 0])
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    n = np.divide(n, ln, out=np.zeros_like(n), where=ln > 0)
    with open(path, "wb") as f:
        f.write(b"\0" * 80)
        f.write(struct.pack("<I", len(tris)))
        rec = np.zeros((len(tris), 13), dtype="<f4")
        rec[:, 0:3] = n
        rec[:, 3:12] = v.reshape(len(tris), 9)
        buf = bytearray()
        for r in rec:
            buf += r.tobytes()[:48] + b"\0\0"
        f.write(bytes(buf))


if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "ref/stl"
    os.makedirs(out_dir, exist_ok=True)
    for src in sorted(glob.glob("ref/upstream/*.3mf")):
        unit, objs = load(src)
        assert unit == "millimeter", (src, unit)
        assert len(objs) == 1, (src, len(objs))
        _, v, t = objs[0]
        stem = os.path.splitext(os.path.basename(src))[0]
        slug = stem.split(" ", 1)[1].lower().replace(" ", "_")
        dst = os.path.join(out_dir, f"{stem[:2]}_{slug}.stl")
        write_stl(dst, v, t)
        print(f"{dst}  {len(t)} tris")
