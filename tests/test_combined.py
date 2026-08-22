"""One rig serving more than one instrument.

A bass viol and a cello need the same column, rods, leadscrew and plates. They
differ in exactly one thing the assembled rig cannot already adjust: 30 mm of
hammer reach. Everything else is a setting — tap height is the crank, the
microphone arm slides in its fins, and the holder clips anywhere on the rods.
"""

import pytest

from gams import BASS_VIOL, CELLO, VIOLIN, Rig, assembly, slider

TOL = 0.05


@pytest.fixture(scope="module")
def both():
    return Rig.covering(BASS_VIOL, CELLO)


def test_it_is_built_for_the_larger_instrument(both):
    assert both.instrument is CELLO
    assert both.covers == (CELLO, BASS_VIOL)
    assert both.reach == Rig(CELLO).reach


def test_the_column_is_the_same_for_both():
    """If these differed, one rig could not serve both."""
    b, c = Rig(BASS_VIOL), Rig(CELLO)
    for attr in ("rod_length", "rod_spacing", "plate_width", "plate_depth",
                 "carriage_w", "tube_od", "knob_d", "handle_len"):
        assert getattr(b, attr) == pytest.approx(getattr(c, attr), abs=TOL), attr
    assert b.hw.rod_d == c.hw.rod_d
    assert b.hw.screw_d == c.hw.screw_d


def test_there_is_a_pivot_for_each_instrument(both):
    assert both.pivot_reaches == (Rig(BASS_VIOL).reach, Rig(CELLO).reach)
    pins = sorted({round(e.arc_center.Y, 1) for e in slider(both).edges()
                   if e.geom_type.name == "CIRCLE"
                   and abs(e.radius - both.pivot_d / 2) < TOL})
    assert pins == [round(r, 1) for r in both.pivot_reaches]


@pytest.mark.parametrize("inst", [BASS_VIOL, CELLO])
def test_each_pivot_lands_on_that_instrument(both, inst):
    """Pin the hammer for an instrument and its head must reach that belly."""
    own = Rig(inst)
    parts = {c.label: c for c in assembly(both, at_reach=own.reach).children}
    head = parts["07_hammer"].bounding_box()
    assert head.min.Z == pytest.approx(own.tap_height, abs=0.1)
    assert head.center().Y == pytest.approx(own.reach, abs=0.5)


def test_asking_for_a_reach_it_has_no_pivot_for_is_an_error(both):
    with pytest.raises(ValueError, match="no pivot"):
        assembly(both, at_reach=205.0)


def test_a_single_instrument_rig_is_unchanged():
    """Covering one instrument must build exactly what it did before."""
    assert Rig.covering(VIOLIN).pivot_reaches == (Rig(VIOLIN).reach,)
    assert slider(Rig.covering(VIOLIN)).volume == pytest.approx(
        slider(Rig(VIOLIN)).volume, rel=1e-9)


def test_every_part_builds_for_the_combined_rig(both):
    from gams import base, clip, grip, handle, holder, knob, mic_arm, top
    for fn in (base, top, slider, holder, mic_arm, clip, knob, handle, grip):
        part = fn(both)
        assert len(part.solids()) == 1 and part.is_valid
