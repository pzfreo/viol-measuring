"""Render reference meshes to PNG so the geometry can be inspected visually."""
import sys, os, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from probe_3mf import load

VIEWS = [("iso", 25, -60), ("front", 0, -90), ("side", 0, 0), ("top", 89, -90)]


def render(verts, tris, out, title=""):
    tri = verts[tris]
    lo, hi = verts.min(0), verts.max(0)
    ctr, span = (lo + hi) / 2, (hi - lo).max() / 2 * 1.1
    fig = plt.figure(figsize=(16, 4.4))
    for i, (nm, elev, azim) in enumerate(VIEWS, 1):
        ax = fig.add_subplot(1, len(VIEWS), i, projection="3d")
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
        light = np.array([0.4, -0.7, 0.6]); light /= np.linalg.norm(light)
        shade = 0.35 + 0.65 * np.abs(n @ light)
        col = np.stack([shade * 0.55, shade * 0.72, shade * 0.95, np.ones_like(shade)], 1)
        pc = Poly3DCollection(tri, facecolors=col, edgecolors=(0, 0, 0, 0.10), linewidths=0.12)
        ax.add_collection3d(pc)
        for setlim, c in ((ax.set_xlim, 0), (ax.set_ylim, 1), (ax.set_zlim, 2)):
            setlim(ctr[c] - span, ctr[c] + span)
        ax.view_init(elev=elev, azim=azim)
        ax.set_box_aspect((1, 1, 1))
        ax.set_title(f"{nm}  (elev={elev} azim={azim})", fontsize=9)
        ax.tick_params(labelsize=6)
        ax.set_xlabel("X", fontsize=7); ax.set_ylabel("Y", fontsize=7); ax.set_zlabel("Z", fontsize=7)
    fig.suptitle(title, fontsize=12)
    fig.tight_layout()
    fig.savefig(out, dpi=105)
    plt.close(fig)
    print(out)


if __name__ == "__main__":
    out_dir = "ref/render"
    os.makedirs(out_dir, exist_ok=True)
    pats = sys.argv[1:] or ["ref/upstream/*.3mf"]
    for pat in pats:
        for src in sorted(glob.glob(pat)):
            _, objs = load(src)
            _, v, t = objs[0]
            stem = os.path.splitext(os.path.basename(src))[0]
            render(v, t, f"{out_dir}/{stem}.png", stem)
