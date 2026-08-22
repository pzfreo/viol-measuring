"""Parametric rebuild of the General Acoustic Measurement Setup."""

from .params import (
    BASS_VIOL, TENOR_VIOL, TREBLE_VIOL, VIOLA, VIOLIN, INSTRUMENTS,
    Fits, Hardware, Instrument, Rig,
)
from .base import base
from .top import top
from .slider import slider
from .knob import knob
from .handle import grip, handle
from .clip import clip
from .holder import holder

__all__ = [
    "BASS_VIOL", "TENOR_VIOL", "TREBLE_VIOL", "VIOLA", "VIOLIN", "INSTRUMENTS",
    "Fits", "Hardware", "Instrument", "Rig", "base", "top", "slider", "knob", "handle", "grip", "clip", "holder",
]
