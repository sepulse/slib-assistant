# Changelog

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
