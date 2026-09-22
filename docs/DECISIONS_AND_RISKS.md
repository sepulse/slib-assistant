# Decisions and Risks

## Decisions

- companion app;
- no direct MDB write;
- human Save;
- multi-provider metadata;
- local cache;
- adapter abstraction;
- UIA/Win32 before keyboard fallback;
- physical S-Lib verification required before claiming real compatibility.

## Risks

### Legacy controls
Mitigation: Win32/UIA + keyboard fallback + probe.

### Incomplete metadata
Mitigation: multiple providers + missing state.

### Conflicting editions/reprints
Mitigation: provenance + review.

### Offline
Mitigation: cache.

### Scanner variations
Mitigation: configurable terminator/manual submit.

### School catalog policy
Mitigation: do not infer local call-number/category rules.

### Character encoding
Mitigation: Unicode internally; verify S-Lib behavior in office.
