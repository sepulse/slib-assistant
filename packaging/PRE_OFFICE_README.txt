S-Lib Assistant 0.2.0 - PRE-OFFICE RC

This package is ready for ISBN lookup, metadata preview/edit, cache, and
pre-office testing.

This bundle also includes SLibUpdater.exe. Keep SLibUpdater.exe in the same
folder as SLibAssistant.exe so future public GitHub releases can be installed
through Bantuan -> Semak Kemas Kini.

The Isi S-Lib action is deliberately locked until the real S-Lib V1001r6
control mapping is captured on the office PC.

Guardrails:
- no direct SLIBV1001.mdb writes
- no automatic Simpan
- no fabricated metadata
- missing values are not used to overwrite S-Lib

Next gate:
Run the separate SLibProbe office package on the office PC.
