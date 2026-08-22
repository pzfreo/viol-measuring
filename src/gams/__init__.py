"""Parametric rebuild of the General Acoustic Measurement Setup."""

from .params import (
    BASS_VIOL, TENOR_VIOL, TREBLE_VIOL, VIOLA, VIOLIN, INSTRUMENTS,
    Fits, Hardware, Instrument, Rig,
)
from .base import base

__all__ = [
    "BASS_VIOL", "TENOR_VIOL", "TREBLE_VIOL", "VIOLA", "VIOLIN", "INSTRUMENTS",
    "Fits", "Hardware", "Instrument", "Rig", "base",
]
