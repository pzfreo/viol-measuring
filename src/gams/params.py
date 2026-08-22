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

import math
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
# Cello figures are the trade standard for a 4/4: body 755, lower bout 440,
# ribs ~4.5 in.  Included because it is the nearest well-documented instrument
# to a bass viol, so published cello acoustics are the best available check on
# whether the large end of this rig is pointed at the right frequencies.
CELLO = Instrument("cello", body_length=755, rib_depth=114, arching=25, lower_bout=440)

INSTRUMENTS = {i.name: i for i in
               (VIOLIN, VIOLA, TREBLE_VIOL, TENOR_VIOL, BASS_VIOL, CELLO)}


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
    slide: float = 0.25           # general sliding fit
    arm_slot: float = 0.06        # microphone arm in the holder's fins


@dataclass(frozen=True)
class Rig:
    """A complete rig, derived from the instrument it must measure."""

    instrument: Instrument
    hardware: Optional[Hardware] = None
    fits: Fits = field(default_factory=Fits)
    also: tuple = ()               # other instruments this rig must also serve

    # --- geometry the design fixes rather than derives (mm) ---
    column_gap: float = 2.5        # column face to the edge of the lower bout
    #   2.5, from the reference: its hammer pivot bore sits at Y=106.5 on a
    #   208 mm bout, and that bore is what puts the head on the tap point.
    mic_overhang: float = 27.17    # how far past the tap point the mic reaches
    #   27.17, not a round 28: the reference arm ends at Y=133.67, and half a
    #   millimetre of reach moves every feature along the arm with it.
    mic_height_frac: float = 0.478  # microphone height, as a fraction of rib depth
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
    bolt_lengths: tuple = (8, 10, 12, 16, 20, 25, 30, 35, 40)  # stock sizes
    min_head_seat: float = 4.0     # keep at least this much flat seat for the head
    head_fit: float = 0.30
    teardrop_k: float = 1.32       # printable hole apex, in units of bolt radius

    # --- slider ---
    tube_wall: float = 2.0         # wall around a linear bearing
    tube_clear: float = 3.5        # tube outer face to the carriage edge
    tube_arc_hw: float = 8.12      # tubes are trimmed to this in Y above the plate
    arm_root_frac: float = 0.216   # arm half-width at the carriage, / carriage width
    arm_waist_frac_hw: float = 0.316  # and at the waist, / the root half-width
    fork_r: float = 8.0            # radius of the fork head
    fork_offset: float = 2.30      # fork head centre, behind the pivot
    fork_top: float = 4.40         # ... and the flat that truncates it, ahead
    arm_waist_frac: float = 0.755  # where the arm is narrowest, as a fraction of reach
    arm_wall: float = 2.0          # side wall of the arm's box section
    # The arm is not hollowed into a box beam: it carries a single 3.5 mm bore
    # for the microphone lead, entering the carriage's front face through a
    # 15 degree cone and running out to the fork.  Its axis stays at mid
    # thickness the whole way and wanders in plan, traced here at 10 mm
    # intervals as (y / pivot reach, x / arm root half-width).
    cable_d: float = 3.5
    cable_mouth_d: float = 7.5     # the cone at the front face
    cable_mouth_deg: float = 15.0  # half-angle
    cable_path: tuple = (
        (-0.07042, 0.54339), (0.00469, 0.56508), (0.09859, 0.53102),
        (0.19249, 0.43485), (0.28638, 0.32050), (0.38028, 0.22368),
        (0.47418, 0.14425), (0.56808, 0.08247), (0.66197, 0.03810),
        (0.75587, 0.01078), (0.86385, 0.00000),
    )
    fork_slot_back: float = 8.9    # slot floor, behind the pivot
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
    clip_h_frac: float = 1.5       # clip height, / rod diameter
    clip_mouth_frac: float = 0.6   # where the clip is cut flat, / rod radius
    channel_d: float = 3.0         # cable channel running beside the rod
    channel_drop: float = 4.59      # channel centre, below the rod axis
    cable_ring_h: float = 3.0      # the cable loop repeats the rod ring, this tall

    # --- microphone arm ---
    # The arm's section grows with its reach — it is the longest unsupported
    # member on the rig after the slider arm.  Fractions come from the violin
    # reference, so that preset is unchanged.
    mic_arm_w_frac: float = 0.0467570  # strut width, / mic reach       (6.25)
    mic_arm_t_frac: float = 0.0276802  # and thickness                   (3.70)
    mic_arm_corner_frac: float = 0.16  # section corner radius, / width   (1.00)
    mic_channel_h_frac: float = 0.405405  # cable channel height, / thickness
    mic_channel_d_frac: float = 0.48   # and length, / arm width          (3.00)
    mic_channel_x_frac: float = 0.048  # channel centre, off the arm's own centre
    mic_window_floor_frac: float = 0.1968  # window floor, / arm width    (1.23)
    mic_arm_root_y_frac: float = 0.109829  # where it clamps, / mic reach
    mic_arm_root_clear: float = 9.35   # arm root, above the tap point
    # The outer section is a rounded rectangle and the channel inside it an
    # obround — not the other way round, which costs 9% of the section area.
    # Three windows cut the +X wall away so the cable can be laid into the
    # channel from the side.  They are placed and sized along the arm's own
    # length, not along Y: in the middle of the bend the arm is steep, and the
    # middle window spans barely 2 mm of Y for the same 10 mm of arm.
    mic_windows: tuple = ((0.3255, 0.3970), (0.5959, 0.6687), (0.8205, 0.8948))
    mic_window_flare: float = 45.0     # end walls, degrees off the floor
    # The S-bend is an arc, a straight, and a second arc, tangent throughout.
    # Fitted to the reference centreline it lands within 0.3 mm, against 0.7
    # for the 22-point traced table it replaces — and it has real tangents, so
    # the swept section cannot wobble between sample points.  Both radii are
    # given as fractions of the drop, so the bend keeps its shape on a rig
    # whose ribs are three times deeper.
    mic_arm_bend_to: float = 0.88180   # where the bend ends, / mic reach
    mic_bend_r1_frac: float = 0.7408   # first radius, / the drop
    mic_bend_r2_frac: float = 0.5953   # second radius, / the drop
    mic_bend_slope: float = 62.58      # the straight between them, degrees
    mic_arm_bend_clear: float = 5.0    # bend starts this far beyond the holder
    # The seat the microphone drops into is a plain 6 mm hole through the arm,
    # which fits the 6 x 2.7 mm electret in the bill of materials.  It fits the
    # reference to 0.006 mm, so it is his hole, not a curve through my samples.
    # Absolute, not scaled: the microphone is the same size on every rig.
    mic_seat_d: float = 6.0
    mic_seat_back: float = 5.70       # its centre, back from the arm's tip
    mic_seat_x: float = 0.70          # ... and off the arm's centreline

    # --- hammer ---
    # Parts 07 and 11 share one outline: a big circle at the head, a small one
    # at the tip, and a long concave arc tangent to both.  Measured off Luca
    # Jost's meshes, where those three radii fit to within 0.002 mm.
    hammer_depth: float = 6.0      # front-to-back, constant the whole length
    hammer_corner_r: float = 0.4   # rounding along both flat faces
    hammer_head_d: float = 12.0    # the struck end
    hammer_tip_d: float = 5.0      # the hanging end
    hammer_flank_r: float = 200.0  # arc joining the two, tangent to both
    hammer_bore_d: float = 5.0     # through the head, on the depth axis
    hammer_cbore_d: float = 9.85   # recess around it, on the +Y face
    hammer_cbore_depth: float = 3.7
    hammer_cavity_d: float = 3.0   # channel from the head bore up the shaft
    handheld_cavity: tuple = (3.4, 1.7)  # part 11 runs a flattened slot instead
    hammer_cavity_y: float = -1.0  # offset from the centre plane
    hammer_cavity_straight_to: float = 36.0   # then it curves out to the face
    hammer_cavity_arc_r: float = 38.0
    hammer_pin_d: float = 1.5      # the pin it hangs on, across the flats
    hammer_pivot_from_top: float = 5.0

    # --- microphone holder ---
    holder_plate_t: float = 3.0    # the arch it spans the rods with
    holder_mouth_y: float = -3.0   # flat the clips snap on through
    arch_outer_b_frac: float = 1.7381  # arch outer semi-height, / its span
    arch_outer_n: float = 1.66     # ... and superellipse exponent
    arch_inner_a_frac: float = 0.5333  # arch inner semi-width, / the span
    arch_inner_b_frac: float = 1.1581  # ... semi-height ...
    arch_inner_n: float = 1.64     # ... and exponent
    fin_t: float = 3.135           # fin thickness either side of the arm slot

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
    handle_len_frac: float = 1.6071  # crank length, / knob diameter
    handle_w: float = 12.0        # width at the socket
    handle_tip_w: float = 6.0      # and at the grip pin
    handle_t: float = 3.0
    handle_socket_fit: float = 0.12
    grip_pin_d: float = 3.70
    grip_pin_h: float = 13.0       # plain pin, up to the retaining head
    # The head is a cone, not a disc: it flares from the pin to 5.70 over the
    # last millimetre, so the sleeve cannot climb off but the print still has
    # a face to grow from.
    grip_head_d: float = 5.70
    grip_head_h: float = 1.0
    grip_od: float = 6.0           # the spinning sleeve
    grip_id: float = 4.4
    grip_h: float = 9.0
    grip_z: float = 3.5            # sleeve base, above the arm
    # The sleeve is diamond knurled, not fluted: two families of eight helical
    # grooves running opposite ways, each turning through 58.7 deg over the
    # sleeve's height.  Straight flutes would give the same volume and the
    # wrong grip - your fingers slide along a flute, which is the one direction
    # this thing has to hold.
    grip_knurl_starts: int = 8
    grip_knurl_angle: float = 12.7  # groove width, degrees
    grip_knurl_twist: float = 66.2  # each family, over the full height
    grip_knurl_phase: float = 22.5  # where the pattern starts
    grip_root_d: float = 5.0        # groove floor

    # --- base plate ---
    corner_r: float = 7.5
    neck_blend_r: float = 6.5
    mount_d: float = 3.5           # M3 clearance for the three mounting points
    mount_cbore_d: float = 5.5
    mount_cbore_t: float = 1.0
    mount_inset: float = 6.0
    lobe_reach_frac: float = 0.28169  # outrigger reach, / arm reach  (30.00)
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
        """Microphone height above the bench, beside the ribs."""
        return self.instrument.rib_depth * self.mic_height_frac

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
    def knob_d(self) -> float:
        return self.hw.screw_d * self.knob_d_frac

    @property
    def handle_len(self) -> float:
        """Crank length — leverage has to keep up with the leadscrew."""
        return self.knob_d * self.handle_len_frac

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

    # --- microphone arm, derived ---

    @property
    def mic_arm_w(self) -> float:
        return self.mic_reach * self.mic_arm_w_frac

    @property
    def mic_arm_t(self) -> float:
        return self.mic_reach * self.mic_arm_t_frac

    @property
    def mic_channel_d(self) -> float:
        return self.mic_arm_w * self.mic_channel_d_frac

    @property
    def mic_channel_h(self) -> float:
        return self.mic_arm_t * self.mic_channel_h_frac

    @property
    def mic_channel_x(self) -> float:
        """Channel centre, off the arm's centreline towards the windows."""
        return self.mic_arm_w * self.mic_channel_x_frac

    @property
    def mic_window_floor(self) -> float:
        """How far in from the arm's centreline a window is cut."""
        return self.mic_arm_w * self.mic_window_floor_frac

    @property
    def mic_arm_corner_r(self) -> float:
        return self.mic_arm_w * self.mic_arm_corner_frac

    @property
    def mic_arm_root_y(self) -> float:
        return self.mic_reach * self.mic_arm_root_y_frac

    @property
    def mic_arm_root_z(self) -> float:
        """Height the arm leaves the column at — just clear of the belly."""
        return self.tap_height + self.mic_arm_root_clear

    @property
    def mic_arm_bend_from(self) -> float:
        """Where the S-bend starts, as a fraction of mic reach.

        Derived rather than fixed: the drop grows with the instrument's ribs
        much faster than the reach does, so a fixed bend span would make the
        bend steeper and steeper until the swept section folds through itself.
        The bend keeps its shape and the straight runs either side take up the
        slack.
        """
        wanted = self.mic_arm_bend_to - self.mic_bend_run / self.mic_reach
        # ... but never before the arm is clear of the fins gripping it, or the
        # arm would be bending inside its own clamp
        clear = (self.arch_span * self.arch_outer_b_frac
                 + self.mic_arm_bend_clear) / self.mic_reach
        return max(wanted, clear)

    @property
    def mic_arm_drop(self) -> float:
        """Height the arm loses between its two straight runs."""
        return self.mic_arm_root_z - self.mic_arm_tip_z

    @property
    def mic_bend_radii(self) -> tuple:
        """The two arc radii of the S-bend."""
        return (self.mic_arm_drop * self.mic_bend_r1_frac,
                self.mic_arm_drop * self.mic_bend_r2_frac)

    @property
    def mic_bend_straight(self) -> float:
        """Length of the straight run between the two arcs.

        Whatever drop the arcs do not account for has to be made up here, so
        this is what closes the bend rather than a free choice.
        """
        r1, r2 = self.mic_bend_radii
        th = math.radians(self.mic_bend_slope)
        return (self.mic_arm_drop - (r1 + r2) * (1 - math.cos(th))) / math.sin(th)

    @property
    def mic_bend_run(self) -> float:
        """How far along Y the whole bend takes."""
        r1, r2 = self.mic_bend_radii
        th = math.radians(self.mic_bend_slope)
        return (r1 + r2) * math.sin(th) + self.mic_bend_straight * math.cos(th)

    @property
    def mic_arm_tip_z(self) -> float:
        """The run that carries the microphone, at microphone height."""
        return self.mic_height

    # --- microphone holder, derived ---

    @property
    def arm_slot_w(self) -> float:
        """The slot the arm slides in — the rig's one tolerance-critical fit.

        Upstream ships the arm in +/-0.05, 0.10 and 0.15 mm widths precisely
        because a printer's tolerance lands on this gap, so it is deliberately
        tighter than a general sliding fit.
        """
        return self.mic_arm_w + self.fits.arm_slot

    @property
    def fin_outer_x(self) -> float:
        return self.arm_slot_w / 2 + self.fin_t

    @property
    def fin_h(self) -> float:
        """Tall enough to take the arm, plus the same clearance as the slot."""
        return self.holder_plate_t + self.mic_arm_t + self.fits.arm_slot

    @property
    def holder_z(self) -> float:
        """Set so the fins land on the arm where it leaves the column."""
        return self.mic_arm_root_z - self.mic_arm_t / 2 - self.holder_plate_t

    @property
    def holder_h(self) -> float:
        return 1.8 * self.hw.rod_d

    @property
    def arch_span(self) -> float:
        return self.rod_x + self.hw.rod_r + self.clip_wall

    # --- rod clamp bolt: length first, then the counterbore to suit ---

    @property
    def clamp_bolt_len(self) -> float:
        """A stock bolt length that reaches the nut without bottoming out.

        Luca Jost's violin uses M4 x 10 and warns it must be exactly that: too
        short and it misses the nut, too long and it hits the print. So the
        length is chosen first, from stock sizes, and the counterbore is cut to
        suit — rather than the other way round.
        """
        nut_t = nut(self.hw.clamp_bolt)[1]
        nut_face = self.rod_x - self.slit_w / 2 - self.jaw_wall
        full = self.plate_width / 2 - nut_face + nut_t     # flush with the nut
        usable = [L for L in self.bolt_lengths if L <= full - self.min_head_seat]
        if not usable:
            raise ValueError("no stock bolt short enough for this clamp")
        return max(usable)

    @property
    def head_cbore_depth(self) -> float:
        """Counterbore depth that makes the chosen bolt come out flush."""
        nut_t = nut(self.hw.clamp_bolt)[1]
        nut_face = self.rod_x - self.slit_w / 2 - self.jaw_wall
        return self.plate_width / 2 - nut_face + nut_t - self.clamp_bolt_len

    @property
    def rod_bore_r(self) -> float:
        return (self.hw.rod_d + self.fits.rod_bore) / 2

    @property
    def rod_x(self) -> float:
        return self.rod_spacing / 2

    @property
    def clip_h(self) -> float:
        return self.hw.rod_d * self.clip_h_frac

    @property
    def clip_mouth_y(self) -> float:
        return self.hw.rod_r * self.clip_mouth_frac

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

    # --- where each part sits on the column ---

    @property
    def hammer_head_z(self) -> float:
        """Centre of the round end that does the striking."""
        return self.hammer_head_d / 2

    @property
    def hammer_tip_z(self) -> float:
        """Centre of the round end it hangs from."""
        return self.hammer_drop - self.hammer_tip_d / 2

    @property
    def hammer_flank(self) -> tuple:
        """Centre (x, z) of the arc that sweeps between the two round ends.

        It is tangent to both, so its centre is fixed by the two radii and the
        distance between them — there is nothing left to choose.
        """
        rh, rt, R = self.hammer_head_d / 2, self.hammer_tip_d / 2, self.hammer_flank_r
        span = self.hammer_tip_z - self.hammer_head_z
        z = self.hammer_head_z + ((R + rh) ** 2 - (R + rt) ** 2 + span ** 2) / (2 * span)
        return math.sqrt((R + rh) ** 2 - (z - self.hammer_head_z) ** 2), z

    @property
    def hammer_tangent_z(self) -> tuple:
        """Heights where the flank arc meets each round end."""
        fx, fz = self.hammer_flank
        rh, rt, R = self.hammer_head_d / 2, self.hammer_tip_d / 2, self.hammer_flank_r
        return (self.hammer_head_z + (fz - self.hammer_head_z) * rh / (R + rh),
                self.hammer_tip_z + (fz - self.hammer_tip_z) * rt / (R + rt))

    @property
    def hammer_pivot_drop(self) -> float:
        """Pivot to head — the pendulum length that actually swings."""
        return self.hammer_drop - self.hammer_pivot_from_top

    @property
    def slider_z(self) -> float:
        """Slider height that lands the hammer head on the tap point.

        The hammer hangs on the pin through the slider's fork, which sits at
        half the plate thickness up the slider, so the whole column height
        follows from where the belly is.
        """
        return self.tap_height + self.hammer_pivot_drop - self.plate_t / 2

    def slider_z_for(self, reach: float) -> float:
        """Slider height for whichever instrument the hammer is pinned for."""
        for inst in self.covers:
            rig = replace(self, instrument=inst, also=())
            if abs(rig.reach - reach) < 0.05:
                return rig.slider_z
        return self.slider_z

    @property
    def clip_z(self) -> float:
        return self.plate_t + 10.0

    @property
    def knob_z(self) -> float:
        return self.rod_length + 2.0

    # --- covering more than one instrument ---

    @property
    def pivot_reaches(self) -> tuple:
        """Every reach the hammer can be pinned at, nearest first.

        One entry for a single-instrument rig.  A rig built to cover a range
        gets one per instrument, and the arm is made long enough for all of
        them.
        """
        if not self.also:
            return (self.reach,)
        reaches = {round(self.reach, 2)}
        for other in self.also:
            reaches.add(round(replace(self, instrument=other, also=()).reach, 2))
        return tuple(sorted(reaches))

    @property
    def covers(self) -> tuple:
        return (self.instrument,) + tuple(self.also)

    def for_instrument(self, instrument: Instrument) -> "Rig":
        return replace(self, instrument=instrument)

    @classmethod
    def covering(cls, *instruments: Instrument, **kwargs) -> "Rig":
        """One rig that serves several instruments.

        Sized to whichever needs the biggest rig, with a hammer pivot position
        for each.  Everything else the instruments differ in is already
        adjustable on the assembled rig: tap height is the crank, microphone
        reach is the arm sliding in its fins, and microphone height is where
        the holder clips to the rods.
        """
        if not instruments:
            raise ValueError("name at least one instrument")
        biggest = max(instruments, key=lambda i: cls(i).reach)
        rest = tuple(i for i in instruments if i is not biggest)
        return cls(biggest, also=rest, **kwargs)

    def summary(self) -> str:
        i, hw = self.instrument, self.hw
        extra = []
        if self.also:
            extra = [f"  also serves    " + ", ".join(o.name for o in self.also),
                     f"  hammer pins at " + ", ".join(f"{r:.0f}" for r in self.pivot_reaches)]
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
        ] + extra)


VIOLIN_RIG = Rig(VIOLIN)
BASS_VIOL_RIG = Rig(BASS_VIOL)
