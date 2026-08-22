"""Rank the parts by how far each is from Luca Jost's original.

Runs the generated fingerprint suites and reports, per part, the metrics that
say something about shape rather than just size: surface deviation is the one
that catches a feature in the wrong place when the volume happens to agree.
"""
import re
import subprocess
import sys

PARTS = ["01_base", "02_top", "03_slider", "04_holder", "05_mic_arm", "06_clip",
         "07_hammer", "08_knob", "09_handle", "10_grip", "11_handheld"]


def run(part):
    out = subprocess.run(
        [sys.executable, "-m", "pytest", f"tests/fingerprint/test_{part}.py", "-q"],
        capture_output=True, text=True).stdout
    got = {"failed": 0, "passed": 0}
    m = re.search(r"(\d+) failed, (\d+) passed", out)
    if m:
        got["failed"], got["passed"] = int(m.group(1)), int(m.group(2))
    else:
        m = re.search(r"(\d+) passed", out)
        if m:
            got["passed"] = int(m.group(1))
    for key, pat in (("vol", r"Volume [\d.]+ is \w+ than ref [\d.]+ by [\d.]+ mm³ \(([\d.]+)%\)"),
                     ("area", r"Surface area [\d.]+ is \w+ than ref [\d.]+ \(([\d.]+)% off\)"),
                     ("haus", r"Hausdorff distance ([\d.]+)mm exceeds ([\d.]+)mm"),
                     ("mean", r"Mean surface deviation ([\d.]+)mm exceeds ([\d.]+)mm")):
        m = re.search(pat, out)
        got[key] = m.groups() if m else None
    return got


def main():
    print(f"{'part':12s} {'fail':>5s} {'pass':>5s}  {'volume':>8s} {'area':>7s} "
          f"{'Hausdorff (tol)':>20s} {'mean (tol)':>16s}")
    rows = []
    for p in PARTS:
        g = run(p)
        vol = f"{g['vol'][0]}%" if g["vol"] else "ok"
        area = f"{g['area'][0]}%" if g["area"] else "ok"
        haus = f"{g['haus'][0]} ({g['haus'][1]})" if g["haus"] else "ok"
        mean = f"{g['mean'][0]} ({g['mean'][1]})" if g["mean"] else "ok"
        print(f"{p:12s} {g['failed']:5d} {g['passed']:5d}  {vol:>8s} {area:>7s} "
              f"{haus:>20s} {mean:>16s}", flush=True)
        rows.append((p, g))
    worst = sorted(rows, key=lambda r: -r[1]["failed"])
    print("\nmost divergent first: " + ", ".join(p for p, _ in worst if _["failed"]))


if __name__ == "__main__":
    main()
