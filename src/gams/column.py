"""Geometry shared by the two plates that carry the column.

The base and the top are the same 60 x 30 plate: two split rod clamps, a
leadscrew bore, a thrust bearing seat and a lightened hub.  They differ only in
which face the bearing seat opens from, and the base adds an outrigger foot.
"""

import math

from build123d import (
    Align, Box, BuildPart, BuildSketch, Circle, Locations, Mode, Plane,
    Polygon, Rectangle, extrude, fillet, mirror,
)

from .params import Rig, cap_head, nut


def sector(r_out, r_in, deg, reach):
    """A sketch of the annulus `r_in`..`r_out` between 0 and `deg` degrees."""
    a = math.radians(deg)
    with BuildSketch(mode=Mode.PRIVATE) as sk:
        Circle(r_out)
        if r_in > 0:
            Circle(r_in, mode=Mode.SUBTRACT)
        Polygon((0, 0), (reach, 0), (reach * math.cos(a), reach * math.sin(a)),
                align=None, mode=Mode.INTERSECT)
    return sk.sketch


def fillet_at(sk, points, radius, tol=1e-6):
    """Fillet the sketch vertices sitting at `points`.

    Vertices are re-queried by position rather than held across operations,
    which keeps this correct after an earlier fillet has rebuilt the wire.
    """
    picked = [v for v in sk.vertices()
              if any(abs(v.X - x) < tol and abs(v.Y - y) < tol for x, y in points)]
    if picked:
        fillet(picked, radius=radius)
    return picked


def tangent_point(centre, radius, frm):
    """Where a line from `frm` touches the circle, on the same side as `frm`.

    Used wherever a straight flank has to run smoothly into a round boss.
    Hulling would do the same job but polygonises the circle, so the boss comes
    out slightly undersize.
    """
    cx, cy = centre
    dx, dy = frm[0] - cx, frm[1] - cy
    dist = math.hypot(dx, dy)
    if dist <= radius:
        raise ValueError("point already inside the circle")
    angle = math.atan2(dy, dx) + math.acos(radius / dist)
    return cx + radius * math.cos(angle), cy + radius * math.sin(angle)


def brace_sketch(rig: Rig):
    """The stiffening brace: an arc between the spokes with a spur to the rim.

    It runs the full thickness of the plate, so the bearing seat has to be cut
    around it rather than through it.  The reference is mirror-symmetric about
    both axes, not four-fold rotational — mirroring, not rotating, is what puts
    the braces in the right quadrants.
    """
    reach = 4 * rig.rim_r
    quadrant = (sector(rig.rim_r * rig.rib_ro_frac, rig.rim_r * rig.rib_ri_frac,
                       rig.brace_deg, reach)
                + sector(rig.rim_r, rig.rim_r * rig.rib_ro_frac,
                         rig.spur_deg, reach))
    half = quadrant + mirror(quadrant, about=Plane.YZ)
    return half + mirror(half, about=Plane.XZ)


def lightening_sketch(rig: Rig):
    """The hub cut: sectors between four spokes, less the brace."""
    with BuildSketch(mode=Mode.PRIVATE) as petals:
        Circle(rig.rim_r)
        Circle(rig.rim_r * rig.light_ri_frac, mode=Mode.SUBTRACT)
        Rectangle(rig.spoke_w, 4 * rig.rim_r, mode=Mode.SUBTRACT)
        Rectangle(4 * rig.rim_r, rig.spoke_w, mode=Mode.SUBTRACT)
    return petals.sketch - brace_sketch(rig)


def seat_sketch(rig: Rig):
    """The thrust bearing seat: a rim-sized disc flatted to the bearing OD.

    The flats locate the bearing; the lobes above and below are lightening.
    The brace passes through, so it is left standing.
    """
    with BuildSketch(mode=Mode.PRIVATE) as seat:
        Circle(rig.rim_r)
        Rectangle(2 * rig.pocket_r, 4 * rig.rim_r, mode=Mode.INTERSECT)
    return seat.sketch - brace_sketch(rig)


def clamp_cutter(rig: Rig, x: float, front_y: float, thickness: float,
                 apex_up: bool = True):
    """The split, cross bolt and nut slot that let a boss pinch its rod.

    Built as a cutting solid at +`x`; mirror it for the other rod.  The bolt
    hole is a teardrop so it prints without support — `apex_up` points it the
    way the part is printed, which for the top plate is inverted.
    """
    hw = rig.hw
    bolt_r = (hw.clamp_bolt + rig.fits.bolt_clear) / 2
    nut_af, nut_t = nut(hw.clamp_bolt)
    bolt_y = front_y - rig.bolt_inset
    bolt_z = thickness / 2
    apex = rig.teardrop_k * bolt_r * (1 if apex_up else -1)
    nut_face_x = x - rig.slit_w / 2 - rig.jaw_wall
    slot_h = thickness - rig.nut_slot_ceiling

    with BuildPart() as cut:
        # radial split: from the bore out to the front edge, full height
        with Locations((x, front_y / 2, thickness / 2)):
            Box(rig.slit_w, front_y, thickness)

        # cross bolt, drawn as a teardrop for support-free printing
        bolt_x0 = x - rig.bolt_reach_in
        with BuildSketch(Plane.YZ.offset(bolt_x0)):
            with Locations((bolt_y, bolt_z)):
                Circle(bolt_r)
            Polygon((bolt_y - bolt_r, bolt_z), (bolt_y + bolt_r, bolt_z),
                    (bolt_y, bolt_z + apex), align=None)
        extrude(amount=rig.plate_width / 2 - bolt_x0)

        # counterbore so the cap head seats flat in the curved outer face
        head_r = (cap_head(hw.clamp_bolt) + rig.head_fit) / 2
        cbore_x0 = rig.plate_width / 2 - rig.head_cbore_depth
        with BuildSketch(Plane.YZ.offset(cbore_x0)):
            with Locations((bolt_y, bolt_z)):
                Circle(head_r)
        extrude(amount=rig.head_cbore_depth)

        # nut slot, loaded from the underside and capped so the nut stays put
        with Locations((nut_face_x - (nut_t + rig.nut_fit) / 2, bolt_y, slot_h / 2)):
            Box(nut_t + rig.nut_fit, nut_af + rig.nut_fit, slot_h)

    return cut.part
