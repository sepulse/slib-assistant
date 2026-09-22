# Release Gates

## Gate 0 — Scope

- [x] No direct MDB write.
- [x] No auto-save.
- [x] No patron data.
- [x] No S-Lib file modification.

## Gate 1 — Core

- [x] App starts.
- [x] Config loads.
- [x] Canonical models stable.
- [x] SQLite cache works.
- [x] Preview/edit works.

## Gate 2 — ISBN + metadata

- [x] ISBN-10 validation.
- [x] ISBN-13 validation.
- [x] normalization.
- [x] >=2 provider support.
- [x] provider timeout/error isolation.
- [x] provenance.
- [x] conflict detection.
- [x] missing remains missing.

## Gate 3 — Automation contract

- [x] Mock adapter passes.
- [x] wrong window blocks.
- [x] empty value does not overwrite.
- [x] abort works.
- [x] Save is never invoked.
- [x] probe utility builds.

## Gate 4 — Automated QA

- [x] unit tests pass.
- [x] integration tests pass.
- [x] guardrail tests pass.
- [x] packaging smoke pass.
- [x] QA evidence written.

## Gate 5 — Office probe

- [ ] S-Lib process detected.
- [ ] `Kemaskini Bahan` window detected.
- [ ] controls captured.
- [ ] tab/focus behavior captured.
- [ ] dropdown behavior captured.
- [ ] no record saved during probe.

## Gate 6 — Real S-Lib mapping

- [ ] ISBN field confirmed.
- [ ] title field confirmed.
- [ ] author fields confirmed.
- [ ] publisher/year/edition fields confirmed.
- [ ] physical description fields confirmed.
- [ ] dropdown mappings confirmed where enabled.
- [ ] keyboard fallback confirmed.

## Gate 7 — Office pilot

Start with 10 books:

- [ ] 0 unintended saves.
- [ ] 0 database corruption.
- [ ] wrong-window protection works.
- [ ] operator can review before save.
- [ ] errors recoverable.

Only then expand to 30–50 books.

## Release status vocabulary

- **PRE-OFFICE RC** — all automated gates green, office probe pending.
- **OFFICE-VERIFIED RC** — real S-Lib mapping proven.
- **V1 STABLE** — office pilot passed.
