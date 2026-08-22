"""Export every part, and the assembly, for a given instrument.

    python tools/export_all.py bass_viol

Name more than one, joined by +, to get a single rig that serves all of them.
It is built to whichever needs the most, with a hammer pivot position for each:

    python tools/export_all.py "bass viol+cello"
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from build123d import export_step, export_stl  # noqa: E402

from gams import (  # noqa: E402
    INSTRUMENTS, Rig, assembly, base, clip, grip, hammer, handheld_hammer,
    handle, holder, knob, mic_arm, slider, top,
)

PARTS = {
    "01_base": base, "02_top": top, "03_slider": slider,
    "04_microphone_holder": holder, "05_microphone_arm": mic_arm,
    "06_cable_clip": clip, "07_hammer": hammer, "08_knob": knob,
    "09_knobhandle": handle, "10_knobhandleknurl": grip,
    "11_handheld_hammer": handheld_hammer,
}


def main(name="violin", out="export"):
    names = [n.strip() for n in name.split("+")]
    rig = Rig.covering(*(INSTRUMENTS[n] for n in names))
    d = pathlib.Path(out) / "_and_".join(n.replace(" ", "_") for n in names)
    d.mkdir(parents=True, exist_ok=True)
    for label, fn in PARTS.items():
        part = fn(rig)
        export_step(part, str(d / f"{label}.step"))
        export_stl(part, str(d / f"{label}.stl"))
        print(f"  {label:24s} {part.volume:9.1f} mm3")
    for reach in rig.pivot_reaches:
        suffix = "" if len(rig.pivot_reaches) == 1 else f"_reach{reach:.0f}"
        export_step(assembly(rig, at_reach=reach),
                    str(d / f"gams_assembly{suffix}.step"))
    print(f"\n{rig.summary()}\n\nwritten to {d}/")


if __name__ == "__main__":
    main(sys.argv[1].replace("_", " ") if len(sys.argv) > 1 else "violin")
