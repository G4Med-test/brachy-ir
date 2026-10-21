# brachy-ir

**Brachytherapy dose validation for Iridium-192 and Iodine-125 sealed
sources**, benchmarked against the TG-43 dosimetry formalism. Built on the
Geant4 `brachytherapy` example.

(The slide calls this test "Brachytherapy (I-192 and I-125)" — I-192 is a
typo for **Ir-192** (Iridium), confirmed by the source macros below.)

---

## 🔬 What this test does

A sealed brachytherapy source (selectable via the `Brachy*` detector/factory
classes: Flexisource and TG186 Ir-192 designs, Bebig Isoseed and Oncura 6711
I-125 designs) is simulated inside a water phantom. The radial/angular dose
distribution around the source is scored and compared to the TG-43 relative
dose tables (`TG43_relative_dose.C`, `brachy_relative_dose.C`).

## 📚 Reference

- Source: `geant-validation-tests/src/brachy-ir` (Geant4 `brachytherapy`
  example, extended for Ir-192/I-125 TG-43 validation).
- AAPM TG-43 dosimetry formalism for brachytherapy sources.

## Import notes

- `main.cc` comes from `Brachy.cc` in `geant-validation-tests/src/brachy-ir`
  (identical to the `brachy-ir.cc` entry point present in the same
  directory — only one copy is kept here). `include/`, `src/` are copied
  as-is.
- `macro/` contains the 11 macros found directly in that source tree
  (kept for reference, not used by CI — none of them are self-contained),
  plus 2 concrete, self-contained macros built from
  `geant-config-generator`'s real `template.conf` — see
  `validation/README.md` for why and how.
- `validation/parser.py` was **rewritten** for the `metadata()`/`parse()`
  module API that `ci-workflows/validation/export.py` actually calls (the
  first version, copied unmodified from
  `geant-config-generator/tests/geant4/brachy-ir/parser.py`, used the old
  `gts.BaseParser` class API — and shelled out to run a ROOT macro as a
  subprocess, now reproduced directly with `uproot` instead). See
  `validation/README.md` for details. The vendored `gts` package is no
  longer needed and was removed.
