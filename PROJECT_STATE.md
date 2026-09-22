# Project State

## Current phase

**PRE-OFFICE RC**

## Confirmed facts

- Target app: S-Lib V1001r6
- Release shown: Rel 20201201
- Data file shown: `SLIBV1001.mdb`
- Barcode scanner currently supplies ISBN only
- Other bibliographic fields are manually keyed in
- User wants companion automation, not new library system
- PC office cannot currently be controlled through Chat On Steroids
- Real S-Lib control tree has not yet been captured
- Windows executables build successfully on Python 3.11 / Windows 10
- GitHub repository is public for source and release distribution
- Safe self-update path is implemented through public GitHub Releases
- Open Library live lookup succeeds with the current Search API
- Google Books provider is implemented and failure-isolated; the current network returned HTTP 429 during live smoke

## Current decision

All pre-office implementation is complete. The project is intentionally stopped
at the office probe gate because real S-Lib control mapping is now the remaining
dependency.

## Completed

- initial implementation plan
- requirements
- architecture
- field mapping draft
- QA plan
- worker/autonomous orchestration docs
- repository/source scaffold
- canonical models and application state
- ISBN-10/ISBN-13 validation and normalization
- Google Books and Open Library providers
- MARC/SRU provider abstraction
- multi-provider resolver with provenance/conflict handling
- local SQLite cache
- compact preview/edit UI
- mock S-Lib adapter
- UIA/Win32 adapter skeleton
- keyboard fallback contract
- read-only SLibProbe utility
- automated unit/integration/guardrail suite
- PyInstaller Windows builds
- pre-office QA evidence
- tooltip/help affordances for primary UI actions
- startup/manual update check
- SHA256-verified update package download
- external updater with backup/rollback

## Pending

- office control capture
- real adapter mapping
- office acceptance

## Blockers

Physical office verification is now the only blocker.

Run the packaged SLibProbe on the office PC with S-Lib open at
Kemaskini Bahan -> Data Baru, then return its output folder.

## Scope lock

V1 excludes:
- direct MDB write
- auto-save
- OCR price
- circulation/patron workflows
- batch migration
