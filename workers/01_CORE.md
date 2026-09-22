# Worker 1 — Core App

## Objective

Implement application foundation without touching metadata provider internals or real S-Lib control mapping.

## Read first

- `/AGENTS.md`
- `/GOAL.md`
- `/docs/ARCHITECTURE.md`
- `/docs/REQUIREMENTS.md`
- `/WORKER_PLAN.md`

## Own

```text
src/slib_assistant/app.py
src/slib_assistant/config.py
src/slib_assistant/models.py
src/slib_assistant/cache.py
src/slib_assistant/ui/**
packaging/**
```

## Deliverables

1. Canonical models.
2. App state machine.
3. Config loader.
4. SQLite cache.
5. Preview UI.
6. Edit-before-fill.
7. Status indicators: confirmed/review/missing.
8. Application error presentation.
9. Packaging skeleton.
10. Unit tests for owned modules where appropriate.

## Constraints

- No direct MDB access.
- No auto-save.
- Do not implement metadata provider logic.
- Do not hardcode real S-Lib controls.
- UI must remain compact Windows utility, not dashboard.

## Expected handoff

```text
RESULT
CHANGES
VALIDATION
BLOCKERS
```
