"""06 Cable Management Clip.

Snaps onto a guide rod and carries the microphone lead down the column, so the
cable cannot swing and add its own damping to the measurement.  It is the same
ring twice: one round the rod, one dropped by an outer radius below it for the
cable, joined by a channel that runs alongside the rod.
"""

from build123d import (
    Align, Box, BuildPart, BuildSketch, Circle, Cylinder, Locations, Mode,
    Plane, extrude,
)

from .params import Rig


def _annulus(outer, inner, at=(0.0, 0.0)):
    with BuildSketch(mode=Mode.PRIVATE) as sk:
        with Locations(at):
            Circle(outer)
            Circle(inner, mode=Mode.SUBTRACT)
    return sk.sketch


def clip(rig: Rig):
    """Build a cable clip for `rig`, rod bore centred on the origin, Z from 0 up."""
    bore_r = rig.hw.rod_d / 2
    outer_r = bore_r + rig.clip_wall
    ch_r = rig.channel_d / 2

    with BuildPart() as part:
        # rings are built already hollow, so one ring's bore cannot eat into
        # the wall of the next
        extrude(to_extrude=_annulus(outer_r, bore_r), amount=rig.clip_h)
        extrude(to_extrude=_annulus(ch_r + rig.clip_wall, ch_r,
                                    (0, -rig.channel_drop)), amount=rig.clip_h)
        extrude(to_extrude=_annulus(outer_r, bore_r, (0, -outer_r)),
                amount=rig.cable_ring_h)

        # the rod and the cable channel both have to stay clear
        Cylinder(bore_r, rig.clip_h,
                 align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        with Locations((0, -rig.channel_drop, 0)):
            Cylinder(ch_r, rig.clip_h,
                     align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # cut flat across the top: what is left is a C that springs over the
        # rod, and the flat is what it prints on
        with Locations((0, rig.clip_mouth_y + 2 * outer_r, rig.clip_h / 2)):
            Box(8 * outer_r, 4 * outer_r, rig.clip_h, mode=Mode.SUBTRACT)

    result = part.part
    assert len(result.solids()) == 1, f"clip split into {len(result.solids())} solids"
    return result
