"""01 Base — the foot of the column.

Carries the two guide rods in split clamps, seats the leadscrew thrust bearing
in its top face, and stands on three mounting points.  The lobe on +Y is an
outrigger: the arm cantilevers out that way, so the third foot has to stay
ahead of the overturning moment.
"""

import math

from build123d import (
    Align, BuildPart, BuildSketch, Circle, Cylinder, Location, Locations, Mode,
    Plane, Polygon, Rectangle, extrude, fillet, mirror,
)

from .column import (clamp_cutter, fillet_at, lightening_sketch, seat_sketch,
                     tangent_point)
from .params import Rig


def base(rig: Rig):
    """Build the base plate for `rig`, in its own frame with Z from 0 up."""
    hw = rig.hw
    t = rig.plate_t
    front_y = rig.plate_depth / 2
    pocket_t = hw.thrust_len
    half_w = rig.plate_width / 2

    mounts = [(-(half_w - rig.mount_inset), -(front_y - rig.mount_inset)),
              ((half_w - rig.mount_inset), -(front_y - rig.mount_inset)),
              (0, rig.lobe_y)]

    with BuildPart() as part:
        with BuildSketch() as sk:
            Rectangle(rig.plate_width, rig.plate_depth)
            with Locations((0, rig.lobe_y)):
                Circle(rig.lobe_r)
            neck_h = rig.lobe_r * rig.neck_frac
            if neck_h < rig.lobe_r:          # flare the neck out to meet the lobe
                tx, ty = tangent_point((0, rig.lobe_y), rig.lobe_r, (neck_h, front_y))
            else:                            # straight neck, tangent to the lobe
                tx, ty = neck_h, rig.lobe_y
            Polygon((-neck_h, front_y), (neck_h, front_y), (tx, ty), (-tx, ty),
                    align=None)
            fillet_at(sk, [(-half_w, -front_y), (half_w, -front_y),
                           (-half_w, front_y), (half_w, front_y)], rig.corner_r)
            fillet_at(sk, [(-neck_h, front_y), (neck_h, front_y)], rig.neck_blend_r)
        extrude(amount=t)

        # break the top perimeter before any holes are cut
        top = [e for e in part.part.edges()
               if abs(e.bounding_box().min.Z - t) < 1e-6
               and abs(e.bounding_box().max.Z - t) < 1e-6]
        fillet(top, radius=rig.top_edge_r)

        # leadscrew clearance, then the bearing seat in the top face: a disc
        # the size of the lightening rim, flatted to the bearing OD so the
        # flats locate it
        Cylinder((hw.screw_d + rig.fits.screw_clear) / 2, t,
                 align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        extrude(to_extrude=seat_sketch(rig).moved(Location((0, 0, t - pocket_t))),
                amount=pocket_t, mode=Mode.SUBTRACT)

        extrude(to_extrude=lightening_sketch(rig), amount=t, mode=Mode.SUBTRACT)

        with Locations((-rig.rod_x, 0, 0), (rig.rod_x, 0, 0)):
            Cylinder(rig.rod_bore_r, t,
                     align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # three mounting points, counterbored from the top
        with Locations(*[(x, y, 0) for x, y in mounts]):
            Cylinder(rig.mount_d / 2, t,
                     align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        with Locations(*[(x, y, t - rig.mount_cbore_t) for x, y in mounts]):
            Cylinder(rig.mount_cbore_d / 2, rig.mount_cbore_t,
                     align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    cutter = clamp_cutter(rig, rig.rod_x, front_y, t, apex_up=True)
    result = part.part - (cutter + mirror(cutter, about=Plane.YZ))
    assert len(result.solids()) == 1, f"base split into {len(result.solids())} solids"
    return result
