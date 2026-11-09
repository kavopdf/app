# Audit state

Stage just finished: **7 — CONFIG (API level, SDK targets, build config)**
Date: 2026-11-09
New findings this stage: **5** (0 × P0, 2 × P1, 1 × P2, 2 × P3)

Stages 1–10 are run in order, one per invocation. Next: **stage 8** — DEAD CODE AND
RESOURCES: classes, methods and fields nothing references; strings and drawables nothing
uses; duplicated code that has drifted apart; paths that can never run.

| Stage | Status | New findings |
|---|---|---|
| 1 WIRING | done 2026-11-06 | 5 |
| 2 WIRING (2nd half) | done 2026-11-06 | 5 |
| 3 CRASH PATHS | done 2026-11-07 | 5 |
| 4 CRASH PATHS — engine | done 2026-11-08 | 5 |
| 5 SECURITY | done 2026-11-08 | 5 |
| 6 SECURITY (2nd half) | done 2026-11-09 | 5 |
| 7 CONFIG | done 2026-11-09 | 5 |
| 8 DEAD CODE | pending | — |
| 9 LOGIC | pending | — |
| 10 SYNTHESIS | pending | — |

Running total: 35 findings across stages 1–7 (36 `### P` headings, one of which is the
CORRECTION-adjacent P3 in stage 6).

Stage 7 headline: the app still targets API 35, and Play has required API 36 for every
update since 31 Aug 2026 — nothing can ship until that is raised. Second P1 is
`java.nio.file` in the engine on a `minSdk 24` build with no core-library desugaring, which
breaks PDF-to-text on Android 7.0/7.1.
