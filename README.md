# S-Lib Assistant

Windows companion app untuk mempercepatkan proses key-in bahan ke **S-Lib V1001r6 (Rel 20201201)**.

## Objektif

Ubah aliran kerja daripada:

> scan ISBN → cari maklumat buku → key-in banyak field secara manual

kepada:

> **scan ISBN → metadata ditemui → preview/edit → satu klik isi S-Lib → staf semak → staf tekan Simpan**

S-Lib kekal sebagai sistem rekod rasmi.

## Guardrails V1

- Jangan tulis terus ke `SLIBV1001.mdb`.
- Jangan auto-click `Simpan`.
- Jangan fabricate metadata.
- Jangan ubah fail pemasangan S-Lib.
- Jangan deploy atau ubah production S-Lib.
- Autofill hanya jika window/form S-Lib yang betul telah disahkan.
- Operator manusia kekal sebagai checkpoint akhir.

## Cara guna repo ini dengan Chat On Steroids

1. Baca `GOAL.md`.
2. Baca `AGENTS.md`.
3. Baca `AUTONOMOUS_RUNBOOK.md`.
4. Prime buka `PROJECT_STATE.md`.
5. Prime spawn workers berdasarkan `WORKER_PLAN.md`.
6. Setiap worker baca task sendiri di `/workers`.
7. Prime integrasi hasil dan jalankan gates dalam `RELEASE_GATES.md`.
8. Berhenti hanya pada `OFFICE_PROBE_GATE.md` jika real S-Lib control data masih belum tersedia.

## Dokumen utama

- `GOAL.md` — objective tunggal projek.
- `AGENTS.md` — peraturan untuk semua workers.
- `AUTONOMOUS_RUNBOOK.md` — cara prime menjalankan projek tanpa berhenti.
- `WORKER_PLAN.md` — pembahagian kerja dan ownership.
- `PROJECT_STATE.md` — status semasa dan blockers.
- `DECISIONS.md` — keputusan teknikal.
- `RELEASE_GATES.md` — syarat sebelum release.
- `OFFICE_PROBE_GATE.md` — langkah physical test di PC pejabat.
- `docs/IMPLEMENTATION_PLAN.md`
- `docs/REQUIREMENTS.md`
- `docs/ARCHITECTURE.md`
- `docs/SLIB_FIELD_MAPPING.md`
- `docs/TEST_AND_ACCEPTANCE.md`
- `docs/DECISIONS_AND_RISKS.md`

## Status awal

**Phase:** PRE-OFFICE RC  
**Real S-Lib office control inspection:** belum dibuat  
**Coding:** pre-office implementation siap  
**Automated QA:** hijau  
**Windows build:** SLibAssistant.exe + SLibProbe.exe  
**MDB mutation:** dilarang untuk V1  
**Auto-save:** dilarang untuk V1
