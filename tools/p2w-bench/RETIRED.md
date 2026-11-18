# RETIRED — files in this directory that describe a pipeline that no longer runs

Nothing here is deleted: a file that is wrong is still evidence of what was tried, and a run that
finds one deserves to know why it is wrong rather than to find it missing.

## The three documents that look live and are not

| file | what it is | what replaced it |
|---|---|---|
| `BASELINE.md` | the old check-id baseline: one row per document, a `40/58` score and a list of failed check ids | `benchmarks/RANKING.csv` - one row per document, `share@5px`, no check ids |
| `DEFECT-CLASSES.md` | the old per-check defect list, keyed by check id (`20_within_10pt`, `47_margins`, ...) | `benchmarks/DEFECT-CLASSES.md` - keyed by measurement signature (`content-missing-nothing-in-its-place`, ...) |
| `INSTRUMENT.md` | how the check-id instrument was defined | `benchmarks/p2w.py` and `tools/p2w-bench/measure_gate.py` |

**`round.py` reads `benchmarks/DEFECT-CLASSES.md` and nothing else.** `class_files()` returns exactly
one path, deliberately - the comment in it explains that reading both is worse than reading either,
because the stale file still carries OPEN rows and `--close-round` would refuse for ever on classes
nobody can fix. That guard is why these three can sit here harmlessly; it is not a reason to read them.

## The patches that cannot be applied

Twenty-three of the twenty-nine patches in `patches/` and `tools/p2w-bench/patches/` do not apply to
`ead0d0e`. They were written against an engine state that no longer exists, and their class labels are
check ids the live classification has none of. `PATCH-AUDIT.md` records the measurement of all
twenty-nine: six apply, none can be kept.

They are kept as files for the same reason as everything else here - the mechanism each one tried is
written down in its diff, and a future fix can read it instead of re-deriving it from a cold start.
`git apply` will refuse them, which is the correct outcome and not a bug to work around.
