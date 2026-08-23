"""How much does the rig move, and does the rod diameter actually decide it?

The hardware ladder — stepping the guide rods and leadscrew up with reach — is
mine, not Luca Jost's, whose design stops at the violin.  This checks whether
it earns its place, by working out where the compliance at the tap point
actually lives.  Run it before believing the ladder:

    python tools/stiffness.py
"""

import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from gams import INSTRUMENTS, Rig, mic_arm, slider  # noqa: E402
from gams.params import HW_10_M8, HW_16_M10  # noqa: E402

E_AL = 69_000.0      # N/mm2, aluminium
E_PLA = 3_500.0      # N/mm2, printed PLA along the layers — generous
PLA = 1.24e-3        # g/mm3
G = 9.81e-3          # N per gram


def rod_droop(rig, rod_d, load_n, lever):
    """Tip movement at the tap point from the two guide rods bending.

    The overhung load is a moment about the rods.  Each rod is built in at
    both plates, so take the slider's height as splitting it into two
    encastre spans and use the stiffer of the two as the effective length —
    the softer one dominates, so this is the optimistic case for the rods.
    """
    i_rod = math.pi * rod_d ** 4 / 64
    a, b = rig.slider_z, rig.rod_length - rig.slider_z
    # rotation at a point load position on a fixed-fixed beam, per unit moment
    span = rig.rod_length
    theta_per_moment = (a * b) / (E_AL * i_rod * span)     # rad per N·mm
    moment = load_n * lever                                 # shared by two rods
    theta = theta_per_moment * moment / 2
    return theta * lever, theta


def arm_droop(rig, load_n):
    """Tip movement from the printed slider arm bending as a cantilever.

    Treated as a beam of the plate's thickness and the arm's mean width, which
    flatters it: the real arm is bored for the cable and tapers to a fork.
    """
    width = (rig.arm_root_hw + rig.arm_waist_hw)             # mean full width
    i_arm = width * rig.plate_t ** 3 / 12
    span = rig.reach - rig.carriage_d / 2
    return load_n * span ** 3 / (3 * E_PLA * i_arm)


def report(rig, hw, label):
    sl, arm = slider(rig), mic_arm(rig)
    load = (sl.volume + arm.volume) * PLA * G                # N, self weight
    lever = rig.reach
    d_rod, theta = rod_droop(rig, hw.rod_d, load, lever)
    d_arm = arm_droop(rig, load)
    total = d_rod + d_arm
    print(f"  {label:22s} rods ⌀{hw.rod_d:<3g} "
          f"rod {d_rod*1000:7.1f} µm   arm {d_arm*1000:7.1f} µm   "
          f"total {total*1000:7.1f} µm   rods are {100*d_rod/total:4.1f}% of it")
    return d_rod, d_arm


def main():
    for names in (["violin"], ["bass viol", "cello"]):
        rig = Rig.covering(*(INSTRUMENTS[n] for n in names))
        print(f"\n{' + '.join(names)}   reach {rig.reach:.1f} mm, "
              f"rods {rig.rod_length:.0f} mm long")
        for hw in (HW_10_M8, HW_16_M10):
            report(replace(rig, hardware=hw), hw, f"on {hw.rod_d} mm rods")


if __name__ == "__main__":
    from dataclasses import replace
    main()
