"""The two parts that clip onto the guide rods.

Both use the same C-ring: bore on the rod, wall 1.25, cut off flat where it
springs over. Reference volumes measured from `ref/upstream/04*.3mf` and
`06*.3mf`.
"""

import pytest

from gams import INSTRUMENTS, VIOLIN, Rig, clip, holder

TOL = 0.05


def test_clip_matches_reference():
    p = clip(Rig(VIOLIN))
    assert len(p.solids()) == 1 and p.is_valid
    bb = p.bounding_box()
    assert (bb.size.X, bb.size.Y, bb.size.Z) == pytest.approx((12.5, 15.5, 15.0), abs=TOL)
    assert p.volume == pytest.approx(558.5, rel=0.03)


def test_holder_matches_reference():
    p = holder(Rig(VIOLIN))
    assert len(p.solids()) == 1 and p.is_valid
    bb = p.bounding_box()
    assert (bb.size.X, bb.size.Y, bb.size.Z) == pytest.approx((52.5, 48.63, 18.0), abs=TOL)
    assert p.volume == pytest.approx(4500.2, rel=0.03)


def test_both_clip_the_same_rod():
    """Clip and holder share one bore size — the guide rod they both grip."""
    rig = Rig(VIOLIN)
    for part in (clip(rig), holder(rig)):
        bores = [e for e in part.edges()
                 if e.geom_type.name == "CIRCLE"
                 and abs(e.radius - rig.hw.rod_d / 2) < TOL]
        assert bores, "no bore matching the guide rod"


def test_holder_spans_both_rods():
    rig = Rig(VIOLIN)
    xs = sorted({round(e.arc_center.X, 1) for e in holder(rig).edges()
                 if e.geom_type.name == "CIRCLE"
                 and abs(e.radius - rig.hw.rod_d / 2) < TOL})
    assert xs == [-rig.rod_x, rig.rod_x]


def test_mic_channel_takes_the_electret():
    """The 6 mm electret has to drop into the fins with a little clearance."""
    rig = Rig(VIOLIN)
    assert 6.0 < rig.mic_channel_w < 6.6


@pytest.mark.parametrize("name", sorted(INSTRUMENTS))
def test_every_preset_builds(name):
    rig = Rig(INSTRUMENTS[name])
    for fn in (clip, holder):
        p = fn(rig)
        assert len(p.solids()) == 1 and p.is_valid
