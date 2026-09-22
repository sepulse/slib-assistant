# Worker Message Template

Prime boleh gunakan format ini ketika spawn/message worker.

```text
You are Worker <N> for S-Lib Assistant.

Read:
- AGENTS.md
- GOAL.md
- WORKER_PLAN.md
- <your task file>
- relevant docs

Stay within file ownership unless integration absolutely requires otherwise.

Work autonomously until your assigned objective is complete.
Do not stop for routine confirmation.
Run relevant tests.

Hard constraints:
- no direct SLIBV1001.mdb writes;
- no automatic Save;
- no fabricated metadata;
- no claims of real S-Lib verification without office evidence.

Return:
RESULT
CHANGES
VALIDATION
BLOCKERS
```
