"""02 Top — the head of the column.

The same plate as the base, with the same split rod clamps, but the thrust
bearing seat opens from the underside so the leadscrew is trapped between the
two bearings.  It prints inverted, so its cross-bolt teardrops point the other
way.
"""

from build123d import (
    Align, BuildPart, BuildSketch, Circle, Cylinder, Locations, Mode, Plane,
    Rectangle, extrude, fillet, mirror,
)

from .column import clamp_cutter, fillet_at, lightening_sketch, seat_sketch
from .params import Rig


def top(rig: Rig):
    """Build the top plate for `rig`, in its own frame with Z from 0 up."""
    hw = rig.hw
    t = rig.plate_t
    front_y = rig.plate_depth / 2
    half_w = rig.plate_width / 2
    pocket_t = hw.thrust_len

    with BuildPart() as part:
        with BuildSketch() as sk:
            Rectangle(rig.plate_width, rig.plate_depth)
            fillet_at(sk, [(-half_w, -front_y), (half_w, -front_y),
                           (-half_w, front_y), (half_w, front_y)], rig.corner_r)
        extrude(amount=t)

        top_edges = [e for e in part.part.edges()
                     if abs(e.bounding_box().min.Z - t) < 1e-6
                     and abs(e.bounding_box().max.Z - t) < 1e-6]
        fillet(top_edges, radius=rig.top_edge_r)

        # leadscrew clearance, and the bearing seat opening downwards
        Cylinder((hw.screw_d + rig.fits.screw_clear) / 2, t,
                 align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        extrude(to_extrude=seat_sketch(rig), amount=pocket_t, mode=Mode.SUBTRACT)
        with Locations((0, 0, pocket_t)):
            Cylinder(rig.thrust_relief_d / 2, rig.thrust_relief_t,
                     align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        extrude(to_extrude=lightening_sketch(rig), amount=t, mode=Mode.SUBTRACT)

        with Locations((-rig.rod_x, 0, 0), (rig.rod_x, 0, 0)):
            Cylinder(rig.rod_bore_r, t,
                     align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    cutter = clamp_cutter(rig, rig.rod_x, front_y, t, apex_up=False)
    result = part.part - (cutter + mirror(cutter, about=Plane.YZ))
    assert len(result.solids()) == 1, f"top split into {len(result.solids())} solids"
    return result
