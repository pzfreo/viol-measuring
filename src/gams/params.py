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
NUT = {3: (5.5, 2.4), 4: (7.0, 3.2), 5: (8.0, 4.0), 6: (10.0, 5.0),
       8: (13.0, 6.5), 10: (17.0, 8.4), 12: (19.0, 10.8)}


def nut(m: float) -> tuple:
    """(across_flats, thickness) for an M`m` hex nut."""
    return NUT[int(m)]


# Head diameter for an ISO 4762 socket head cap screw, by thread size.
CAP_HEAD = {3: 5.5, 4: 7.0, 5: 8.5, 6: 10.0, 8: 13.0, 10: 16.0, 12: 18.0}


def cap_head(m: float) -> float:
    """Head diameter of an M`m` socket head cap screw."""
    return CAP_HEAD[int(m)]


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
    bearing_pocket: float = 0.00  # press fit on the bearing OD, no clearance
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
    nut_slot_ceiling: float = 2.54  # material left over the nut slot
    bolt_inset: float = 5.0         # cross bolt, in from the front edge
    bolt_reach_in: float = 8.0      # how far the bolt hole runs past the rod centre
    head_cbore_depth: float = 5.0   # counterbore seating the cap head
    head_fit: float = 0.30
    teardrop_k: float = 1.32       # printable hole apex, in units of bolt radius

    # --- slider ---
    tube_wall: float = 2.0         # wall around a linear bearing
    tube_clear: float = 3.5        # tube outer face to the carriage edge
    tube_arc_hw: float = 8.12      # tubes are trimmed to this in Y above the plate
    arm_root_frac: float = 0.216   # arm half-width at the carriage, / carriage width
    arm_waist_frac_hw: float = 0.316  # and at the waist, / the root half-width
    arm_skin: float = 3.4          # skin either side of the arm's hollow core
    fork_r: float = 8.0            # radius of the fork head
    fork_offset: float = 2.51      # fork head centre, behind the pivot
    arm_waist_frac: float = 0.755  # where the arm is narrowest, as a fraction of reach
    arm_wall: float = 2.0          # side wall of the arm's box section
    arm_core_w: float = 3.5        # width of the arm's hollow core
    arm_core_x0_frac: float = 0.473  # core offset where it starts, / arm root half-width
    arm_core_zero_frac: float = 0.707  # where the core crosses the centreline, / reach
    arm_hollow_from_frac: float = 0.151  # where the arm's core starts, / reach
    arm_hollow_to_frac: float = 0.896    # and where it stops
    post_inner_deg: float = 59.9   # post half-angle at the bore
    post_outer_deg: float = 29.8   # post half-angle at the rim
    post_step_frac: float = 0.46   # where the post steps in, across the tube wall
    fork_gap: float = 6.0          # slot the hammer swings in
    pivot_d: float = 4.0           # hammer pivot bolt
    hex_fit: float = 0.20          # clearance on the leadscrew nut across flats
    nut_trap_z: float = 1.9        # underside of the drive nut pocket
    nut_trap_h: float = 6.1        # height of the drive nut pocket

    # --- cable clip ---
    clip_wall: float = 1.25
    clip_h: float = 15.0
    clip_mouth_y: float = 3.0      # the clip is cut off flat here, and snaps on
    channel_d: float = 3.0         # cable channel running beside the rod
    channel_drop: float = 4.59      # channel centre, below the rod axis
    cable_ring_h: float = 3.0      # the cable loop repeats the rod ring, this tall

    # --- microphone arm ---
    mic_arm_w: float = 6.25        # strut width
    mic_arm_t: float = 3.66        # and thickness
    # the outer section is an obround: its ends are fully rounded, radius t/2
    mic_channel_h: float = 1.20    # cable channel inside the strut
    mic_channel_d: float = 2.35
    mic_channel_face: float = 1.23  # +X edge of the channel, and of the open wall
    # Two windows where the +X wall is cut away so the cable can be laid into
    # the channel.  Everywhere else the section stays a closed box — which is
    # what keeps the arm stiff in twist through the bend, where it matters.
    mic_windows: tuple = ((0.4366, 0.5261), (0.8172, 0.8993))
    mic_arm_root_y: float = 15.0   # where it clamps to the column
    mic_arm_root_z: float = 54.35
    mic_arm_tip_z: float = 14.34   # centreline height of the run carrying the mic
    mic_arm_bend_from: float = 0.485  # S-curve start, as a fraction of mic reach
    mic_arm_bend_to: float = 0.877    # and end
    # Traced centreline of the S-bend, as (y / mic_reach, height above the tip
    # run / total drop).  A plain spline between the two ends is far too gentle
    # — the real bend is roughly twice as steep at its inflection, and that
    # extra path length is worth ~11% of the arm's volume.
    mic_arm_bend: tuple = (
        (0.4851, 0.9998), (0.5037, 0.9965), (0.5224, 0.9872), (0.5410, 0.9732),
        (0.5597, 0.9527), (0.5784, 0.9262), (0.5970, 0.8922), (0.6157, 0.8507),
        (0.6343, 0.7985), (0.6530, 0.7327), (0.6716, 0.6452), (0.6903, 0.5237),
        (0.7090, 0.3982), (0.7276, 0.2902), (0.7463, 0.2100), (0.7649, 0.1460),
        (0.7836, 0.0937), (0.8022, 0.0552), (0.8209, 0.0285), (0.8396, 0.0107),
        (0.8582, 0.0020), (0.8769, 0.0000),
    )
    mic_slot_from: float = 0.940      # opening the microphone drops into
    mic_slot_to: float = 0.977

    # --- hammer ---
    hammer_depth: float = 6.0      # front-to-back, constant the whole length
    hammer_corner_r: float = 0.5
    hammer_fork_w: float = 5.2     # slot up the middle of the head
    hammer_fork_z: tuple = (1.6, 11.0)
    hammer_core_w: float = 2.67    # hollow core up the shaft
    hammer_core_z: tuple = (3.6, 45.9)
    hammer_slot_h: float = 1.0     # the slot the pivot pin passes through
    hammer_slot_d: float = 1.33
    hammer_pivot_from_top: float = 4.95  # pivot slot, down from the top
    handheld_core_w: float = 2.43  # the handheld variant is a little more solid
    # (local z, half-width) up the hammer, measured off the reference
    hammer_profile: tuple = (
        (0.0, 1.85), (0.4, 2.06), (2.4, 4.76), (4.4, 5.71), (6.4, 6.00),
        (8.4, 5.59), (10.4, 5.24), (12.4, 4.88), (14.4, 4.53), (16.4, 4.29),
        (18.4, 4.06), (20.4, 3.71), (22.4, 3.47), (24.4, 3.35), (26.4, 3.12),
        (28.4, 2.88), (30.4, 2.76), (32.4, 2.65), (34.4, 2.53), (36.4, 2.41),
        (40.4, 2.29), (48.4, 2.29), (52.4, 2.41), (55.45, 2.06),
    )

    # --- microphone holder ---
    holder_h: float = 18.0         # clip height
    holder_plate_t: float = 3.0    # the arch it spans the rods with
    holder_mouth_y: float = -3.0   # flat the clips snap on through
    arch_outer_b: float = 45.625   # arch outer edge: semi-height ...
    arch_outer_n: float = 1.66     # ... and superellipse exponent
    arch_inner_a: float = 14.00    # arch inner edge: semi-width ...
    arch_inner_b: float = 30.40    # ... semi-height ...
    arch_inner_n: float = 1.64     # ... and exponent
    fin_h: float = 6.70            # fins that grip the microphone
    mic_channel_w: float = 6.31    # the 6 mm electret sits in here
    fin_outer_x: float = 6.29

    # --- knob ---
    knob_d_frac: float = 3.5       # knob diameter, / leadscrew diameter
    knob_h: float = 11.0           # body height
    knurl_teeth: int = 9
    knurl_depth: float = 0.84
    knurl_from: float = 5.85       # knurling starts this far up the body
    knob_bore_h: float = 1.45      # clearance bore below the captive nut
    knob_nut_h: float = 8.1        # nut pocket height
    knob_boss_d: float = 11.96     # boss between body and drive post
    knob_boss_h: float = 2.0
    knob_post_af: float = 6.98     # hex post the handle sockets onto
    knob_post_h: float = 3.0

    # --- knob handle ---
    handle_len: float = 45.0       # socket centre to grip centre
    handle_w: float = 12.0        # width at the socket
    handle_tip_w: float = 6.0      # and at the grip pin
    handle_t: float = 3.0
    handle_socket_fit: float = 0.11
    grip_pin_d: float = 3.64
    grip_pin_h: float = 13.95
    grip_flange_d: float = 4.64
    grip_flange_h: float = 1.0
    grip_od: float = 6.0           # the spinning sleeve
    grip_id: float = 4.4
    grip_h: float = 9.0
    grip_z: float = 3.5            # sleeve base, above the arm
    grip_flutes: int = 16
    grip_flute_d: float = 0.82

    # --- base plate ---
    corner_r: float = 7.5
    neck_blend_r: float = 6.5
    mount_d: float = 3.5           # M3 clearance for the three mounting points
    mount_cbore_d: float = 5.5
    mount_cbore_t: float = 1.0
    mount_inset: float = 6.0
    lobe_reach_frac: float = 0.2830# outrigger reach, as a fraction of arm reach
    lobe_r_extra: float = -0.25     # tune the outrigger lobe away from its derived size

    # --- lightening around the leadscrew ---
    rim_extra: float = 2.0         # rim outside the bearing pocket
    top_edge_r: float = 1.0        # break on the top face perimeter
    spoke_w: float = 7.0           # width of the four webs carrying the bearing boss
    light_ri_frac: float = 0.4923  # inner radius of the lightening, fraction of the rim
    rib_ri_frac: float = 0.8462    # stiffening brace, inner radius / rim
    rib_ro_frac: float = 0.9231    # stiffening brace, outer radius / rim
    brace_deg: float = 60.0        # how far the brace sweeps round from the spoke
    spur_deg: float = 30.0         # how far its radial spur reaches round
    neck_frac: float = 1.0         # outrigger neck width, as a fraction of the lobe

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
    def pocket_r(self) -> float:
        """Bearing pocket radius — a press fit on the thrust bearing OD."""
        return (self.hw.thrust_od + self.fits.bearing_pocket) / 2

    @property
    def rim_r(self) -> float:
        """Outer radius of the lightened region around the leadscrew."""
        return self.pocket_r + self.rim_extra

    @property
    def lobe_r(self) -> float:
        return self.mount_cbore_d / 2 + 2 * self.wall_t + self.lobe_r_extra

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
    def tube_od(self) -> float:
        """Outer diameter of a linear bearing tube on the slider."""
        return self.hw.bearing_od + 2 * self.tube_wall

    @property
    def carriage_w(self) -> float:
        return self.rod_spacing + self.tube_od + 2 * self.tube_clear

    @property
    def carriage_d(self) -> float:
        return self.tube_od + 2 * self.tube_clear

    @property
    def arm_root_hw(self) -> float:
        """Arm half-width where it leaves the carriage.

        Proportional to the carriage, so a longer arm gets a deeper section
        rather than tapering away to nothing.
        """
        return self.carriage_w * self.arm_root_frac

    @property
    def arm_waist_hw(self) -> float:
        """Arm half-width at its narrowest, just before the fork head."""
        return self.arm_root_hw * self.arm_waist_frac_hw

    @property
    def pivot_y(self) -> float:
        """The hammer hangs on the instrument centreline."""
        return self.reach

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
