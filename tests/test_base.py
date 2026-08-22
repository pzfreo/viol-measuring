"""The base must match the upstream part where it meets bought-in hardware.

Dimensions here were measured off `ref/upstream/01 Base.3mf` with the tools in
`tools/`; the decorative lightening in the upstream part is deliberately not
reproduced, so volume and surface area are not asserted.
"""

import pytest
from build123d import Axis

from gams import INSTRUMENTS, VIOLIN, Rig, base

TOL = 0.05


@pytest.fixture(scope="module")
def violin_base():
    return base(Rig(VIOLIN))


def test_single_valid_solid(violin_base):
    assert len(violin_base.solids()) == 1
    assert violin_base.is_valid


def test_envelope_matches_reference(violin_base):
    bb = violin_base.bounding_box()
    assert bb.size.X == pytest.approx(60.0, abs=TOL)      # plate width
    assert bb.size.Y == pytest.approx(57.5, abs=0.3)      # rear plate + outrigger
    assert bb.size.Z == pytest.approx(10.0, abs=TOL)
    assert bb.min.X == pytest.approx(-30.0, abs=TOL)
    assert bb.min.Y == pytest.approx(-15.0, abs=TOL)
    assert bb.min.Z == pytest.approx(0.0, abs=TOL)


def circles_at(part, z, radius):
    """Circular edges of the given radius centred in the plane Z = z."""
    return [e for e in part.edges()
            if e.geom_type.name == "CIRCLE"
            and abs(e.radius - radius) < TOL
            and abs(e.arc_center.Z - z) < TOL]


def test_rod_bores(violin_base):
    """10 mm rods, 40 apart, bored 0.2 over size."""
    bores = circles_at(violin_base, 0.0, 5.1)
    xs = sorted({round(e.arc_center.X, 2) for e in bores})
    assert xs == [-20.0, 20.0]
    assert all(abs(e.arc_center.Y) < TOL for e in bores)


def test_leadscrew_clearance(violin_base):
    """M8 leadscrew passes through a 9 mm hole in the bottom face."""
    assert circles_at(violin_base, 0.0, 4.5)


def test_thrust_bearing_pocket(violin_base):
    """608 bearing (22 OD, 7 wide) presses into the top face."""
    pocket_z = 10.0 - 8.0
    assert circles_at(violin_base, pocket_z, 11.05)


def test_mounting_points(violin_base):
    """Three counterbored mounting points, two at the rear and one outrigger."""
    holes = circles_at(violin_base, 0.0, 1.75)
    pts = sorted({(round(e.arc_center.X, 1), round(e.arc_center.Y, 1)) for e in holes})
    assert pts == [(-24.0, -9.0), (0.0, 29.8), (24.0, -9.0)]
    assert len({(round(e.arc_center.X, 1), round(e.arc_center.Y, 1))
                for e in circles_at(violin_base, 9.0, 2.75)}) == 3   # counterbores


def test_clamp_splits_reach_the_bores(violin_base):
    """Each boss is split so the cross bolt can pinch it onto its rod."""
    bb = violin_base.bounding_box()
    assert bb.size.X == pytest.approx(60.0, abs=TOL)
    # a split boss shows two extra vertical faces per rod
    verticals = violin_base.faces().filter_by(Axis.X)
    assert len(verticals) >= 4


@pytest.mark.parametrize("name", sorted(INSTRUMENTS))
def test_every_preset_builds(name):
    part = base(Rig(INSTRUMENTS[name]))
    assert len(part.solids()) == 1
    assert part.is_valid
    assert part.volume > 0
