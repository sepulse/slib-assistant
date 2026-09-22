# AGENTS.md — S-Lib Assistant

Arahan ini terpakai kepada prime dan semua Chat On Steroids workers.

## Authority order

1. User instructions.
2. `GOAL.md`.
3. `REQUIREMENTS.md` dan guardrails.
4. `DECISIONS.md`.
5. Worker-specific task.
6. Implementation preference.

Jika bercanggah, ikut sumber yang lebih tinggi.

## Working mode

- Kerja autonomously hingga task worker selesai.
- Jangan berhenti untuk meminta confirmation rutin.
- Jangan mengembangkan scope tanpa sebab.
- Jangan ubah guardrails keselamatan.
- Jangan claim real S-Lib verification tanpa evidence daripada PC pejabat.

## Safety invariants

DILARANG:

- write/update/delete terus ke `SLIBV1001.mdb`;
- mengubah schema MDB;
- auto-click `Simpan`;
- hook/inject ke process S-Lib;
- modify executable/DLL S-Lib;
- fabricate metadata;
- overwrite field S-Lib dengan nilai kosong;
- coordinate-only automation tanpa fallback/validation jika ada pilihan lebih selamat;
- commit secrets/API keys.

## Required implementation properties

- ISBN validation mesti deterministic.
- Provider layer mesti modular.
- Satu provider gagal tidak boleh menggagalkan keseluruhan lookup.
- Setiap metadata field yang diisi mesti mempunyai provenance.
- Conflict mesti visible kepada operator.
- Missing mesti kekal missing.
- Autofill mesti verify window/form sebelum mutation.
- `ESC` / cancel path mesti wujud.
- Log tidak boleh mengandungi patron/student data.

## File ownership

Ikut `WORKER_PLAN.md`.

Worker tidak boleh edit file yang dimiliki worker lain kecuali:
- prime memberi arahan;
- perubahan kecil benar-benar diperlukan untuk compile/test;
- worker menyatakan perubahan itu dalam handoff.

## Testing rule

Jangan lapor "siap" tanpa menjalankan test yang relevan.

Handoff worker mesti dalam format:

```text
RESULT
...

CHANGES
...

VALIDATION
...

BLOCKERS
...
```

## Real S-Lib evidence rule

Mock adapter ≠ real S-Lib verification.

Apa-apa claim seperti:
- "field mapping confirmed"
- "UIA works"
- "dropdown mapping correct"
- "autofill stable"

hanya boleh dibuat selepas evidence PC pejabat.

Sebelum itu gunakan label:
- implemented;
- simulated;
- pending office verification.

## Documentation rule

Jika keputusan architecture berubah:
- update `DECISIONS.md`;
- update `PROJECT_STATE.md`;
- jika scope berubah, update `REQUIREMENTS.md`.

## No deploy rule

Projek ini local Windows utility. Jangan publish/deploy ke production environment tanpa arahan user.
