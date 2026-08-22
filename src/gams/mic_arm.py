"""05 Microphone arm.

A strut that clamps to the column and reaches out and down to put the
microphone beside the instrument.  The cable runs in a channel along it, which
is the whole point: a lead flapping in free air adds its own damping to what
you are trying to measure.

The section is a rounded rectangle with an obround channel inside it.  Three
windows cut the +X wall away so the cable can be laid in from the side rather
than threaded, each about 10 mm of arm with its end walls flared at 45°.
Between them the section stays closed, which is what keeps the arm stiff in
twist through the bend, where it is longest and least supported.
"""

import math

from build123d import (
    BuildLine, BuildPart, BuildSketch, CenterArc, Cylinder, Line, Locations,
    Mode, Plane, Polygon, RectangleRounded, SlotOverall, Vector, Wire, add,
    extrude, sweep,
)

from .params import Rig


def _path(rig: Rig):
    """The arm's centreline: straight, arc, straight, arc, straight.

    Every joint is tangent, so the swept section never kinks and the outer
    surface stays smooth through the bend — which a spline through sampled
    points does not guarantee.
    """
    r1, r2 = rig.mic_bend_radii
    th = rig.mic_bend_slope
    z0, z1 = rig.mic_arm_root_z, rig.mic_arm_tip_z
    y0 = rig.mic_arm_bend_from * rig.mic_reach
    y3 = y0 + rig.mic_bend_run

    with BuildLine(Plane.YZ) as path:
        Line((rig.mic_arm_root_y, z0), (y0, z0))
        a1 = CenterArc((y0, z0 - r1), r1, start_angle=90, arc_size=-th)
        a2 = CenterArc((y3, z1 + r2), r2, start_angle=270 - th, arc_size=th)
        Line(a1 @ 1, a2 @ 0)
        Line((y3, z1), (rig.mic_reach, z1))
    return path.line


def _window(rig: Rig, wire, t0: float, t1: float):
    """One side window, as a wedge to subtract.

    Cut square to the arm rather than square to Y: two of the three sit on the
    bend, where those are nowhere near the same thing — the middle window
    spans barely 2 mm of Y for its 10 mm of arm.
    """
    floor = rig.mic_window_floor
    depth = rig.mic_arm_w          # generous; everything outboard of the floor
    flare = depth / math.tan(math.radians(rig.mic_window_flare))
    half = (t1 - t0) * wire.length / 2

    t = (t0 + t1) / 2
    tangent = Vector(wire % t)
    binormal = Vector(1, 0, 0).cross(tangent)
    plane = Plane(origin=wire @ t, x_dir=(1, 0, 0), z_dir=binormal)
    with BuildPart(mode=Mode.PRIVATE) as cut:
        with BuildSketch(plane) as sk:
            Polygon((floor, -half), (floor + depth, -half - flare),
                    (floor + depth, half + flare), (floor, half), align=None)
        extrude(sk.sketch, amount=2 * rig.mic_arm_t, both=True)
    return cut.part


def mic_arm(rig: Rig):
    """Build the microphone arm for `rig`, in assembly coordinates."""
    line = _path(rig)
    wire = Wire.combine(line.edges())[0]

    start = Plane(origin=(0, rig.mic_arm_root_y, rig.mic_arm_root_z),
                  x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    with BuildSketch(start) as outer:
        RectangleRounded(rig.mic_arm_w, rig.mic_arm_t, rig.mic_arm_corner_r)
    with BuildSketch(start) as core:
        with Locations((rig.mic_channel_x, 0)):
            SlotOverall(rig.mic_channel_d, rig.mic_channel_h)

    with BuildPart() as part:
        sweep(outer.sketch, path=wire)
        sweep(core.sketch, path=wire, mode=Mode.SUBTRACT)

        for t0, t1 in rig.mic_windows:
            add(_window(rig, wire, t0, t1), mode=Mode.SUBTRACT)

        # the seat the microphone drops into, near the tip
        with Locations((rig.mic_seat_x, rig.mic_reach - rig.mic_seat_back,
                        rig.mic_arm_tip_z)):
            Cylinder(rig.mic_seat_d / 2, 2 * rig.mic_arm_t, mode=Mode.SUBTRACT)

    result = part.part
    assert len(result.solids()) == 1, f"arm split into {len(result.solids())} solids"
    return result
