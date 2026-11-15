# Pipeline audit: the orchestration was reading files nobody writes

## What was wrong

The measurement layer was replaced with `benchmarks/p2w.py` + `benchmarks/gate.py`, which
write `benchmarks/RANKING.csv` and `benchmarks/STATE.json`. The orchestration was not
updated. It still read `BASELINE.md`, `RESULTS.jsonl` and `tools/p2w-bench/DEFECT-CLASSES.md`,
none of which the new pipeline writes.

The result was a phase machine reading an empty table, and every consequence of that:

| component | was reading | is written by the new pipeline? | effect |
|---|---|---|---|
| round.py rows() | tools/BASELINE.md | no | `(0, 0)` - "0 of 0 documents scored" |
| round.py open_classes() | tools/DEFECT-CLASSES.md | no | always 0 - a round could close with every class OPEN |
| round.py release() | tools/DEFECT-CLASSES.md | no | the "do not waste the slot" guard never fired |
| round.py --close-round | tools/DEFECT-CLASSES.md | no | closed rounds with nothing fixed |
| measure_gate.py | BASELINE.md, RESULTS.jsonl | no | passed vacuously (0 == 0) or refused for ever |
| classify_gate.py | DEFECT-CLASSES.md + RESULTS.jsonl | no | **could never return 0** |

**The last row is the one that would have killed rounds 2 and 3.** `classify_gate` required
a `Documents measured: **N of M**` header and a non-empty `RESULTS.jsonl`. With the new
pipeline there is no `RESULTS.jsonl` at all, so it appended "the .docx store is empty" on
every run and always exited 1. The phase would have stopped at classify, the fixer would
never have run, no round would ever close, and rounds 2 and 3 would never have happened -
while all three crons reported success.

## What was changed

**round.py**
- `rows()` reads `benchmarks/RANKING.csv`; a row counts as scored when `share5` is a number
- `class_files()` is the one place that decides which class file the round is judged
  against, and it prefers `benchmarks/DEFECT-CLASSES.md`. Reading both was worse than
  either: the stale `tools/` file still carries OPEN rows, so `--close-round` would refuse
  for ever on classes nobody can fix.
- `open_classes()`, `release()` and `--close-round` all use it, and all match `OPEN` as a
  **cell** rather than `endswith("| OPEN |")` - that old test silently stopped working the
  moment a column was added to its right.
- `--force-round` and `--remeasure` now clear all three slot claims, not one. A claim left
  over from the previous round reads as "a run is working" and idles the first run of the
  new round for up to 45 minutes.
- `status()` no longer promises "208 documents" regardless of the corpus.

**measure_gate.py** - rewritten against `RANKING.csv`:
- every row must be scored, or exempted in `EXEMPT.json` with a reason
- no document may appear twice
- the corpus must hold at least 211 synthetic + the real documents in
  `benchmarks/realworld/`, so a corpus that failed to build cannot read as "all measured"
- **the committed measurement must be stamped with the current round**

**classify_gate.py** - rewritten against `RANKING.csv` + `benchmarks/DEFECT-CLASSES.md`.
It still requires the `Documents measured: **N of M**` header, because a count is content
and survives being copied and checked out, while a timestamp does not.

**gate.py** - stamps `STATE.json` with the round it measured.

## The hole the round stamp closes

A closed round keeps its `RANKING.csv`. So "every row scored" stays true across the round
boundary, and round 2 could have advanced to classify on **round 1's numbers** before the
baseline measured anything. Rounds 2 and 3 would then have run on stale data and proved
nothing. `gate.py` now writes the round into `STATE.json` and `measure_gate` refuses when
that stamp does not match the machine's round.

## Dry run, all three rounds

    round 1 closed -> phase measure, round 2
    negative test ok: round 2 refuses to advance before re-measuring
    round 2 closed -> phase measure, round 3
    negative test ok: round 3 refuses to advance before re-measuring
    round 3 closed -> phase done

    FINAL: round 3 of 3, phase done
    APK may ship: YES

Negative paths also verified: `--advance` refuses while measure is unfinished,
`--close-round` refuses from any phase but fix, and `--close-round` refuses while any class
file still holds an OPEN row.

## Still true, and worth stating

The dry run proves the **state machine** walks three rounds. It does not prove the work
inside them is good - that is what the baseline, classifier and fixer runs are for. What it
does prove is that a round cannot close early, cannot advance on another round's numbers,
and cannot reach `done` without having passed through fix three times.
