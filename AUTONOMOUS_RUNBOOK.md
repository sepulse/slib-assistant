# Autonomous Runbook

Dokumen ini untuk prime Chat On Steroids.

## Operating model

Prime bertindak sebagai:
- integrator;
- task router;
- reviewer;
- release gate owner.

Workers bertindak sebagai parallel implementers/reviewers.

## Start sequence

### 1. Recon

Prime baca:

```text
README.md
GOAL.md
AGENTS.md
PROJECT_STATE.md
WORKER_PLAN.md
docs/*
```

Kemudian inspect repository state.

### 2. Freeze initial contracts

Sebelum spawn workers, prime pastikan sekurang-kurangnya kontrak berikut jelas:

- canonical `BookMetadata`;
- provider interface;
- resolver output;
- cache API;
- S-Lib adapter API;
- field mapping;
- error/result types.

Jika tiada code lagi, prime boleh scaffold interface/contracts dahulu atau assign kepada Core worker dengan ownership jelas.

### 3. Spawn workers

Default parallel workers:

- Core
- Metadata
- S-Lib Automation
- QA

Jangan spawn lebih ramai semata-mata untuk speed jika ownership bertindih.

### 4. Worker independence

Setiap worker:
- baca `AGENTS.md`;
- baca worker task;
- edit hanya ownership area;
- run tests;
- return structured handoff.

### 5. Integrate

Prime:
- review diffs;
- reconcile contracts;
- run whole-suite tests;
- fix integration;
- update `PROJECT_STATE.md`.

### 6. Autonomous continuation

Jika tests merah:
- diagnose;
- fix;
- rerun.

Jika implementation incomplete:
- message/revive worker yang relevan atau prime lengkapkan.

Jangan berhenti kepada user untuk isu biasa.

### 7. Physical gate

Apabila segala yang boleh disiapkan tanpa PC pejabat selesai:

- build `SLibProbe.exe` atau diagnostic script;
- hasilkan `probe-output.json` format;
- lengkapkan `OFFICE_PROBE_GATE.md`;
- package release candidate;
- update `PROJECT_STATE.md`.

Pada titik ini sahaja prime boleh berhenti untuk menunggu output PC pejabat.

### 8. Final office integration

Selepas probe output tersedia:

- finalize real control mapping;
- build adapter;
- run controlled acceptance;
- update mapping;
- execute release gates.

## Stop conditions

Prime hanya stop dan minta user input jika salah satu benar:

1. Physical S-Lib evidence wajib.
2. School catalog policy diperlukan.
3. Secret/API credential diperlukan.
4. Irreversible external action diperlukan.
5. Requirement bercanggah dan tiada safe default.

## Anti-patterns

Jangan:
- spawn workers yang edit file sama;
- biar worker design architecture masing-masing tanpa contract;
- claim stable build hanya kerana unit tests pass;
- tambah OCR/V1.1 sebelum V1 gate hijau;
- optimize UI sebelum resolver + adapter contract stabil.
