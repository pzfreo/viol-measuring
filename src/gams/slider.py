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
    Align, Axis, Box, BuildLine, BuildPart, BuildSketch, Circle, Cone, Cylinder,
    Line, Location, Locations, Mode, Plane, Polygon, Rectangle, RegularPolygon,
    Spline, add, extrude, fillet, make_hull, mirror, offset, sweep,
)

from .column import sector, tangent_point
from .params import Rig, nut


def _plan(rig: Rig):
    """Plan outline: the carriage, the tapered arm and the fork head."""
    half_d = rig.carriage_d / 2
    head_y = rig.pivot_y - rig.fork_offset        # the head sits behind the pivot
    waist_y = rig.pivot_y * rig.arm_waist_frac
    waist_hw = rig.arm_waist_hw

    # The arm narrows to a waist and then flares into the fork head on
    # straight tangent flanks.
    tx, ty = tangent_point((0, head_y), rig.fork_r, (waist_hw, waist_y))

    with BuildSketch(mode=Mode.PRIVATE) as arm:
        Polygon((-rig.arm_root_hw, half_d), (rig.arm_root_hw, half_d),
                (waist_hw, waist_y), (-waist_hw, waist_y), align=None)
        Polygon((-waist_hw, waist_y), (waist_hw, waist_y), (tx, ty), (-tx, ty),
                align=None)
        with Locations((0, head_y)):
            Circle(rig.fork_r)
        # the head is a truncated round, not a full one
        with Locations((0, rig.pivot_y + rig.fork_top + rig.fork_r)):
            Rectangle(4 * rig.fork_r, 2 * rig.fork_r, mode=Mode.SUBTRACT)

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
        # Each bearing is held by two posts, one either side. In section a
        # post is L-shaped: wide where it wraps the bearing, stepping in at
        # the rim so the relief between posts is a slot rather than a gap.
        reach = 4 * rig.tube_od
        outer = rig.tube_od / 2
        step_r = bore_r + (outer - bore_r) * rig.post_step_frac
        quarter = (sector(step_r, bore_r, rig.post_inner_deg, reach)
                   + sector(outer, step_r, rig.post_outer_deg, reach))
        post = quarter + mirror(quarter, about=Plane.XZ)
        posts = post + mirror(post, about=Plane.YZ)
        with BuildSketch(mode=Mode.PRIVATE) as ring:
            Circle(outer)
            Circle(bore_r, mode=Mode.SUBTRACT)
        one = ring.sketch - posts
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

        # the microphone lead runs through the arm, entering the carriage's
        # front face through a cone so the cable is not chafed on the edge
        z = t / 2
        pts = [(rig.arm_root_hw * xf, rig.pivot_y * yf, z) for yf, xf in rig.cable_path]
        face_y = -rig.carriage_d / 2
        with BuildLine() as bore:
            Line((pts[0][0], face_y, z), pts[0])
            Spline(*pts)
        with BuildSketch(Plane(origin=(pts[0][0], face_y, z), x_dir=(1, 0, 0),
                               z_dir=(0, 1, 0)), mode=Mode.PRIVATE) as sec:
            Circle(rig.cable_d / 2)
        sweep(sec.sketch, path=bore.line, mode=Mode.SUBTRACT)

        mouth = ((rig.cable_mouth_d - rig.cable_d) / 2
                 / math.tan(math.radians(rig.cable_mouth_deg)))
        with Locations(Location((pts[0][0], face_y, z), (-90, 0, 0))):
            Cone(rig.cable_mouth_d / 2, rig.cable_d / 2, mouth,
                 align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # the slot the hammer swings in, and a pivot hole for each reach
        reaches = rig.pivot_reaches
        slot_lo = reaches[0] - rig.fork_slot_back
        slot_hi = reaches[-1] + 2 * rig.fork_r
        with Locations((0, (slot_lo + slot_hi) / 2, t / 2)):
            Box(rig.fork_gap, slot_hi - slot_lo, t, mode=Mode.SUBTRACT)
        for y in reaches:
            with Locations((0, y, t / 2)):
                Cylinder(rig.pivot_d / 2, 4 * rig.fork_r, rotation=(0, 90, 0),
                         mode=Mode.SUBTRACT)

    result = part.part
    assert len(result.solids()) == 1, f"slider split into {len(result.solids())} solids"
    return result
