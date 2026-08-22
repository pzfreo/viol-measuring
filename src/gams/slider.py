"""03 Slider — the carriage that sets the tap height.

Rides the two guide rods on linear bearings, driven up and down by the
leadscrew through a captive nut, and carries the arm that reaches out over the
instrument.  The hammer hangs from the fork at the end of that arm, on the
instrument's centreline.

The arm is a hollow box beam: it is the longest cantilever in the rig, so its
bending stiffness sets how much the tap point moves between taps.
"""

import math

from build123d import (
    Align, Axis, Box, BuildPart, BuildSketch, Circle, Cylinder, Locations, Mode,
    Location, Plane, Polygon, Rectangle, RegularPolygon, add, extrude, fillet,
    make_hull, mirror, offset,
)

from .column import sector
from .params import Rig, nut


def _plan(rig: Rig):
    """Plan outline: the carriage, the tapered arm and the fork head."""
    half_d = rig.carriage_d / 2
    head_y = rig.pivot_y - rig.fork_offset        # the head sits behind the pivot
    tip_y = head_y - rig.fork_r
    tip_hw = rig.arm_root_hw - rig.arm_taper * (tip_y - half_d)

    with BuildSketch(mode=Mode.PRIVATE) as arm:
        Polygon((-rig.arm_root_hw, half_d), (rig.arm_root_hw, half_d),
                (tip_hw, tip_y), (-tip_hw, tip_y), align=None)
        with Locations((0, head_y)):
            Circle(rig.fork_r)
        make_hull()                                # tangent flanks into the head

    with BuildSketch(mode=Mode.PRIVATE) as plan:
        Rectangle(rig.carriage_w, rig.carriage_d)
        fillet(plan.vertices(), radius=rig.corner_r)
        add_arm = arm.sketch
    return plan.sketch + add_arm


def slider(rig: Rig):
    """Build the slider for `rig`, in its own frame with Z from 0 up."""
    hw = rig.hw
    t = rig.plate_t
    tube_h = hw.bearing_len
    bore_r = (hw.bearing_od + rig.fits.bearing_pocket) / 2
    nut_af, _ = nut(hw.screw_d)

    with BuildPart() as part:
        extrude(to_extrude=_plan(rig), amount=t)

        # bearing tubes, split front and back so they can be printed and
        # pinched onto the bearings
        with Locations((-rig.rod_x, 0, 0), (rig.rod_x, 0, 0)):
            Cylinder(rig.tube_od / 2, tube_h,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((-rig.rod_x, 0, 0), (rig.rod_x, 0, 0)):
            Cylinder(bore_r, tube_h,
                     align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        # relieve each bore fore and aft: through the carriage it is a slot,
        # above it there is nothing left but two posts per bearing
        reach = 4 * rig.tube_od
        a = rig.bore_relief_deg
        upper = (sector(rig.tube_od / 2, bore_r, 180 - a, reach)
                 - sector(rig.tube_od / 2, bore_r, a, reach))
        one = upper + mirror(upper, about=Plane.XZ)
        relief = one.moved(Location((rig.rod_x, 0, 0))) \
            + one.moved(Location((-rig.rod_x, 0, 0)))
        extrude(to_extrude=relief, amount=tube_h, mode=Mode.SUBTRACT)

        # leadscrew, with the drive nut trapped in the middle of the plate
        Cylinder((hw.screw_d + rig.fits.screw_clear) / 2, t,
                 align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        nut_t = (nut_af + rig.hex_fit) / math.cos(math.radians(30)) / 2
        with BuildSketch(Plane.XY.offset(rig.nut_trap_z), mode=Mode.PRIVATE) as hexa:
            RegularPolygon(nut_t, 6, major_radius=True, rotation=90)
        extrude(to_extrude=hexa.sketch, amount=rig.nut_trap_h, mode=Mode.SUBTRACT)

        # hollow the arm out into a box beam — the skins do the work, the core
        # only adds mass at the end of the longest cantilever in the rig
        y0, y1 = rig.arm_hollow_from, rig.arm_hollow_to
        cx0 = rig.arm_core_x0 + rig.arm_core_slope * (y0 - 20.0)
        cx1 = rig.arm_core_x0 + rig.arm_core_slope * (y1 - 20.0)
        hw = rig.arm_core_w / 2
        with BuildSketch(Plane.XY.offset(rig.arm_skin), mode=Mode.PRIVATE) as core:
            Polygon((cx0 - hw, y0), (cx0 + hw, y0), (cx1 + hw, y1), (cx1 - hw, y1),
                    align=None)
            add(_plan(rig), mode=Mode.INTERSECT)
        extrude(to_extrude=core.sketch, amount=t - 2 * rig.arm_skin, mode=Mode.SUBTRACT)

        # fork slot and the hammer pivot
        with Locations((0, rig.pivot_y, t / 2)):
            Box(rig.fork_gap, 4 * rig.fork_r, t, mode=Mode.SUBTRACT)
        with Locations((0, rig.pivot_y, t / 2)):
            Cylinder(rig.pivot_d / 2, 4 * rig.fork_r, rotation=(0, 90, 0),
                     mode=Mode.SUBTRACT)

    result = part.part
    assert len(result.solids()) == 1, f"slider split into {len(result.solids())} solids"
    return result
