# Final QA

## Build

Version: 0.1.0 PRE-OFFICE RC
Commit: N/A - starter folder is not initialized as a Git repository
Date: 2026-09-22

## Gates

- Scope: PASS
- Core: PASS
- Metadata: PASS
- Automation contract: PASS
- Automated QA: PASS
- Office probe: PENDING PHYSICAL OFFICE EVIDENCE
- Real mapping: PENDING PHYSICAL OFFICE EVIDENCE
- Office pilot: PENDING PHYSICAL OFFICE EVIDENCE

## Test results

### Unit

PASS. ISBN validation/conversion, resolver, provider normalization/error handling,
cache, config safety, field mapper, and mock S-Lib adapter are covered.

### Integration

PASS. Provider failure isolation, offline cache hit, and force-refresh behavior
are covered.

### Packaging

PASS. PyInstaller produced:

- dist/SLibAssistant.exe
- dist/SLibProbe.exe

The application executable remained running during launch smoke until the QA
process deliberately closed it. SLibProbe executed successfully and produced its
expected output bundle; with no S-Lib window open on this machine it correctly
reported slib_detected=false.

### Guardrails

PASS. Automated checks cover:

- no direct MDB write path;
- no automatic Save invocation;
- wrong-window blocking;
- empty-value skip;
- abort;
- editable-control content redaction in the probe.

## Provider evidence

Open Library live lookup for ISBN 9789836276964 succeeded using the current
Search API and returned a bibliographic record.

Google Books returned HTTP 429 from the current network during live smoke.
This is treated as a provider-local failure; automated integration tests confirm
that another provider can still resolve the book.

## Known limitations

- Real S-Lib control IDs/classes are not yet known.
- UIA/Win32 field selectors remain deliberately unconfigured.
- Keyboard fallback tab order remains deliberately unconfigured.
- Dropdown mappings remain pending office evidence.
- No claim of real S-Lib autofill compatibility is made yet.

## Final status

**PRE-OFFICE RC**

All work that can be completed without physical S-Lib evidence is complete.
Proceed with OFFICE_PROBE_GATE.md.
