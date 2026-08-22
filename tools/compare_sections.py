"""Slice the reference and the rebuilt part on the same planes and tabulate.

The fingerprint suites say *that* a part diverges; this says *where*. Both
meshes are cut on identical planes and the section's bounding box and area
printed side by side, so a feature at the wrong height shows up as a run of
rows rather than a single number.

    python tools/compare_sections.py 07_hammer Z 40
"""
import pathlib
import struct
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from section_mesh import AX, slice_mesh  # noqa: E402

SCRATCH = pathlib.Path("/private/tmp/claude-501/-Users-paul-repos-viol-measuring/a1511b08-d3b4-4a42-8438-d5ee90c77428/scratchpad")

import gams  # noqa: E402
from gams import VIOLIN, Rig  # noqa: E402

BUILDERS = {
    "01_base": "base", "02_top": "top", "03_slider": "slider",
    "04_holder": "holder", "05_mic_arm": "mic_arm", "06_clip": "clip",
    "07_hammer": "hammer", "08_knob": "knob", "09_handle": "handle",
    "10_grip": "grip", "11_handheld": "handheld_hammer",
}


def read_stl(path):
    """Vertices and triangle indices from an STL, binary or ASCII."""
    raw = pathlib.Path(path).read_bytes()
    n = struct.unpack("<I", raw[80:84])[0] if len(raw) >= 84 else 0
    if len(raw) == 84 + n * 50 and n:
        tri = np.frombuffer(raw, dtype=np.uint8, count=n * 50, offset=84).reshape(n, 50)
        v = tri[:, 12:48].copy().view("<f4").reshape(n * 3, 3).astype(float)
    else:
        v = np.array([[float(x) for x in ln.split()[1:4]]
                      for ln in raw.decode("utf8", "replace").splitlines()
                      if ln.strip().startswith("vertex")])
    return v, np.arange(len(v)).reshape(-1, 3)


def tessellate(part, tol=0.02):
    """Same, from a build123d part, via its triangulation."""
    from build123d import export_stl
    out = SCRATCH / "_cmp.stl"
    export_stl(part, str(out), tolerance=tol, angular_tolerance=0.1)
    return read_stl(out)


def seg_stats(segs, rows=400):
    """Bounding box and enclosed area of a set of section segments.

    The segments come out of the slicer unordered, so the area is integrated
    by scanline — for each horizontal line, sort the crossings and sum the
    inside intervals — rather than by a shoelace, which would need loops.
    """
    if not len(segs):
        return None
    p = segs.reshape(-1, 2)
    u0, u1, v0, v1 = p[:, 0].min(), p[:, 0].max(), p[:, 1].min(), p[:, 1].max()
    if v1 - v0 < 1e-9:
        return u0, u1, v0, v1, 0.0, len(segs)
    a, b = segs[:, 0, :], segs[:, 1, :]
    vs = np.linspace(v0, v1, rows + 2)[1:-1]
    dv = (v1 - v0) / (rows + 1)
    total = 0.0
    for v in vs:
        hit = (a[:, 1] > v) != (b[:, 1] > v)
        if not hit.any():
            continue
        aa, bb = a[hit], b[hit]
        t = (v - aa[:, 1]) / (bb[:, 1] - aa[:, 1])
        xs = np.sort(aa[:, 0] + t * (bb[:, 0] - aa[:, 0]))
        total += np.sum(xs[1::2] - xs[0::2])
    return u0, u1, v0, v1, total * dv, len(segs)


def main():
    name, axis, steps = sys.argv[1], sys.argv[2].upper(), int(sys.argv[3])
    rv, rt = read_stl(f"ref/stl/{name}.stl")
    part = getattr(gams, BUILDERS[name])(Rig(VIOLIN))
    mv, mt = tessellate(part)

    a = AX[axis]
    lo = min(rv[:, a].min(), mv[:, a].min())
    hi = max(rv[:, a].max(), mv[:, a].max())
    o1, o2 = [c for c in "XYZ" if c != axis]
    print(f"{name}  cut along {axis}   ref {rv[:,a].min():.2f}..{rv[:,a].max():.2f}"
          f"   mine {mv[:,a].min():.2f}..{mv[:,a].max():.2f}")
    print(f"{axis:>6} | {o1+'- ref/mine':>16} {o1+'+ ref/mine':>16} "
          f"| {o2+'- ref/mine':>16} {o2+'+ ref/mine':>16} | {'area ref/mine':>17}")
    for v in np.linspace(lo + (hi - lo) * 0.005, hi - (hi - lo) * 0.005, steps):
        r = seg_stats(slice_mesh(rv, rt, axis, v))
        m = seg_stats(slice_mesh(mv, mt, axis, v))
        if r is None and m is None:
            continue
        f = lambda x, i: "   --  " if x is None else f"{x[i]:7.2f}"
        flag = ""
        if r and m:
            for i in range(4):
                if abs(r[i] - m[i]) > 0.25:
                    flag = " <<<"
            if abs(r[4] - m[4]) > 0.03 * max(r[4], 1e-9):
                flag = " <<<"
        elif r or m:
            flag = " <<< missing"
        print(f"{v:6.2f} | {f(r,0)}/{f(m,0)} {f(r,1)}/{f(m,1)} "
              f"| {f(r,2)}/{f(m,2)} {f(r,3)}/{f(m,3)} "
              f"| {f(r,4)}/{f(m,4)}{flag}")


if __name__ == "__main__":
    main()
