# P2W Watchdog - Run Report

**24 Nov 2026**

> **1 stage stopped: txt**

The pipeline is moving. The fixer holds the slot and the ledger records its attempts inside the window. One row is red: the `.txt` table is 18.8 h old and both of its inputs moved underneath it. This pass implemented the refresh route rather than describing it again.

## Stages

| stage | state | progress | age |
|:--|:--|--:|--:|
| measure-google | done | 213 of 212 | 2.4 h |
| matrix | done | 213 of 213 | 2.4 h |
| classify | superseded | | 1.8 h |
| fix | moving | | 0.4 h |
| txt | **stopped** | 199 clean, 14 failing | 18.8 h |

## Trend

| | 2026-11-23 | 2026-11-24 | |
|:--|--:|--:|:--|
| .docx open | 59 | **59** | no change |
| .txt failing | 14 | **14** | no change |
| Google measured | 190 | **190** | no change |
| Google clean | 30 | **29** | -1 |

A row that does not move is the signal. The `.txt` row has not moved on consecutive watchdog passes.

## Round

The phase is `fix`.

## What this pass did

* Read health.py, health.py --stalled, stage.py, progress.py --json, round.py --phase and status.py.
* Appended today's row to benchmarks/PROGRESS.md and committed it. No past row was edited.
* **txt stopped - acted, not noted.** restamp_txt.py alone cannot refresh the table: it re-scores the `.txt` files already on disk and refuses in a fresh pod, so the refresh needs p2w.py first. Written into BASELINE-BRIEF.md as a new section, so the next baseline run refreshes the `.txt` half outside the measure phase, claims the baseline slot, and touches nothing else. The evidence and what would overturn it are in BLOCKERS.md.
* No slot was released and none was forced: the fixer claim is fresh, well inside the stale threshold, so it is a working run.
* Nothing was reopened: the phase is `fix`, not `done`.

## The blind spot

This run has **no cron tool**. A paused, zombie or stale-fire cron cannot be moved from here, and health.py reads files - it cannot see the platform. The exact calls that would have been made are named in BLOCKERS.md. No cron was recreated, so no id changed.
