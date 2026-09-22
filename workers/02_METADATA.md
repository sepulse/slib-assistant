# Worker 2 — Metadata

## Objective

Implement ISBN → canonical metadata pipeline.

## Read first

- `/AGENTS.md`
- `/GOAL.md`
- `/docs/ARCHITECTURE.md`
- `/docs/REQUIREMENTS.md`
- `/docs/SLIB_FIELD_MAPPING.md`

## Own

```text
src/slib_assistant/isbn.py
src/slib_assistant/providers/**
src/slib_assistant/resolver.py
tests/fixtures/metadata/**
tests/unit/test_isbn*
tests/unit/test_provider*
tests/unit/test_resolver*
```

## Deliverables

1. ISBN-10/13 normalization.
2. Checksum validation.
3. Google Books provider.
4. Open Library provider.
5. MARC/SRU provider abstraction; concrete provider only if reliable public endpoint is available.
6. Timeout/error isolation.
7. Canonical normalization.
8. Provenance per field.
9. Conflict detection.
10. Missing-data preservation.
11. Fixtures for:
   - Malaysian books;
   - imported books;
   - ISBN-10;
   - incomplete metadata;
   - conflicts.

## Rules

- Never fabricate metadata.
- One provider failure must not fail lookup.
- External source data must be normalized but raw evidence retained.
- Do not assume DDC if absent.
- Price is not part of ISBN and is out of scope V1 default autofill.

## Expected handoff

```text
RESULT
CHANGES
VALIDATION
BLOCKERS
```
