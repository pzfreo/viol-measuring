"""05 Microphone arm.

A strut that clamps to the column and reaches out and down to put the
microphone beside the instrument.  The cable runs in a channel along it, which
is the whole point: a lead flapping in free air adds its own damping to what
you are trying to measure.

The channel is enclosed for almost the whole run and opens through two short
windows, so the cable can be laid in from the side rather than threaded.  That
matters structurally: an open section is far softer in twist than a closed one,
and the original keeps the box closed through the bend, where the arm is
longest and least supported.
"""

from build123d import (
    Box, BuildLine, BuildPart, BuildSketch, Line, Locations, Mode, Plane,
    RectangleRounded, SlotOverall, Spline, sweep,
)

from .params import Rig


def _path_points(rig: Rig):
    """Centreline of the arm: root, the traced S-bend, then the tip run."""
    z0, z3 = rig.mic_arm_root_z, rig.mic_arm_tip_z
    drop = z0 - z3
    # every third traced point: enough to hold the shape, few enough that
    # the spline does not wobble between them and break the sweep
    traced = list(rig.mic_arm_bend)
    keep = traced[::3] + ([traced[-1]] if (len(traced) - 1) % 3 else [])
    bend = [(0, yf * rig.mic_reach, z3 + zf * drop) for yf, zf in keep]
    return ([(0, rig.mic_arm_root_y, z0)] + bend
            + [(0, rig.mic_reach, z3)])


def mic_arm(rig: Rig):
    """Build the microphone arm for `rig`, in assembly coordinates."""
    pts = _path_points(rig)

    # straight, S-bend, straight — a single spline through all four points
    # overshoots above the root, which would make the arm taller than it is
    with BuildLine() as path:
        Line(pts[0], pts[1])
        Spline(*pts[1:-1], tangents=((0, 1, 0), (0, 1, 0)))
        Line(pts[-2], pts[-1])

    start = Plane(origin=pts[0], x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    with BuildSketch(start) as outer:
        # fully rounded ends — the reference section is an obround, not a
        # rounded rectangle, and the difference is ~9% of the arm's volume
        SlotOverall(rig.mic_arm_w, rig.mic_arm_t)
    core_x = rig.mic_channel_face - rig.mic_channel_d / 2
    with BuildSketch(start) as core:
        with Locations((core_x, 0)):
            RectangleRounded(rig.mic_channel_d, rig.mic_channel_h,
                             rig.mic_channel_h / 2 - 0.01)

    with BuildPart() as part:
        sweep(outer.sketch, path=path.line)
        sweep(core.sketch, path=path.line, mode=Mode.SUBTRACT)

        # two windows in the +X wall, so the cable can be laid into the channel
        for f0, f1 in rig.mic_windows:
            y0, y1 = rig.mic_reach * f0, rig.mic_reach * f1
            with Locations((rig.mic_arm_w, (y0 + y1) / 2,
                            (rig.mic_arm_root_z + rig.mic_arm_tip_z) / 2)):
                Box(2 * (rig.mic_arm_w - rig.mic_channel_face), y1 - y0,
                    4 * (rig.mic_arm_root_z - rig.mic_arm_tip_z), mode=Mode.SUBTRACT)

        # the opening the microphone drops into, near the tip
        y_a = rig.mic_reach * rig.mic_slot_from
        y_b = rig.mic_reach * rig.mic_slot_to
        with Locations((rig.mic_arm_w / 4, (y_a + y_b) / 2, rig.mic_arm_tip_z)):
            Box(rig.mic_arm_w, y_b - y_a, 2 * rig.mic_arm_t, mode=Mode.SUBTRACT)

    result = part.part
    assert len(result.solids()) == 1, f"mic arm split into {len(result.solids())} solids"
    return result
