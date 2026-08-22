"""05 Microphone arm.

Clamps to the column and reaches out and down to put the microphone beside the
instrument, with the cable running inside it. Reference from
`ref/upstream/05 Microphone arm.3mf`.
"""

import pytest

from gams import INSTRUMENTS, VIOLIN, Rig, mic_arm

TOL = 0.1


def test_matches_reference():
    p = mic_arm(Rig(VIOLIN))
    assert len(p.solids()) == 1 and p.is_valid
    bb = p.bounding_box()
    assert bb.size.X == pytest.approx(6.25, abs=TOL)
    assert bb.size.Y == pytest.approx(118.99, abs=TOL)
    assert bb.size.Z == pytest.approx(43.70, abs=TOL)
    assert p.volume == pytest.approx(2193.6, rel=0.03)


def test_reaches_the_microphone_position():
    """The tip has to land where the rig says the microphone goes."""
    rig = Rig(VIOLIN)
    bb = mic_arm(rig).bounding_box()
    assert bb.max.Y == pytest.approx(rig.mic_reach, abs=0.5)
    assert bb.min.Z == pytest.approx(rig.mic_arm_tip_z - rig.mic_arm_t / 2, abs=0.2)


def test_cable_runs_inside_it():
    """A lead flapping in free air would damp what we are measuring."""
    rig = Rig(VIOLIN)
    assert rig.mic_channel_d < rig.mic_arm_w
    assert rig.mic_channel_h < rig.mic_arm_t
    solid_section = rig.mic_arm_w * rig.mic_arm_t
    assert rig.mic_channel_d * rig.mic_channel_h < solid_section / 2


@pytest.mark.parametrize("name", sorted(INSTRUMENTS))
def test_every_preset_builds(name):
    p = mic_arm(Rig(INSTRUMENTS[name]))
    assert len(p.solids()) == 1 and p.is_valid
