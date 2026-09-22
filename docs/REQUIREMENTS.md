# Requirements

## In scope V1

- barcode scanner ISBN input;
- manual ISBN input;
- ISBN validation;
- multi-provider lookup;
- resolver;
- provenance;
- conflict handling;
- local cache;
- preview/edit;
- S-Lib autofill;
- logging;
- Windows executable;
- diagnostic probe.

## Out of scope V1

- direct MDB write;
- auto-save;
- patron/circulation automation;
- OCR price;
- cloud sync;
- bulk migration.

## Functional requirements

- FR-001 scanner HID input
- FR-002 ISBN-10/13 validation
- FR-003 multi-provider support
- FR-004 provider failure isolation
- FR-005 provenance per filled field
- FR-006 conflict detection
- FR-007 no fabrication
- FR-008 preview/edit
- FR-009 local cache
- FR-010 S-Lib window verification
- FR-011 bibliographic field fill
- FR-012 missing values never overwrite
- FR-013 abort
- FR-014 no auto-save
- FR-015 safe logging

## Non-functional

- cache hit target <1 sec;
- ordinary online lookup target <5 sec;
- modular provider layer;
- modular S-Lib adapter;
- stable package should not require global Python install;
- safe degradation when offline.
