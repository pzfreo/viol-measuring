"""07 Hammer and 11 Handheld Hammer — the impulse hammers.

Both are the same lever: a ⌀12 round head, a ⌀5 round tail, and a long
concave flank arc tangent to both, extruded 6 mm and rounded along its two
flat faces.  Part 07 hangs from a pin through the tail and swings; part 11 you
hold and tap with.

They differ only inside.  Both are bored through the head with a recess on one
face, and both run a channel from that bore up the shaft, straight for the
first two thirds and then curving out through one flat face.  In part 07 that
channel is round; in part 11 it is a flattened slot.  Part 07 alone carries
the small cross hole it hangs on.

Every dimension here was measured off Luca Jost's meshes.  Where a shape is
described as an arc it fits one to better than 0.005 mm, so these are his
radii, not a curve fitted through sampled points.
"""

import math

from build123d import (
    Axis, BuildLine, BuildPart, BuildSketch, CenterArc, Circle, Cylinder, Line,
    Location, Locations, Mode, Plane, Rectangle, SlotOverall, add, extrude,
    fillet, sweep,
)

from .params import Rig


def _outline(rig: Rig):
    """The lever's silhouette, in the XZ plane, head end at Z=0.

    Built as the two round ends plus a slab between them, with the flank arcs
    cut away as two large discs.  Because each disc is tangent to both ends,
    the cut lands exactly on them and leaves no step — which a hull of the two
    circles could not do, the flank being concave.
    """
    fx, fz = rig.hammer_flank
    z0, z1 = rig.hammer_tangent_z
    rh = rig.hammer_head_d / 2
    with BuildSketch(Plane.XZ) as sk:
        with Locations((0, rig.hammer_head_z)):
            Circle(rh)
        with Locations((0, rig.hammer_tip_z)):
            Circle(rig.hammer_tip_d / 2)
        with Locations((0, (z0 + z1) / 2)):
            Rectangle(2 * rh, z1 - z0)
        with Locations((fx, fz), (-fx, fz)):
            Circle(rig.hammer_flank_r, mode=Mode.SUBTRACT)
    return sk.sketch


def _cavity(rig: Rig, handheld: bool):
    """The channel up the shaft, as a solid to subtract.

    Its path leaves the head bore straight up the centre, then rolls over onto
    an arc that carries it out through one face near the tail.  Sweeping the
    section along that path is what puts the wall thickness on the outside of
    the curve where the reference has it.
    """
    cy, R = rig.hammer_cavity_y, rig.hammer_cavity_arc_r
    with BuildPart(mode=Mode.PRIVATE) as tube:
        with BuildLine(Plane.YZ) as path:
            Line((cy, rig.hammer_head_z), (cy, rig.hammer_cavity_straight_to))
            CenterArc((cy - R, rig.hammer_cavity_straight_to), R,
                      start_angle=0, arc_size=math.degrees(
                          math.acos(1 - (cy + rig.hammer_depth) / R)))
        with BuildSketch(Plane.XY.offset(rig.hammer_head_z)) as sec:
            with Locations((0, cy)):
                if handheld:
                    SlotOverall(*rig.handheld_cavity)
                else:
                    Circle(rig.hammer_cavity_d / 2)
        sweep(sec.sketch, path=path.line)
    return tube.part


def hammer(rig: Rig, handheld: bool = False):
    """Build part 07 for `rig`, head at Z=0.

    `handheld` builds part 11 instead: no hanging pin hole, and a flattened
    channel in place of the round one.
    """
    d = rig.hammer_depth
    with BuildPart() as part:
        extrude(_outline(rig), amount=d / 2, both=True)
        fillet(part.faces().filter_by(Axis.Y).edges(), rig.hammer_corner_r)

        # bore through the head, with its recess on one face only
        with Locations(Location((0, 0, rig.hammer_head_z), (90, 0, 0))):
            Cylinder(rig.hammer_bore_d / 2, 2 * d, mode=Mode.SUBTRACT)
        cbore = rig.hammer_cbore_depth
        with Locations(Location((0, d / 2 - cbore / 2, rig.hammer_head_z), (90, 0, 0))):
            Cylinder(rig.hammer_cbore_d / 2, cbore, mode=Mode.SUBTRACT)

        add(_cavity(rig, handheld), mode=Mode.SUBTRACT)

        if not handheld:
            pin_z = rig.hammer_drop - rig.hammer_pivot_from_top
            with Locations(Location((0, 0, pin_z), (0, 90, 0))):
                Cylinder(rig.hammer_pin_d / 2, 4 * rig.hammer_head_d,
                         mode=Mode.SUBTRACT)

    result = part.part
    assert len(result.solids()) == 1, f"hammer split into {len(result.solids())} solids"
    return result


def handheld_hammer(rig: Rig):
    """11 Handheld Hammer — the same lever, tapped by hand off the rig."""
    return hammer(rig, handheld=True)
