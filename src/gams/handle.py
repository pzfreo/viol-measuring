"""09 Knobhandle and 10 Knobhandleknurl — the folding crank.

The arm sockets onto the hex post on top of the knob; a pin at its far end
carries a sleeve that spins freely, so your fingers stay put while the knob
turns.  The sleeve is retained by a small flange on the pin.
"""

import math

from build123d import (
    Align, BuildPart, BuildSketch, Circle, Cylinder, Locations, Mode, Plane,
    PolarLocations, Polygon, RegularPolygon, extrude,
)

from .params import Rig


def handle(rig: Rig):
    """The crank arm, in its own frame with Z from 0 up and the socket at X=Y=0."""
    with BuildPart() as part:
        # the arm is the outline wrapped round a big boss at the socket and a
        # small one at the pin — tangent flanks, not a parallel bar
        r1, r2, L = rig.handle_w / 2, rig.handle_tip_w / 2, rig.handle_len
        psi = math.asin((r2 - r1) / L)
        t1 = (r1 * math.cos(psi), r1 * math.sin(psi))
        t2 = (r2 * math.cos(psi), -L + r2 * math.sin(psi))
        with BuildSketch(mode=Mode.PRIVATE) as sk:
            Circle(r1)
            with Locations((0, -L)):
                Circle(r2)
            Polygon(t1, t2, (-t2[0], t2[1]), (-t1[0], t1[1]), align=None)
        extrude(to_extrude=sk.sketch, amount=rig.handle_t)

        af = (rig.knob_post_af + rig.handle_socket_fit) / 2 / math.cos(math.radians(30))
        with BuildSketch(mode=Mode.PRIVATE) as socket:
            RegularPolygon(af, 6, major_radius=True, rotation=90)
        extrude(to_extrude=socket.sketch, amount=rig.handle_t, mode=Mode.SUBTRACT)

        with Locations((0, -rig.handle_len, 0)):
            Cylinder(rig.grip_pin_d / 2, rig.grip_pin_h,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, -rig.handle_len, rig.grip_pin_h - rig.grip_flange_h)):
            Cylinder(rig.grip_flange_d / 2, rig.grip_flange_h,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))

    result = part.part
    assert len(result.solids()) == 1, f"handle split into {len(result.solids())} solids"
    return result


def grip(rig: Rig):
    """The knurled sleeve, in its own frame with Z from 0 up."""
    with BuildPart() as part:
        Cylinder(rig.grip_od / 2, rig.grip_h,
                 align=(Align.CENTER, Align.CENTER, Align.MIN))
        with PolarLocations(rig.grip_od / 2, rig.grip_flutes):
            Cylinder(rig.grip_flute_d / 2, rig.grip_h,
                     align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        Cylinder(rig.grip_id / 2, rig.grip_h,
                 align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    result = part.part
    assert len(result.solids()) == 1, f"grip split into {len(result.solids())} solids"
    return result
