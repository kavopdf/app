# P2W Watchdog - Run Report

**22 Nov 2026 · 00:20 IST**

> **The pipeline is moving. Two stages done, two moving, one red - and the red one is a phase gate, not a stopped stage.**

## Stages

| stage | state | progress | age |
|:--|:--|--:|--:|
| measure-google | done | 213 of 213 | 0.2 h |
| matrix | done | 213 of 213 | 0.1 h |
| classify | **stopped** |  | 10.3 h |
| fix | moving |  | 0.4 h |
| txt | moving | 197 clean, 16 failing | 1.4 h |

## Trend

| | 2026-11-20 | 2026-11-21 | |
|:--|--:|--:|:--|
| .docx open | 60 | **59** | -1 |
| .txt failing | 46 | **23** | -23 |
| Google measured | 192 | **192** | no change |
| Google clean | 7 | **6** | -1 |

The row is not new work: `progress.py` found today already has one, so this pass appended nothing and edited no past row. That row stands at 23 failing .txt while the live table reads 16 of 213, because the .txt table was rewritten after the row was written. Read today's number from the stages table above, not from the trend.

## The one red row, read to the evidence

`stage.py` says the stage is classify - the class table is older than the results. `round.py --phase` says the phase is fix. `CLASSIFIER-BRIEF.md` opens with "if the phase is not classify, output not my turn and stop", so the classifier cron has been exiting without work since the class table was last regenerated this morning. From fix there is no way back: `round.py --advance` refuses, and `round.py --reopen` refuses because the phase is not done. That is a phase gate, not a dead cron.

What the content actually says, checked with the tools that own the question:

* `classrow.py` dry run prints 0 rows would change. The LibreOffice class table is current in content; `health.py`'s red row on it compares commit dates, so that half of the red is the instrument, not the work.
* `classify_google.py --check` prints STALE, regenerate it, against the 213 documents measured on the current engine at 18:19-18:28 UTC. The Google class table is genuinely behind those results.
* Neither half blocks the fixer. `classpick.py` computes leverage from `benchmarks/gverify/` directly and printed `t08_line_order` from live results, and the last kept attempt moved 11 documents. The fixer is choosing on current evidence.

## What this pass did not do, and why

* Did not classify. Grouping and ranking is the classifier's job, not the watchdog's.
* Did not close the round to get back to measure. It archives a round whose fix phase is working and blanks the scores.
* Did not force-release the fixer slot. `ROUND.json` holds a claim minutes old and `health.py` reads fix moving; the 22:13 blocker row records a force release that killed a live run and made the next run rebuild its fix from scratch.
* Did not run STEP 3 or STEP 4 A/B. This watchdog has no `cron` tool, so a paused or zombie cron cannot be moved by automation. That is a missing tool, not a decision for a person, and BLOCKERS.md carries the exact calls that are unavailable: `cron(action="list")`, then `cron(action="runs", cron_id=...)` on the classifier, then pause and resume once if `next_fire_at` is stale, never left paused.

## The decision, recorded in BLOCKERS.md

One code change fixes this and nothing else does: give `round.py` a reclassify path - when `stage.py` says classify and the class table's content is stale, allow fix to classify without closing the round and without touching the fixer slot - or let `CLASSIFIER-BRIEF.md` regenerate the class tables on stale content regardless of phase. Overturned if a fixer run ever picks a class the current table no longer lists, or if `classpick.py` starts ranking from the class table instead of `benchmarks/gverify/`. Until then classify reads red every pass while the fixer keeps working.
