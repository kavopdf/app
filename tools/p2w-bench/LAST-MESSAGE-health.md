# P2W Watchdog - Run Report

**22 Nov 2026 · 09:22 IST**

> Nothing is stopped.

## Stages

| stage | state | progress | age |
|:--|:--|--:|--:|
| measure-google | done | 213 of 213 | 3.1 h |
| matrix | done | 213 of 213 | 9.4 h |
| classify | superseded |  | 2.5 h |
| fix | moving |  | 0.9 h |
| txt | moving | 197 clean, 16 failing | 10.7 h |

## Trend

| | 2026-11-21 | 2026-11-22 | |
|:--|--:|--:|:--|
| .docx open | 59 | **59** | no change |
| .txt failing | 23 | **16** | -7 |
| Google measured | 192 | **192** | no change |
| Google clean | 6 | **23** | +17 |

## The fix slot

The fix stage is moving; the slot is what went wrong. The run that claimed it just before nine wrote no
beacon for twenty minutes, and its claim aged past the fixer's own stale window of ten minutes, so I
released it with round.py --release-fixer --force. The run was not dead. It landed its attempt, its
finding and its run report about twenty minutes after my release, and the platform still marks it running.

The stale window is the defect, not the run: the comment beside it says forty-five minutes and the value
is ten, and a run inside one long measurement step writes no beacon until that step finishes. A watchdog
that trusts the window will keep freeing live slots, and two runs editing the engine at once is the
failure the claim exists to prevent. It is written up in BLOCKERS.md with what would close it.

gaps.py also records two silences between a release and the next claim that are longer than the spacing
between the two fixer slots. Whether those are missed fires or busy slots is exactly what
cron(action="list") would answer, and no agent in this pipeline holds it.

## The cron tool

**This watchdog has no cron tool**, so a paused, zombie or stale-firing cron cannot be moved by
automation. That is a missing tool, not a judgement call for a person to make. The exact calls I would
have made: cron(action="list") to read the crons, and for a zombie run cron(action="delete",
cron_id="<id>") followed by cron(action="create", name=<same>, schedule=<same>, prompt=<same>); for a
stale next_fire_at, cron(action="pause", cron_id="<id>") followed by cron(action="resume",
cron_id="<id>"). None of that ran.

## What this pass did

* Read health.py, health.py --stalled, stage.py, progress.py, round.py --phase, status.py, gaps.py and
  the tail of TIMELINE.jsonl.
* Released a fixer claim that read stale and was not; corrected the record in BLOCKERS.md when the run's
  own commits showed it had been alive.
* Wrote the missing cron tool into BLOCKERS.md.

