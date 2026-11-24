# P2W Watchdog - Run Report

**25 Nov 2026 · 00:18 IST**

> **2 stage(s) stopped: fix, txt**

## Stages

> **Today's row is stale** - google: committed row says 190, the data says 191; google_clean: committed row says 35, the data says 36. The trend below is the committed row; the data has moved.


| stage | state | progress | age |
|:--|:--|--:|--:|
| measure-google | done | 213 of 213 | 3.5 h |
| matrix | done | 213 of 213 | 20.5 h |
| classify | moving |  | 4.8 h |
| fix | **stopped** | 1 attempt(s) in 3 h | 1.7 h |
| txt | **stopped** | 199 clean, 14 failing | 14.5 h |

## Trend

| | 2026-11-23 | 2026-11-24 | |
|:--|--:|--:|:--|
| .docx open | 59 | **59** | no change |
| .txt failing | 14 | **14** | no change |
| Google measured | 190 | **190** | no change |
| Google clean | 30 | **35** | +5 |

## What this pass did

* Read health.py, health.py --stalled, stage.py, progress.py and round.py --phase.
* **A stage is stopped** - see BLOCKERS.md.


## fix: stopped on the beacon, not on output

The run that holds the slot claimed it, beaconed once, and has been silent inside one long step since.
Its claim is still inside round.py's release window, so a forced release would have put a second run
into the engine while the first may still be alive. The slot was left alone; the next scheduled fixer
takes it when the window closes. What would overturn that: the same claim still silent past the
window, with a clean engine tree.

## txt: 14 failing that the baseline cannot move

The .txt table is newer than the engine and both scripts that can change a .txt score, so re-scoring
reproduces it byte for byte. Those 14 failures are engine work and belong to the fixer, not to the
baseline cron. What would overturn that: a .txt table older than its own inputs.

## The trend, and the overturn the previous pass left

The .docx open and .txt failing columns did not move again. Google clean did - the committed row says
35 and the live data says 36 - so the row is reported stale rather than served as current, and the
next row carries the newer figure.

The previous pass left one checkable overturn on the pending queue: if it still held at the same count
at this pass, the queue itself was the stall. It did not hold. classpick.py still refuses a new class
on pending items, but the count has fallen well below what the earlier row recorded, so the queue is
draining and is not the stall. No class was parked, and no phase was re-opened - round.py --reopen
refuses, because the phase is fix and not done.

## The platform, and what this pass could not do

This watchdog has no cron tool, so a paused or zombie cron cannot be moved by automation. The exact
calls it would have made, with the ids from HEALTH-BRIEF's table, are written in BLOCKERS.md. That is
a missing tool, not a decision waiting for a person.

## Instruments repaired

* health.py's fix row asserted "the slot is free" whenever a run stopped beaconing. It was not free:
  the claim was held, and every other run would have stood down. The line now prints the beacon age
  and the age at which round.py frees the claim, read from round.py itself. No threshold moved.
* cronreport.py's stages table was split in two by its own stale-row banner, which printed between the
  header row and the first data row. The banner now sits above the table.
