# Worker 3 — S-Lib Automation

## Objective

Implement safe S-Lib adapter architecture and diagnostic probe without claiming real-PC verification.

## Read first

- `/AGENTS.md`
- `/GOAL.md`
- `/docs/SLIB_FIELD_MAPPING.md`
- `/OFFICE_PROBE_GATE.md`

## Own

```text
src/slib_assistant/slib/**
tools/slib_probe/**
tests/unit/test_slib*
tests/integration/test_slib_mock*
```

## Required adapter API

Target shape:

```python
detect()
verify_new_record_form()
get_capabilities()
fill_text(field, value)
select_option(field, value)
fill_record(mapped_record)
abort()
```

## Deliverables

1. Adapter protocol/interface.
2. Mock adapter for full automated tests.
3. UIA/Win32 adapter skeleton.
4. Keyboard fallback adapter.
5. Window title/process validation.
6. Abort mechanism.
7. Empty-value skip behaviour.
8. Per-field result logging.
9. `SLibProbe` tool that can inspect:
   - window title;
   - process;
   - control tree/class names;
   - automation IDs/names if exposed;
   - focus/tab observations if possible.
10. Probe output machine-readable JSON.

## Hard constraints

- Do not write MDB.
- Do not invoke Save.
- Do not alter S-Lib installation.
- Coordinate click automation is last resort.
- Do not claim field IDs are confirmed until office probe evidence exists.

## Expected handoff

```text
RESULT
CHANGES
VALIDATION
BLOCKERS
```
