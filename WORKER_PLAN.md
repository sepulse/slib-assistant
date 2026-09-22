# Worker Plan

## Prime / Integrator

Owns:
- repository integration;
- contracts shared antara modules;
- `PROJECT_STATE.md`;
- `DECISIONS.md`;
- release gates;
- final cross-module QA.

Prime boleh edit mana-mana file bila perlu untuk integration.

---

## Worker 1 — Core App

Task file:
`workers/01_CORE.md`

Owns:

```text
src/slib_assistant/app.py
src/slib_assistant/config.py
src/slib_assistant/models.py
src/slib_assistant/cache.py
src/slib_assistant/ui/**
packaging/**
```

Primary objective:
- application shell;
- canonical models;
- config;
- cache;
- preview/edit UI;
- packaging skeleton.

---

## Worker 2 — Metadata

Task file:
`workers/02_METADATA.md`

Owns:

```text
src/slib_assistant/isbn.py
src/slib_assistant/providers/**
src/slib_assistant/resolver.py
tests/fixtures/metadata/**
tests/unit/test_isbn*
tests/unit/test_provider*
tests/unit/test_resolver*
```

Primary objective:
- ISBN validation;
- providers;
- normalization;
- provenance;
- conflict resolver.

---

## Worker 3 — S-Lib Automation

Task file:
`workers/03_SLIB_AUTOMATION.md`

Owns:

```text
src/slib_assistant/slib/**
tools/slib_probe/**
tests/unit/test_slib*
tests/integration/test_slib_mock*
```

Primary objective:
- adapter interfaces;
- mock adapter;
- UIA/Win32 implementation skeleton;
- keyboard fallback;
- diagnostic/probe utility.

---

## Worker 4 — QA

Task file:
`workers/04_QA.md`

Owns:

```text
tests/**
qa/**
```

Exception:
QA must not overwrite tests explicitly owned by Metadata/S-Lib workers without coordination.

Primary objective:
- acceptance fixtures;
- integration tests;
- guardrail tests;
- packaging smoke tests;
- release evidence.

---

## Merge/order dependency

Recommended:

1. Core + Metadata + S-Lib work in parallel.
2. QA begins against contracts/mocks immediately.
3. Prime integrates.
4. QA reruns full suite.
5. Probe package built.
6. Office gate.
7. Prime completes real adapter mapping.
8. Final QA.
