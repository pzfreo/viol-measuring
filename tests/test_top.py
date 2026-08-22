"""The top plate shares the base's plate geometry, mirrored where it must be.

Dimensions measured off `ref/upstream/02 Top.3mf`, which sits at Z 190..200 in
the assembly frame; the part itself is built with Z from 0 up.
"""

import pytest

from gams import INSTRUMENTS, VIOLIN, Rig, top

TOL = 0.05


@pytest.fixture(scope="module")
def violin_top():
    return top(Rig(VIOLIN))


def circles_at(part, z, radius):
    return [e for e in part.edges()
            if e.geom_type.name == "CIRCLE"
            and abs(e.radius - radius) < TOL
            and abs(e.arc_center.Z - z) < TOL]


def test_single_valid_solid(violin_top):
    assert len(violin_top.solids()) == 1
    assert violin_top.is_valid


def test_envelope(violin_top):
    bb = violin_top.bounding_box()
    assert (bb.size.X, bb.size.Y, bb.size.Z) == pytest.approx((60.0, 30.0, 10.0), abs=TOL)


def test_no_outrigger_or_mounting_points(violin_top):
    """The top carries no feet — those belong to the base alone."""
    assert violin_top.bounding_box().max.Y == pytest.approx(15.0, abs=TOL)
    assert not circles_at(violin_top, 0.0, 1.75)


def test_rod_bores(violin_top):
    xs = sorted({round(e.arc_center.X, 2) for e in circles_at(violin_top, 0.0, 5.1)})
    assert xs == [-20.0, 20.0]


def test_seat_opens_downwards(violin_top):
    """The bearing seat is cut from the underside, 7 deep."""
    assert circles_at(violin_top, 7.0, 13.0)


def test_matches_reference_volume(violin_top):
    assert violin_top.volume == pytest.approx(10650.4, rel=0.01)


@pytest.mark.parametrize("name", sorted(INSTRUMENTS))
def test_every_preset_builds(name):
    part = top(Rig(INSTRUMENTS[name]))
    assert len(part.solids()) == 1
    assert part.is_valid
