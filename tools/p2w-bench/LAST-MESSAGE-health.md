# Pipeline watchdog - 23 Nov 2026, 12:25 IST

**Answer: the pipeline is moving. No stage is stopped.**

## The five stages

| stage | state | progress | age |
|---|---|---|---|
| measure-google | done | 213 of 213 | 3.9 h |
| matrix | done | 213 of 213 | 4.5 h |
| classify | superseded | - | 3.8 h |
| fix | moving | 2 attempt(s) in the last three hours | 0.8 h |
| txt | superseded | 199 clean, 14 failing | 0.9 h |

The fix row read stopped when this pass opened: a run was still marked running and had not beaconed for longer than the fixer's stale window. It has since taken the slot again and is beaconing - claim 5.8 min old, verdict WORKING. So nothing needed forcing, and the pair of fixer crons did what the pair exists to do.

## The trend

docx open 59 -> 59, no change. google 192 -> 190. google clean 23 -> 28.

Today's row already existed, so nothing was appended; it reads txt failing 16 where the live table reads 14, so the row is behind the tables rather than wrong when it was written. I did not amend it.

txt failing moving off 16 is real but narrow: it came from a corrected verifier, not from the engine. t09_page_furniture was kept at 11:00 with no engine change, and the re-stamp left 199 of 213 clean with no newly failing document. docx open has not moved in three rows.

## The round

phase fix.

## What I did, and what I could not

The reopen check refused, correctly: the phase is fix, not done.

I did not force-release the fixer slot. Its claim was 44.9 min old against the fixer's stale window and the window closed on its own; the relay then claimed at 12:14 and is alive. A force release kills the claim, not the wedge, and that is how the day's forced releases ended.

The platform half cannot run. This watchdog has no cron tool, so a paused cron, a stale next_fire_at and a zombie run are invisible and unmovable from here. The exact call I would have made is cron with action list, then cron with action runs on the fixer cron and the relay cron. Both cron ids and the whole sequence are written into BLOCKERS.md.

## The .docx stall - my decision

docx open has not moved off 59 in three rows, which is longer than a day, so this is a decision and not a report.

The instrument is not lying: measure_gate reads engine docx 4a607e4b793fb348, tree 4a607e4b793fb348 - READY, every document measured. The class is not unwinnable either: 00_page_count was proven in Google and the patch is committed.

What is wrong is the one step that turns a kept engine change into a moved number, the full-corpus re-measure. gate.py at a corpus-sized budget does not finish inside one call: it returns no output, writes neither table, and a run inside it writes no beacon. The run that went silent at 11:28 died there, and the run that claimed at 12:14 is in the same step now.

The replacement, recorded in BLOCKERS.md: chunk the re-measure so each call fits and a beacon lands between chunks, because gate.py resumes across calls where p2w.py restarts at zero. Then commit the engine, RANKING.csv and STATE.json together, because regress.py will not stamp a table older than the engine it claims to describe.

What would overturn it: a fixer run that completes a corpus re-measure and commits RANKING.csv with the engine, or any future row where docx open differs from 59.

## Also corrected

The 09:05 decision that the .txt stage was stopped by a broken rotation is overturned by its own criterion - a .txt attempt appeared after 21 Nov and txt failing moved off 16. Both happened today.
