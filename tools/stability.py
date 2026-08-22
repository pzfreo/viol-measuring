"""Will the rig stand up?

Computes the assembly's centre of gravity and checks it against the support
polygon formed by the base's three mounting points, for each instrument preset
and at the worst slider height.

Densities (g/cm3): printed parts PLA, guide rods aluminium (the BOM specifies
aluminium), leadscrew and bearings steel.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from build123d import CenterOf, Location  # noqa: E402

from gams import INSTRUMENTS, Rig, assembly  # noqa: E402

PLA, ALUMINIUM, STEEL = 1.24e-3, 2.70e-3, 7.85e-3   # g/mm3

DENSITY = {
    "guide_rod": ALUMINIUM,
    "leadscrew": STEEL,
    "linear_bearing": STEEL,
    "thrust_bearing": STEEL,
}


def density_for(label):
    for key, rho in DENSITY.items():
        if label.startswith(key):
            return rho
    return PLA


def cog(rig: Rig):
    """(mass_g, x, y, z) for the whole assembly, and a per-part breakdown."""
    parts = []
    total_m = 0.0
    mx = my = mz = 0.0
    for child in assembly(rig).children:
        rho = density_for(child.label)
        m = child.volume * rho
        c = child.center(CenterOf.MASS)
        parts.append((child.label, m, c))
        total_m += m
        mx += m * c.X
        my += m * c.Y
        mz += m * c.Z
    return total_m, (mx / total_m, my / total_m, mz / total_m), parts


def support_polygon(rig: Rig):
    """The three mounting points the base stands on, in plan."""
    half_w = rig.plate_width / 2
    front = rig.plate_depth / 2
    return [(-(half_w - rig.mount_inset), -(front - rig.mount_inset)),
            ((half_w - rig.mount_inset), -(front - rig.mount_inset)),
            (0.0, rig.lobe_y)]


def margin_to_edges(point, poly):
    """Signed distance from `point` to each edge; negative means outside."""
    px, py = point
    out = []
    n = len(poly)
    # polygon is counter-clockwise or clockwise; use the sign of the area
    area2 = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1]
                for i in range(n))
    sign = 1.0 if area2 > 0 else -1.0
    for i in range(n):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % n]
        ex, ey = bx - ax, by - ay
        length = (ex * ex + ey * ey) ** 0.5
        cross = (ex * (py - ay) - ey * (px - ax)) / length
        out.append((f"{i}-{(i + 1) % n}", sign * cross))
    return out


G = 9.81e-3   # N per gram


def edge_distance(point, a, b):
    """Perpendicular distance from `point` to the line a-b (unsigned)."""
    ex, ey = b[0] - a[0], b[1] - a[1]
    length = (ex * ex + ey * ey) ** 0.5
    return abs(ex * (point[1] - a[1]) - ey * (point[0] - a[0])) / length


def tipping_loads(rig, mass, cog_xy):
    """What it takes to tip the rig over, three ways."""
    poly = support_polygon(rig)
    w = mass * G
    out = {}

    # a downward load on the end of the slider arm, where the hammer hangs
    tip = (0.0, rig.pivot_y)
    best = None
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        d_cog = edge_distance(cog_xy, a, b)
        d_tip = edge_distance(tip, a, b)
        # only edges the load is on the far side of can be tipped about
        if d_tip <= 0:
            continue
        f = w * d_cog / d_tip
        if best is None or f < best:
            best = f
    out["down on the arm tip"] = best

    # a horizontal push at the top of the column, backwards
    margins = margin_to_edges(cog_xy, poly)
    worst = min(m for _, m in margins)
    out["horizontal at the column top"] = w * worst / rig.rod_length
    return out


def report(name):
    rig = Rig(INSTRUMENTS[name])
    mass, (cx, cy, cz), parts = cog(rig)
    poly = support_polygon(rig)
    margins = margin_to_edges((cx, cy), poly)
    worst = min(m for _, m in margins)

    print(f"\n=== {name}")
    print(f"  mass            {mass:8.1f} g")
    print(f"  centre of gravity  X {cx:6.1f}   Y {cy:6.1f}   Z {cz:6.1f}")
    print(f"  feet            " + "  ".join(f"({x:.0f},{y:.0f})" for x, y in poly))
    print(f"  margin to each edge: " + "  ".join(f"{n} {m:+6.1f}" for n, m in margins))
    print(f"  {'STABLE' if worst > 0 else 'TIPS OVER'} — worst margin {worst:+.1f} mm")

    for how, f in tipping_loads(rig, mass, (cx, cy)).items():
        print(f"  tips under {f:6.2f} N ({f / G:6.0f} g) — {how}")

    hammer = next(m for label, m, _ in parts if label.startswith("07_"))
    print(f"  hammer mass     {hammer:8.2f} g")

    heavy = sorted(parts, key=lambda p: -p[1])[:5]
    print("  heaviest parts:")
    for label, m, c in heavy:
        print(f"    {label:22s} {m:7.1f} g   at Y {c.Y:6.1f}  Z {c.Z:6.1f}")
    return worst


if __name__ == "__main__":
    names = sys.argv[1:] or list(INSTRUMENTS)
    for n in names:
        report(n)
