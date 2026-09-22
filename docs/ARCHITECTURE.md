# Architecture

```text
USB Scanner
   ↓
ISBN Engine
   ↓
Cache ────── hit ─────────────┐
   │ miss                     │
   ↓                          │
Providers                     │
   ↓                          │
Resolver                      │
   ↓                          │
Canonical BookMetadata ◄──────┘
   ↓
Preview/Edit UI
   ↓
Field Mapper
   ↓
S-Lib Adapter
   ├─ Mock
   ├─ UIA/Win32
   └─ Keyboard fallback
   ↓
S-Lib V1001r6
```

## Boundaries

Assistant owns:
- lookup;
- normalization;
- preview;
- cache;
- autofill.

S-Lib owns:
- persistence;
- internal validation;
- accession/control numbers;
- final Save.

## Confidence states

- HIGH
- MEDIUM
- REVIEW
- MISSING

Confidence is rule-based evidence status, not an AI guess.

## Suggested stack

Initial suggestion:
- Python 3.11+
- pywinauto
- Python standard-library HTTP client
- dataclasses
- SQLite
- PyInstaller

Stack may change if actual S-Lib controls demand it.
