# Reference material

`upstream/` holds Luca Jost's original `.3mf` parts, vendored unchanged from
[General-Acoustic-Measurement-Setup][upstream] (MIT). Everything in this
rebuild was measured from these, and the generated fingerprint suites in
`tests/fingerprint/` are checked against them.

Three directories are **not** in the repository because they are derived from
`upstream/` and are large. Regenerate them when you need them:

```bash
# STL copies of the reference parts, used to generate the fingerprint suites
PYTHONPATH=tools python tools/3mf_to_stl.py

# four-view renders of each reference part
PYTHONPATH=tools python tools/render_mesh.py

# cross-sections through a part, for reading dimensions off it
PYTHONPATH=tools python tools/section_mesh.py "ref/upstream/01 Base.3mf" Z "0.5,2,5,8" out.png
```

The other tools in `tools/` read the same references directly:

| tool | what it does |
|---|---|
| `probe_3mf.py` | bounding boxes and mesh statistics |
| `features.py` | fits circles to a cross-section — hole centres and diameters |
| `occupancy.py` | material-vs-void map on a plane, when an outline is ambiguous |
| `diff_mesh.py` | where a rebuilt part differs from its reference |
| `volume_diff.py` | localises that difference by layer |
| `arcfit.py` | decomposes a section outline into lines and arcs |
| `revolve_profile.py` | recovers the profile of a turned part |
| `stability.py` | centre of gravity and tipping loads for an assembly |

[upstream]: https://github.com/luca-jost-violins/General-Acoustic-Measurement-Setup
