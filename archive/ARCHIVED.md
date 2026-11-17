# Archived files - where they are, and how to get one back

Nothing here was deleted from the repository's history. Each file below was removed from HEAD
because no tool the pipeline runs opens it, and it remains readable at the commit named here.

    git show 845ff42:tools/p2w-bench/RATCHET.json

That command works for every path below, for ever.

The decision was made by measurement, not by eye: `tools/p2w-bench/archive.py --report` greps
every tool the crons actually run for an EXACT reference - not a substring, because
`RANKING-BASELINE.csv` matches `BASELINE` and that false positive is exactly how a live file gets
archived by mistake.

| file | size | why it was not live |
|---|---|---|
| `tools/p2w-bench/RATCHET.json` | 562 KB | read only by retired ratchet.py and the old verify_google flow |
| `tools/p2w-bench/RATCHET-20261112-095333.json` | 394 KB | timestamped backup of a file nothing reads |
| `tools/p2w-bench/RATCHET-20261112-095452.json` | 394 KB | timestamped backup of a file nothing reads |
| `tools/p2w-bench/RATCHET-20261113-062943.json` | 399 KB | timestamped backup of a file nothing reads |
| `tools/p2w-bench/RATCHET-20261113-075538.json` | 398 KB | timestamped backup of a file nothing reads |
| `tools/p2w-bench/RATCHET-20261113-084751.json` | 394 KB | timestamped backup of a file nothing reads |
| `tools/p2w-bench/RATCHET-TXT-20261112-095333.json` | 51 KB | timestamped .txt backup, same as above |
| `tools/p2w-bench/RATCHET-TXT-20261112-095452.json` | 51 KB | timestamped .txt backup, same as above |
| `tools/p2w-bench/REMAINING-DEFECTS-ARCHIVE.md` | 312 KB | a file with ARCHIVE already in its name |
| `tools/p2w-bench/base208-position.json` | 146 KB | position dump from the 208-document era; the corpus is 213 |
| `tools/p2w-bench/DEFECTS.md` | 127 KB | old defect table; DEFECT-CLASSES.md replaced it |
| `tools/p2w-bench/VISUAL-SCORE.md` | 103 KB | old visual score table, superseded by RANKING.csv |
| `tools/p2w-bench/BATCH-LOG.md` | 70 KB | the old batch model's log; the baseline now measures all 213 in one run |

Total: 3.3 MB, about a quarter of the repository at the time.

## What stays, and why

`BASELINE.md` was NOT archived even though the briefs call it a dead file: `round.py` still reads
it on a round close (lines 719-754). Archiving a file a live tool opens is how a pipeline breaks
quietly. The briefs should stop calling it dead, or round.py should stop reading it - one of the
two, not neither.

`RUN-LOG.md`, `TRACE.md`, `TIMELINE.jsonl`, `INCIDENTS.md` and `HYPOTHESES.md` are read by
round.py, handoff.py, hypothesis.py and trace.py, so they cannot go. They are append-only, so
archive.py ROTATES them instead: the newest lines stay where the tools expect them and everything
older moves to `archive/<date>/<name>.head`. Rotated, never truncated.

## What runs this

    python3 tools/p2w-bench/archive.py --report    what is unused, and how much
    python3 tools/p2w-bench/archive.py             do it - once per day, idempotent

It checks its own date, so any cron can call it for almost nothing, and it exits 0 always:
housekeeping must never fail a run.
