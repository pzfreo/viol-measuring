"""07 Hammer — the impulse hammer that hangs from the slider arm.

A pendulum: it hangs on a pin through the slot near its top, and you lift and
release it so the head strikes the belly at the same speed every time.  The
shaft is hollow and the head forked, which keeps the moving mass low without
losing stiffness — a floppy hammer smears the impulse and costs you bandwidth.
"""

from build123d import (
    Align, Box, BuildPart, BuildSketch, Locations, Mode, Plane, RectangleRounded,
    loft,
)

from .params import Rig


def hammer(rig: Rig, handheld: bool = False):
    """Build the impulse hammer for `rig`, head at Z=0.

    `handheld` builds part 11 instead: the same hammer without the pivot
    slot, for tapping by hand rather than swinging it from the arm.
    """
    d = rig.hammer_depth
    r = rig.hammer_corner_r

    with BuildPart() as part:
        sections = []
        for z, half in rig.hammer_profile:
            with BuildSketch(Plane.XY.offset(z)) as sk:
                RectangleRounded(2 * half, d, min(r, half - 0.01, d / 2 - 0.01))
            sections.append(sk)
        loft()

        # slot up the middle of the head, so it straddles rather than blocks
        z0, z1 = rig.hammer_fork_z
        with Locations((0, 0, (z0 + z1) / 2)):
            Box(rig.hammer_fork_w, 2 * d, z1 - z0, mode=Mode.SUBTRACT)

        # hollow shaft
        c0, c1 = rig.hammer_core_z
        core_w = rig.handheld_core_w if handheld else rig.hammer_core_w
        with Locations((0, 0, (c0 + c1) / 2)):
            Box(core_w, core_w, c1 - c0, mode=Mode.SUBTRACT)

        # the slot the pivot pin passes through — the handheld one has none
        if not handheld:
            pivot_z = rig.hammer_drop - rig.hammer_pivot_from_top
            with Locations((0, 0, pivot_z)):
                Box(4 * max(h for _, h in rig.hammer_profile), rig.hammer_slot_d,
                    rig.hammer_slot_h, mode=Mode.SUBTRACT)

    result = part.part
    assert len(result.solids()) == 1, f"hammer split into {len(result.solids())} solids"
    return result


def handheld_hammer(rig: Rig):
    """11 Handheld Hammer — the same head, tapped by hand off the rig."""
    return hammer(rig, handheld=True)
