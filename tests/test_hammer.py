"""07 Hammer — the pendulum that delivers the impulse.

Its length is the rig's `hammer_drop`, so the head lands on the tap point when
the slider is at its measured height. Reference volume from
`ref/upstream/07 Hammer.3mf`.
"""

import math

import pytest

from gams import INSTRUMENTS, VIOLIN, Rig, hammer, handheld_hammer

TOL = 0.05


def test_matches_reference():
    p = hammer(Rig(VIOLIN))
    assert len(p.solids()) == 1 and p.is_valid
    bb = p.bounding_box()
    assert (bb.size.X, bb.size.Y) == pytest.approx((12.0, 6.0), abs=0.1)
    assert p.volume == pytest.approx(1684.7, rel=0.03)


def test_length_is_the_pendulum_drop():
    """Head to pivot is what puts the tap point at the belly."""
    rig = Rig(VIOLIN)
    assert hammer(rig).bounding_box().size.Z == pytest.approx(rig.hammer_drop, abs=0.1)


def test_fits_the_slider_fork():
    """The shaft has to swing freely in the fork it hangs from."""
    rig = Rig(VIOLIN)
    assert rig.hammer_tip_d <= rig.fork_gap
    assert rig.hammer_depth <= rig.fork_gap


def test_head_is_the_widest_part():
    """The mass belongs at the striking end, not up by the pin."""
    rig = Rig(VIOLIN)
    assert rig.hammer_head_d > rig.hammer_tip_d
    assert rig.hammer_head_z < rig.hammer_drop / 4


def test_flank_arc_is_tangent_to_both_ends():
    """Luca Jost's outline is one R200 arc touching both round ends.

    Tangency is what makes the taper smooth rather than kinked, and it is the
    reason the flank centre is derived rather than typed in.
    """
    rig = Rig(VIOLIN)
    fx, fz = rig.hammer_flank
    R = rig.hammer_flank_r
    for centre_z, d in ((rig.hammer_head_z, rig.hammer_head_d),
                        (rig.hammer_tip_z, rig.hammer_tip_d)):
        assert math.hypot(fx, fz - centre_z) == pytest.approx(R + d / 2, abs=1e-6)


def test_handheld_matches_reference():
    p = handheld_hammer(Rig(VIOLIN))
    assert len(p.solids()) == 1 and p.is_valid
    assert p.volume == pytest.approx(1766.1, rel=0.03)


def test_handheld_has_no_pivot_slot():
    """It is tapped by hand, so nothing hangs it — and it is the heavier for it."""
    rig = Rig(VIOLIN)
    assert handheld_hammer(rig).volume > hammer(rig).volume


@pytest.mark.parametrize("name", sorted(INSTRUMENTS))
def test_every_preset_builds(name):
    for fn in (hammer, handheld_hammer):
        p = fn(Rig(INSTRUMENTS[name]))
        assert len(p.solids()) == 1 and p.is_valid
