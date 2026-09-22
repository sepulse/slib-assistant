# Technical Decisions

## D-001 — Companion app

S-Lib Assistant is a separate Windows utility. S-Lib remains system of record.

## D-002 — Database boundary

No direct write to `SLIBV1001.mdb` in V1.

## D-003 — Human save

Operator presses `Simpan` manually.

## D-004 — Barcode meaning

Barcode scanner provides ISBN only. ISBN is the lookup key, not embedded metadata.

## D-005 — Metadata strategy

Use multi-provider resolver with provenance and conflict detection.

Initial provider candidates:
- Google Books
- Open Library
- MARC/SRU where a stable source is available

## D-006 — Cache

Use local SQLite cache.

## D-007 — Automation strategy

Priority:

1. Win32/UI Automation
2. keyboard/focus fallback
3. coordinate automation only as last resort

## D-008 — Architecture boundary

Real S-Lib automation must sit behind an adapter interface so all other modules can be built/tested without office access.

## D-009 — Real verification wording

Before office probe:
- "implemented"
- "simulated"
- "pending office verification"

After office evidence only:
- "confirmed on S-Lib"

## D-010 — V1 UI

Compact Windows utility:
- scan field
- metadata preview
- source/conflict status
- edit
- `Isi S-Lib`

No complex dashboard.

## D-011 — Runtime baseline

V1 supports Python 3.11+ for development and uses PyInstaller for standalone
Windows executables.

## D-012 — Open Library integration

Use the current Open Library Search API for ISBN lookup. The legacy Books API is
not used as the primary path.

## D-013 — Provider availability

Provider HTTP errors, rate limits, malformed responses, and not-found results are
isolated per provider. A failed provider does not invalidate successful results
from another provider.
