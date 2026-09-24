# Changelog

## 0.3.4 — Raw Input scanner observer

- Replaced S-Lib textbox polling with Windows Raw Input HID observation.
- Scanner input is no longer intercepted, redirected, cleared or rewritten.
- S-Lib receives the ISBN normally while Assistant receives a parallel copy.
- Detection is independent of S-Lib control IDs/focus mapping and therefore
  does not depend on the legacy VB6 textbox exposing the expected automation ID.
- A scan is routed only when S-Lib is foreground, timing is scanner-like and
  ISBN-10/ISBN-13 checksum validation succeeds.
- Added idle-finalization for scanners with no Enter/Tab suffix.

## 0.3.3 — Polling scanner monitor

- Removed the low-level keyboard hook used by the 0.3.2 office pilot.
- Scanner Mode now observes the confirmed S-Lib ISBN textbox (control ID 59)
  instead of intercepting keystrokes.
- Barcode input always goes to S-Lib first, so Scanner Mode cannot swallow it.
- A valid ISBN is queued directly to S-Lib Assistant; only after the Assistant
  acknowledges receipt is that exact ISBN cleared from the S-Lib textbox.
- Added visible Scanner Mode status messages so office validation can confirm
  whether the real ISBN/ISSN control has been detected before scanning.

## 0.3.2 — Office scanner routing pilot

- Retired the separate coordinate-based Scanner Guard pilot.
- Added Scanner Mode directly inside S-Lib Assistant on Windows.
- Scanner digits are allowed into S-Lib while observed; only a confirmed
  ISBN terminator is intercepted after the S-Lib ISBN field has been safely
  restored to its exact pre-scan value.
- Successful scans are delivered directly to the Assistant ISBN field and
  trigger lookup without mouse coordinates or synthetic keyboard input.
- Routing is fail-open: if validation/restoration is uncertain, the barcode
  remains in S-Lib and Enter/Tab is allowed through normally.

## 0.2.0 — 2026-09-22

- Public GitHub source/release distribution.
- Safe self-update checks against stable semantic-version GitHub Releases.
- SHA256 verification before update installation.
- External \`SLibUpdater.exe\` with backup and rollback on replacement failure.
- Automatic update check on startup, configurable in \`config.toml\`.
- Manual update check under **Bantuan → Semak Kemas Kini**.
- Tooltips for ISBN actions, metadata fields, confidence status, abort and S-Lib fill.
- About dialog with application version.
- Release packaging scripts for Windows app, updater, office probe and office handoff.

The S-Lib autofill control mapping remains pending physical office probe evidence.

## 0.1.0 — 2026-09-22

- Initial PRE-OFFICE RC.
- ISBN validation and normalization.
- Google Books and Open Library providers.
- Multi-provider resolver with provenance/conflict handling.
- SQLite metadata cache.
- Editable metadata preview.
- Read-only S-Lib office probe.
- Safe automation adapter scaffolding with no direct MDB writes and no auto-save.
