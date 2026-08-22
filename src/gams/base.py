"""01 Base — the foot of the column.

Carries the two guide rods in split clamps, houses the leadscrew thrust
bearing, and stands on three mounting points.  The lobe on +Y is an outrigger:
the arm cantilevers out that way, so the third foot has to stay ahead of the
overturning moment.
"""

import math

from build123d import (
    Align, Box, BuildPart, BuildSketch, Circle, Cylinder, Locations, Mode,
    Plane, Polygon, Rectangle, extrude, fillet, mirror,
)

from .params import Rig, nut


def _tangent_point(centre, radius, frm):
    """Where a line from `frm` touches the circle, on the same side as `frm`.

    Used to flare the outrigger neck into the lobe.  Meeting the circle at a
    tangent rather than crossing it leaves no sliver of material at the join.
    """
    cx, cy = centre
    dx, dy = frm[0] - cx, frm[1] - cy
    dist = math.hypot(dx, dy)
    if dist <= radius:
        raise ValueError("neck already inside the lobe; reduce neck_frac")
    angle = math.atan2(dy, dx) + math.acos(radius / dist)
    return cx + radius * math.cos(angle), cy + radius * math.sin(angle)


def _fillet_at(sk, points, radius, tol=1e-6):
    """Fillet the sketch vertices sitting at `points`.

    Vertices are re-queried by position rather than held across operations,
    which keeps this correct after an earlier fillet has rebuilt the wire.
    """
    picked = [v for v in sk.vertices()
              if any(abs(v.X - x) < tol and abs(v.Y - y) < tol for x, y in points)]
    if picked:
        fillet(picked, radius=radius)
    return picked


def clamp_cutter(rig: Rig, x: float, front_y: float, thickness: float):
    """The split, cross bolt and nut trap that let a boss pinch its rod.

    Built as a cutting solid at +`x`; mirror it for the other rod.  The bolt
    hole is a teardrop so it prints without support.
    """
    hw = rig.hw
    bolt_r = (hw.clamp_bolt + rig.fits.bolt_clear) / 2
    nut_af, nut_t = nut(hw.clamp_bolt)
    nut_w = nut_af + rig.nut_fit
    bolt_y = front_y - 5.0
    bolt_z = thickness / 2
    nut_face_x = x - rig.slit_w / 2 - rig.jaw_wall

    with BuildPart() as cut:
        # radial split: from the bore out to the front edge, full height
        with Locations((x, front_y / 2, thickness / 2)):
            Box(rig.slit_w, front_y, thickness)

        # cross bolt, drawn as a teardrop for support-free printing
        with BuildSketch(Plane.YZ.offset(x - rig.boss_r)):
            with Locations((bolt_y, bolt_z)):
                Circle(bolt_r)
            Polygon((bolt_y - bolt_r, bolt_z),
                    (bolt_y + bolt_r, bolt_z),
                    (bolt_y, bolt_z + rig.teardrop_k * bolt_r),
                    align=None)
        extrude(amount=rig.plate_width / 2 - x + rig.boss_r)

        # nut trap, loaded from the underside
        with Locations((nut_face_x - nut_t / 2, bolt_y, bolt_z / 2)):
            Box(nut_t, nut_w, bolt_z)

    return cut.part


def base(rig: Rig):
    """Build the base plate for `rig`."""
    hw = rig.hw
    t = rig.plate_t
    front_y = rig.plate_depth / 2
    pocket_t = hw.thrust_len

    mounts = [(-(rig.plate_width / 2 - rig.mount_inset), -(front_y - rig.mount_inset)),
              ((rig.plate_width / 2 - rig.mount_inset), -(front_y - rig.mount_inset)),
              (0, rig.lobe_y)]

    with BuildPart() as part:
        with BuildSketch() as sk:
            Rectangle(rig.plate_width, rig.plate_depth)
            with Locations((0, rig.lobe_y)):
                Circle(rig.lobe_r)
            neck_h = rig.lobe_r * rig.neck_frac
            if neck_h < rig.lobe_r:      # flare the neck out to meet the lobe
                tx, ty = _tangent_point((0, rig.lobe_y), rig.lobe_r, (neck_h, front_y))
            else:                        # straight neck, tangent to the lobe
                tx, ty = neck_h, rig.lobe_y
            Polygon((-neck_h, front_y), (neck_h, front_y), (tx, ty), (-tx, ty),
                    align=None)
            # square corners get a plain round; the reentrant waist where the
            # outrigger neck meets the plate gets a larger blend
            half_w = rig.plate_width / 2
            _fillet_at(sk, [(-half_w, -front_y), (half_w, -front_y),
                            (-half_w, front_y), (half_w, front_y)], rig.corner_r)
            _fillet_at(sk, [(-neck_h, front_y), (neck_h, front_y)],
                       rig.neck_blend_r)
        extrude(amount=t)

        # leadscrew clearance, and the thrust bearing pocket in the top face
        Cylinder((hw.screw_d + rig.fits.screw_clear) / 2, t,
                 align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        with Locations((0, 0, t - pocket_t)):
            Cylinder(rig.pocket_r, pocket_t,
                     align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # lightening: four holes on the diagonals, inside a rim, crossed by a
        # thin annular rib that keeps the plate stiff in torsion
        mid = rig.rim_r * rig.rib_mid_frac
        with BuildSketch(mode=Mode.PRIVATE) as petals:
            Circle(rig.rim_r)
            Circle(rig.rim_r * rig.light_ri_frac, mode=Mode.SUBTRACT)
            Rectangle(rig.spoke_w, 4 * rig.rim_r, mode=Mode.SUBTRACT)
            Rectangle(4 * rig.rim_r, rig.spoke_w, mode=Mode.SUBTRACT)
        with BuildSketch(mode=Mode.PRIVATE) as rib:
            Circle(mid + rig.rib_w / 2)
            Circle(mid - rig.rib_w / 2, mode=Mode.SUBTRACT)
        extrude(to_extrude=petals.sketch - rib.sketch, amount=t, mode=Mode.SUBTRACT)

        # guide rod bores
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

    cutter = clamp_cutter(rig, rig.rod_x, front_y, t)
    result = part.part - (cutter + mirror(cutter, about=Plane.YZ))
    assert len(result.solids()) == 1, f"base split into {len(result.solids())} solids"
    return result
