# Audit state

Stage just finished: **3 — CRASH PATHS**
Date: 2026-11-07
New findings this stage: **5** (0 × P0, 0 × P1, 4 × P2, 1 × P3)

Stages 1–10 are run in order, one per invocation. Next: **stage 4** — crash paths in
the PDF engine (`engine/*.java`): glyph and text arrays, font and resource lookups,
page tree walks, and every place a malformed PDF could reach an unchecked index.

| Stage | Status | New findings |
|---|---|---|
| 1 WIRING | done 2026-11-06 | 5 |
| 2 WIRING (2nd half) | done 2026-11-06 | 5 |
| 3 CRASH PATHS | done 2026-11-07 | 5 |
| 4 CRASH PATHS — engine | pending | — |
| 5 SECURITY | pending | — |
| 6 SECURITY (2nd half) | pending | — |
| 7 CONFIG | pending | — |
| 8 DEAD CODE | pending | — |
| 9 LOGIC | pending | — |
| 10 SYNTHESIS | pending | — |
