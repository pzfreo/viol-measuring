"""The knob and its folding handle drive the leadscrew.

Reference volumes measured from `ref/upstream/08-10*.3mf`.
"""

import pytest

from gams import INSTRUMENTS, VIOLIN, Rig, grip, handle, knob

TOL = 0.05


def test_knob_matches_reference():
    p = knob(Rig(VIOLIN))
    assert len(p.solids()) == 1 and p.is_valid
    bb = p.bounding_box()
    assert (bb.size.X, bb.size.Y, bb.size.Z) == pytest.approx((28.0, 28.0, 16.0), abs=TOL)
    assert p.volume == pytest.approx(5676.8, rel=0.03)


def test_handle_matches_reference():
    p = handle(Rig(VIOLIN))
    assert len(p.solids()) == 1 and p.is_valid
    bb = p.bounding_box()
    assert bb.size.X == pytest.approx(12.0, abs=TOL)
    assert bb.size.Y == pytest.approx(54.0, abs=TOL)
    assert p.volume == pytest.approx(1423.5, rel=0.03)


def test_grip_matches_reference():
    p = grip(Rig(VIOLIN))
    assert len(p.solids()) == 1 and p.is_valid
    assert p.bounding_box().size.Z == pytest.approx(9.0, abs=TOL)
    assert p.volume == pytest.approx(79.2, rel=0.03)


def test_handle_sockets_onto_the_knob_post():
    """The socket must clear the post it drives, or the crank will not seat."""
    rig = Rig(VIOLIN)
    socket_af = rig.knob_post_af + rig.handle_socket_fit
    assert socket_af > rig.knob_post_af
    assert socket_af - rig.knob_post_af < 0.4


def test_grip_spins_on_its_pin():
    rig = Rig(VIOLIN)
    assert rig.grip_id > rig.grip_pin_d          # free to turn
    assert rig.grip_head_d > rig.grip_id         # but retained by the head
    assert rig.grip_z + rig.grip_h <= rig.grip_pin_h  # and clear of it


@pytest.mark.parametrize("name", sorted(INSTRUMENTS))
def test_every_preset_builds(name):
    rig = Rig(INSTRUMENTS[name])
    for fn in (knob, handle, grip):
        p = fn(rig)
        assert len(p.solids()) == 1 and p.is_valid
