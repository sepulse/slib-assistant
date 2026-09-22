# Implementation Plan — S-Lib Assistant

## Objective

Build a Windows companion app:

```text
Scan ISBN
→ Validate/normalize
→ Local cache
→ Multi-provider lookup
→ Normalize/merge
→ Preview/conflict review
→ Isi S-Lib
→ Operator review
→ Operator presses Save
```

## Phase 0 — Bootstrap
Estimated: 30–45 min

- repo structure;
- dependency management;
- config;
- logging;
- fixtures;
- contracts.

## Phase 1 — S-Lib adapter contract
Estimated: 1–2 h

- adapter interface;
- mock adapter;
- safe window verification;
- UIA/Win32 skeleton;
- keyboard fallback;
- probe utility design.

## Phase 2 — ISBN engine
Estimated: 45–60 min

- USB HID input;
- ISBN-10/13;
- checksum;
- normalization;
- invalid barcode handling.

## Phase 3 — Providers
Estimated: 2–3 h

- Google Books;
- Open Library;
- MARC/SRU abstraction;
- timeout/error isolation.

## Phase 4 — Resolver
Estimated: 1.5–2.5 h

Canonical fields:

```text
isbn13
isbn10
title
subtitle
authors[]
corporate_author
publisher
publication_place
publication_year
edition
language
page_count
physical_description
dimensions
series
subjects[]
ddc
lcc
notes
price
sources[]
field_confidence{}
```

Rules:
- merge;
- normalize;
- provenance;
- conflict;
- no fabrication.

## Phase 5 — Cache
Estimated: 45–60 min

SQLite:
- books
- provider_results
- lookup_log
- settings

## Phase 6 — Preview UI
Estimated: 1.5–2 h

- scan field;
- metadata;
- confirmed/review/missing;
- edit;
- refresh;
- Isi S-Lib.

## Phase 7 — Field mapping
Estimated: 1–2 h

Map canonical fields to S-Lib.

## Phase 8 — Autofill
Estimated: 2–4 h

- verify S-Lib;
- fill non-empty fields;
- dropdown mapping;
- abort;
- per-field logs;
- never Save.

## Phase 9 — QA
Estimated: 2–3 h

20–30 mixed books + failure cases.

## Phase 10 — Packaging
Estimated: 1–2 h

- Windows executable;
- local config;
- writable cache/log directory;
- probe build.

## Practical estimate

- PoC: 2–3 hours
- MVP: 8–12 active hours
- Stable office build: 12–18 active hours
- Worst-case legacy control hardening: 2–3 workdays

The biggest uncertainty is real S-Lib control behavior.
