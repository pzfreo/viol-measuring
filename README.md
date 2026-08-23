# A tap-testing rig that fits your instrument

![The same rig built for a violin and for a cello](docs/hero.png)

*The same rig, printed for a violin (left) and a cello (right) — same rods,
same bearings, same leadscrew, same clamp hardware. Nothing was redrawn: you
give it the instrument's dimensions and every part follows.*

---

This is [Luca Jost's General Acoustic Measurement Setup][upstream] rebuilt so
that it scales. His rig is a lovely piece of design: a printed column with a
sliding arm, a pendulum hammer that taps the belly at the same speed every
time, and a microphone on a curved arm beside the ribs. It is dimensioned for a
violin.

If you work on violas da gamba, cellos, or anything else with deeper ribs and a
wider lower bout, those dimensions do not fit. This version asks you for the
instrument instead:

```
body length 660    ribs 125    lower bout 380
```

and works out the rest — how far the arm must reach, how high the tap point
sits, how tall the column needs to be, and where the hammer pins.

## Which instrument?

| preset | body | ribs | lower bout | tap point | reach | column |
|---|---|---|---|---|---|---|
| `violin` | 355 | 30 | 208 | 45 up | 106 out | 200 |
| `viola` | 410 | 34 | 240 | 50 | 122 | 200 |
| `treble viol` | 370 | 62 | 230 | 80 | 117 | 250 |
| `tenor viol` | 490 | 88 | 290 | 108 | 147 | 250 |
| `bass viol` | 660 | 125 | 380 | 147 | 192 | 300 |
| `cello` | 755 | 114 | 440 | 139 | 222 | 300 |

All dimensions in mm. Every preset runs on **Luca Jost's hardware** — ⌀10
aluminium rods, an M8 leadscrew, LM10UU linear bearings, 608 thrust bearings,
M4 clamp screws. Only the rod length changes.

The `violin` preset reproduces his original rig. Every part was measured back
off his mesh files and rebuilt to match — if you want to know how closely, and
where it does not, that is in [FIDELITY.md](FIDELITY.md).

The viol figures are mid-range for surviving consort instruments, which vary far
more than the violin family does. If yours differs, see
[Changing the numbers](#changing-the-numbers).

## Making one

You need [uv](https://github.com/astral-sh/uv), or any Python 3.10+ with pip.

```bash
git clone https://github.com/pzfreo/viol-measuring
cd viol-measuring
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python build123d numpy

.venv/bin/python tools/export_all.py "bass viol"
```

That writes all eleven parts as STL and STEP into `export/bass_viol/`, plus the
whole rig assembled as a single STEP so you can look it over before spending a
weekend printing. It also prints the rig's key dimensions, so you can check them
against your instrument first. Use any preset name from the table; `violin` is
the default.

**Everything prints without support.** The cross-bolt holes are teardrop-shaped
for exactly that reason, and each part is oriented so a flat face is the build
surface. Three parts need a print pause to capture a nut — the exported bill of
materials says which, and when.

## What to buy

**[BOM.md](BOM.md)** has the full list for the cello / bass viol rig: printed
masses, exact bolt lengths, bearing designations and print orientations, all
generated from the model so it cannot drift from the geometry. Regenerate it for
any other instrument:

```bash
.venv/bin/python tools/make_bom.py "tenor viol"
```

The bought-in parts are Luca Jost's [original list][upstream] — two aluminium
guide rods, a threaded rod, linear bearings, two 608 bearings, M4 hardware,
electret microphones and a Behringer UCA-202. His README has purchase links, and
for a larger rig the only change is the length of the rods and the leadscrew.

## One rig for more than one instrument

A bass viol and a cello want **the same rig**: same rods, same leadscrew, same
300 mm column, same plates and carriage. They differ in exactly one thing the
assembled rig cannot already adjust — 30 mm of hammer reach. Everything else is
a setting: tap height is the crank, the microphone arm slides in its fins, and
the holder clips anywhere on the rods.

So build one, and give the arm a pivot hole for each:

```bash
.venv/bin/python tools/export_all.py "bass viol+cello"
```

Move the pin, wind the crank, and it is set for the other instrument.

## Three things worth knowing before you measure

**Bolt it down.** The three counterbored holes in the base are not feet — they
take M3 screws into a board. Free-standing, the violin rig tips under about 48 g
applied to the end of the arm and the cello rig under 56 g; that is a hand
resting on it. This is true of the original rig too, not something the larger
sizes introduced. Bolted to a board it is not close.

**Check your frequency range.** The measurement template that ships with the
original (`ref/upstream/GMS_template.txt`) plots from 200 Hz. A cello's A0 air
mode sits at roughly 93–120 Hz, and a bass viol's will be similar — *below the
bottom of the default plot*. The single most diagnostic low mode would not be on
screen. The 0.3 s sample window is also coarse for a sharp air mode. Both want
changing for anything larger than a viola.

**This is not a free-free measurement.** The rig lays the instrument on its back
on the bench. Modal work normally supports the instrument on foam or hangs it on
elastic, precisely to avoid the bench damping it. For a violin the difference is
small; for a cello-sized instrument resting its ribs on a bench it is
proportionally larger. Worth one controlled comparison before trusting absolute
numbers at the large end.

## Changing the numbers

If your instrument is not one of the presets, or you have measured your own, one
line does it:

```python
from gams import Instrument, Rig

my_viol = Instrument("my bass", body_length=680, rib_depth=132,
                     arching=24, lower_bout=395)

print(Rig(my_viol).summary())
```

That prints the rig those four numbers imply. Everything else — reach, tap
height, column height, arm section — follows.

The fits are adjustable too, if your printer runs tight or loose. The one that
matters most is the slot the microphone arm slides in: the original ships the
arm in ±0.05, ±0.10 and ±0.15 mm widths for exactly this reason. Here it is a
single number (`fits.arm_slot`, default 0.06 mm) rather than four models.

## Before you print: what is proven and what is not

**The violin preset is his design**, built and iterated in practice. Everything
below applies to the larger sizes.

**None of the larger presets has been printed or used.** How the arm section
grows with reach, how the microphone arm's bend stretches, where the hammer
pins — none of that is in his design, because his design is for a violin. They
are a considered starting point, not a proven rig.

**The larger rigs are soft, and I have not fixed it.** At a cello's reach the
printed slider arm carries 91% of the movement at the tap point, and the rig's
first mode lands near 52 Hz — below a cello's A0 at about 100 Hz, so the rig can
ring inside the band you are trying to measure. What would help is a deeper arm
section, since stiffness goes as the cube of depth. See
[FIDELITY.md](FIDELITY.md#the-hardware-ladder-and-why-it-is-gone) for the
working, including a rule this repo used to have that did not survive it.

**The two M4 grub screws are not modelled**, and I do not know where they go.
His build video threads them into the slider after the linear bearings. No hole
for them has been found. Buy them; if you work out where they go, please open an
issue.

**There is no published rig at this size to check against.** Joseph Curtin's
[Impulse Measurement Rig][curtin-rig], the reference instrument in this field,
covers *"violins and violas of any size"* and does not do cellos.

## Sources and further reading

If you are new to this, start with Gough — it is the clearest overview of what
you are actually measuring and why.

**Violin family acoustics**

- Colin Gough, [*Violin Acoustics*][gough-at], Acoustics Today (2016) —
  [PDF][gough-pdf], [supplementary text][gough-supp], [media][gough-media]
- Colin Gough, [*Violin acoustics: an introduction and recent
  developments*][gough-musica] (MusICA seminar); his site: [colingough.com][gough-site]
- Jim Woodhouse, [*Euphonics: the science of musical
  instruments*][euphonics] — the online reference work; see especially
  [signature modes and formants][euphonics-modes] and [experimental modal
  analysis][euphonics-ema]
- George Bissinger's papers and the Strad3D datasets: [strad3d.org][strad3d]
- [Modal analysis of violins and cellos][asa-cello], Acoustical Society of
  America — one of the few sources giving cello mode frequencies

**Measurement practice**

- [VSA-Oberlin Acoustics Workshop][oberlin] and its
  [YouTube channel][oberlin-yt] — the annual gathering where most of this is
  worked out
- Joseph Curtin, [Impulse Measurement Rig][curtin-rig] — the commercial
  reference rig; useful for what it specifies (a few-gram impulse hammer, an
  omnidirectional condenser mic, meaningful data to 7 kHz)
- [ObiApp][obiapp], the free analysis software by Chris Rogers and Joseph
  Curtin that goes with it
- George Stoppani's [modal analysis software][stoppani] — acquisition, mode
  fitting, mode shapes and animation; widely used by makers
- Martin Schleske on [modal analysis][schleske] and [sound analysis
  method][schleske-method]
- [Support conditions for free boundary-condition modal testing][free-free] —
  why foam and elastic suspension are the norm

There is more detail, including the numbers behind the frequency-range warning
above, in [`REFERENCE.md`](REFERENCE.md).

## Credit

The design is **Luca Jost's**. The column, the pendulum hammer, the sliding arm,
the curved microphone arm, the split clamps, the choice of hardware — all of it
is his, and it is a genuinely good piece of design that repaid careful
measurement. This repository only re-expresses it as parameters so it can be
made larger.

His original: [luca-jost-violins/General-Acoustic-Measurement-Setup][upstream].
Please start there, and use his README for the parts list and purchase links.

## Licence

MIT, matching the original. See [LICENSE](LICENSE).

*(A note for Luca, if you find this: the `LICENSE` in your repository still has
the placeholder `[year] [fullname]` where the copyright line should be — that is
[issue #1][upstream-issue] on your repo. Filling it in would make it easier for
people to build on your work with confidence.)*

[upstream]: https://github.com/luca-jost-violins/General-Acoustic-Measurement-Setup
[upstream-issue]: https://github.com/luca-jost-violins/General-Acoustic-Measurement-Setup/issues/1
[gough-at]: https://acousticstoday.org/violin-acoustics-colin-e-gough/
[gough-pdf]: https://acousticstoday.org/wp-content/uploads/2016/06/Gough.pdf
[gough-supp]: https://acousticstoday.org/supplementary-text-violinacoustics-colin-e-gough/
[gough-media]: https://acousticstoday.org/violin-acoustics-media/
[gough-musica]: https://www.musica.ed.ac.uk/archive/2017/colin-gough/
[gough-site]: http://colingough.com/
[euphonics]: https://euphonics.org/
[euphonics-modes]: https://euphonics.org/5-3-signature-modes-and-formants/
[euphonics-ema]: https://euphonics.org/10-5-experimental-modal-analysis/
[strad3d]: https://strad3d.org/articles.html
[asa-cello]: https://acoustics.org/pressroom/httpdocs/135th/rossing.htm
[oberlin]: https://josephcurtinstudios.com/research/oberlin-workshop/
[oberlin-yt]: https://www.youtube.com/@oberlinacousticsworkshop9137
[curtin-rig]: https://josephcurtinstudios.com/research/measurement-rig/
[obiapp]: https://sites.google.com/view/oberlinacoustics/home
[stoppani]: http://www.stoppani.co.uk/Technical.htm
[schleske]: https://www.schleske.de/en/research/introduction-violin-acoustics/modal-analysis.html
[schleske-method]: https://www.schleske.de/en/research/introduction-violin-acoustics/sound-analysis/method.html
[free-free]: https://www.osti.gov/servlets/purl/1266149
