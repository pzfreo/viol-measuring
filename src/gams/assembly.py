"""The whole rig, assembled.

The upstream `.3mf` files all share one coordinate frame — base at Z 0, the
microphone holder at 49.5, the slider at 95, the top plate at 190, the knob at
202 — so the assembly is just each part placed at the offset the reference
already implies.  Z is the column axis, +Y reaches out over the instrument, and
the bench top is Z 0.
"""

from build123d import Color, Compound, Cylinder, Location, Align

from .base import base
from .clip import clip
from .hammer import hammer
from .handle import grip, handle
from .holder import holder
from .knob import knob
from .mic_arm import mic_arm
from .params import Rig
from .slider import slider
from .top import top

# (label, builder, placement) — placement takes the rig and returns a Location.
PRINTED = (
    ("01_base", base, lambda r: Location((0, 0, 0))),
    ("02_top", top, lambda r: Location((0, 0, r.rod_length - r.plate_t))),
    ("03_slider", slider, lambda r: Location((0, 0, r.slider_z))),
    ("04_microphone_holder", holder, lambda r: Location((0, 0, r.holder_z))),
    ("05_microphone_arm", mic_arm, lambda r: Location((0, 0, 0))),
    ("06_cable_clip", clip, lambda r: Location((r.rod_x, 0, r.clip_z))),
    ("07_hammer", hammer,
     lambda r: Location((0, r.pivot_y, r.slider_z + r.plate_t / 2 - r.hammer_pivot_drop))),
    ("08_knob", knob, lambda r: Location((0, 0, r.knob_z))),
    ("09_knobhandle", handle, lambda r: Location((0, 0, r.knob_z + r.knob_h + r.knob_boss_h))),
    ("10_knobhandleknurl", grip,
     lambda r: Location((0, -r.handle_len, r.knob_z + r.knob_h + r.knob_boss_h + r.grip_z))),
)


def _bought_in(rig: Rig):
    """The rods, leadscrew and bearings — not printed, but they set the fits."""
    hw = rig.hw
    parts = []

    for sign in (1, -1):
        rod = Cylinder(hw.rod_d / 2, rig.rod_length,
                       align=(Align.CENTER, Align.CENTER, Align.MIN))
        rod.label = f"guide_rod_{'a' if sign > 0 else 'b'}"
        parts.append(rod.moved(Location((sign * rig.rod_x, 0, 0))))

    screw_len = rig.knob_z + rig.knob_bore_h + rig.knob_nut_h
    screw = Cylinder(hw.screw_d / 2, screw_len,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
    screw.label = "leadscrew"
    parts.append(screw)

    for sign in (1, -1):
        b = Cylinder(hw.bearing_od / 2, hw.bearing_len,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
        b.label = f"linear_bearing_{'a' if sign > 0 else 'b'}"
        parts.append(b.moved(Location((sign * rig.rod_x, 0, rig.slider_z))))

    for label, z in (("thrust_bearing_lower", rig.plate_t - hw.thrust_len),
                     ("thrust_bearing_upper", rig.rod_length - rig.plate_t)):
        b = Cylinder(hw.thrust_od / 2, hw.thrust_len,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
        b.label = label
        parts.append(b.moved(Location((0, 0, z))))

    return parts


def assembly(rig: Rig, hardware: bool = True):
    """The complete rig as a labelled Compound, ready to export as STEP."""
    children = []
    for label, builder, place in PRINTED:
        part = builder(rig).moved(place(rig))
        part.label = label
        part.color = Color(0.45, 0.62, 0.85)
        children.append(part)

    if hardware:
        for part in _bought_in(rig):
            part.color = Color(0.72, 0.72, 0.75)
            children.append(part)

    asm = Compound(children=children)
    asm.label = f"gams_{rig.instrument.name.replace(' ', '_')}"
    return asm
