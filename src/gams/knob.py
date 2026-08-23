"""08 Knob — the handwheel that drives the leadscrew.

An M8 nut is trapped in its underside, so turning the knob raises and lowers
the slider.  The knurled rim is what you actually grip; the hex post on top
takes the folding handle.
"""

import math

from build123d import (
    Align, Axis, BuildPart, BuildSketch, Circle, Cylinder, Locations, Mode,
    Plane, PolarLocations, RegularPolygon, extrude, fillet,
)

from .params import Rig, nut


def knob(rig: Rig):
    """Build the leadscrew knob for `rig`, in its own frame with Z from 0 up."""
    hw = rig.hw
    body_r = hw.screw_d * rig.knob_d_frac / 2
    nut_af, _ = nut(hw.screw_d)

    with BuildPart() as part:
        Cylinder(body_r, rig.knob_h, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # knurl the upper rim: cut flutes rather than add teeth, so the
        # nominal diameter stays the one you measure.  The cutter is far
        # bigger than the cut is deep, which is what makes each flute a broad
        # scallop your finger sits in rather than a groove it catches on.
        with Locations((0, 0, rig.knurl_from)):
            with PolarLocations(body_r + rig.knurl_cutter_r - rig.knurl_depth,
                                rig.knurl_teeth):
                Cylinder(rig.knurl_cutter_r, rig.knob_h - rig.knurl_from,
                         align=(Align.CENTER, Align.CENTER, Align.MIN),
                         mode=Mode.SUBTRACT)
        if rig.knurl_crest_r:
            # break the ridge between flutes, so the grip has no sharp arris
            crest = [e for e in part.part.edges().filter_by(Axis.Z)
                     if abs(math.hypot(e.center().X, e.center().Y) - body_r) < 0.02]
            fillet(crest, rig.knurl_crest_r)

        with Locations((0, 0, rig.knob_h)):
            Cylinder(rig.knob_boss_d / 2, rig.knob_boss_h,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildSketch(Plane.XY.offset(rig.knob_h + rig.knob_boss_h),
                         mode=Mode.PRIVATE) as post:
            RegularPolygon(rig.knob_post_af / 2 / math.cos(math.radians(30)), 6,
                           major_radius=True, rotation=90)
        extrude(to_extrude=post.sketch, amount=rig.knob_post_h)

        # leadscrew clearance, then the captive nut above it
        Cylinder((hw.screw_d + rig.fits.screw_clear) / 2, rig.knob_bore_h,
                 align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        af = (nut_af + rig.hex_fit) / 2 / math.cos(math.radians(30))
        with BuildSketch(Plane.XY.offset(rig.knob_bore_h), mode=Mode.PRIVATE) as trap:
            RegularPolygon(af, 6, major_radius=True, rotation=90)
        extrude(to_extrude=trap.sketch, amount=rig.knob_nut_h, mode=Mode.SUBTRACT)

    result = part.part
    assert len(result.solids()) == 1, f"knob split into {len(result.solids())} solids"
    return result
