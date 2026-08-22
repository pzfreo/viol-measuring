"""Render the README hero: the violin rig beside the bass viol rig.

Uses its own shaded renderer rather than the CAD preview, so the image reads
as a photograph of two printed rigs rather than a screenshot.
"""

import pathlib
import struct
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from build123d import Location, export_stl  # noqa: E402

from gams import BASS_VIOL, VIOLIN, Rig, assembly  # noqa: E402


def read_stl(path):
    with open(path, "rb") as f:
        f.read(80)
        n = struct.unpack("<I", f.read(4))[0]
        data = np.frombuffer(f.read(n * 50), dtype=np.uint8).reshape(n, 50)
    return data[:, 12:48].copy().view("<f4").reshape(n, 3, 3).astype(float)


def view_vector(elev, azim):
    """Unit vector from the scene toward the camera, for matplotlib's angles."""
    e, a = np.radians(elev), np.radians(azim)
    return np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])


def cull_and_sort(tri, col, view):
    """Drop back faces, then order the rest far-to-near.

    Matplotlib has no depth buffer, so without this the insides of the columns
    are drawn over their fronts and the rig looks transparent.
    """
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    n = np.divide(n, ln, out=np.zeros_like(n), where=ln > 0)
    facing = n @ view > 0
    tri, col = tri[facing], col[facing]
    depth = tri.mean(axis=1) @ view
    order = np.argsort(depth)
    return tri[order], col[order]


def shade(tri, base, light=(0.35, -0.75, 0.56)):
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    n = np.divide(n, ln, out=np.zeros_like(n), where=ln > 0)
    lt = np.array(light, float)
    lt /= np.linalg.norm(lt)
    lam = np.clip(n @ lt, 0, 1)
    k = 0.42 + 0.58 * lam                       # ambient + diffuse
    spec = np.clip(n @ lt, 0, 1) ** 24 * 0.35   # a little sheen
    col = np.clip(np.stack([k * base[0] + spec, k * base[1] + spec,
                            k * base[2] + spec], 1), 0, 1)
    return np.concatenate([col, np.ones((len(col), 1))], 1)


def main(out="docs/hero.png", azim=-62, elev=13, dpi=170):
    gap = 130.0
    rigs = [(Rig(VIOLIN), (0.36, 0.55, 0.80)), (Rig(BASS_VIOL), (0.80, 0.58, 0.33))]
    widths = [assembly(r).bounding_box().size.X for r, _ in rigs]
    x = (widths[0] + widths[1]) / 2 + gap

    tmp = pathlib.Path("export")
    tmp.mkdir(exist_ok=True)
    tris, cols = [], []
    for (rig, colour), dx in zip(rigs, (-x / 2, x / 2)):
        path = tmp / f"_hero_{rig.instrument.name.replace(' ', '_')}.stl"
        export_stl(assembly(rig).moved(Location((dx, 0, 0))), str(path))
        t = read_stl(path)
        tris.append(t)
        cols.append(shade(t, colour))
    tri = np.concatenate(tris)
    col = np.concatenate(cols)
    tri, col = cull_and_sort(tri, col, view_vector(elev, azim))

    lo, hi = tri.reshape(-1, 3).min(0), tri.reshape(-1, 3).max(0)
    ctr = (lo + hi) / 2
    pad = 1.06
    size = (hi - lo) * pad

    fig = plt.figure(figsize=(12, 7.0), facecolor="white")
    ax = fig.add_subplot(111, projection="3d", facecolor="white")
    ax.add_collection3d(Poly3DCollection(tri, facecolors=col, linewidths=0,
                                         shade=False, zsort="min"))
    for setlim, c in ((ax.set_xlim, 0), (ax.set_ylim, 1)):
        setlim(ctr[c] - size[c] / 2, ctr[c] + size[c] / 2)
    ax.set_zlim(-2, hi[2] * pad)
    ax.set_box_aspect(tuple(size))   # true proportions, no distortion
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    fig.tight_layout(pad=0)
    fig.savefig(out, dpi=dpi, bbox_inches="tight", facecolor="white")
    print(f"{out}  ({len(tri)} triangles)")


if __name__ == "__main__":
    main()
