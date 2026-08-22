"""05 Microphone arm.

A hollow strut that clamps to the column and reaches out and down to put the
microphone beside the instrument.  The cable runs inside it, which is the whole
point: a lead flapping in free air adds its own damping to what you are trying
to measure.
"""

from build123d import (
    Box, BuildLine, BuildPart, BuildSketch, Line, Locations, Mode, Plane,
    RectangleRounded, Spline, sweep,
)

from .params import Rig


def _path_points(rig: Rig):
    """Key points of the arm centreline: root, bend start, bend end, tip."""
    y0, z0 = rig.mic_arm_root_y, rig.mic_arm_root_z
    y3, z3 = rig.mic_reach, rig.mic_arm_tip_z
    return ((0, y0, z0),
            (0, rig.mic_reach * rig.mic_arm_bend_from, z0),
            (0, rig.mic_reach * rig.mic_arm_bend_to, z3),
            (0, y3, z3))


def mic_arm(rig: Rig):
    """Build the microphone arm for `rig`, in assembly coordinates."""
    pts = _path_points(rig)

    # straight, S-bend, straight — a single spline through all four points
    # overshoots above the root, which would make the arm taller than it is
    with BuildLine() as path:
        Line(pts[0], pts[1])
        Spline(pts[1], pts[2], tangents=((0, 1, 0), (0, 1, 0)))
        Line(pts[2], pts[3])

    start = Plane(origin=pts[0], x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    with BuildSketch(start) as outer:
        RectangleRounded(rig.mic_arm_w, rig.mic_arm_t, rig.mic_arm_corner_r)
    with BuildSketch(start) as core:
        RectangleRounded(rig.mic_channel_d, rig.mic_channel_h,
                         rig.mic_channel_h / 2 - 0.01)

    with BuildPart() as part:
        sweep(outer.sketch, path=path.line)
        sweep(core.sketch, path=path.line, mode=Mode.SUBTRACT)

        # the opening the microphone drops into, near the tip
        y_a = rig.mic_reach * rig.mic_slot_from
        y_b = rig.mic_reach * rig.mic_slot_to
        with Locations((rig.mic_arm_w / 4, (y_a + y_b) / 2, rig.mic_arm_tip_z)):
            Box(rig.mic_arm_w, y_b - y_a, 2 * rig.mic_arm_t, mode=Mode.SUBTRACT)

    result = part.part
    assert len(result.solids()) == 1, f"mic arm split into {len(result.solids())} solids"
    return result
