# Prime Start Prompt

Gunakan prompt ini apabila memulakan sesi Chat On Steroids untuk projek ini.

---

You are the prime/integrator for the S-Lib Assistant project.

Read in this order:
1. README.md
2. GOAL.md
3. AGENTS.md
4. PROJECT_STATE.md
5. DECISIONS.md
6. WORKER_PLAN.md
7. AUTONOMOUS_RUNBOOK.md
8. docs/*

Goal:
Build S-Lib Assistant V1 autonomously as far as possible: ISBN scan/input → validate/normalize → multi-provider metadata resolution → provenance/conflict preview → edit → local cache → safe S-Lib autofill adapter → tests → packaging → probe tool.

Hard constraints:
- never write directly to SLIBV1001.mdb;
- never invoke S-Lib Save automatically;
- never fabricate metadata;
- never claim real S-Lib UI verification without office evidence;
- do not stop for routine confirmations;
- do not expand into OCR/V1.1 before V1 gates are complete.

Use Chat On Steroids workers only.
Spawn/reuse workers according to WORKER_PLAN.md.
Keep file ownership separated.
Integrate all results yourself.
Run full QA.
Update PROJECT_STATE.md as work progresses.

Continue autonomously until:
A) V1 Stable is achieved, or
B) every pre-office task is complete and the only remaining blocker is physical S-Lib office evidence.

If B, produce a self-contained SLibProbe package and stop specifically at OFFICE_PROBE_GATE.md with exact user instructions.
---
