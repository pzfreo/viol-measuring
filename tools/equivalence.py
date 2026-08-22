"""Rank the parts by how far each is from Luca Jost's original.

Runs the generated fingerprint suites and reports the metrics that say
something about shape rather than just size.  Cross-section results are shown
separately: cad-fingerprint sums each section wire as its own face, so holes
are added to the area instead of subtracted, and on a pocketed part that test
compares two wrong numbers (pzfreo/cad-fingerprint#5).  Volume, surface area,
mass properties and surface deviation are unaffected.
"""
import re
import subprocess
import sys

PARTS = ["01_base", "02_top", "03_slider", "04_holder", "05_mic_arm", "06_clip",
         "07_hammer", "08_knob", "09_handle", "10_grip", "11_handheld"]

SUSPECT = ("cross_section",)


def run(part):
    out = subprocess.run(
        [sys.executable, "-m", "pytest", f"tests/fingerprint/test_{part}.py", "-q",
         "--tb=no", "-rf"], capture_output=True, text=True).stdout
    failed = re.findall(r"^FAILED \S+::(\w+)::(\w+)", out, re.M)
    trusted = sum(1 for _, t in failed if not any(s in t for s in SUSPECT))
    suspect = len(failed) - trusted
    got = {"trusted": trusted, "suspect": suspect}
    for key, pat in (("vol", r"Volume [\d.]+ is \w+ than ref [\d.]+ by [\d.]+ mm³ \(([\d.]+)%\)"),
                     ("area", r"Surface area [\d.]+ is \w+ than ref [\d.]+ \(([\d.]+)% off\)"),
                     ("haus", r"Hausdorff distance ([\d.]+)mm exceeds [\d.]+mm.*?95th pct ([\d.]+)"),
                     ("mean", r"Mean surface deviation ([\d.]+)mm exceeds ([\d.]+)mm")):
        m = re.search(pat, out, re.S)
        got[key] = m.groups() if m else None
    return got


def main():
    print(f"{'part':12s} {'fail':>5s} {'(§)':>5s}  {'volume':>7s} {'area':>6s} "
          f"{'Hausdorff':>10s} {'95th pct':>9s} {'mean dev':>9s}")
    rows = []
    for p in PARTS:
        g = run(p)
        f = lambda k, i, s="ok": f"{g[k][i]}" if g[k] else s
        print(f"{p:12s} {g['trusted']:5d} {g['suspect']:5d}  "
              f"{f('vol', 0):>7s} {f('area', 0):>6s} {f('haus', 0):>10s} "
              f"{f('haus', 1):>9s} {f('mean', 0):>9s}", flush=True)
        rows.append((p, g))
    worst = sorted(rows, key=lambda r: -r[1]["trusted"])
    print("\n§ = failures of the cross-section tests affected by "
          "pzfreo/cad-fingerprint#5, which are not evidence either way.")
    left = [p for p, g in worst if g["trusted"]]
    print("still diverging: " + (", ".join(left) if left else "none"))


if __name__ == "__main__":
    main()
