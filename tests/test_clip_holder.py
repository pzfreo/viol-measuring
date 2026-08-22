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


def test_fins_grip_the_microphone_arm():
    """The fins take the arm, not the microphone — that is the fit the upstream
    part set ships +/-0.15 mm variants of."""
    rig = Rig(VIOLIN)
    assert rig.arm_slot_w > rig.mic_arm_w          # the arm goes in
    assert rig.arm_slot_w - rig.mic_arm_w < 0.35   # but not sloppily


@pytest.mark.parametrize("name", sorted(INSTRUMENTS))
def test_every_preset_builds(name):
    rig = Rig(INSTRUMENTS[name])
    for fn in (clip, holder):
        p = fn(rig)
        assert len(p.solids()) == 1 and p.is_valid


def test_assembly_has_no_interference():
    """Every printed part must clear every other where the rig is assembled."""
    from itertools import combinations

    from gams import assembly

    kids = list(assembly(Rig(VIOLIN), hardware=False).children)
    assert len(kids) == 10
    for a, b in combinations(kids, 2):
        overlap = a & b
        vol = getattr(overlap, "volume", 0.0)
        assert vol < 0.5, f"{a.label} interferes with {b.label}: {vol:.1f} mm3"


def test_assembly_puts_the_hammer_on_the_tap_point():
    """The whole column height exists to land the head on the belly."""
    from gams import assembly

    rig = Rig(VIOLIN)
    kids = {c.label: c for c in assembly(rig, hardware=False).children}
    head_z = kids["07_hammer"].bounding_box().min.Z
    assert head_z == pytest.approx(rig.tap_height, abs=0.1)
    assert kids["07_hammer"].bounding_box().center().Y == pytest.approx(rig.pivot_y, abs=0.5)
