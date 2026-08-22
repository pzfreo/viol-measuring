"""Parameters for the acoustic measurement rig.

The rig is a vertical column standing on the bench beside an instrument that
lies on its back.  A slider on the column carries an arm reaching out over the
instrument; an impulse hammer hangs from the end of that arm, and a second,
lower arm carries the microphone.

Every rig dimension below derives from the instrument being measured.  The
upstream GAMS parts were dimensioned for a violin, and reading them back
recovers the relationships used here (upstream value in brackets):

    tap height   = rib depth + belly arching        30 + 15 = 45   [49.0]
    hammer reach = lower bout / 2 + column gap     208 / 2 + 2 = 106  [106.5]
    mic height   = rib depth / 2                        30 / 2 = 15   [~16]
    mic reach    = hammer reach + mic overhang        106 + 28 = 134  [133.7]

so `Rig(VIOLIN)` reproduces the upstream geometry, and the gamba presets follow
from the same rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Optional

MM = 1.0


# --------------------------------------------------------------------------
# Instruments
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Instrument:
    """The dimensions of the instrument that drive the rig.

    Measured with the instrument on its back on the bench: `rib_depth` is the
    rib height at the lower bout and `arching` the height of the belly above
    the ribs, so `rib_depth + arching` is how far the tap point sits above the
    bench.
    """

    name: str
    body_length: float      # top block to bottom block, along the belly
    rib_depth: float        # rib height at the lower bout
    arching: float          # belly crown above the rib line
    lower_bout: float       # widest point of the lower bout

    @property
    def tap_height(self) -> float:
        """Height of the belly above the bench."""
        return self.rib_depth + self.arching

    @property
    def half_bout(self) -> float:
        return self.lower_bout / 2


# Violin-family figures are standard; the viol figures are mid-range for
# surviving consort instruments, which vary far more than the violin family.
VIOLIN = Instrument("violin", body_length=355, rib_depth=30, arching=15, lower_bout=208)
VIOLA = Instrument("viola", body_length=410, rib_depth=34, arching=16, lower_bout=240)
TREBLE_VIOL = Instrument("treble viol", body_length=370, rib_depth=62, arching=18, lower_bout=230)
TENOR_VIOL = Instrument("tenor viol", body_length=490, rib_depth=88, arching=20, lower_bout=290)
BASS_VIOL = Instrument("bass viol", body_length=660, rib_depth=125, arching=22, lower_bout=380)

INSTRUMENTS = {i.name: i for i in (VIOLIN, VIOLA, TREBLE_VIOL, TENOR_VIOL, BASS_VIOL)}


# --------------------------------------------------------------------------
# Hardware
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Hardware:
    """Bought-in parts.  Sizes step up with reach to keep the column stiff."""

    rod_d: float             # guide rod diameter
    bearing_od: float        # linear bearing outer diameter
    bearing_len: float       # linear bearing length
    screw_d: float           # leadscrew major diameter
    thrust_od: float         # leadscrew thrust bearing outer diameter
    thrust_len: float        # leadscrew thrust bearing width
    clamp_bolt: float        # rod clamp bolt (M-size)
    grub: float              # arm clamp grub screw (M-size)

    @property
    def rod_r(self) -> float:
        return self.rod_d / 2


# 10 mm rods / M8 / 608 bearings is the upstream hardware.
HW_10_M8 = Hardware(rod_d=10, bearing_od=19, bearing_len=29, screw_d=8,
                    thrust_od=22, thrust_len=7, clamp_bolt=4, grub=4)
HW_12_M10 = Hardware(rod_d=12, bearing_od=21, bearing_len=30, screw_d=10,
                     thrust_od=26, thrust_len=8, clamp_bolt=4, grub=4)
HW_16_M10 = Hardware(rod_d=16, bearing_od=28, bearing_len=37, screw_d=10,
                     thrust_od=30, thrust_len=9, clamp_bolt=5, grub=5)

# Reach at which each step becomes necessary.  A printed cantilever on 10 mm
# rods is already marginal at the violin's 106 mm; beyond that the column
# deflects enough to move the tap point between taps.
HARDWARE_LADDER = ((120, HW_10_M8), (180, HW_12_M10), (float("inf"), HW_16_M10))


# Across-flats and thickness for ISO 4032 hex nuts, by thread size.
NUT = {3: (5.5, 2.4), 4: (7.0, 3.2), 5: (8.0, 4.0), 6: (10.0, 5.0), 8: (13.0, 6.5)}


def nut(m: float) -> tuple:
    """(across_flats, thickness) for an M`m` hex nut."""
    return NUT[int(m)]


def hardware_for_reach(reach: float) -> Hardware:
    for limit, hw in HARDWARE_LADDER:
        if reach <= limit:
            return hw
    raise AssertionError("ladder must end in inf")


# --------------------------------------------------------------------------
# Rig
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Fits:
    """Printing clearances, applied to bores that take a bought-in part.

    Replaces the upstream ``Microphone arm/`` +/-0.15 mm model variants: tune
    these once for your printer rather than reprinting a different model.
    """

    rod_bore: float = 0.20        # guide rod through a clamped boss
    bearing_pocket: float = 0.10  # press fit, wants to be tight
    screw_clear: float = 1.00     # leadscrew clearance hole
    bolt_clear: float = 0.30      # bolt clearance hole
    slide: float = 0.25           # sliding fit, e.g. the mic arm in its clamp


@dataclass(frozen=True)
class Rig:
    """A complete rig, derived from the instrument it must measure."""

    instrument: Instrument
    hardware: Optional[Hardware] = None
    fits: Fits = field(default_factory=Fits)

    # --- geometry the design fixes rather than derives (mm) ---
    column_gap: float = 2.0        # column face to the edge of the lower bout
    mic_overhang: float = 28.0     # how far past the tap point the mic reaches
    hammer_drop: float = 55.5      # pivot to head, i.e. the pendulum length
    plate_t: float = 10.0          # base and top plate thickness
    wall: float = 5.0              # material around a bore
    stock_rod_step: float = 50.0   # guide rod stock comes in multiples of this
    headroom: float = 30.0         # slider travel above the highest tap point

    # --- clamped joints ---
    slit_w: float = 1.20           # radial split that lets a boss pinch its rod
    jaw_wall: float = 1.20         # material between the slit and the nut pocket
    nut_fit: float = 0.30
    teardrop_k: float = 1.32       # printable hole apex, in units of bolt radius

    # --- base plate ---
    corner_r: float = 5.0
    neck_blend_r: float = 8.0
    mount_d: float = 3.5           # M3 clearance for the three mounting points
    mount_cbore_d: float = 5.5
    mount_cbore_t: float = 1.0
    mount_inset: float = 6.0
    lobe_reach_frac: float = 0.28  # outrigger reach, as a fraction of arm reach
    neck_frac: float = 0.75        # outrigger neck width, as a fraction of the lobe

    # --- derived ---

    @property
    def hw(self) -> Hardware:
        return self.hardware or hardware_for_reach(self.reach)

    @property
    def reach(self) -> float:
        """Column axis to tap point, i.e. to the instrument centreline."""
        return self.instrument.half_bout + self.column_gap

    @property
    def tap_height(self) -> float:
        return self.instrument.tap_height

    @property
    def mic_reach(self) -> float:
        return self.reach + self.mic_overhang

    @property
    def mic_height(self) -> float:
        return self.instrument.rib_depth / 2

    @property
    def rod_spacing(self) -> float:
        """Centre distance between the two guide rods."""
        return 4 * self.hw.rod_d

    @property
    def wall_t(self) -> float:
        """Material around a guide rod bore.  Grows with the rod it carries."""
        return max(self.wall, 0.5 * self.hw.rod_d)

    @property
    def boss_r(self) -> float:
        """Outer radius of a boss carrying a guide rod."""
        return self.hw.rod_r + self.wall_t

    @property
    def plate_depth(self) -> float:
        """Depth of the rear plate, Y = -plate_depth/2 .. +plate_depth/2."""
        return 2 * self.boss_r + 10.0

    @property
    def lobe_r(self) -> float:
        return self.mount_cbore_d / 2 + 2 * self.wall_t

    @property
    def lobe_y(self) -> float:
        """Outrigger foot centre.  Must stay ahead of the arm's overturning moment."""
        return max(self.plate_depth / 2 + self.lobe_r + 2,
                   self.reach * self.lobe_reach_frac)

    @property
    def rod_bore_r(self) -> float:
        return (self.hw.rod_d + self.fits.rod_bore) / 2

    @property
    def rod_x(self) -> float:
        return self.rod_spacing / 2

    @property
    def plate_width(self) -> float:
        return self.rod_spacing + 2 * self.boss_r

    @property
    def pivot_height(self) -> float:
        """Height of the hammer pivot when the head is at the tap point."""
        return self.tap_height + self.hammer_drop

    @property
    def slider_h(self) -> float:
        return self.hw.bearing_len

    @property
    def rod_length(self) -> float:
        """Guide rod length, rounded up to a stock multiple."""
        need = (self.pivot_height + self.slider_h + self.plate_t
                + self.headroom)
        step = self.stock_rod_step
        return step * (int(need / step) + (1 if need % step else 0))

    @property
    def column_height(self) -> float:
        """Bench to the top of the top plate."""
        return self.rod_length

    def for_instrument(self, instrument: Instrument) -> "Rig":
        return replace(self, instrument=instrument)

    def summary(self) -> str:
        i, hw = self.instrument, self.hw
        return "\n".join([
            f"{i.name}: body {i.body_length:.0f}, ribs {i.rib_depth:.0f},"
            f" bout {i.lower_bout:.0f}",
            f"  tap point      {self.reach:7.1f} out, {self.tap_height:6.1f} up",
            f"  microphone     {self.mic_reach:7.1f} out, {self.mic_height:6.1f} up",
            f"  hammer pivot   {self.pivot_height:7.1f} up",
            f"  rods           {hw.rod_d:.0f} mm dia,"
            f" {self.rod_spacing:.0f} apart, {self.rod_length:.0f} long",
            f"  leadscrew      M{hw.screw_d:.0f}",
            f"  plate          {self.plate_width:.1f} wide,"
            f" {self.plate_depth:.1f} deep, {self.plate_t:.0f} thick",
            f"  outrigger      {self.lobe_y:7.1f} out",
        ])


VIOLIN_RIG = Rig(VIOLIN)
BASS_VIOL_RIG = Rig(BASS_VIOL)
