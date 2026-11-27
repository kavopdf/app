# P2W Watchdog - Run Report

**28 Nov 2026 · 03:14 IST**

> **1 stage(s) stopped: matrix** - and the gap is a stale half, not one missing file.

## Stages

| stage | state | progress | age |
|:--|:--|--:|--:|
| measure-google | done | 214 of 214 | 5.7 h |
| matrix | **stopped** | 213 of 214 (37 on the engine in the tree) | 5.5 h |
| classify | superseded |  | 1.0 h |
| fix | moving | 3 attempt(s) in 3 h | 0.5 h |
| txt | moving | 208 clean, 6 failing | 7.2 h |

## Trend

| | 2026-11-26 | 2026-11-27 | |
|:--|--:|--:|:--|
| .docx open | 60 | **116** | +56 |
| .txt failing | 8 | **6** | -2 |
| Google measured | 205 | **206** | +1 |
| Google clean | 47 | **46** | -1 |

## What this pass did

**Matrix is stopped because its LibreOffice half is an engine old, not because a document is missing.** Of the 213 LibreOffice results on disk, 37 carry the engine in the tree. The row used to read "213 of 214" and point at one file; health.py now reports the engine-stamped count beside it, and this report prints it. gverify's last LibreOffice commit was 16:12 UTC, which is the 5.5 h the row reports.

**Today's row was adrift from the live tables and is amended.** It read docx open below the live 116. The .docx table was re-measured on the engine in the tree at 20:43 UTC and the fixer's own report says the table it replaced was optimistic, so the +56 is an honest re-measurement, not 56 new regressions. progress.py --amend rewrote today's row and kept the old numbers in its note. No past row was touched.

**What did not fire, and why.** round.py --phase is fix, so the reopen refused and nothing was reopened. status.py reads IDLE with the slot free, so no dead run held the fixer slot and --release-fixer --force was not run. The fixer half is alive: 3 attempts in the last 3 h, newest commit minutes before this pass.

**No cron tool in this pass.** STEP 3 and the two cron repair steps did not run, and no cron was recreated. This run cannot list crons, read a run, or pause and resume one, so whether the gverify cron is firing, paused or zombie is not knowable from here. The exact calls it would have made are written into BLOCKERS.md.

**Decision.** Matrix is not a coordination fault and not yet a day-old stall: it moved at 16:12 UTC and the wall it hit is the pod's corpus - the LibreOffice planner can only see 37 of the 214 documents, so it reports nothing stale and exits. Nothing is parked. What would overturn this: a gverify pass that commits LibreOffice results and still leaves the on-engine count below 213, or this same row still reading 37 on engine at a pass a day from now. Either turns it into a woken cron or a corpus-build fault, and then it is decided, not recorded again.
