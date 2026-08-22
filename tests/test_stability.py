"""Will it stand up?

The rig cantilevers a long arm out over the instrument, so where the centre of
gravity lands relative to the three mounting points is a design constraint, not
an afterthought. These tests guard the outrigger's scaling: the gamba presets
reach much further out, and the foot has to keep up.
"""

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))

from stability import cog, margin_to_edges, support_polygon, tipping_loads  # noqa: E402

from gams import BASS_VIOL, INSTRUMENTS, VIOLIN, Rig  # noqa: E402


def worst_margin(rig):
    mass, (cx, cy, _), _ = cog(rig)
    return mass, min(m for _, m in margin_to_edges((cx, cy), support_polygon(rig)))


@pytest.mark.parametrize("name", sorted(INSTRUMENTS))
def test_centre_of_gravity_is_over_the_feet(name):
    """Static balance, before anything is leaned on."""
    _, margin = worst_margin(Rig(INSTRUMENTS[name]))
    assert margin > 5.0, f"{name}: only {margin:.1f} mm from tipping"


def test_the_outrigger_keeps_up_with_the_reach():
    """A bass viol reaches nearly twice as far out as a violin.

    The foot scales with reach, so the bigger rig must not end up closer to
    tipping than the smaller one — which is what would happen if the outrigger
    were left at a fixed length.
    """
    _, violin = worst_margin(Rig(VIOLIN))
    _, bass = worst_margin(Rig(BASS_VIOL))
    assert bass > violin


def test_it_is_not_a_free_standing_rig():
    """Records the load that tips it — the reason the base is bolted down.

    Both the violin preset (which reproduces upstream) and the bass viol tip
    under loads you would apply by resting a hand on the arm. The three
    counterbored M3 holes in the base are what stops that, and this test exists
    so nobody later mistakes the positive static margin above for adequacy.
    """
    for inst in (VIOLIN, BASS_VIOL):
        rig = Rig(inst)
        mass, (cx, cy, _), _ = cog(rig)
        loads = tipping_loads(rig, mass, (cx, cy))
        assert loads["down on the arm tip"] < 2.0, (
            "free-standing tipping load has changed — if the rig is now stable "
            "unbolted, revisit the note in NOTES.md"
        )
