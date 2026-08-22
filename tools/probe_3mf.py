"""Read the upstream .3mf reference meshes and report basic geometry.

Used only to recover dimensions for the build123d rebuild; not part of the model.
"""
import sys, zipfile, glob, os
import xml.etree.ElementTree as ET
import numpy as np

NS = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}


def load(path):
    with zipfile.ZipFile(path) as z:
        name = next(n for n in z.namelist() if n.endswith(".model"))
        root = ET.fromstring(z.read(name))
    unit = root.get("unit", "millimeter")
    objs = []
    for obj in root.iter():
        if not obj.tag.endswith("}object"):
            continue
        mesh = next((c for c in obj if c.tag.endswith("}mesh")), None)
        if mesh is None:
            continue
        verts, tris = [], []
        for c in mesh:
            if c.tag.endswith("}vertices"):
                verts = [(float(v.get("x")), float(v.get("y")), float(v.get("z"))) for v in c]
            elif c.tag.endswith("}triangles"):
                tris = [(int(t.get("v1")), int(t.get("v2")), int(t.get("v3"))) for t in c]
        if verts:
            objs.append((obj.get("id"), np.array(verts), np.array(tris)))
    return unit, objs


def report(path):
    unit, objs = load(path)
    print(f"\n=== {os.path.basename(path)}  (unit={unit}, objects={len(objs)})")
    for oid, v, t in objs:
        lo, hi = v.min(0), v.max(0)
        print(f"  obj {oid}: {len(v)} verts, {len(t)} tris")
        print(f"    bbox  X {lo[0]:8.3f} .. {hi[0]:8.3f}  size {hi[0]-lo[0]:8.3f}")
        print(f"          Y {lo[1]:8.3f} .. {hi[1]:8.3f}  size {hi[1]-lo[1]:8.3f}")
        print(f"          Z {lo[2]:8.3f} .. {hi[2]:8.3f}  size {hi[2]-lo[2]:8.3f}")


if __name__ == "__main__":
    files = sys.argv[1:] or sorted(glob.glob("ref/upstream/*.3mf"))
    for f in files:
        report(f)
