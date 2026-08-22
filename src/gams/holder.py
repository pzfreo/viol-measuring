"""04 Microphone holder.

Clips onto both guide rods and arches forward over the column, carrying a pair
of fins that grip the *microphone arm* — not the microphone itself.  The arm
slides in that slot, which is how the microphone's height and reach are set,
and it is why the upstream part set ships the arm in +/-0.05, 0.10 and 0.15 mm
widths: the fit between these fins and the arm is the one dimension a printer's
tolerance can spoil.
"""

from build123d import (
    Align, Box, BuildPart, BuildSketch, Circle, Cylinder, Locations, Mode,
    Polygon, Rectangle, add, extrude,
)

from .params import Rig


def _superellipse(a, b, n, y_floor, steps=96):
    """Half a superellipse |x/a|^n + |y/b|^n = 1, closed off flat at `y_floor`.

    The reference arch is neither circular nor elliptical — it narrows faster
    than a circle and slower than an ellipse — and a superellipse fits it to
    better than 0.03 of a semi-axis.
    """
    pts = []
    for i in range(steps + 1):
        y = b * i / steps
        x = a * max(0.0, 1 - (y / b) ** n) ** (1 / n)
        pts.append((x, y))
    pts = [(x, y) for x, y in pts if x > 1e-6] + [(0.0, b)]
    return ([(a, y_floor)] + pts
            + [(-x, y) for x, y in reversed(pts)] + [(-a, y_floor)])


def holder(rig: Rig):
    """Build the microphone holder for `rig`, on the rig axis with Z from 0 up."""
    bore_r = rig.hw.rod_d / 2
    outer_r = bore_r + rig.clip_wall
    y0 = rig.holder_mouth_y

    outer_a = rig.rod_x + outer_r
    with BuildSketch(mode=Mode.PRIVATE) as arch:
        Polygon(*_superellipse(outer_a, rig.arch_outer_b, rig.arch_outer_n, y0),
                align=None)
        Polygon(*_superellipse(rig.arch_inner_a, rig.arch_inner_b,
                               rig.arch_inner_n, y0),
                align=None, mode=Mode.SUBTRACT)

    with BuildPart() as part:
        extrude(to_extrude=arch.sketch, amount=rig.holder_plate_t)

        # fins either side of the slot the arm slides in
        with BuildSketch(mode=Mode.PRIVATE) as fins:
            for sign in (1, -1):
                with Locations((sign * (rig.arm_slot_w / 2 + rig.fin_outer_x) / 2, 0)):
                    Rectangle(rig.fin_outer_x - rig.arm_slot_w / 2, 4 * rig.arch_outer_b)
            add(arch.sketch, mode=Mode.INTERSECT)   # fins live on the arch only
        extrude(to_extrude=fins.sketch, amount=rig.fin_h)

        # a clip on each rod, built already hollow
        for sign in (1, -1):
            with BuildSketch(mode=Mode.PRIVATE) as ring:
                with Locations((sign * rig.rod_x, 0)):
                    Circle(outer_r)
                    Circle(bore_r, mode=Mode.SUBTRACT)
            extrude(to_extrude=ring.sketch, amount=rig.holder_h)
        with Locations((-rig.rod_x, 0, 0), (rig.rod_x, 0, 0)):
            Cylinder(bore_r, rig.holder_h,
                     align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # everything is cut off flat where the clips spring over the rods
        with Locations((0, y0 - 4 * outer_a, rig.holder_h / 2)):
            Box(8 * outer_a, 8 * outer_a, rig.holder_h, mode=Mode.SUBTRACT)

    result = part.part
    assert len(result.solids()) == 1, f"holder split into {len(result.solids())} solids"
    return result
