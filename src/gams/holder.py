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
    Rectangle, add, extrude,
)
# aliased: `fillet` is also the name of this module's own arch parameter
from build123d import fillet as fillet_

from .params import Rig


def _arch(span, radius, fillet, y_floor):
    """One curve of the arch: two big arcs meeting at a filleted point.

    Luca Jost's outline is not the superellipse it looks like.  Both its
    curves are arcs of a radius twice the span, struck from centres out on the
    rod axis either side, meeting at a point that is then rounded off.  Fitted
    to his mesh the arcs land within 0.01 mm, which is his construction rather
    than a curve through my samples.

    Building it as the overlap of two discs puts the arcs in exactly, and a
    fillet on the one sharp vertex closes the top the same way he did.
    """
    c = radius - span
    with BuildSketch(mode=Mode.PRIVATE) as sk:
        with Locations((-c, 0)):
            Circle(radius)
        with Locations((c, 0)):
            Circle(radius, mode=Mode.INTERSECT)
        apex = max(sk.vertices(), key=lambda v: v.Y)
        fillet_(apex, fillet)
        # cut the tails off below the mouth
        with Locations((0, y_floor - 2 * radius)):
            Rectangle(4 * radius, 4 * radius, mode=Mode.SUBTRACT)
    return sk.sketch


def holder(rig: Rig):
    """Build the microphone holder for `rig`, on the rig axis with Z from 0 up."""
    bore_r = rig.hw.rod_d / 2
    outer_r = bore_r + rig.clip_wall
    y0 = rig.holder_mouth_y
    # the arch springs from the rod axis; everything below it is clip
    arch_y0 = rig.arch_floor_y

    span = rig.arch_span
    arch_b = rig.arch_height
    with BuildSketch(mode=Mode.PRIVATE) as arch:
        add(_arch(span, span * rig.arch_outer_r_frac,
                  span * rig.arch_outer_apex_frac, arch_y0))
        add(_arch(span * rig.arch_inner_w_frac, span * rig.arch_inner_r_frac,
                  span * rig.arch_inner_apex_frac, arch_y0), mode=Mode.SUBTRACT)

    with BuildPart() as part:
        extrude(to_extrude=arch.sketch, amount=rig.holder_plate_t)

        # fins either side of the slot the arm slides in
        with BuildSketch(mode=Mode.PRIVATE) as fins:
            for sign in (1, -1):
                with Locations((sign * (rig.arm_slot_w / 2 + rig.fin_outer_x) / 2, 0)):
                    Rectangle(rig.fin_outer_x - rig.arm_slot_w / 2, 4 * arch_b)
            add(arch.sketch, mode=Mode.INTERSECT)   # fins live on the arch only
        extrude(to_extrude=fins.sketch, amount=rig.fin_h)

        # Each fin is filleted into the plate along its outside — the joint
        # that would crack first, since the fins stand clear of everything
        # holding them and the arm is pushed sideways against them to set the
        # microphone.  Not along the inside: a fillet in the slot would foul
        # the arm it is there to guide, and the reference has none.
        slot = rig.arm_slot_w / 2
        feet = [e for f in part.part.faces()
                if f.bounding_box().min.Z > rig.holder_plate_t - 0.01
                and f.bounding_box().max.Z > rig.holder_plate_t + 0.01
                for e in f.edges()
                if abs(e.bounding_box().min.Z - rig.holder_plate_t) < 0.01
                and abs(e.bounding_box().max.Z - rig.holder_plate_t) < 0.01
                and max(abs(e.bounding_box().min.X),
                        abs(e.bounding_box().max.X)) > slot + 0.05]
        if feet:
            fillet_(feet, rig.fin_foot_r)

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
        with Locations((0, y0 - 4 * span, rig.holder_h / 2)):
            Box(8 * span, 8 * span, rig.holder_h, mode=Mode.SUBTRACT)

    result = part.part
    assert len(result.solids()) == 1, f"holder split into {len(result.solids())} solids"
    return result
