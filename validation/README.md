# Portal JSON parser

Rewritten from `geant-config-generator/tests/geant4/brachy-ir/parser.py`
(old `gts.BaseParser`, which merged repeated-seed job groups and shelled out
to `root -l -b -q brachy_relative_dose.C`) for the module-level
`metadata()`/`parse()` API that `ci-workflows/validation/export.py`
actually calls. `brachy_relative_dose.C`'s radial-binning of the `"h20"` 2D
energy-deposition histogram is reproduced directly with `uproot` (no ROOT
binary, no PyROOT on the runner); there is no job-group merge any more.

## The macros: not self-contained in their original form, and why

None of the macros shipped in `geant-validation-tests/src/brachy-ir`
(`FlexiSourceMacro.mac`, `IodineSourceMacro.mac`, …) are self-contained —
each does `/control/execute <name>_primary.mac` for its GPS source
definition, rejected by `read_macro()`. The real, working configuration is
`geant-config-generator/tests/geant4/brachy-ir/template.conf`, which also
adds a `/testem/phys/addPhysics %PHYSLIST%` line **missing** from every
`geant-validation-tests` macro (physics-list selection only happens through
config-generator's own templating), and expands `%RADSOURCE%` to a literal
`include <file>` directive, evaluated by config-generator's own templating
layer before Geant4 ever sees the macro — not a native Geant4 command.

`macro/Flexi_emstandard_opt0.mac` and `macro/Oncura_emstandard_opt0.mac`
reproduce `template.conf` with the physics list fixed to `emstandard_opt0`,
with `%RADSOURCE%` inlined directly:

- **Flexi** (Ir-192): `geant-config-generator/tests/geant4/brachy-ir/iridium_source_primary.mac`
  (identical to `geant-validation-tests/src/brachy-ir/iridium_source_primary.mac`)
  — a tabulated multi-line gamma spectrum from Ir-192 decay.
- **Oncura** (I-125): `geant-config-generator/tests/geant4/brachy-ir/includes/oncura_source`
  — an actual **radioactive ion decay** (`/gps/ion 53 125 53 0.`, Iodine-125,
  letting `G4RadioactiveDecay` generate the real decay spectrum) and the
  physically-correct Oncura 6711 seed dimensions (0.247 mm radius,
  1.397 mm half-length). This is **not** the same source definition as
  `geant-validation-tests/src/brachy-ir/IodineSourceMacro.mac`
  (`/control/execute iodine_source_primary.mac`), which approximates I-125
  as a crude mono-energetic 35 keV gamma at the (wrong, Flexi-sized)
  0.30 mm/1.75 mm geometry — the config-generator version was used here as
  the more physically faithful, actually-validated one.

`params.conf`'s other 4 physics lists (`emstandard_opt3`/`opt4`,
`empenelope`, `emlivermore`) and the `Leipzig`/`TG186` source variants
(not part of config-generator's own production sweep, which only covers
Flexi/Oncura — matching the slide's "Ir-192 and I-125") are not included;
generate more macros the same way if needed.

## The radial binning

`brachy_relative_dose.C` loops ROOT bins `k=0..800` over an 801-bin axis
(ROOT bins are 1-indexed, 1..801) — that is, bin 0 (**underflow**) through
bin 800, one short of the actual last bin (801). Reproducing that exact
off-by-one via `uproot` would require matching ROOT's underflow bin-center
convention bin-for-bin; since the physical effect is negligible (the
underflow bin is always empty at this geometry, and the dropped outer bin
is far outside the 10 cm region of interest), this port instead sums over
the full 801 **real** bins (`flow=False`), a deliberate, documented
deviation from the original's literal loop bounds — the rest of the
algorithm (4×radius-mm binning, normalization to the 1 cm/90° reference
point, `R > 0.05 cm` cutoff) is unchanged.
