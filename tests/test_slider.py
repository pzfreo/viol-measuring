"""The slider carries the arm, so its dimensions set where the hammer lands.

Measured off `ref/upstream/03 Slider.3mf`, which sits at Z 95..124 in the
assembly frame; the part is built with Z from 0 up.
"""

import pytest

from gams import INSTRUMENTS, VIOLIN, Rig, slider

TOL = 0.05


@pytest.fixture(scope="module")
def violin_slider():
    return slider(Rig(VIOLIN))


def test_single_valid_solid(violin_slider):
    assert len(violin_slider.solids()) == 1
    assert violin_slider.is_valid


def test_envelope(violin_slider):
    """70 wide, 29 tall — the height is the linear bearing's own length."""
    bb = violin_slider.bounding_box()
    assert bb.size.X == pytest.approx(70.0, abs=TOL)
    assert bb.size.Z == pytest.approx(29.0, abs=TOL)
    assert bb.min.Y == pytest.approx(-15.0, abs=TOL)


def test_bearing_bores_are_a_press_fit(violin_slider):
    """LM10UU is 19.0 OD and goes in with no clearance."""
    bores = [e for e in violin_slider.edges()
             if e.geom_type.name == "CIRCLE" and abs(e.radius - 9.5) < TOL]
    xs = sorted({round(e.arc_center.X, 1) for e in bores})
    assert xs == [-20.0, 20.0]


def test_hammer_hangs_on_the_instrument_centreline(violin_slider):
    """The pivot sits at the rig's reach — half the lower bout, plus clearance."""
    rig = Rig(VIOLIN)
    pivots = [e for e in violin_slider.edges()
              if e.geom_type.name == "CIRCLE"
              and abs(e.radius - rig.pivot_d / 2) < TOL]
    assert pivots
    assert all(abs(e.arc_center.Y - rig.pivot_y) < 0.5 for e in pivots)


def test_matches_reference_volume(violin_slider):
    """Still coarse: the arm's internal geometry is not fully recovered."""
    assert violin_slider.volume == pytest.approx(29652.7, rel=0.15)


@pytest.mark.parametrize("name", sorted(INSTRUMENTS))
def test_every_preset_builds(name):
    part = slider(Rig(INSTRUMENTS[name]))
    assert len(part.solids()) == 1
    assert part.is_valid
