# Reference data for sizing the rig

Gathered while checking whether the large end of this rig is pointed at the
right frequencies. The short version: **published acoustics for the violin
family stops at the viola**, so the cello is the nearest well-documented
instrument to a bass viol and is the best available proxy.

## Instrument dimensions

| | body | lower bout | rib depth | source |
|---|---|---|---|---|
| violin | 355 | 208 | 30 | trade standard |
| viola | 410 | 240 | 34 | trade standard |
| treble viol | 370 | 230 | 62 | mid-range for surviving instruments |
| tenor viol | 490 | 290 | 88 | " |
| bass viol | 660 | 380 | 125 | " |
| **cello (4/4)** | **755** | **440** | **~114** | Aitchison & Mnatzaganian; Alabaster |

A cello is dimensionally very close to a bass viol — slightly longer and wider,
slightly shallower ribs. `CELLO` is now a preset, and it builds and stands.

## Where the modes are

This is what matters for the rig, because it sets the band the arm must not
ring in and the band the software has to plot.

| mode | violin | cello |
|---|---|---|
| A0 (Helmholtz air) | ~272 Hz | **~93-120 Hz** |
| CBR | ~407 Hz | — |
| B1- / B1+ | ~462 / 551 Hz | B1 is the highest peak **below 300 Hz** |
| bridge hill | ~2.3 kHz | two hills, ~1 kHz and 2-2.3 kHz |
| bridge sway / bend / bounce | — | 1.5 / 2.2 / 3.1 kHz (Reinicke) |

Cello modes have been measured up to ~5 kHz, with 61 individual modes counted
below 1.5 kHz.

### This breaks the shipped software settings

`ref/upstream/GMS_template.txt` plots from **200 Hz** (`X Range` starts at
2.0E+2). A cello or bass viol's A0 sits at 93-120 Hz — **below the bottom of
the default plot**. The single most diagnostic low mode would simply not be on
screen.

Also `Sample time = 0.3 s`, which is 3.3 Hz of native resolution. At 93 Hz that
is 3.6% — usable but coarse for a sharp air mode. Both want changing for
anything cello-sized.

## The hammer: 2 g is right after all

I had flagged the 2.1 g hammer as suspiciously light and possibly a scaling
gap. It is not. Joseph Curtin's Impulse Measurement Rig uses a PCB 086C80
impulse hammer with "a head weighing just a few grams", tapping the bridge.
A few grams is professional practice, so the upstream hammer is deliberate.

What remains open is *energy*, not bandwidth: a few-gram head is fine for
exciting a wide band, but whether it puts enough into a cello-sized top is
untested — see below.

## Nobody else does this size

Curtin's rig — the reference instrument in this field — states it accommodates
"violins and violas of any size". **Cellos are not supported.** Strad3D's
entire dataset is violins. The ObiApp analysis software is described as being
for violins.

So extending a tap rig to cello and gamba size is not a solved problem being
reimplemented here. That is worth knowing before trusting the bass viol preset:
there is no published rig geometry to check it against.

## How large instruments are supported for modal work

Free-free conditions are the norm: softly supported on foam, or hung on
elastic/bungee. The rule of thumb is that the first flexible mode should be
about ten times the highest rigid-body mode for the support to be ignorable.

This rig assumes the instrument lies on its back on the bench, which is not a
free-free condition. For a violin the difference is small; for a cello-sized
instrument resting its ribs on a bench the contact damping is proportionally
larger. Worth a controlled comparison before trusting absolute numbers at the
large end.

## Sources

### Violin family acoustics

- Colin Gough, [*Violin Acoustics*, Acoustics Today (2016)](https://acousticstoday.org/violin-acoustics-colin-e-gough/)
  — [PDF](https://acousticstoday.org/wp-content/uploads/2016/06/Gough.pdf),
  [supplementary text](https://acousticstoday.org/supplementary-text-violinacoustics-colin-e-gough/),
  [media](https://acousticstoday.org/violin-acoustics-media/)
- Colin Gough, [*Violin acoustics: an introduction and recent developments*](https://www.musica.ed.ac.uk/archive/2017/colin-gough/) (MusICA seminar)
- Colin Gough, [colingough.com](http://colingough.com/) and [violinacoustics.com](https://violinacoustics.com/)
- Jim Woodhouse, [*Euphonics*](https://euphonics.org/) —
  [signature modes and formants](https://euphonics.org/5-3-signature-modes-and-formants/),
  [experimental modal analysis](https://euphonics.org/10-5-experimental-modal-analysis/)
- [Modal analysis of violins and cellos](https://acoustics.org/pressroom/httpdocs/135th/rossing.htm), Acoustical Society of America
- George Bissinger's papers and datasets, [strad3d.org](https://strad3d.org/articles.html)

### Measurement practice

- Joseph Curtin, [Impulse Measurement Rig](https://josephcurtinstudios.com/research/measurement-rig/)
- [VSA-Oberlin Acoustics Workshop](https://josephcurtinstudios.com/research/oberlin-workshop/)
  and its [YouTube channel](https://www.youtube.com/@oberlinacousticsworkshop9137)
- [ObiApp](https://sites.google.com/view/oberlinacoustics/home), Chris Rogers and Joseph Curtin
- George Stoppani, [acoustic analysis software](http://www.stoppani.co.uk/Technical.htm)
  — Acquisition, ModeFit, ModeShape, FRFOverlay, GS Spectrum Analyser
- Martin Schleske, [modal analysis](https://www.schleske.de/en/research/introduction-violin-acoustics/modal-analysis.html)
  and [sound analysis method](https://www.schleske.de/en/research/introduction-violin-acoustics/sound-analysis/method.html)
- [Support conditions for free boundary-condition modal testing](https://www.osti.gov/servlets/purl/1266149)

### Instrument dimensions

- [Cello measurement — Aitchison & Mnatzaganian](https://www.aitchisoncellos.com/cello-measurement/)
- [Cello specifications — Alabaster Handcrafted Instruments](https://guitars.davidalabaster.com/cello-specification-pricing/)
